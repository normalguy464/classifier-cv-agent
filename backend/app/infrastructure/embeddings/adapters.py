from __future__ import annotations

import hashlib
import importlib
import math
import re
import unicodedata
from collections.abc import Callable, Sequence
from enum import StrEnum
from typing import Annotated, Protocol, Self, cast

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.app.infrastructure.config.artifacts import EmbeddingModelArtifact


class EmbeddingInputType(StrEnum):
    QUERY = "query"
    PASSAGE = "passage"


class EmbeddingError(RuntimeError):
    pass


class EmbeddingUnavailableError(EmbeddingError):
    pass


class EmbeddingOutputError(EmbeddingError):
    pass


class EmbeddingResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    model_identifier: Annotated[str, Field(min_length=1, max_length=512)]
    model_version: Annotated[str, Field(min_length=1, max_length=256)]
    dimension: int = Field(ge=1, le=65535)
    vectors: Annotated[tuple[tuple[float, ...], ...], Field(min_length=1)]

    @model_validator(mode="after")
    def validate_vectors(self) -> Self:
        for vector in self.vectors:
            if len(vector) != self.dimension:
                raise ValueError("embedding vectors must match the declared dimension")
            if not all(math.isfinite(value) for value in vector):
                raise ValueError("embedding vectors must contain finite values")
        return self


class EmbeddingAdapter(Protocol):
    @property
    def model_identifier(self) -> str: ...

    @property
    def model_version(self) -> str: ...

    def embed(
        self,
        texts: Sequence[str],
        input_type: EmbeddingInputType,
    ) -> EmbeddingResult: ...


class SentenceTransformerModel(Protocol):
    def encode(
        self,
        sentences: list[str],
        *,
        normalize_embeddings: bool,
        convert_to_numpy: bool,
    ) -> object: ...


SentenceTransformerFactory = Callable[[str, str | None], SentenceTransformerModel]


def _validated_texts(texts: Sequence[str]) -> tuple[str, ...]:
    normalized = tuple(unicodedata.normalize("NFKC", text).strip() for text in texts)
    if not normalized or any(not text for text in normalized):
        raise ValueError("embedding input must contain non-empty strings")
    return normalized


class HashingEmbeddingAdapter:
    def __init__(
        self,
        dimension: int = 64,
        model_identifier: str = "deterministic-hashing-embedding",
        model_version: str = "1.0.0",
    ) -> None:
        if dimension < 2 or dimension > 65535:
            raise ValueError("hashing embedding dimension must be between 2 and 65535")
        if not model_identifier.strip() or not model_version.strip():
            raise ValueError("embedding model metadata must be non-empty")
        self._dimension = dimension
        self._model_identifier = model_identifier.strip()
        self._model_version = model_version.strip()

    @property
    def model_identifier(self) -> str:
        return self._model_identifier

    @property
    def model_version(self) -> str:
        return self._model_version

    def embed(
        self,
        texts: Sequence[str],
        input_type: EmbeddingInputType,
    ) -> EmbeddingResult:
        validated = _validated_texts(texts)
        vectors = tuple(self._vector(text, input_type) for text in validated)
        return EmbeddingResult(
            model_identifier=self.model_identifier,
            model_version=self.model_version,
            dimension=self._dimension,
            vectors=vectors,
        )

    def _vector(self, text: str, input_type: EmbeddingInputType) -> tuple[float, ...]:
        tokens = re.findall(r"\w+", text.casefold(), flags=re.UNICODE)
        values = [0.0] * self._dimension
        for token in (input_type.value, *tokens):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], byteorder="big") % self._dimension
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            values[index] += sign
        norm = math.sqrt(sum(value * value for value in values))
        if norm == 0:
            raise EmbeddingOutputError("hashing embedding produced a zero vector")
        return tuple(value / norm for value in values)


