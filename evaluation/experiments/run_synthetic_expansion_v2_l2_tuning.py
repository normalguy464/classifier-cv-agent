from __future__ import annotations

import argparse
import asyncio
import json
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from math import sqrt
from pathlib import Path
from statistics import mean, pstdev
from typing import cast

from backend.app.agents.classifier.routing import route_classification
from backend.app.agents.classifier.scoring import (
    L3ProviderRequest,
    L2ScoringTrace,
    aggregate_level_scores,
    score_l1,
    score_l2_with_trace,
    score_l3,
)
from backend.app.agents.classifier.scoring.l2_policy import build_query_coverage_l2_policy
from backend.app.contracts import (
    CVProfile,
    ClassificationDecision,
    JobProfile,
    LevelScoreStatus,
    ScoringRubric,
)
from backend.app.infrastructure.embeddings import EmbeddingInputType
from backend.app.infrastructure.llm import DeterministicCoreL3Provider
from evaluation.datasets.synthetic_expansion import (
    ApprovedDatasetReview,
    SyntheticPairAnnotation,
    file_sha256,
)
from evaluation.experiments.run_synthetic_expansion_v2_diagnostic import (
    ExpansionEmbeddingRuntime,
    build_diagnostic_routing_policy,
    build_expansion_l1_policy,
    default_embedding_runtime,
    load_development,
)
from evaluation.experiments.stage6_config import load_stage6_candidate_set
from evaluation.experiments.synthetic_expansion_l2_config import (
    CONFIG_PATH,
    ExpansionL2Candidate,
    ExpansionL2CandidateSet,
    load_expansion_l2_candidate_set,
)
from evaluation.metrics import calculate_metrics

REPORT_PATH = Path("evaluation/reports/synthetic_expansion_v2_l2_tuning_v1.json")


class PrecomputedCoreEmbeddingAdapter:
    def __init__(
        self,
        query_vectors: dict[str, tuple[float, ...]],
        passage_vectors: dict[str, tuple[float, ...]],
        query_count: int,
    ) -> None:
        if query_count < 1:
            raise ValueError("query_count must be positive")
        self._query_vectors = query_vectors
        self._passage_vectors = passage_vectors
        self._query_count = query_count

    def embed(self, texts: tuple[str, ...]) -> tuple[tuple[float, ...], ...]:
        if len(texts) < self._query_count:
            raise ValueError("embedding input is shorter than query_count")
        return tuple(self._query_vectors[text] for text in texts[: self._query_count]) + tuple(
            self._passage_vectors[text] for text in texts[self._query_count :]
        )


