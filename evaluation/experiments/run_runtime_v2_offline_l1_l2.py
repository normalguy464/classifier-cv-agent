from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from math import sqrt
from pathlib import Path
from statistics import mean, pstdev
from typing import Literal, Self, cast

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.app.agents.classifier.scoring import L2ScoreCalibrator, score_l1, score_l2_with_trace
from backend.app.agents.classifier.scoring.l2 import L2ScoringTrace
from backend.app.agents.classifier.scoring.l2_policy import (
    L2CoverageConfiguration,
    build_query_coverage_l2_policy,
)
from backend.app.contracts import (
    CVProfile,
    ClassificationDecision,
    EvidenceStatus,
    JobProfile,
    LevelScoreStatus,
    ScoringRubric,
)
from backend.app.domain import L1Policy, L2Policy
from backend.app.infrastructure.config import (
    RepositoryConfigurationLoader,
    build_l1_policy,
    build_l2_policy,
    load_yaml_artifact,
)
from backend.app.infrastructure.config.artifacts import (
    L1RulesConfigurationArtifact,
    ModelsConfigurationArtifact,
)
from backend.app.infrastructure.embeddings import (
    EmbeddingAdapter,
    EmbeddingInputType,
    SentenceTransformerEmbeddingAdapter,
)
from backend.app.infrastructure.calibration import SklearnExtraTreesL2Calibrator
from evaluation.datasets.runtime_v2 import (
    RuntimeV2ReviewedManifest,
    RuntimeV2SplitManifest,
    file_sha256,
    validate_runtime_v2_reviewed,
)
from evaluation.datasets.synthetic_expansion import (
    ApprovedDatasetReview,
    SyntheticPairAnnotation,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = Path("evaluation/configs/runtime_v2_offline_l1_l2_v1.yaml")
BASELINE_REPORT_PATH = Path("evaluation/reports/runtime_v2_offline_l1_l2_baseline_v1.json")
CANDIDATE_REPORT_PATH = Path("evaluation/reports/runtime_v2_offline_l1_l2_candidate_v1.json")


class FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class L1QualityPolicy(FrozenModel):
    minimum_development_requirement_accuracy: Decimal = Field(ge=0, le=1)
    minimum_validation_requirement_accuracy: Decimal = Field(ge=0, le=1)
    maximum_development_unsafe_mismatches: int = Field(ge=0)
    maximum_validation_unsafe_mismatches: int = Field(ge=0)


class L2QualityPolicy(FrozenModel):
    maximum_development_total_score_mae: Decimal = Field(ge=0, le=100)
    maximum_validation_total_score_mae: Decimal = Field(ge=0, le=100)
    maximum_development_criterion_mae: Decimal = Field(ge=0, le=100)
    maximum_validation_criterion_mae: Decimal = Field(ge=0, le=100)
    minimum_development_score_correlation: Decimal = Field(ge=-1, le=1)
    minimum_validation_score_correlation: Decimal = Field(ge=-1, le=1)
    minimum_development_score_range: Decimal = Field(ge=0, le=100)
    minimum_validation_score_range: Decimal = Field(ge=0, le=100)
    minimum_pass_over_waitlist_margin: Decimal = Field(ge=0, le=100)
    minimum_waitlist_over_reject_margin: Decimal = Field(ge=0, le=100)


class OfflineSelectionPolicy(FrozenModel):
    development_may_change_candidate: Literal[True]
    validation_may_select_candidate: Literal[True]
    frozen_test_may_change_candidate: Literal[False]
    require_all_l1_checks: Literal[True]
    require_all_l2_checks: Literal[True]


class RuntimeV2OfflineConfiguration(FrozenModel):
    schema_version: Literal["1.0.0"]
    experiment_id: Literal["runtime-v2-offline-l1-l2-v1"]
    experiment_version: Literal["1.0.0"]
    status: Literal["approved_for_offline_baseline_and_tuning"]
    reviewed_dataset_directory: Path
    split_manifest_path: Path
    baseline_runtime_directory: Path
    candidate_runtime_directory: Path
    stage7_v1_test_allowed: Literal[False]
    llm_provider_calls_allowed: Literal[False]
    l1_quality_policy: L1QualityPolicy
    l2_quality_policy: L2QualityPolicy
    selection_policy: OfflineSelectionPolicy

    @model_validator(mode="after")
    def validate_paths(self) -> Self:
        paths = (
            self.reviewed_dataset_directory,
            self.split_manifest_path,
            self.baseline_runtime_directory,
            self.candidate_runtime_directory,
        )
        if any(path.is_absolute() or ".." in path.parts for path in paths):
            raise ValueError("offline configuration paths must be repository-relative")
        return self


@dataclass(frozen=True, slots=True)
class OfflineEmbeddingRuntime:
    adapter: EmbeddingAdapter
    model_identifier: str
    model_version: str
    configured_model_executed: bool


@dataclass(frozen=True, slots=True)
class OfflinePolicySet:
    candidate_id: str
    runtime_directory: Path
    l1_by_job: dict[str, L1Policy]
    l2_by_job: dict[str, L2Policy]
    l2_score_calibrator: L2ScoreCalibrator | None = None


@dataclass(frozen=True, slots=True)
class OfflineCaseResult:
    pair_id: str
    role: str
    expected_label: ClassificationDecision
    human_total_score: float
    human_criterion_scores: tuple[float, ...]
    human_requirement_statuses: dict[str, EvidenceStatus]
    l1_score: float
    l1_requirement_statuses: dict[str, EvidenceStatus]
    l2_score: float
    l2_criterion_scores: tuple[float, ...]
    l2_raw_similarities: tuple[float, ...]


class PrecomputedEmbeddingBridge:
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


def load_offline_configuration(
    repository_root: Path,
    configuration_path: Path = CONFIG_PATH,
) -> RuntimeV2OfflineConfiguration:
    payload = yaml.safe_load((repository_root / configuration_path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("offline L1/L2 configuration must be a mapping")
    return RuntimeV2OfflineConfiguration.model_validate(cast(dict[str, object], payload))


def _timestamp(value: str) -> datetime:
    try:
        timestamp = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError("generated_at must be an ISO 8601 timestamp") from error
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("generated_at must include a timezone")
    return timestamp


def load_offline_data(
    repository_root: Path,
    configuration: RuntimeV2OfflineConfiguration,
) -> tuple[
    tuple[SyntheticPairAnnotation, ...],
    dict[str, CVProfile],
    dict[str, JobProfile],
    dict[str, ScoringRubric],
    RuntimeV2ReviewedManifest,
    RuntimeV2SplitManifest,
]:
    reviewed_directory = repository_root / configuration.reviewed_dataset_directory
    source_directory = repository_root / "data/runtime_v2/to_review/development_v1"
    report = validate_runtime_v2_reviewed(
        reviewed_directory,
        source_directory,
        repository_root,
    )
    if not report.passed or report.warnings:
        raise ValueError("reviewed Runtime v2 data must pass QC without warnings")
    manifest_path = reviewed_directory / "manifest.json"
    manifest = RuntimeV2ReviewedManifest.model_validate_json(
        manifest_path.read_text(encoding="utf-8")
    )
    split = RuntimeV2SplitManifest.model_validate_json(
        (repository_root / configuration.split_manifest_path).read_text(encoding="utf-8")
    )
    if split.source_manifest_sha256 != file_sha256(manifest_path):
        raise ValueError("offline split source hash does not match reviewed data")
    profiles = {
        item.cv_profile_id: item
        for item in (
            CVProfile.model_validate_json(line)
            for line in (reviewed_directory / "cv_profiles.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        )
    }
    jobs = {
        item.job_profile_id: item
        for item in (
            JobProfile.model_validate_json(line)
            for line in (reviewed_directory / "job_profiles.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        )
    }
    rubrics = {
        item.rubric_id: item
        for item in (
            ScoringRubric.model_validate_json(line)
            for line in (reviewed_directory / "rubrics.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        )
    }
    pairs = tuple(
        SyntheticPairAnnotation.model_validate_json(line)
        for line in (reviewed_directory / "pairs.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    )
    if {item.pair_id for item in pairs} != set(split.development.pair_ids) | set(
        split.validation.pair_ids
    ):
        raise ValueError("offline split does not cover exactly the reviewed pairs")
    return pairs, profiles, jobs, rubrics, manifest, split


def build_offline_policy_set(
    repository_root: Path,
    runtime_directory: Path,
    candidate_id: str,
    jobs: dict[str, JobProfile],
    rubrics: dict[str, ScoringRubric],
    unfrozen_candidate: bool,
) -> OfflinePolicySet:
    if unfrozen_candidate:
        l1_artifact = load_yaml_artifact(
            repository_root / runtime_directory / "l1_rules.yaml",
            L1RulesConfigurationArtifact,
        )
        models_artifact = load_yaml_artifact(
            repository_root / runtime_directory / "models.yaml",
            ModelsConfigurationArtifact,
        )
        l1_artifacts_by_job = {item.job_profile_id: item for item in l1_artifact.policies}
        rubrics_by_job = {item.job_profile_id: item for item in rubrics.values()}
        matching = models_artifact.embedding.matching
        configuration = L2CoverageConfiguration(
            similarity_floor=matching.similarity_floor,
            similarity_ceiling=matching.similarity_ceiling,
            top_k=matching.top_k,
            minimum_query_score=matching.minimum_query_score,
            section_weights=tuple((item.section, item.weight) for item in matching.section_weights),
            query_profile=matching.query_profile,
        )
        l1_by_job = {job_id: build_l1_policy(l1_artifacts_by_job[job_id]) for job_id in jobs}
        l2_by_job = {
            job_id: build_query_coverage_l2_policy(
                job,
                rubrics_by_job[job_id],
                configuration,
            )
            for job_id, job in jobs.items()
        }
        return OfflinePolicySet(
            candidate_id=candidate_id,
            runtime_directory=runtime_directory,
            l1_by_job=l1_by_job,
            l2_by_job=l2_by_job,
            l2_score_calibrator=(
                None
                if models_artifact.embedding.calibration is None
                else SklearnExtraTreesL2Calibrator(
                    repository_root,
                    models_artifact.embedding.calibration,
                )
            ),
        )
    loader = RepositoryConfigurationLoader(
        repository_root,
        repository_root / runtime_directory,
    )
    l1_by_job: dict[str, L1Policy] = {}
    l2_by_job: dict[str, L2Policy] = {}
    for job_id, expected_job in jobs.items():
        loaded = loader.load_for_job(job_id)
        if loaded.job_profile != expected_job:
            raise ValueError(f"runtime Job Profile differs from reviewed data: {job_id}")
        l1_by_job[job_id] = loader.load_l1_policy(job_id)
        l2_by_job[job_id] = build_l2_policy(loaded)
    return OfflinePolicySet(
        candidate_id=candidate_id,
        runtime_directory=runtime_directory,
        l1_by_job=l1_by_job,
        l2_by_job=l2_by_job,
    )


def default_embedding_runtime(
    repository_root: Path,
    runtime_directory: Path,
    reference_job_id: str,
    unfrozen_candidate: bool,
) -> OfflineEmbeddingRuntime:
    if unfrozen_candidate:
        models_artifact = load_yaml_artifact(
            repository_root / runtime_directory / "models.yaml",
            ModelsConfigurationArtifact,
        )
        embedding_artifact = models_artifact.embedding
    else:
        loader = RepositoryConfigurationLoader(
            repository_root,
            repository_root / runtime_directory,
        )
        embedding_artifact = loader.load_for_job(reference_job_id).models_artifact.embedding
    adapter = SentenceTransformerEmbeddingAdapter.from_configuration(embedding_artifact)
    return OfflineEmbeddingRuntime(
        adapter=adapter,
        model_identifier=adapter.model_identifier,
        model_version=adapter.model_version,
        configured_model_executed=True,
    )


def build_precomputed_bridges(
    pairs: tuple[SyntheticPairAnnotation, ...],
    profiles: dict[str, CVProfile],
    policy_set: OfflinePolicySet,
    embedding_runtime: OfflineEmbeddingRuntime,
) -> dict[int, PrecomputedEmbeddingBridge]:
    policies = tuple(policy_set.l2_by_job.values())
    query_texts = tuple(
        dict.fromkeys(
            text
            for policy in policies
            for criterion in policy.criteria
            for text in criterion.query_texts
        )
    )
    used_profile_ids = {pair.cv_profile_id for pair in pairs}
    passage_texts = tuple(
        dict.fromkeys(
            item.text for profile_id in used_profile_ids for item in profiles[profile_id].evidence
        )
    )
    query_result = embedding_runtime.adapter.embed(query_texts, EmbeddingInputType.QUERY)
    passage_result = embedding_runtime.adapter.embed(passage_texts, EmbeddingInputType.PASSAGE)
    query_vectors = dict(zip(query_texts, query_result.vectors, strict=True))
    passage_vectors = dict(zip(passage_texts, passage_result.vectors, strict=True))
    return {
        query_count: PrecomputedEmbeddingBridge(query_vectors, passage_vectors, query_count)
        for query_count in {policy.query_count for policy in policies}
    }


def _trace_similarities(trace: L2ScoringTrace) -> tuple[float, ...]:
    return tuple(
        float(match.raw_similarity)
        for criterion in trace.criteria
        for query in criterion.query_traces
        for match in query.selected_matches
    )


def evaluate_offline_cases(
    pairs: tuple[SyntheticPairAnnotation, ...],
    profiles: dict[str, CVProfile],
    rubrics: dict[str, ScoringRubric],
    policy_set: OfflinePolicySet,
    bridges: dict[int, PrecomputedEmbeddingBridge],
) -> tuple[OfflineCaseResult, ...]:
    results: list[OfflineCaseResult] = []
    for pair in pairs:
        profile = profiles[pair.cv_profile_id]
        rubric = rubrics[pair.rubric_id]
        l1 = score_l1(profile, rubric, policy_set.l1_by_job[pair.job_profile_id])
        l2_policy = policy_set.l2_by_job[pair.job_profile_id]
        l2, trace = score_l2_with_trace(
            profile,
            rubric,
            l2_policy,
            bridges[l2_policy.query_count],
            policy_set.l2_score_calibrator,
        )
        if (
            l1.status is not LevelScoreStatus.AVAILABLE
            or l2.status is not LevelScoreStatus.AVAILABLE
            or l1.score is None
            or l2.score is None
            or trace is None
        ):
            raise RuntimeError("configured offline L1/L2 scoring was unavailable or invalid")
        review = cast(ApprovedDatasetReview, pair.review)
        results.append(
            OfflineCaseResult(
                pair_id=pair.pair_id,
                role=pair.role.value,
                expected_label=review.final_label,
                human_total_score=float(pair.total_score),
                human_criterion_scores=tuple(
                    float(item.awarded_points) for item in pair.criterion_assessments
                ),
                human_requirement_statuses={
                    item.requirement_id: item.evidence_status
                    for item in pair.critical_requirement_assessments
                },
                l1_score=float(l1.score),
                l1_requirement_statuses={
                    item.requirement_id: item.evidence_status for item in l1.requirement_assessments
                },
                l2_score=float(l2.score),
                l2_criterion_scores=tuple(
                    float(item.weighted_score) for item in l2.criterion_assessments
                ),
                l2_raw_similarities=_trace_similarities(trace),
            )
        )
    return tuple(results)


def _correlation(left: tuple[float, ...], right: tuple[float, ...]) -> float:
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


def build_partition_summary(cases: tuple[OfflineCaseResult, ...]) -> dict[str, object]:
    requirement_count = 0
    requirement_matches = 0
    unsafe_mismatches = 0
    mismatch_cases: list[dict[str, object]] = []
    for case in cases:
        mismatches: list[dict[str, object]] = []
        for requirement_id, human_status in case.human_requirement_statuses.items():
            predicted_status = case.l1_requirement_statuses[requirement_id]
            requirement_count += 1
            requirement_matches += predicted_status is human_status
            unsafe = predicted_status is not human_status and predicted_status in {
                EvidenceStatus.SATISFIED,
                EvidenceStatus.UNSATISFIED,
            }
            unsafe_mismatches += unsafe
            if predicted_status is not human_status:
                mismatches.append(
                    {
                        "requirement_id": requirement_id,
                        "human_status": human_status.value,
                        "predicted_status": predicted_status.value,
                        "unsafe": unsafe,
                    }
                )
        if mismatches:
            mismatch_cases.append({"pair_id": case.pair_id, "mismatches": mismatches})
    l2_scores = tuple(case.l2_score for case in cases)
    human_scores = tuple(case.human_total_score for case in cases)
    criterion_errors = tuple(
        abs(predicted - human)
        for case in cases
        for predicted, human in zip(
            case.l2_criterion_scores,
            case.human_criterion_scores,
            strict=True,
        )
    )
    label_scores: defaultdict[ClassificationDecision, list[float]] = defaultdict(list)
    for case in cases:
        label_scores[case.expected_label].append(case.l2_score)
    label_means = {label.value: mean(label_scores[label]) for label in ClassificationDecision}
    raw_similarities = tuple(value for case in cases for value in case.l2_raw_similarities)
    return {
        "pair_count": len(cases),
        "label_counts": dict(Counter(case.expected_label.value for case in cases)),
        "l1": {
            "requirement_count": requirement_count,
            "requirement_status_accuracy": requirement_matches / requirement_count,
            "requirement_mismatch_count": requirement_count - requirement_matches,
            "unsafe_requirement_mismatch_count": unsafe_mismatches,
            "score_minimum": min(case.l1_score for case in cases),
            "score_maximum": max(case.l1_score for case in cases),
            "mismatch_cases": mismatch_cases,
        },
        "l2": {
            "score_mean": mean(l2_scores),
            "score_standard_deviation": pstdev(l2_scores),
            "score_minimum": min(l2_scores),
            "score_maximum": max(l2_scores),
            "score_range": max(l2_scores) - min(l2_scores),
            "total_score_mae": mean(
                abs(predicted - human)
                for predicted, human in zip(l2_scores, human_scores, strict=True)
            ),
            "criterion_mae": mean(criterion_errors),
            "score_correlation": _correlation(l2_scores, human_scores),
            "label_score_means": label_means,
            "pass_over_waitlist_margin": (
                label_means[ClassificationDecision.PASS.value]
                - label_means[ClassificationDecision.WAITLIST.value]
            ),
            "waitlist_over_reject_margin": (
                label_means[ClassificationDecision.WAITLIST.value]
                - label_means[ClassificationDecision.REJECT.value]
            ),
            "raw_similarity_minimum": min(raw_similarities),
            "raw_similarity_maximum": max(raw_similarities),
        },
        "cases": [
            {
                "pair_id": case.pair_id,
                "role": case.role,
                "expected_label": case.expected_label.value,
                "human_total_score": case.human_total_score,
                "l1_score": case.l1_score,
                "l2_score": case.l2_score,
                "l2_criterion_scores": list(case.l2_criterion_scores),
            }
            for case in cases
        ],
    }


def _numeric_value(values: dict[str, object], key: str) -> float:
    value = values[key]
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValueError(f"offline metric is not numeric: {key}")
    return float(value)


def evaluate_quality_checks(
    development: dict[str, object],
    validation: dict[str, object],
    configuration: RuntimeV2OfflineConfiguration,
) -> dict[str, bool]:
    development_l1 = cast(dict[str, object], development["l1"])
    validation_l1 = cast(dict[str, object], validation["l1"])
    development_l2 = cast(dict[str, object], development["l2"])
    validation_l2 = cast(dict[str, object], validation["l2"])
    l1_policy = configuration.l1_quality_policy
    l2_policy = configuration.l2_quality_policy
    checks = {
        "l1_development_requirement_accuracy": _numeric_value(
            development_l1, "requirement_status_accuracy"
        )
        >= float(l1_policy.minimum_development_requirement_accuracy),
        "l1_validation_requirement_accuracy": _numeric_value(
            validation_l1, "requirement_status_accuracy"
        )
        >= float(l1_policy.minimum_validation_requirement_accuracy),
        "l1_development_unsafe_mismatches": _numeric_value(
            development_l1, "unsafe_requirement_mismatch_count"
        )
        <= l1_policy.maximum_development_unsafe_mismatches,
        "l1_validation_unsafe_mismatches": _numeric_value(
            validation_l1, "unsafe_requirement_mismatch_count"
        )
        <= l1_policy.maximum_validation_unsafe_mismatches,
        "l2_development_total_score_mae": _numeric_value(development_l2, "total_score_mae")
        <= float(l2_policy.maximum_development_total_score_mae),
        "l2_validation_total_score_mae": _numeric_value(validation_l2, "total_score_mae")
        <= float(l2_policy.maximum_validation_total_score_mae),
        "l2_development_criterion_mae": _numeric_value(development_l2, "criterion_mae")
        <= float(l2_policy.maximum_development_criterion_mae),
        "l2_validation_criterion_mae": _numeric_value(validation_l2, "criterion_mae")
        <= float(l2_policy.maximum_validation_criterion_mae),
        "l2_development_score_correlation": _numeric_value(development_l2, "score_correlation")
        >= float(l2_policy.minimum_development_score_correlation),
        "l2_validation_score_correlation": _numeric_value(validation_l2, "score_correlation")
        >= float(l2_policy.minimum_validation_score_correlation),
        "l2_development_score_range": _numeric_value(development_l2, "score_range")
        >= float(l2_policy.minimum_development_score_range),
        "l2_validation_score_range": _numeric_value(validation_l2, "score_range")
        >= float(l2_policy.minimum_validation_score_range),
        "l2_development_pass_over_waitlist_margin": _numeric_value(
            development_l2, "pass_over_waitlist_margin"
        )
        >= float(l2_policy.minimum_pass_over_waitlist_margin),
        "l2_validation_pass_over_waitlist_margin": _numeric_value(
            validation_l2, "pass_over_waitlist_margin"
        )
        >= float(l2_policy.minimum_pass_over_waitlist_margin),
        "l2_development_waitlist_over_reject_margin": _numeric_value(
            development_l2, "waitlist_over_reject_margin"
        )
        >= float(l2_policy.minimum_waitlist_over_reject_margin),
        "l2_validation_waitlist_over_reject_margin": _numeric_value(
            validation_l2, "waitlist_over_reject_margin"
        )
        >= float(l2_policy.minimum_waitlist_over_reject_margin),
    }
    return checks


def run_offline_evaluation(
    repository_root: Path,
    generated_at: datetime,
    runtime_kind: Literal["baseline", "candidate"] = "baseline",
    embedding_runtime: OfflineEmbeddingRuntime | None = None,
) -> dict[str, object]:
    if generated_at.tzinfo is None or generated_at.utcoffset() is None:
        raise ValueError("generated_at must include a timezone")
    configuration = load_offline_configuration(repository_root)
    pairs, profiles, jobs, rubrics, manifest, split = load_offline_data(
        repository_root,
        configuration,
    )
    runtime_directory = (
        configuration.baseline_runtime_directory
        if runtime_kind == "baseline"
        else configuration.candidate_runtime_directory
    )
    policy_set = build_offline_policy_set(
        repository_root,
        runtime_directory,
        f"runtime-v2-{runtime_kind}-l1-l2-v1",
        jobs,
        rubrics,
        runtime_kind == "candidate",
    )
    runtime = embedding_runtime or default_embedding_runtime(
        repository_root,
        runtime_directory,
        next(iter(jobs)),
        runtime_kind == "candidate",
    )
    bridges = build_precomputed_bridges(pairs, profiles, policy_set, runtime)
    results = evaluate_offline_cases(pairs, profiles, rubrics, policy_set, bridges)
    results_by_id = {item.pair_id: item for item in results}
    development = build_partition_summary(
        tuple(results_by_id[pair_id] for pair_id in split.development.pair_ids)
    )
    validation = build_partition_summary(
        tuple(results_by_id[pair_id] for pair_id in split.validation.pair_ids)
    )
    checks = evaluate_quality_checks(development, validation, configuration)
    return {
        "schema_version": "1.0.0",
        "report_id": f"runtime-v2-offline-l1-l2-{runtime_kind}-v1",
        "generated_at": generated_at.isoformat(),
        "runtime_kind": runtime_kind,
        "candidate_id": policy_set.candidate_id,
        "llm_provider_calls_made": False,
        "stage7_v1_test_accessed": False,
        "traceability": {
            "configuration_path": CONFIG_PATH.as_posix(),
            "configuration_sha256": file_sha256(repository_root / CONFIG_PATH),
            "reviewed_dataset_manifest_sha256": file_sha256(
                repository_root / configuration.reviewed_dataset_directory / "manifest.json"
            ),
            "split_manifest_sha256": file_sha256(
                repository_root / configuration.split_manifest_path
            ),
            "runtime_directory": runtime_directory.as_posix(),
            "runtime_manifest_sha256": (
                None
                if runtime_kind == "candidate"
                else file_sha256(repository_root / runtime_directory / "runtime_manifest.yaml")
            ),
            "l1_rules_sha256": file_sha256(repository_root / runtime_directory / "l1_rules.yaml"),
            "models_sha256": file_sha256(repository_root / runtime_directory / "models.yaml"),
            "dataset_id": manifest.dataset_id,
            "embedding_model_identifier": runtime.model_identifier,
            "embedding_model_version": runtime.model_version,
            "configured_embedding_model_executed": runtime.configured_model_executed,
        },
        "development": development,
        "validation": validation,
        "quality_gate": {"passed": all(checks.values()), "checks": checks},
        "limitations": [
            "The dataset is synthetic and human-reviewed by one reviewer.",
            "Development and validation are both tuning data and cannot support final performance claims.",
            "The frozen Stage 7 v1 test is excluded and remains an immutable runtime v1 result.",
            "No L3 provider output is included in this offline checkpoint.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated-at", required=True)
    parser.add_argument("--runtime-kind", choices=("baseline", "candidate"), default="baseline")
    parser.add_argument("--report-path")
    arguments = parser.parse_args()
    runtime_kind = cast(Literal["baseline", "candidate"], arguments.runtime_kind)
    generated_at = _timestamp(cast(str, arguments.generated_at))
    report = run_offline_evaluation(REPOSITORY_ROOT, generated_at, runtime_kind)
    default_path = BASELINE_REPORT_PATH if runtime_kind == "baseline" else CANDIDATE_REPORT_PATH
    report_path = (
        Path(cast(str, arguments.report_path))
        if arguments.report_path is not None
        else default_path
    )
    output_path = REPOSITORY_ROOT / report_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(output_path)


if __name__ == "__main__":
    main()