class SentenceTransformerEmbeddingAdapter:
    def __init__(
        self,
        model_identifier: str,
        model_version: str,
        model_revision: str | None = None,
        expected_dimension: int | None = None,
        query_prefix: str = "query",
        passage_prefix: str = "passage",
        model_factory: SentenceTransformerFactory | None = None,
    ) -> None:
        if not model_identifier.strip() or not model_version.strip():
            raise ValueError("embedding model metadata must be non-empty")
        if expected_dimension is not None and expected_dimension < 1:
            raise ValueError("expected embedding dimension must be positive")
        if not query_prefix.strip() or not passage_prefix.strip():
            raise ValueError("embedding prefixes must be non-empty")
        if query_prefix.strip() == passage_prefix.strip():
            raise ValueError("embedding query and passage prefixes must differ")
        self._model_identifier = model_identifier.strip()
        self._model_version = model_version.strip()
        self._model_revision = model_revision.strip() if model_revision is not None else None
        self._expected_dimension = expected_dimension
        self._prefixes = {
            EmbeddingInputType.QUERY: query_prefix.strip(),
            EmbeddingInputType.PASSAGE: passage_prefix.strip(),
        }
        self._model_factory = model_factory or self._default_model_factory
        self._model: SentenceTransformerModel | None = None

    @classmethod
    def from_configuration(
        cls,
        configuration: EmbeddingModelArtifact,
        model_factory: SentenceTransformerFactory | None = None,
    ) -> SentenceTransformerEmbeddingAdapter:
        return cls(
            model_identifier=configuration.model_identifier,
            model_version=(configuration.resolved_revision or configuration.model_version),
            model_revision=configuration.resolved_revision,
            expected_dimension=configuration.dimension,
            query_prefix=configuration.query_prefix,
            passage_prefix=configuration.passage_prefix,
            model_factory=model_factory,
        )

    @property
    def model_identifier(self) -> str:
        return self._model_identifier

    @property
    def model_version(self) -> str:
        return self._model_version

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    def embed(
        self,
        texts: Sequence[str],
        input_type: EmbeddingInputType,
    ) -> EmbeddingResult:
        validated = _validated_texts(texts)
        prefixed = [f"{self._prefixes[input_type]}: {text}" for text in validated]
        model = self._load_model()
        try:
            encoded = model.encode(
                prefixed,
                normalize_embeddings=True,
                convert_to_numpy=True,
            )
        except Exception as error:
            raise EmbeddingUnavailableError("sentence transformer encoding failed") from error
        array = np.asarray(encoded, dtype=np.float64)
        self._validate_array(array, len(validated))
        dimension = int(array.shape[1])
        return EmbeddingResult(
            model_identifier=self.model_identifier,
            model_version=self.model_version,
            dimension=dimension,
            vectors=tuple(tuple(float(value) for value in row) for row in array),
        )

    def _load_model(self) -> SentenceTransformerModel:
        if self._model is None:
            try:
                self._model = self._model_factory(
                    self.model_identifier,
                    self._model_revision,
                )
            except Exception as error:
                raise EmbeddingUnavailableError(
                    "sentence transformer model loading failed"
                ) from error
        return self._model

    def _validate_array(
        self, array: np.ndarray[tuple[int, ...], np.dtype[np.float64]], rows: int
    ) -> None:
        if array.ndim != 2 or array.shape[0] != rows or array.shape[1] < 1:
            raise EmbeddingOutputError("sentence transformer returned an invalid matrix shape")
        if self._expected_dimension is not None and array.shape[1] != self._expected_dimension:
            raise EmbeddingOutputError(
                "sentence transformer dimension does not match configuration"
            )
        if not np.isfinite(array).all():
            raise EmbeddingOutputError("sentence transformer returned non-finite values")
        norms = np.linalg.norm(array, axis=1)
        if np.any(norms == 0):
            raise EmbeddingOutputError("sentence transformer returned a zero vector")

    @staticmethod
    def _default_model_factory(
        model_identifier: str,
        model_revision: str | None,
    ) -> SentenceTransformerModel:
        module = importlib.import_module("sentence_transformers")
        factory = cast(Callable[..., SentenceTransformerModel], module.SentenceTransformer)
        if model_revision is None:
            return factory(model_identifier)
        return factory(model_identifier, revision=model_revision)


class CoreEmbeddingAdapterBridge:
    def __init__(self, adapter: EmbeddingAdapter, query_count: int) -> None:
        if query_count < 1:
            raise ValueError("core embedding query_count must be positive")
        self._adapter = adapter
        self._query_count = query_count

    def embed(self, texts: tuple[str, ...]) -> tuple[tuple[float, ...], ...]:
        if self._query_count > len(texts):
            raise ValueError("core embedding query_count exceeds input count")
        query_vectors = self._adapter.embed(
            texts[: self._query_count],
            EmbeddingInputType.QUERY,
        ).vectors
        passage_texts = texts[self._query_count :]
        if not passage_texts:
            return query_vectors
        passage_vectors = self._adapter.embed(
            passage_texts,
            EmbeddingInputType.PASSAGE,
        ).vectors
        return query_vectors + passage_vectors
