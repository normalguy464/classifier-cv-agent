from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from math import sqrt

from backend.app.contracts import CVProfile, DecisionThresholds, JobProfile
from backend.app.infrastructure.embeddings import EmbeddingAdapter, EmbeddingInputType
from evaluation.baselines.models import BaselinePrediction, threshold_decision
from evaluation.baselines.tfidf import job_text

SCORE_QUANTUM = Decimal("0.01")


def _cosine(left: tuple[float, ...], right: tuple[float, ...]) -> Decimal:
    numerator = sum(left_value * right_value for left_value, right_value in zip(left, right))
    left_norm = sqrt(sum(value * value for value in left))
    right_norm = sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        raise ValueError("embedding baseline received a zero vector")
    bounded = max(-1.0, min(1.0, numerator / (left_norm * right_norm)))
    return Decimal(str(bounded))


class EmbeddingOnlyBaseline:
    def __init__(
        self,
        adapter: EmbeddingAdapter,
        similarity_floor: Decimal,
        similarity_ceiling: Decimal,
        top_k: int,
    ) -> None:
        if similarity_floor >= similarity_ceiling:
            raise ValueError("embedding similarity range must be increasing")
        if top_k < 1:
            raise ValueError("embedding top_k must be positive")
        self._adapter = adapter
        self._similarity_floor = similarity_floor
        self._similarity_ceiling = similarity_ceiling
        self._top_k = top_k

    def predict(
        self,
        cv_profile: CVProfile,
        job_profile: JobProfile,
        thresholds: DecisionThresholds,
    ) -> BaselinePrediction:
        query = self._adapter.embed(
            (job_text(job_profile),),
            EmbeddingInputType.QUERY,
        ).vectors[0]
        passages = self._adapter.embed(
            tuple(item.text for item in cv_profile.evidence),
            EmbeddingInputType.PASSAGE,
        ).vectors
        similarities = sorted(
            (_cosine(query, passage) for passage in passages),
            reverse=True,
        )[: self._top_k]
        mean_similarity = sum(similarities, Decimal("0")) / Decimal(len(similarities))
        bounded = max(
            self._similarity_floor,
            min(self._similarity_ceiling, mean_similarity),
        )
        score = (
            (bounded - self._similarity_floor)
            / (self._similarity_ceiling - self._similarity_floor)
            * Decimal("100")
        ).quantize(SCORE_QUANTUM, rounding=ROUND_HALF_UP)
        return BaselinePrediction(
            score=score,
            decision=threshold_decision(score, thresholds),
            baseline_identifier=f"embedding-only-{self._adapter.model_version}",
        )
