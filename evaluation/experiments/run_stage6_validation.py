from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from collections import Counter
from dataclasses import asdict, dataclass, replace
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from statistics import mean
from typing import cast

from backend.app.agents.classifier.routing import route_classification
from backend.app.agents.classifier.scoring import (
    L3Provider,
    L3ProviderRequest,
    aggregate_level_scores,
    score_l1,
    score_l2,
    score_l3,
)
from backend.app.contracts import (
    ClassificationDecision,
    LevelScoreStatus,
)
from backend.app.domain import (
    BoundaryRule,
    L2Policy,
    LevelAssessment,
    RoutingPolicy,
)
from backend.app.infrastructure.config import (
    RepositoryConfigurationLoader,
    build_l2_policy,
    build_routing_policy,
)
from backend.app.infrastructure.embeddings import (
    CoreEmbeddingAdapterBridge,
    EmbeddingAdapter as RuntimeEmbeddingAdapter,
    HashingEmbeddingAdapter,
    SentenceTransformerEmbeddingAdapter,
)
from backend.app.infrastructure.llm import DeterministicCoreL3Provider
from evaluation.datasets import ReviewedStage4Example, load_stage6_validation
from evaluation.experiments.stage6_config import (
    Stage6Candidate,
    Stage6CandidateSet,
    load_stage6_candidate_set,
)
from evaluation.metrics import ClassificationMetrics, calculate_metrics

REPORT_PATH = Path("evaluation/reports/stage6_validation_tuning_v1.json")
SPLIT_MANIFEST_PATH = Path("data/splits/stage6_split_manifest_v1.json")


@dataclass(frozen=True, slots=True)
class EmbeddingRuntime:
    adapter: RuntimeEmbeddingAdapter
    model_identifier: str
    configured_model_version: str
    resolved_model_revision: str
    configured_model_executed: bool

    def __post_init__(self) -> None:
        if (
            not self.model_identifier.strip()
            or not self.configured_model_version.strip()
            or not self.resolved_model_revision.strip()
        ):
            raise ValueError("embedding runtime metadata must not be empty")


@dataclass(frozen=True, slots=True)
class L3ExecutionMetadata:
    strategy_identifier: str
    provider_identifier: str
    model_identifier: str
    prompt_version: str
    live_provider_executed: bool

    def __post_init__(self) -> None:
        if (
            not self.strategy_identifier.strip()
            or not self.provider_identifier.strip()
            or not self.model_identifier.strip()
            or not self.prompt_version.strip()
        ):
            raise ValueError("L3 execution metadata must not be empty")


@dataclass(frozen=True, slots=True)
class ValidationAssessments:
    example: ReviewedStage4Example
    l1: LevelAssessment
    configured_l2_by_candidate: dict[str, LevelAssessment]
    hashing_l2: LevelAssessment
    l3: LevelAssessment
    routing_policy: RoutingPolicy


@dataclass(frozen=True, slots=True)
class CandidateOutcome:
    candidate: Stage6Candidate
    predictions: tuple[ClassificationDecision, ...]
    metrics: ClassificationMetrics
    needs_review_recall: float
    false_reject_case_ids: tuple[str, ...]
    unsafe_pass_case_ids: tuple[str, ...]
    mismatch_case_ids: tuple[str, ...]
    review_rate: float
    decision_distribution: dict[str, int]
    review_reason_distribution: dict[str, int]
    cases: tuple[dict[str, object], ...]


class CachingCoreEmbeddingAdapter:
    def __init__(self, bridge: CoreEmbeddingAdapterBridge) -> None:
        self._bridge = bridge
        self._cache: dict[
            tuple[str, ...],
            tuple[tuple[float, ...], ...],
        ] = {}

    def embed(self, texts: tuple[str, ...]) -> tuple[tuple[float, ...], ...]:
        if texts not in self._cache:
            self._cache[texts] = self._bridge.embed(texts)
        return self._cache[texts]


