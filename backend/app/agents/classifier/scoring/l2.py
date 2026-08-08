from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from math import isfinite, sqrt
from typing import Final, Protocol, TypeAlias, cast

from backend.app.contracts import (
    CVProfile,
    Evidence,
    EvidenceSection,
    EvidenceStatus,
    LevelScoreStatus,
    ScoringRubric,
)
from backend.app.domain import (
    CriterionAssessment,
    L2CriterionPolicy,
    L2Policy,
    L2ScoringMode,
    LevelAssessment,
    ScoringInputError,
    ScoringLevel,
)

EmbeddingVector: TypeAlias = tuple[float, ...]
SCORE_QUANTUM: Final[Decimal] = Decimal("0.01")


class EmbeddingAdapter(Protocol):
    def embed(self, texts: tuple[str, ...]) -> tuple[EmbeddingVector, ...]: ...


class L2ScoreCalibrator(Protocol):
    def calibrate(
        self,
        job_profile_id: str,
        criterion_scores: tuple[Decimal, ...],
    ) -> tuple[Decimal, ...]: ...


class _InvalidEmbeddingOutput(Exception):
    pass


@dataclass(frozen=True, slots=True)
class L2EvidenceMatch:
    evidence_id: str
    section: EvidenceSection
    raw_similarity: Decimal
    normalized_score: Decimal
    adjusted_score: Decimal


@dataclass(frozen=True, slots=True)
class L2QueryTrace:
    query_text: str
    selected_matches: tuple[L2EvidenceMatch, ...]
    effective_score: Decimal
    meets_minimum: bool


@dataclass(frozen=True, slots=True)
class L2CriterionTrace:
    criterion_id: str
    weighted_score: Decimal
    query_traces: tuple[L2QueryTrace, ...]


@dataclass(frozen=True, slots=True)
class L2ScoringTrace:
    criteria: tuple[L2CriterionTrace, ...]


def _validate_policy(
    rubric: ScoringRubric,
    policy: L2Policy,
) -> dict[str, L2CriterionPolicy]:
    if policy.job_profile_id != rubric.job_profile_id:
        raise ScoringInputError("L2 policy job_profile_id must match the rubric")
    policies_by_id = {item.criterion_id: item for item in policy.criteria}
    rubric_ids = {item.criterion_id for item in rubric.criteria}
    policy_ids = set(policies_by_id)
    if policy_ids != rubric_ids:
        raise ScoringInputError("L2 policy criteria must exactly match the rubric criteria")
    return policies_by_id


def _validate_vectors(
    vectors: object,
    expected_count: int,
) -> tuple[EmbeddingVector, ...]:
    if not isinstance(vectors, tuple):
        raise _InvalidEmbeddingOutput
    raw_vectors = cast(tuple[object, ...], vectors)
    if len(raw_vectors) != expected_count:
        raise _InvalidEmbeddingOutput
    dimension: int | None = None
    validated: list[EmbeddingVector] = []
    for raw_vector in raw_vectors:
        if not isinstance(raw_vector, tuple):
            raise _InvalidEmbeddingOutput
        vector = cast(tuple[object, ...], raw_vector)
        if not vector:
            raise _InvalidEmbeddingOutput
        if dimension is None:
            dimension = len(vector)
        if len(vector) != dimension:
            raise _InvalidEmbeddingOutput
        values: list[float] = []
        for value in vector:
            if isinstance(value, bool) or not isinstance(value, (float, int)):
                raise _InvalidEmbeddingOutput
            numeric_value = float(value)
            if not isfinite(numeric_value):
                raise _InvalidEmbeddingOutput
            values.append(numeric_value)
        if sqrt(sum(value * value for value in values)) == 0:
            raise _InvalidEmbeddingOutput
        validated.append(tuple(values))
    return tuple(validated)


def _cosine_similarity(left: EmbeddingVector, right: EmbeddingVector) -> Decimal:
    numerator = sum(left_value * right_value for left_value, right_value in zip(left, right))
    left_norm = sqrt(sum(value * value for value in left))
    right_norm = sqrt(sum(value * value for value in right))
    similarity = numerator / (left_norm * right_norm)
    bounded = min(1.0, max(-1.0, similarity))
    return Decimal(str(bounded))


