from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pytest

from backend.app.infrastructure.config import RepositoryConfigurationLoader
from backend.app.infrastructure.embeddings import (
    CoreEmbeddingAdapterBridge,
    EmbeddingInputType,
    EmbeddingOutputError,
    EmbeddingUnavailableError,
    HashingEmbeddingAdapter,
    SentenceTransformerEmbeddingAdapter,
    SentenceTransformerModel,
)


class RecordingSentenceTransformer:
    def __init__(self, output: object) -> None:
        self.output = output
        self.calls: list[tuple[list[str], bool, bool]] = []

    def encode(
        self,
        sentences: list[str],
        *,
        normalize_embeddings: bool,
        convert_to_numpy: bool,
    ) -> object:
        self.calls.append((sentences, normalize_embeddings, convert_to_numpy))
        return self.output


class PrefixRecordingSentenceTransformer:
    def __init__(self) -> None:
        self.calls: list[list[str]] = []

    def encode(
        self,
        sentences: list[str],
        *,
        normalize_embeddings: bool,
        convert_to_numpy: bool,
    ) -> object:
        self.calls.append(sentences)
        return np.array([[1.0, 0.0] for _ in sentences], dtype=np.float64)


def test_hashing_embedding_is_deterministic_bounded_and_normalized() -> None:
    adapter = HashingEmbeddingAdapter(dimension=32)

    first = adapter.embed(("Python và SQL", "REST API"), EmbeddingInputType.PASSAGE)
    second = adapter.embed(("Python và SQL", "REST API"), EmbeddingInputType.PASSAGE)

    assert first == second
    assert first.dimension == 32
    assert first.vectors[0] != first.vectors[1]
    assert all(
        math.isclose(math.sqrt(sum(value * value for value in vector)), 1.0)
        for vector in first.vectors
    )
    assert all(math.isfinite(value) for vector in first.vectors for value in vector)


@pytest.mark.parametrize("texts", [(), ("",), ("  ",)])
def test_embedding_adapters_reject_empty_or_blank_input(texts: tuple[str, ...]) -> None:
    adapter = HashingEmbeddingAdapter()

    with pytest.raises(ValueError, match="non-empty strings"):
        adapter.embed(texts, EmbeddingInputType.QUERY)


def test_sentence_transformer_adapter_is_lazy_and_uses_e5_prefixes() -> None:
    model = RecordingSentenceTransformer(np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float64))
    factory_calls: list[tuple[str, str | None]] = []

    def factory(model_identifier: str, model_revision: str | None) -> SentenceTransformerModel:
        factory_calls.append((model_identifier, model_revision))
        return model

    adapter = SentenceTransformerEmbeddingAdapter(
        model_identifier="test/multilingual-model",
        model_version="model-v1",
        expected_dimension=2,
        model_factory=factory,
    )

    assert adapter.is_loaded is False
    result = adapter.embed(("kỹ năng Python", "dự án SQL"), EmbeddingInputType.PASSAGE)

    assert adapter.is_loaded is True
    assert factory_calls == [("test/multilingual-model", None)]
    assert model.calls == [
        (
            ["passage: kỹ năng Python", "passage: dự án SQL"],
            True,
            True,
        )
    ]
    assert result.dimension == 2
    assert result.vectors == ((1.0, 0.0), (0.0, 1.0))


def test_sentence_transformer_adapter_uses_versioned_model_configuration() -> None:
    root = Path(__file__).resolve().parents[2]
    configuration = RepositoryConfigurationLoader(root).load_models_artifact().embedding
    model = PrefixRecordingSentenceTransformer()

    def factory(model_identifier: str, model_revision: str | None) -> SentenceTransformerModel:
        return model

    adapter = SentenceTransformerEmbeddingAdapter.from_configuration(
        configuration,
        model_factory=factory,
    )

    assert adapter.model_identifier == "intfloat/multilingual-e5-base"
    assert adapter.model_version == "multilingual-e5-base"
    with pytest.raises(EmbeddingOutputError, match="dimension"):
        adapter.embed(("query",), EmbeddingInputType.QUERY)