def _timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError("generated_at must be an ISO 8601 timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("generated_at must include a timezone")
    return parsed


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def _score(value: Decimal | None) -> float | None:
    if value is None:
        return None
    return float(value)


def _configured_runtime(
    repository_root: Path,
    first_job_profile_id: str,
    candidate_set: Stage6CandidateSet,
) -> EmbeddingRuntime:
    loaded = RepositoryConfigurationLoader(repository_root).load_for_job(first_job_profile_id)
    configuration = loaded.models_artifact.embedding
    return EmbeddingRuntime(
        adapter=SentenceTransformerEmbeddingAdapter.from_configuration(configuration),
        model_identifier=configuration.model_identifier,
        configured_model_version=configuration.model_version,
        resolved_model_revision=(candidate_set.model_strategy.embedding_resolved_revision),
        configured_model_executed=True,
    )


async def _assess_validation(
    repository_root: Path,
    examples: tuple[ReviewedStage4Example, ...],
    embedding_runtime: EmbeddingRuntime,
    candidate_set: Stage6CandidateSet,
    l3_provider: L3Provider | None = None,
    l3_prompt_version: str | None = None,
) -> tuple[ValidationAssessments, ...]:
    loader = RepositoryConfigurationLoader(repository_root)
    configured_bridge = CachingCoreEmbeddingAdapter(
        CoreEmbeddingAdapterBridge(
            embedding_runtime.adapter,
            query_count=5,
        )
    )
    hashing_bridge = CoreEmbeddingAdapterBridge(
        HashingEmbeddingAdapter(dimension=768),
        query_count=5,
    )
    assessments: list[ValidationAssessments] = []
    for example in examples:
        loaded = loader.load_for_job(example.job_profile_id)
        configured_model = loaded.models_artifact.embedding
        if embedding_runtime.configured_model_executed and (
            embedding_runtime.model_identifier != configured_model.model_identifier
            or embedding_runtime.configured_model_version != configured_model.model_version
        ):
            raise ValueError("Stage 6 runtime must match configured embedding metadata")
        l1_policy = loader.load_l1_policy(example.job_profile_id)
        l1 = score_l1(example.cv_profile, loaded.rubric, l1_policy)
        base_l2_policy = build_l2_policy(loaded)
        configured_l2_by_candidate = {
            candidate.candidate_id: score_l2(
                example.cv_profile,
                loaded.rubric,
                _candidate_l2_policy(base_l2_policy, candidate),
                configured_bridge,
            )
            for candidate in candidate_set.candidates
        }
        hashing_l2 = score_l2(
            example.cv_profile,
            loaded.rubric,
            base_l2_policy,
            hashing_bridge,
        )
        active_l3_provider = l3_provider or DeterministicCoreL3Provider(l1_policy)
        l3 = await score_l3(
            L3ProviderRequest(
                cv_profile=example.cv_profile,
                job_profile=loaded.job_profile,
                rubric=loaded.rubric,
                prompt_version=(
                    l3_prompt_version or loaded.classification_config.models.prompt_version
                ),
            ),
            active_l3_provider,
        )
        assessments.append(
            ValidationAssessments(
                example=example,
                l1=l1,
                configured_l2_by_candidate=configured_l2_by_candidate,
                hashing_l2=hashing_l2,
                l3=l3,
                routing_policy=build_routing_policy(loaded),
            )
        )
    if embedding_runtime.configured_model_executed and any(
        assessment.status is not LevelScoreStatus.AVAILABLE
        for item in assessments
        for assessment in item.configured_l2_by_candidate.values()
    ):
        raise RuntimeError("configured multilingual L2 failed during Stage 6 validation")
    return tuple(assessments)


def _candidate_l2_policy(
    base: L2Policy,
    candidate: Stage6Candidate,
) -> L2Policy:
    matching = candidate.l2_matching
    return replace(
        base,
        criteria=tuple(
            replace(
                criterion,
                similarity_floor=matching.similarity_floor,
                similarity_ceiling=matching.similarity_ceiling,
                top_k=matching.top_k,
            )
            for criterion in base.criteria
        ),
    )


def _candidate_routing_policy(
    base: RoutingPolicy,
    candidate: Stage6Candidate,
) -> RoutingPolicy:
    offset = candidate.boundary_offset_points
    return replace(
        base,
        pass_minimum=candidate.thresholds.pass_minimum,
        waitlist_minimum=candidate.thresholds.waitlist_minimum,
        disagreement_points=candidate.disagreement_points,
        boundary_rules=(
            BoundaryRule(
                rule_id="lower-threshold-boundary",
                minimum=candidate.thresholds.waitlist_minimum - offset,
                maximum=candidate.thresholds.waitlist_minimum + offset,
            ),
            BoundaryRule(
                rule_id="upper-threshold-boundary",
                minimum=candidate.thresholds.pass_minimum - offset,
                maximum=candidate.thresholds.pass_minimum + offset,
            ),
        ),
    )


def _metrics_payload(metrics: ClassificationMetrics) -> dict[str, object]:
    return {
        "sample_count": metrics.sample_count,
        "accuracy": metrics.accuracy,
        "macro_f1": metrics.macro_f1,
        "cohen_kappa": metrics.cohen_kappa,
        "labels": {label: asdict(label_metrics) for label, label_metrics in metrics.labels.items()},
        "confusion_matrix": [list(row) for row in metrics.confusion_matrix],
    }


def _candidate_payload(candidate: Stage6Candidate) -> dict[str, object]:
    return {
        "candidate_id": candidate.candidate_id,
        "description": candidate.description,
        "l2_matching": {
            "similarity_floor": float(candidate.l2_matching.similarity_floor),
            "similarity_ceiling": float(candidate.l2_matching.similarity_ceiling),
            "top_k": candidate.l2_matching.top_k,
        },
        "aggregation": {
            "l1_deterministic_rules": float(candidate.aggregation.l1_deterministic_rules),
            "l2_section_semantic_matching": float(
                candidate.aggregation.l2_section_semantic_matching
            ),
            "l3_evidence_grounded_reasoning": float(
                candidate.aggregation.l3_evidence_grounded_reasoning
            ),
        },
        "thresholds": {
            "pass_minimum": float(candidate.thresholds.pass_minimum),
            "waitlist_minimum": float(candidate.thresholds.waitlist_minimum),
        },
        "disagreement_points": float(candidate.disagreement_points),
        "boundary_offset_points": float(candidate.boundary_offset_points),
    }


def _candidate_outcome(
    assessments: tuple[ValidationAssessments, ...],
    candidate: Stage6Candidate,
    use_hashing_l2: bool,
) -> CandidateOutcome:
    expected = tuple(item.example.final_label for item in assessments)
    predictions: list[ClassificationDecision] = []
    cases: list[dict[str, object]] = []
    reason_counts: Counter[str] = Counter()
    for item in assessments:
        l2 = (
            item.hashing_l2
            if use_hashing_l2
            else item.configured_l2_by_candidate[candidate.candidate_id]
        )
        aggregation = aggregate_level_scores(
            (item.l1, l2, item.l3),
            candidate.aggregation,
        )
        routing = route_classification(
            aggregation,
            item.l1.requirement_assessments,
            _candidate_routing_policy(item.routing_policy, candidate),
        )
        predictions.append(routing.decision)
        reason_counts.update(routing.reasons)
        cases.append(
            {
                "cv_profile_id": item.example.cv_profile.cv_profile_id,
                "job_profile_id": item.example.job_profile_id,
                "expected_label": item.example.final_label.value,
                "predicted_label": routing.decision.value,
                "label_match": routing.decision is item.example.final_label,
                "level_scores": {
                    "l1": _score(item.l1.score),
                    "l2": _score(l2.score),
                    "l3": _score(item.l3.score),
                },
                "final_score": _score(routing.final_score),
                "review_reasons": list(routing.reasons),
            }
        )
    predicted = tuple(predictions)
    expected_needs_review = tuple(
        index
        for index, label in enumerate(expected)
        if label is ClassificationDecision.NEEDS_REVIEW
    )
    needs_review_hits = sum(
        predicted[index] is ClassificationDecision.NEEDS_REVIEW for index in expected_needs_review
    )
    needs_review_recall = needs_review_hits / len(expected_needs_review)
    false_reject_ids = tuple(
        item.example.cv_profile.cv_profile_id
        for item, expected_label, predicted_label in zip(
            assessments,
            expected,
            predicted,
            strict=True,
        )
        if predicted_label is ClassificationDecision.REJECT
        and expected_label is not ClassificationDecision.REJECT
    )
    unsafe_pass_ids = tuple(
        item.example.cv_profile.cv_profile_id
        for item, expected_label, predicted_label in zip(
            assessments,
            expected,
            predicted,
            strict=True,
        )
        if predicted_label is ClassificationDecision.PASS
        and expected_label
        in {
            ClassificationDecision.REJECT,
            ClassificationDecision.NEEDS_REVIEW,
        }
    )
    mismatch_ids = tuple(
        item.example.cv_profile.cv_profile_id
        for item, expected_label, predicted_label in zip(
            assessments,
            expected,
            predicted,
            strict=True,
        )
        if predicted_label is not expected_label
    )
    return CandidateOutcome(
        candidate=candidate,
        predictions=predicted,
        metrics=calculate_metrics(expected, predicted),
        needs_review_recall=needs_review_recall,
        false_reject_case_ids=false_reject_ids,
        unsafe_pass_case_ids=unsafe_pass_ids,
        mismatch_case_ids=mismatch_ids,
        review_rate=(
            sum(label is ClassificationDecision.NEEDS_REVIEW for label in predicted)
            / len(predicted)
        ),
        decision_distribution=dict(sorted(Counter(label.value for label in predicted).items())),
        review_reason_distribution=dict(sorted(reason_counts.items())),
        cases=tuple(cases),
    )


def _eligible(
    outcome: CandidateOutcome,
    candidate_set: Stage6CandidateSet,
) -> bool:
    policy = candidate_set.selection_policy
    return (
        Decimal(str(outcome.needs_review_recall)) >= policy.required_needs_review_recall
        and len(outcome.false_reject_case_ids) <= policy.required_false_reject_count
        and len(outcome.unsafe_pass_case_ids) <= policy.required_unsafe_pass_count
        and Decimal(str(outcome.review_rate)) <= policy.maximum_review_rate
    )


def _outcome_payload(
    outcome: CandidateOutcome,
    candidate_set: Stage6CandidateSet,
    include_cases: bool,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "candidate": _candidate_payload(outcome.candidate),
        "eligible_for_recommendation": _eligible(outcome, candidate_set),
        "safety": {
            "needs_review_recall": outcome.needs_review_recall,
            "false_reject_count": len(outcome.false_reject_case_ids),
            "false_reject_case_ids": list(outcome.false_reject_case_ids),
            "unsafe_pass_count": len(outcome.unsafe_pass_case_ids),
            "unsafe_pass_case_ids": list(outcome.unsafe_pass_case_ids),
        },
        "review_rate": outcome.review_rate,
        "decision_distribution": outcome.decision_distribution,
        "review_reason_distribution": outcome.review_reason_distribution,
        "label_match_count": len(outcome.predictions) - len(outcome.mismatch_case_ids),
        "label_mismatch_count": len(outcome.mismatch_case_ids),
        "label_mismatch_case_ids": list(outcome.mismatch_case_ids),
        "metrics": _metrics_payload(outcome.metrics),
    }
    if include_cases:
        payload["cases"] = list(outcome.cases)
    return payload


def _level_summary(
    assessments: tuple[ValidationAssessments, ...],
) -> dict[str, object]:
    candidate_ids = tuple(assessments[0].configured_l2_by_candidate)
    configured_l2_averages = {
        candidate_id: mean(
            float(cast(Decimal, item.configured_l2_by_candidate[candidate_id].score))
            for item in assessments
        )
        for candidate_id in candidate_ids
    }
    hashing_l2_scores = tuple(
        float(item.hashing_l2.score) for item in assessments if item.hashing_l2.score is not None
    )
    l3_scores = tuple(float(item.l3.score) for item in assessments if item.l3.score is not None)
    return {
        "average_l1": mean(float(cast(Decimal, item.l1.score)) for item in assessments),
        "average_configured_l2_by_candidate": configured_l2_averages,
        "average_hashing_l2": (mean(hashing_l2_scores) if hashing_l2_scores else None),
        "average_l3": mean(l3_scores) if l3_scores else None,
    }


async def run(
    repository_root: Path,
    generated_at: datetime,
    embedding_runtime: EmbeddingRuntime | None = None,
    l3_provider: L3Provider | None = None,
    l3_execution: L3ExecutionMetadata | None = None,
) -> dict[str, object]:
    if generated_at.tzinfo is None or generated_at.utcoffset() is None:
        raise ValueError("generated_at must include a timezone")
    examples = load_stage6_validation(repository_root)
    candidate_set = load_stage6_candidate_set(repository_root)
    runtime = embedding_runtime or _configured_runtime(
        repository_root,
        examples[0].job_profile_id,
        candidate_set,
    )
    execution = l3_execution or L3ExecutionMetadata(
        strategy_identifier="deterministic-offline-evidence-scorer-v1",
        provider_identifier="deterministic_fake",
        model_identifier="deterministic-evidence-scorer-v1",
        prompt_version="l3-evidence-rubric-v1",
        live_provider_executed=False,
    )
    if (l3_provider is None) != (not execution.live_provider_executed):
        raise ValueError("live L3 provider and execution metadata must be supplied together")
    assessments = await _assess_validation(
        repository_root,
        examples,
        runtime,
        candidate_set,
        l3_provider,
        execution.prompt_version,
    )
    outcomes = tuple(
        _candidate_outcome(assessments, candidate, use_hashing_l2=False)
        for candidate in candidate_set.candidates
    )
    current_candidate = next(
        candidate
        for candidate in candidate_set.candidates
        if candidate.candidate_id == "approved-current-v1"
    )
    hashing_outcome = _candidate_outcome(
        assessments,
        current_candidate,
        use_hashing_l2=True,
    )
    eligible_outcomes = tuple(outcome for outcome in outcomes if _eligible(outcome, candidate_set))
    candidate_order = {
        candidate.candidate_id: index for index, candidate in enumerate(candidate_set.candidates)
    }
    recommended = (
        max(
            eligible_outcomes,
            key=lambda outcome: (
                outcome.metrics.macro_f1,
                -outcome.review_rate,
                outcome.metrics.accuracy,
                -candidate_order[outcome.candidate.candidate_id],
            ),
        )
        if eligible_outcomes
        else None
    )
    manifest_path = repository_root / SPLIT_MANIFEST_PATH
    return {
        "report_schema_version": "1.0.0",
        "report_id": "stage6-validation-tuning-v1",
        "report_scope": (
            "stage6-validation-only-live-l3"
            if execution.live_provider_executed
            else "stage6-validation-only-controlled-l3"
        ),
        "is_final_performance": False,
        "generated_at": generated_at.isoformat(),
        "split_traceability": {
            "split_manifest_file": SPLIT_MANIFEST_PATH.as_posix(),
            "split_manifest_sha256": _sha256(manifest_path),
            "validation_partition_id": "stage6-validation-v1",
            "validation_sample_count": len(examples),
            "frozen_test_partition_id": "stage7-frozen-test-v1",
            "frozen_test_evaluated": False,
            "frozen_test_results_generated": False,
        },
        "candidate_set": {
            "candidate_set_id": candidate_set.candidate_set_id,
            "candidate_set_version": candidate_set.candidate_set_version,
            "source_configuration_version": (candidate_set.source_configuration_version),
            "source_models_configuration_version": (
                candidate_set.source_models_configuration_version
            ),
            "candidate_protection_rules_fixed": (candidate_set.candidate_protection_rules_fixed),
            "selection_policy": candidate_set.selection_policy.model_dump(mode="json"),
        },
        "execution_strategy": {
            "l1": "versioned-deterministic-rules",
            "configured_l2_model_identifier": runtime.model_identifier,
            "configured_l2_model_version": runtime.configured_model_version,
            "configured_l2_resolved_revision": runtime.resolved_model_revision,
            "configured_multilingual_l2_executed": (runtime.configured_model_executed),
            "comparison_l2": "deterministic-hashing-embedding-1.0.0",
            "l3": execution.strategy_identifier,
            "l3_provider_identifier": execution.provider_identifier,
            "l3_model_identifier": execution.model_identifier,
            "live_llm_provider_executed": execution.live_provider_executed,
            "prompt_version": execution.prompt_version,
        },
        "level_summary": _level_summary(assessments),
        "model_strategy_comparison_at_current_config": {
            "configured_l2": _outcome_payload(
                next(
                    outcome
                    for outcome in outcomes
                    if outcome.candidate.candidate_id == "approved-current-v1"
                ),
                candidate_set,
                include_cases=False,
            ),
            "hashing_l2": _outcome_payload(
                hashing_outcome,
                candidate_set,
                include_cases=False,
            ),
        },
        "candidate_results": [
            _outcome_payload(
                outcome,
                candidate_set,
                include_cases=True,
            )
            for outcome in outcomes
        ],
        "recommendation": {
            "candidate_id": (
                recommended.candidate.candidate_id if recommended is not None else None
            ),
            "status": "provisional_pending_human_approval",
            "requires_human_approval": True,
            "ranking_rule": (
                "Meet review-recall, false-Reject and unsafe-Pass constraints; "
                "stay within the maximum review rate; then maximize Macro-F1 "
                "and prefer lower review rate."
            ),
        },
        "freeze_readiness": {
            "embedding_model_evaluated": runtime.configured_model_executed,
            "aggregation_and_threshold_candidates_evaluated": True,
            "live_llm_model_evaluated": execution.live_provider_executed,
            "prompt_quality_with_live_llm_evaluated": execution.live_provider_executed,
            "configuration_frozen": False,
            "blocking_decision": (
                (
                    "Human approval is required before freezing the recommended live LLM candidate."
                    if recommended is not None
                    else "No live LLM candidate satisfies every Stage 6 selection constraint."
                )
                if execution.live_provider_executed
                else (
                    "Choose whether the internship release freezes deterministic L3 "
                    "or runs an environment-configured LLM validation before Gate 6."
                )
            ),
        },
    }


def write_report(
    repository_root: Path,
    generated_at: datetime,
    output_path: Path = REPORT_PATH,
) -> Path:
    report = asyncio.run(run(repository_root, generated_at))
    absolute_output = repository_root / output_path
    absolute_output.parent.mkdir(parents=True, exist_ok=True)
    absolute_output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return absolute_output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--generated-at",
        default=datetime.now().astimezone().isoformat(timespec="seconds"),
    )
    parser.add_argument("--output", default=REPORT_PATH.as_posix())
    arguments = parser.parse_args()
    repository_root = Path(__file__).resolve().parents[2]
    write_report(
        repository_root,
        _timestamp(cast(str, arguments.generated_at)),
        Path(cast(str, arguments.output)),
    )


if __name__ == "__main__":
    main()