def _normalized_similarity_score(
    similarity: Decimal,
    policy: L2CriterionPolicy,
) -> Decimal:
    bounded = min(policy.similarity_ceiling, max(policy.similarity_floor, similarity))
    normalized = (
        (bounded - policy.similarity_floor)
        / (policy.similarity_ceiling - policy.similarity_floor)
        * Decimal("100")
    )
    return normalized.quantize(SCORE_QUANTUM, rounding=ROUND_HALF_UP)


def _eligible_evidence(
    cv_profile: CVProfile,
    policy: L2CriterionPolicy,
) -> tuple[Evidence, ...]:
    allowed_sections = set(policy.evidence_sections)
    return tuple(item for item in cv_profile.evidence if item.section in allowed_sections)


def _evidence_match(
    policy: L2CriterionPolicy,
    query_vector: EmbeddingVector,
    evidence: Evidence,
    evidence_vector: EmbeddingVector,
) -> L2EvidenceMatch:
    raw_similarity = _cosine_similarity(query_vector, evidence_vector)
    normalized_score = _normalized_similarity_score(raw_similarity, policy)
    adjusted_score = (normalized_score * policy.section_weight(evidence.section)).quantize(
        SCORE_QUANTUM, rounding=ROUND_HALF_UP
    )
    return L2EvidenceMatch(
        evidence_id=evidence.evidence_id,
        section=evidence.section,
        raw_similarity=raw_similarity,
        normalized_score=normalized_score,
        adjusted_score=adjusted_score,
    )


def _legacy_assessment(
    policy: L2CriterionPolicy,
    criterion_weight: Decimal,
    query_vector: EmbeddingVector,
    evidence: tuple[Evidence, ...],
    evidence_vectors: dict[str, EmbeddingVector],
) -> tuple[CriterionAssessment, L2CriterionTrace]:
    if not evidence:
        assessment = CriterionAssessment(
            criterion_id=policy.criterion_id,
            weighted_score=Decimal("0"),
            evidence_status=EvidenceStatus.MISSING,
            evidence_ids=(),
            rationale="No evidence is available in the configured CV sections.",
        )
        return assessment, L2CriterionTrace(
            criterion_id=policy.criterion_id,
            weighted_score=Decimal("0"),
            query_traces=(
                L2QueryTrace(
                    query_text=policy.query_text,
                    selected_matches=(),
                    effective_score=Decimal("0"),
                    meets_minimum=False,
                ),
            ),
        )
    ranked = sorted(
        (
            (_cosine_similarity(query_vector, evidence_vectors[item.evidence_id]), item)
            for item in evidence
        ),
        key=lambda pair: (-pair[0], pair[1].evidence_id),
    )
    selected = tuple(ranked[: policy.top_k])
    mean_similarity = sum((item[0] for item in selected), Decimal("0")) / Decimal(len(selected))
    normalized_score = _normalized_similarity_score(mean_similarity, policy)
    weighted_score = (normalized_score * criterion_weight / Decimal("100")).quantize(
        SCORE_QUANTUM, rounding=ROUND_HALF_UP
    )
    matches = tuple(
        _evidence_match(policy, query_vector, item, evidence_vectors[item.evidence_id])
        for _, item in selected
    )
    trace = L2CriterionTrace(
        criterion_id=policy.criterion_id,
        weighted_score=weighted_score,
        query_traces=(
            L2QueryTrace(
                query_text=policy.query_text,
                selected_matches=matches,
                effective_score=normalized_score,
                meets_minimum=weighted_score > Decimal("0"),
            ),
        ),
    )
    if weighted_score == Decimal("0"):
        return CriterionAssessment(
            criterion_id=policy.criterion_id,
            weighted_score=weighted_score,
            evidence_status=EvidenceStatus.MISSING,
            evidence_ids=(),
            rationale="No section-level evidence reached the configured semantic relevance floor.",
        ), trace
    return CriterionAssessment(
        criterion_id=policy.criterion_id,
        weighted_score=weighted_score,
        evidence_status=EvidenceStatus.SATISFIED,
        evidence_ids=tuple(item[1].evidence_id for item in selected),
        rationale=f"Top section-level semantic similarity was {selected[0][0]:.4f}.",
    ), trace


