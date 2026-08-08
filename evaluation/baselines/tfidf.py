from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal, ROUND_HALF_UP
from importlib import import_module
from typing import Final, Protocol, cast

from backend.app.contracts import CVProfile, DecisionThresholds, JobProfile
from evaluation.baselines.models import BaselinePrediction, threshold_decision

SCORE_QUANTUM: Final[Decimal] = Decimal("0.01")


class SparseMatrix(Protocol):
    def __getitem__(self, key: slice) -> SparseMatrix: ...


class SimilarityRow(Protocol):
    def __getitem__(self, index: int) -> float: ...


class SimilarityMatrix(Protocol):
    def __getitem__(self, index: int) -> SimilarityRow: ...


class FittedVectorizer(Protocol):
    def fit_transform(self, raw_documents: Sequence[str]) -> SparseMatrix: ...


class VectorizerFactory(Protocol):
    def __call__(self, *, ngram_range: tuple[int, int]) -> FittedVectorizer: ...


class CosineSimilarity(Protocol):
    def __call__(self, first: SparseMatrix, second: SparseMatrix) -> SimilarityMatrix: ...


_text_module = import_module("sklearn.feature_extraction.text")
_pairwise_module = import_module("sklearn.metrics.pairwise")
_vectorizer_factory = cast(
    VectorizerFactory,
    getattr(_text_module, "TfidfVectorizer"),
)
_cosine_similarity = cast(
    CosineSimilarity,
    getattr(_pairwise_module, "cosine_similarity"),
)


def job_text(job_profile: JobProfile) -> str:
    parts = [job_profile.title, *job_profile.responsibilities]
    parts.extend(
        value
        for requirement in job_profile.requirements
        for value in (requirement.title, requirement.description)
    )
    return " ".join(parts)


def cv_text(cv_profile: CVProfile) -> str:
    parts = [cv_profile.summary or ""]
    parts.extend(skill.name for skill in cv_profile.skills)
    parts.extend(item.text for item in cv_profile.evidence)
    return " ".join(parts)


class TfidfCosineBaseline:
    def predict(
        self,
        cv_profile: CVProfile,
        job_profile: JobProfile,
        thresholds: DecisionThresholds,
    ) -> BaselinePrediction:
        matrix = _vectorizer_factory(ngram_range=(1, 2)).fit_transform(
            (job_text(job_profile), cv_text(cv_profile))
        )
        similarity = float(_cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
        score = (Decimal(str(similarity)) * Decimal("100")).quantize(
            SCORE_QUANTUM,
            rounding=ROUND_HALF_UP,
        )
        return BaselinePrediction(
            score=score,
            decision=threshold_decision(score, thresholds),
            baseline_identifier="tfidf-cosine-v1",
        )