def test_five_role_runtime_pins_the_resolved_embedding_revision() -> None:
    root = Path(__file__).resolve().parents[2]
    configuration = (
        RepositoryConfigurationLoader(
            root,
            root / "configs" / "runtime" / "five_role_v1",
        )
        .load_models_artifact()
        .embedding
    )
    model = PrefixRecordingSentenceTransformer()
    factory_calls: list[tuple[str, str | None]] = []

    def factory(model_identifier: str, model_revision: str | None) -> SentenceTransformerModel:
        factory_calls.append((model_identifier, model_revision))
        return model

    adapter = SentenceTransformerEmbeddingAdapter.from_configuration(
        configuration,
        model_factory=factory,
    )

    assert adapter.model_version == "d128750597153bb5987e10b1c3493a34e5a4502a"
    with pytest.raises(EmbeddingOutputError, match="dimension"):
        adapter.embed(("query",), EmbeddingInputType.QUERY)
    assert factory_calls == [
        (
            "intfloat/multilingual-e5-base",
            "d128750597153bb5987e10b1c3493a34e5a4502a",
        )
    ]


def test_sentence_transformer_adapter_reuses_loaded_model() -> None:
    model = RecordingSentenceTransformer(np.array([[1.0, 0.0]], dtype=np.float64))
    factory_calls = 0

    def factory(model_identifier: str, model_revision: str | None) -> SentenceTransformerModel:
        nonlocal factory_calls
        factory_calls += 1
        return model

    adapter = SentenceTransformerEmbeddingAdapter(
        "test/model",
        "v1",
        expected_dimension=2,
        model_factory=factory,
    )

    adapter.embed(("first",), EmbeddingInputType.QUERY)
    adapter.embed(("second",), EmbeddingInputType.QUERY)

    assert factory_calls == 1


def test_core_embedding_bridge_preserves_query_and_passage_prefixes() -> None:
    model = PrefixRecordingSentenceTransformer()

    def factory(model_identifier: str, model_revision: str | None) -> SentenceTransformerModel:
        return model

    adapter = SentenceTransformerEmbeddingAdapter(
        "test/model",
        "v1",
        expected_dimension=2,
        query_prefix="query",
        passage_prefix="passage",
        model_factory=factory,
    )
    bridge = CoreEmbeddingAdapterBridge(adapter, query_count=2)

    vectors = bridge.embed(("criterion one", "criterion two", "CV evidence"))

    assert len(vectors) == 3
    assert model.calls == [
        ["query: criterion one", "query: criterion two"],
        ["passage: CV evidence"],
    ]


def test_core_embedding_bridge_validates_query_count() -> None:
    adapter = HashingEmbeddingAdapter()

    with pytest.raises(ValueError, match="positive"):
        CoreEmbeddingAdapterBridge(adapter, query_count=0)

    bridge = CoreEmbeddingAdapterBridge(adapter, query_count=2)
    with pytest.raises(ValueError, match="exceeds"):
        bridge.embed(("only one",))


def test_sentence_transformer_adapter_reports_loading_failure() -> None:
    def failing_factory(
        model_identifier: str,
        model_revision: str | None,
    ) -> SentenceTransformerModel:
        raise RuntimeError("model unavailable")

    adapter = SentenceTransformerEmbeddingAdapter(
        "test/model",
        "v1",
        model_factory=failing_factory,
    )

    with pytest.raises(EmbeddingUnavailableError, match="model loading failed"):
        adapter.embed(("query",), EmbeddingInputType.QUERY)


@pytest.mark.parametrize(
    "output",
    [
        np.array([1.0, 0.0], dtype=np.float64),
        np.array([[1.0, 0.0, 0.0]], dtype=np.float64),
        np.array([[float("nan"), 0.0]], dtype=np.float64),
        np.array([[0.0, 0.0]], dtype=np.float64),
    ],
)
def test_sentence_transformer_adapter_rejects_anomalous_output(output: object) -> None:
    model = RecordingSentenceTransformer(output)

    def factory(model_identifier: str, model_revision: str | None) -> SentenceTransformerModel:
        return model

    adapter = SentenceTransformerEmbeddingAdapter(
        "test/model",
        "v1",
        expected_dimension=2,
        model_factory=factory,
    )

    with pytest.raises(EmbeddingOutputError):
        adapter.embed(("query",), EmbeddingInputType.QUERY)