def _coverage_query_trace(
    policy: L2CriterionPolicy,
    query_text: str,
    query_vector: EmbeddingVector,
    evidence: tuple[Evidence, ...],
    evidence_vectors: dict[str, EmbeddingVector],
) -> L2QueryTrace:
    matches = tuple(
        _evidence_match(policy, query_vector, item, evidence_vectors[item.evidence_id])
        for item in evidence
    )
    ranked = sorted(
        matches,
        key=lambda item: (-item.adjusted_score, -item.raw_similarity, item.evidence_id),
    )
    selected = tuple(ranked[: policy.top_k])
    query_score = (
        sum((item.adjusted_score for item in selected), Decimal("0")) / Decimal(len(selected))
        if selected
        else Decimal("0")
    ).quantize(SCORE_QUANTUM, rounding=ROUND_HALF_UP)
    meets_minimum = query_score >= policy.minimum_query_score and query_score > Decimal("0")
    return L2QueryTrace(
        query_text=query_text,
        selected_matches=selected,
        effective_score=query_score if meets_minimum else Decimal("0"),
        meets_minimum=meets_minimum,
    )


def _coverage_assessment(
    policy: L2CriterionPolicy,
    criterion_weight: Decimal,
    query_vectors: tuple[EmbeddingVector, ...],
    evidence: tuple[Evidence, ...],
    evidence_vectors: dict[str, EmbeddingVector],
) -> tuple[CriterionAssessment, L2CriterionTrace]:
    query_traces = tuple(
        _coverage_query_trace(policy, query_text, query_vector, evidence, evidence_vectors)
        for query_text, query_vector in zip(policy.query_texts, query_vectors, strict=True)
    )
    normalized_score = (
        sum((item.effective_score for item in query_traces), Decimal("0"))
        / Decimal(len(query_traces))
    ).quantize(SCORE_QUANTUM, rounding=ROUND_HALF_UP)
    weighted_score = (normalized_score * criterion_weight / Decimal("100")).quantize(
        SCORE_QUANTUM, rounding=ROUND_HALF_UP
    )
    trace = L2CriterionTrace(
        criterion_id=policy.criterion_id,
        weighted_score=weighted_score,
        query_traces=query_traces,
    )
    active_traces = tuple(item for item in query_traces if item.meets_minimum)
    if not active_traces:
        return CriterionAssessment(
            criterion_id=policy.criterion_id,
            weighted_score=Decimal("0"),
            evidence_status=EvidenceStatus.MISSING,
            evidence_ids=(),
            rationale="No semantic query reached the configured relevance and section-quality minimum.",
        ), trace
    evidence_ids = tuple(
        dict.fromkeys(
            match.evidence_id
            for query_trace in active_traces
            for match in query_trace.selected_matches
            if match.adjusted_score > Decimal("0")
        )
    )
    selected_raw = tuple(
        match.raw_similarity
        for query_trace in query_traces
        for match in query_trace.selected_matches
    )
    mean_raw = sum(selected_raw, Decimal("0")) / Decimal(len(selected_raw))
    return CriterionAssessment(
        criterion_id=policy.criterion_id,
        weighted_score=weighted_score,
        evidence_status=EvidenceStatus.SATISFIED,
        evidence_ids=evidence_ids,
        rationale=(
            f"Semantic query coverage was {len(active_traces)}/{len(query_traces)}; "
            f"mean selected raw similarity was {mean_raw:.4f}."
        ),
    ), trace


def _criterion_assessment(
    policy: L2CriterionPolicy,
    criterion_weight: Decimal,
    query_vectors: tuple[EmbeddingVector, ...],
    evidence: tuple[Evidence, ...],
    evidence_vectors: dict[str, EmbeddingVector],
) -> tuple[CriterionAssessment, L2CriterionTrace]:
    if policy.scoring_mode is L2ScoringMode.QUERY_COVERAGE:
        return _coverage_assessment(
            policy,
            criterion_weight,
            query_vectors,
            evidence,
            evidence_vectors,
        )
    return _legacy_assessment(
        policy,
        criterion_weight,
        query_vectors[0],
        evidence,
        evidence_vectors,
    )


def score_l2(
    cv_profile: CVProfile,
    rubric: ScoringRubric,
    policy: L2Policy,
    embedding_adapter: EmbeddingAdapter,
    score_calibrator: L2ScoreCalibrator | None = None,
) -> LevelAssessment:
    assessment, _ = score_l2_with_trace(
        cv_profile,
        rubric,
        policy,
        embedding_adapter,
        score_calibrator,
    )
    return assessment