def _timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError("generated_at must be an ISO 8601 timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("generated_at must include a timezone")
    return parsed


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        raise ValueError("percentile input must not be empty")
    ordered = sorted(values)
    position = (len(ordered) - 1) * percentile
    lower_index = int(position)
    upper_index = min(lower_index + 1, len(ordered) - 1)
    fraction = position - lower_index
    return ordered[lower_index] * (1 - fraction) + ordered[upper_index] * fraction


def _pearson(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or len(left) < 2:
        raise ValueError("correlation inputs must have equal length of at least two")
    left_mean = mean(left)
    right_mean = mean(right)
    numerator = sum(
        (left_value - left_mean) * (right_value - right_mean)
        for left_value, right_value in zip(left, right, strict=True)
    )
    left_scale = sqrt(sum((value - left_mean) ** 2 for value in left))
    right_scale = sqrt(sum((value - right_mean) ** 2 for value in right))
    if left_scale == 0 or right_scale == 0:
        return 0.0
    return numerator / (left_scale * right_scale)


def _trace_payload(trace: L2ScoringTrace) -> dict[str, object]:
    return {
        item.criterion_id: {
            "weighted_score": float(item.weighted_score),
            "query_count": len(item.query_traces),
            "covered_query_count": sum(query.meets_minimum for query in item.query_traces),
            "selected_raw_similarities": [
                float(match.raw_similarity)
                for query in item.query_traces
                for match in query.selected_matches
            ],
        }
        for item in trace.criteria
    }


def _candidate_summary(
    candidate: ExpansionL2Candidate,
    cases: list[dict[str, object]],
) -> dict[str, object]:
    l2_scores = [cast(float, item["l2_score"]) for item in cases]
    human_scores = [cast(float, item["human_total_score"]) for item in cases]
    expected = tuple(ClassificationDecision(cast(str, item["expected_label"])) for item in cases)
    predicted = tuple(ClassificationDecision(cast(str, item["predicted_label"])) for item in cases)
    candidate_groups: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for item in cases:
        candidate_groups[cast(str, item["candidate_reference"])].append(
            (cast(float, item["l2_score"]), cast(float, item["human_total_score"]))
        )
    grouped_l2 = [mean(value[0] for value in items) for items in candidate_groups.values()]
    grouped_human = [mean(value[1] for value in items) for items in candidate_groups.values()]
    raw_similarities = [
        raw
        for item in cases
        for criterion in cast(dict[str, dict[str, object]], item["criterion_trace"]).values()
        for raw in cast(list[float], criterion["selected_raw_similarities"])
    ]
    criterion_absolute_errors = [
        abs(l2_score - human_score)
        for item in cases
        for l2_score, human_score in zip(
            cast(list[float], item["l2_criterion_scores"]),
            cast(list[float], item["human_criterion_scores"]),
            strict=True,
        )
    ]
    role_scenario_scores: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for item in cases:
        role_scenario_scores[cast(str, item["role"])][cast(str, item["scenario"])].append(
            cast(float, item["l2_score"])
        )
    role_contrast = {
        role: {
            "strong_mean": mean(scenarios["strong"]),
            "hard_negative_mean": mean(scenarios["hard_negative"]),
            "margin": mean(scenarios["strong"]) - mean(scenarios["hard_negative"]),
        }
        for role, scenarios in role_scenario_scores.items()
    }
    review_support = sum(label is ClassificationDecision.NEEDS_REVIEW for label in expected)
    review_hits = sum(
        actual is ClassificationDecision.NEEDS_REVIEW
        and prediction is ClassificationDecision.NEEDS_REVIEW
        for actual, prediction in zip(expected, predicted, strict=True)
    )
    false_reject_count = sum(
        actual is not ClassificationDecision.REJECT and prediction is ClassificationDecision.REJECT
        for actual, prediction in zip(expected, predicted, strict=True)
    )
    unsafe_pass_count = sum(
        prediction is ClassificationDecision.PASS
        and actual in {ClassificationDecision.REJECT, ClassificationDecision.NEEDS_REVIEW}
        for actual, prediction in zip(expected, predicted, strict=True)
    )
    metrics = calculate_metrics(expected, predicted)
    review_reason_counts: dict[str, int] = defaultdict(int)
    for item in cases:
        for reason in cast(list[str], item["review_reasons"]):
            review_reason_counts[reason] += 1
    return {
        "candidate_id": candidate.candidate_id,
        "configuration": {
            "similarity_floor": float(candidate.similarity_floor),
            "similarity_ceiling": float(candidate.similarity_ceiling),
            "top_k": candidate.top_k,
            "minimum_query_score": float(candidate.minimum_query_score),
        },
        "l2_score": {
            "mean": mean(l2_scores),
            "standard_deviation": pstdev(l2_scores),
            "minimum": min(l2_scores),
            "maximum": max(l2_scores),
            "exact_100_count": sum(value == 100.0 for value in l2_scores),
            "exact_100_rate": sum(value == 100.0 for value in l2_scores) / len(l2_scores),
            "total_score_mae": mean(
                abs(l2_score - human_score)
                for l2_score, human_score in zip(l2_scores, human_scores, strict=True)
            ),
            "criterion_weighted_mae": mean(criterion_absolute_errors),
            "candidate_grouped_correlation": _pearson(grouped_l2, grouped_human),
        },
        "raw_similarity_percentiles": {
            "p05": _percentile(raw_similarities, 0.05),
            "p25": _percentile(raw_similarities, 0.25),
            "p50": _percentile(raw_similarities, 0.50),
            "p75": _percentile(raw_similarities, 0.75),
            "p95": _percentile(raw_similarities, 0.95),
        },
        "role_contrast": role_contrast,
        "strong_over_hard_negative_role_count": sum(
            values["margin"] > 0 for values in role_contrast.values()
        ),
        "hybrid_diagnostic": {
            "accuracy": metrics.accuracy,
            "macro_f1": metrics.macro_f1,
            "needs_review_recall": review_hits / review_support,
            "review_rate": sum(label is ClassificationDecision.NEEDS_REVIEW for label in predicted)
            / len(predicted),
            "false_reject_count": false_reject_count,
            "unsafe_pass_count": unsafe_pass_count,
            "review_reason_counts": dict(sorted(review_reason_counts.items())),
        },
    }


def precompute_l2_adapters(
    annotations: tuple[SyntheticPairAnnotation, ...],
    profiles: dict[str, CVProfile],
    jobs: dict[str, JobProfile],
    rubrics: dict[str, ScoringRubric],
    candidate_set: ExpansionL2CandidateSet,
    runtime: ExpansionEmbeddingRuntime,
) -> dict[int, PrecomputedCoreEmbeddingAdapter]:
    reference_candidate = candidate_set.candidates[0]
    configuration = candidate_set.coverage_configuration(reference_candidate)
    policies = {
        (annotation.job_profile_id, annotation.rubric_id): build_query_coverage_l2_policy(
            jobs[annotation.job_profile_id],
            rubrics[annotation.rubric_id],
            configuration,
        )
        for annotation in annotations
    }
    query_texts = tuple(
        dict.fromkeys(
            query_text
            for policy in policies.values()
            for criterion in policy.criteria
            for query_text in criterion.query_texts
        )
    )
    used_profile_ids = {annotation.cv_profile_id for annotation in annotations}
    passage_texts = tuple(
        dict.fromkeys(
            evidence.text
            for profile_id in used_profile_ids
            for evidence in profiles[profile_id].evidence
        )
    )
    query_result = runtime.adapter.embed(query_texts, EmbeddingInputType.QUERY)
    passage_result = runtime.adapter.embed(passage_texts, EmbeddingInputType.PASSAGE)
    query_vectors = dict(zip(query_texts, query_result.vectors, strict=True))
    passage_vectors = dict(zip(passage_texts, passage_result.vectors, strict=True))
    query_counts = {policy.query_count for policy in policies.values()}
    return {
        query_count: PrecomputedCoreEmbeddingAdapter(
            query_vectors,
            passage_vectors,
            query_count,
        )
        for query_count in query_counts
    }


async def run(
    repository_root: Path,
    generated_at: datetime,
    embedding_runtime: ExpansionEmbeddingRuntime | None = None,
    configuration_path: Path = CONFIG_PATH,
) -> dict[str, object]:
    if generated_at.tzinfo is None or generated_at.utcoffset() is None:
        raise ValueError("generated_at must include a timezone")
    candidate_set = load_expansion_l2_candidate_set(repository_root, configuration_path)
    annotations, profiles, jobs, rubrics, split = load_development(
        repository_root,
        candidate_set.reviewed_dataset_directory,
        candidate_set.split_manifest_path,
    )
    if candidate_set.dataset_id != split.source_dataset_id:
        raise ValueError("L2 candidate dataset does not match the development split")
    if candidate_set.dataset_version != split.source_dataset_version:
        raise ValueError("L2 candidate dataset version does not match the development split")
    if candidate_set.development_partition_id != split.development.partition_id:
        raise ValueError("L2 development partition does not match the configured split")
    if candidate_set.held_out_partition_id != split.held_out.partition_id:
        raise ValueError("L2 held-out partition does not match the configured split")
    runtime = embedding_runtime or default_embedding_runtime(repository_root)
    stage6_candidates = load_stage6_candidate_set(repository_root)
    aggregation_candidate = next(
        item for item in stage6_candidates.candidates if item.candidate_id == "approved-current-v1"
    )
    routing_policy = build_diagnostic_routing_policy(repository_root, aggregation_candidate)
    embedding_bridges = precompute_l2_adapters(
        annotations,
        profiles,
        jobs,
        rubrics,
        candidate_set,
        runtime,
    )
    case_results: dict[str, list[dict[str, object]]] = {
        item.candidate_id: [] for item in candidate_set.candidates
    }
    for annotation in annotations:
        profile = profiles[annotation.cv_profile_id]
        job = jobs[annotation.job_profile_id]
        rubric = rubrics[annotation.rubric_id]
        l1_policy = build_expansion_l1_policy(annotation.role, job.job_profile_id)
        l1 = score_l1(profile, rubric, l1_policy)
        l3 = await score_l3(
            request=L3ProviderRequest(
                cv_profile=profile,
                job_profile=job,
                rubric=rubric,
                prompt_version=stage6_candidates.model_strategy.prompt_version,
            ),
            provider=DeterministicCoreL3Provider(l1_policy),
        )
        for candidate in candidate_set.candidates:
            policy = build_query_coverage_l2_policy(
                job,
                rubric,
                candidate_set.coverage_configuration(candidate),
            )
            l2, trace = score_l2_with_trace(
                profile,
                rubric,
                policy,
                embedding_bridges[policy.query_count],
            )
            if l2.status is not LevelScoreStatus.AVAILABLE or trace is None:
                raise RuntimeError("configured multilingual L2 failed during tuning")
            aggregation = aggregate_level_scores(
                (l1, l2, l3),
                aggregation_candidate.aggregation,
            )
            routing = route_classification(
                aggregation,
                l1.requirement_assessments,
                routing_policy,
            )
            review = cast(ApprovedDatasetReview, annotation.review)
            case_results[candidate.candidate_id].append(
                {
                    "pair_id": annotation.pair_id,
                    "candidate_reference": annotation.candidate_reference,
                    "role": annotation.role.value,
                    "scenario": annotation.scenario.value,
                    "expected_label": review.final_label.value,
                    "predicted_label": routing.decision.value,
                    "human_total_score": float(annotation.total_score),
                    "human_criterion_scores": [
                        float(item.awarded_points) for item in annotation.criterion_assessments
                    ],
                    "l1_score": float(cast(Decimal, l1.score)),
                    "l2_score": float(cast(Decimal, l2.score)),
                    "l3_score": float(cast(Decimal, l3.score)),
                    "l2_criterion_scores": [
                        float(item.weighted_score) for item in l2.criterion_assessments
                    ],
                    "criterion_trace": _trace_payload(trace),
                    "final_score": (
                        None if routing.final_score is None else float(routing.final_score)
                    ),
                    "review_reasons": list(routing.reasons),
                }
            )
    summaries = [
        _candidate_summary(candidate, case_results[candidate.candidate_id])
        for candidate in candidate_set.candidates
    ]
    l2_eligible = [
        item
        for item in summaries
        if cast(dict[str, float], item["l2_score"])["exact_100_rate"]
        <= float(candidate_set.selection_policy.maximum_exact_ceiling_rate)
        and item["strong_over_hard_negative_role_count"]
        == candidate_set.selection_policy.required_strong_over_hard_negative_roles
    ]
    l2_recommendation = min(
        l2_eligible,
        key=lambda item: (
            cast(dict[str, float], item["l2_score"])["total_score_mae"],
            -cast(dict[str, float], item["l2_score"])["candidate_grouped_correlation"],
        ),
        default=None,
    )
    hybrid_safety_gate_candidates = [
        item
        for item in l2_eligible
        if cast(dict[str, float], item["hybrid_diagnostic"])["false_reject_count"]
        == candidate_set.selection_policy.required_false_reject_count
        and cast(dict[str, float], item["hybrid_diagnostic"])["unsafe_pass_count"]
        == candidate_set.selection_policy.required_unsafe_pass_count
    ]
    return {
        "report_schema_version": "1.1.0",
        "report_id": candidate_set.report_id,
        "report_scope": "silver-development-l2-query-coverage-tuning",
        "is_final_performance": False,
        "generated_at": generated_at.isoformat(),
        "traceability": {
            "candidate_configuration_file": configuration_path.as_posix(),
            "candidate_configuration_sha256": file_sha256(repository_root / configuration_path),
            "dataset_manifest_sha256": file_sha256(
                repository_root / candidate_set.reviewed_dataset_directory / "manifest.json"
            ),
            "split_manifest_sha256": file_sha256(
                repository_root / candidate_set.split_manifest_path
            ),
            "dataset_id": split.source_dataset_id,
            "dataset_version": split.source_dataset_version,
            "development_partition_id": split.development.partition_id,
            "development_pair_count": split.development.pair_count,
            "held_out_partition_id": split.held_out.partition_id,
            "held_out_evaluated": False,
            "original_stage6_frozen_test_evaluated": False,
            "candidate_set_id": candidate_set.candidate_set_id,
            "candidate_set_version": candidate_set.candidate_set_version,
            "query_strategy_version": candidate_set.query_strategy_version,
            "embedding_model_identifier": runtime.model_identifier,
            "embedding_resolved_revision": runtime.resolved_revision,
        },
        "selection": {
            "l2_recommended_candidate_id": (
                None if l2_recommendation is None else l2_recommendation["candidate_id"]
            ),
            "hybrid_safety_gate_candidate_ids": [
                item["candidate_id"] for item in hybrid_safety_gate_candidates
            ],
            "hybrid_configuration_freeze_eligible": False,
            "hybrid_configuration_freeze_blockers": [
                "L3 uses a deterministic fake rather than the configured provider.",
                "The recommended candidate routes 150/150 cases to Needs Review; 144 have level disagreement and the remaining cases trigger other quality gates.",
            ],
        },
        "candidate_summaries": summaries,
        "cases_by_candidate": case_results,
        "limitations": [
            "Tuning uses synthetic Silver development data reviewed by one person.",
            "Five pairs from one candidate are correlated and metrics are grouped where applicable.",
            "The held-out Silver partition and original Stage 6 frozen test remain unexecuted.",
            "Hybrid diagnostics still use deterministic L3 and cannot freeze an L3 strategy.",
            "L2 separates role-aligned profiles from hard negatives but does not establish or refute factual claims by itself.",
        ],
    }


def write_report(
    repository_root: Path,
    generated_at: datetime,
    output_path: Path = REPORT_PATH,
    embedding_runtime: ExpansionEmbeddingRuntime | None = None,
    configuration_path: Path = CONFIG_PATH,
) -> Path:
    report = asyncio.run(run(repository_root, generated_at, embedding_runtime, configuration_path))
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
    parser.add_argument("--configuration", default=CONFIG_PATH.as_posix())
    arguments = parser.parse_args()
    write_report(
        Path(__file__).resolve().parents[2],
        _timestamp(cast(str, arguments.generated_at)),
        Path(cast(str, arguments.output)),
        configuration_path=Path(cast(str, arguments.configuration)),
    )


if __name__ == "__main__":
    main()