def score_l2_with_trace(
    cv_profile: CVProfile,
    rubric: ScoringRubric,
    policy: L2Policy,
    embedding_adapter: EmbeddingAdapter,
    score_calibrator: L2ScoreCalibrator | None = None,
) -> tuple[LevelAssessment, L2ScoringTrace | None]:
    policies_by_id = _validate_policy(rubric, policy)
    ordered_policies = tuple(policies_by_id[item.criterion_id] for item in rubric.criteria)
    configured_sections = {
        section for item in ordered_policies for section in item.evidence_sections
    }
    evidence = tuple(item for item in cv_profile.evidence if item.section in configured_sections)
    query_texts = tuple(query_text for item in ordered_policies for query_text in item.query_texts)
    texts = query_texts + tuple(item.text for item in evidence)
    try:
        raw_vectors = embedding_adapter.embed(texts)
    except Exception:
        return (
            LevelAssessment.unavailable(
                ScoringLevel.L2,
                "L2 embedding provider is unavailable.",
            ),
            None,
        )
    try:
        vectors = _validate_vectors(raw_vectors, len(texts))
    except _InvalidEmbeddingOutput:
        return (
            LevelAssessment.invalid(
                ScoringLevel.L2,
                "L2 embedding provider returned invalid vectors.",
            ),
            None,
        )
    query_vectors = vectors[: len(query_texts)]
    evidence_vectors = {
        item.evidence_id: vector
        for item, vector in zip(evidence, vectors[len(query_texts) :], strict=True)
    }
    criteria_by_id = {item.criterion_id: item for item in rubric.criteria}
    results: list[tuple[CriterionAssessment, L2CriterionTrace]] = []
    query_offset = 0
    for criterion_policy in ordered_policies:
        criterion_query_count = len(criterion_policy.query_texts)
        results.append(
            _criterion_assessment(
                criterion_policy,
                criteria_by_id[criterion_policy.criterion_id].weight,
                query_vectors[query_offset : query_offset + criterion_query_count],
                _eligible_evidence(cv_profile, criterion_policy),
                evidence_vectors,
            )
        )
        query_offset += criterion_query_count
    assessments = tuple(item[0] for item in results)
    traces = tuple(item[1] for item in results)
    if score_calibrator is not None:
        try:
            calibrated_scores = score_calibrator.calibrate(
                rubric.job_profile_id,
                tuple(item.weighted_score for item in assessments),
            )
        except (RuntimeError, ValueError):
            return (
                LevelAssessment.unavailable(
                    ScoringLevel.L2,
                    "L2 score calibration is unavailable or invalid.",
                ),
                None,
            )
        if len(calibrated_scores) != len(assessments):
            return (
                LevelAssessment.invalid(
                    ScoringLevel.L2,
                    "L2 score calibrator returned an invalid criterion count.",
                ),
                None,
            )
        try:
            assessments = tuple(
                CriterionAssessment(
                    criterion_id=assessment.criterion_id,
                    weighted_score=score.quantize(SCORE_QUANTUM, rounding=ROUND_HALF_UP),
                    evidence_status=assessment.evidence_status,
                    evidence_ids=assessment.evidence_ids,
                    rationale=f"{assessment.rationale} Calibrated by the configured L2 model.",
                )
                for assessment, score in zip(assessments, calibrated_scores, strict=True)
            )
        except ScoringInputError:
            return (
                LevelAssessment.invalid(
                    ScoringLevel.L2,
                    "L2 score calibrator returned out-of-range criterion scores.",
                ),
                None,
            )
        traces = tuple(
            L2CriterionTrace(
                criterion_id=trace.criterion_id,
                weighted_score=assessment.weighted_score,
                query_traces=trace.query_traces,
            )
            for assessment, trace in zip(assessments, traces, strict=True)
        )
    level = LevelAssessment(
        level=ScoringLevel.L2,
        status=LevelScoreStatus.AVAILABLE,
        score=sum(
            (assessment.weighted_score for assessment in assessments),
            Decimal("0"),
        ).quantize(SCORE_QUANTUM, rounding=ROUND_HALF_UP),
        criterion_assessments=assessments,
    )
    return level, L2ScoringTrace(criteria=traces)
