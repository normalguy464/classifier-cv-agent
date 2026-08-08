from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Annotated, Literal, Self, cast

from pydantic import Field, model_validator

from backend.app.contracts import (
    CVProfile,
    ClassificationDecision,
    EvidenceStatus,
    JobProfile,
    ScoringRubric,
)
from backend.app.contracts.common import ContractModel, Identifier, NonEmptyText
from backend.app.infrastructure.config import RepositoryConfigurationLoader
from evaluation.datasets.synthetic_expansion import (
    ApprovedDatasetReview,
    DatasetRole,
    DatasetTier,
    PII_PATTERNS,
    PROTECTED_FIELD_NAMES,
    PendingDatasetReview,
    SyntheticPairAnnotation,
    SyntheticScenario,
    file_sha256,
)


class Stage7FileDigest(ContractModel):
    path: NonEmptyText
    sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    record_count: int = Field(ge=1)


class Stage7PriorDatasetReference(ContractModel):
    dataset_id: Identifier
    cv_profiles_path: NonEmptyText
    cv_profiles_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


class Stage7TestManifest(ContractModel):
    schema_version: Literal["1.1.0"]
    dataset_id: Literal["stage7-five-role-test-v1", "stage7-five-role-runtime-v2-test-v1"]
    dataset_version: Literal["1.0.0", "1.0.1"]
    status: Literal["draft_for_human_review"]
    generated_at: datetime
    source_type: Literal["synthetic_new_profiles"]
    runtime_configuration_set_id: Literal["five-role-runtime-v1", "five-role-runtime-v2"]
    runtime_manifest_path: NonEmptyText
    runtime_manifest_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    cv_schema_version: Literal["1.0.0"]
    job_profile_schema_version: Literal["1.0.0"]
    rubric_schema_version: Literal["1.0.0"]
    candidate_count: Literal[50]
    job_profile_count: Literal[5]
    rubric_count: Literal[5]
    pair_count: Literal[50]
    role_pair_counts: dict[DatasetRole, int]
    scenario_pair_counts: dict[SyntheticScenario, int]
    draft_label_counts: dict[ClassificationDecision, int]
    dataset_tier: Literal[DatasetTier.BRONZE]
    ground_truth_status: Literal["pending_human_review"]
    minimum_human_reviewers_for_gold: Literal[2]
    locked_for_evaluation: Literal[False]
    classifier_results_generated: Literal[False]
    llm_requests_made: Literal[False]
    source_dataset_version: Literal["1.0.0", "2.0.0"]
    source_manifest_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    prior_datasets: Annotated[tuple[Stage7PriorDatasetReference, ...], Field(min_length=1)]
    provenance: Annotated[tuple[NonEmptyText, ...], Field(min_length=1)]
    files: Annotated[tuple[Stage7FileDigest, ...], Field(min_length=1)]

    @model_validator(mode="after")
    def validate_manifest_counts(self) -> Stage7TestManifest:
        if self.generated_at.tzinfo is None or self.generated_at.utcoffset() is None:
            raise ValueError("generated_at must include a timezone")
        if self.role_pair_counts != {role: 10 for role in DatasetRole}:
            raise ValueError("stage 7 test set must contain ten pairs per role")
        if self.scenario_pair_counts != {scenario: 5 for scenario in SyntheticScenario}:
            raise ValueError("stage 7 test set must contain five pairs per scenario")
        expected_labels = {
            ClassificationDecision.PASS: 10,
            ClassificationDecision.WAITLIST: 10,
            ClassificationDecision.REJECT: 5,
            ClassificationDecision.NEEDS_REVIEW: 25,
        }
        if self.draft_label_counts != expected_labels:
            raise ValueError("stage 7 draft label distribution is invalid")
        file_paths = tuple(item.path for item in self.files)
        if len(file_paths) != len(set(file_paths)):
            raise ValueError("stage 7 file paths must be unique")
        prior_paths = tuple(item.cv_profiles_path for item in self.prior_datasets)
        if len(prior_paths) != len(set(prior_paths)):
            raise ValueError("stage 7 prior dataset paths must be unique")
        return self


class Stage7QualityReport(ContractModel):
    schema_version: Literal["1.0.0"]
    dataset_id: Identifier
    candidate_count: int = Field(ge=0)
    job_profile_count: int = Field(ge=0)
    rubric_count: int = Field(ge=0)
    pair_count: int = Field(ge=0)
    role_pair_counts: dict[DatasetRole, int]
    scenario_pair_counts: dict[SyntheticScenario, int]
    draft_label_counts: dict[ClassificationDecision, int]
    prior_candidate_overlap_count: int = Field(ge=0)
    prior_profile_id_overlap_count: int = Field(ge=0)
    prior_exact_evidence_overlap_count: int = Field(ge=0)
    maximum_prior_cv_token_jaccard: Decimal = Field(
        ge=Decimal("0"),
        le=Decimal("1"),
        decimal_places=4,
    )
    classifier_results_generated: bool
    errors: tuple[NonEmptyText, ...]
    warnings: tuple[NonEmptyText, ...]

    @property
    def passed(self) -> bool:
        return not self.errors


class Stage7EvaluationPreconditions(ContractModel):
    runtime_status: Literal["frozen_for_stage7"]
    dataset_status: Literal["human_reviewed_gold"]
    minimum_human_reviewers: Literal[2]
    human_review_mode: Literal["two_person_consensus_panel"]
    qc_errors_required: Literal[0]
    qc_warnings_required: Literal[0]
    classifier_results_generated_before_lock: Literal[False]
    prior_candidate_overlap_required: Literal[0]
    prior_profile_id_overlap_required: Literal[0]
    prior_exact_evidence_overlap_required: Literal[0]
    provider_calls_require_separate_user_authorization: Literal[True]


class Stage7EvaluationMetrics(ContractModel):
    minimum_accuracy: Decimal = Field(ge=Decimal("0"), le=Decimal("1"))
    minimum_macro_f1: Decimal = Field(ge=Decimal("0"), le=Decimal("1"))
    minimum_needs_review_recall: Decimal = Field(ge=Decimal("0"), le=Decimal("1"))
    maximum_false_reject_count: Literal[0]
    maximum_unsafe_pass_count: Literal[0]
    minimum_requirement_status_accuracy: Decimal = Field(
        ge=Decimal("0"),
        le=Decimal("1"),
    )
    maximum_unsafe_requirement_mismatch_count: Literal[0]
    maximum_criterion_mae: Decimal = Field(ge=Decimal("0"), le=Decimal("25"))
    maximum_total_score_mae: Decimal = Field(ge=Decimal("0"), le=Decimal("100"))
    maximum_review_rate: Decimal = Field(ge=Decimal("0"), le=Decimal("1"))
    minimum_valid_output_rate: Decimal = Field(ge=Decimal("0"), le=Decimal("1"))
    minimum_stability_exact_requirement_agreement: Decimal = Field(
        ge=Decimal("0"),
        le=Decimal("1"),
    )
    minimum_stability_route_agreement: Decimal = Field(
        ge=Decimal("0"),
        le=Decimal("1"),
    )
    maximum_stability_score_range: Decimal = Field(ge=Decimal("0"), le=Decimal("100"))


class Stage7RequestPolicy(ContractModel):
    primary_case_count: Literal[50]
    stability_case_count: Literal[5]
    repeats_per_stability_case: Literal[1]
    intended_request_count: Literal[55]
    maximum_http_request_count: Literal[60]
    retry_count_per_attempt: Literal[1]
    stop_on_provider_unavailability: Literal[True]
    persist_raw_provider_response: Literal[False]
    minimum_request_interval_seconds: Literal[1]
    request_timeout_seconds: Literal[60]
    max_completion_tokens: Literal[4096]
    reasoning_effort: Literal["none"]
    include_temperature_parameter: Literal[False]
    input_usd_per_million_tokens: Decimal = Field(gt=Decimal("0"))
    cached_input_usd_per_million_tokens: Decimal = Field(gt=Decimal("0"))
    output_usd_per_million_tokens: Decimal = Field(gt=Decimal("0"))
    assumed_max_input_tokens_per_request: Literal[12000]
    maximum_estimated_experiment_cost_usd: Decimal = Field(gt=Decimal("0"))

    @model_validator(mode="after")
    def validate_cost_policy(self) -> Self:
        actual = (
            self.input_usd_per_million_tokens,
            self.cached_input_usd_per_million_tokens,
            self.output_usd_per_million_tokens,
            self.maximum_estimated_experiment_cost_usd,
        )
        if actual != (
            Decimal("0.75"),
            Decimal("0.075"),
            Decimal("4.50"),
            Decimal("2.00"),
        ):
            raise ValueError("Stage 7 cost policy differs from the approved request plan")
        return self


class Stage7EvaluationProtocol(ContractModel):
    schema_version: Literal["1.0.0", "1.0.1"]
    protocol_id: Literal[
        "stage7-five-role-frozen-evaluation-v1",
        "stage7-five-role-runtime-v2-frozen-evaluation-v1",
    ]
    protocol_version: Literal["1.0.0", "1.0.1"]
    status: Literal["approved_for_frozen_evaluation"]
    approved_at: datetime
    runtime_configuration_set_id: Literal["five-role-runtime-v1", "five-role-runtime-v2"]
    test_dataset_id: Literal[
        "stage7-five-role-test-v1",
        "stage7-five-role-runtime-v2-test-v1",
    ]
    tuning_allowed: Literal[False]
    test_output_may_change_runtime: Literal[False]
    preconditions: Stage7EvaluationPreconditions
    metrics: Stage7EvaluationMetrics
    request_policy: Stage7RequestPolicy
    baselines: tuple[
        Literal["keyword", "tfidf", "embedding"],
        Literal["keyword", "tfidf", "embedding"],
        Literal["keyword", "tfidf", "embedding"],
    ]
    ablations: tuple[NonEmptyText, ...]
    bootstrap_seed: Literal[20260807, 20260808]
    bootstrap_resamples: Literal[2000]
    report_per_role_metrics: Literal[True]
    report_confusion_matrix: Literal[True]
    report_latency_and_usage: Literal[True]
    limitations_required: Literal[True]
    stability_pair_ids: Annotated[tuple[Identifier, ...], Field(min_length=5, max_length=5)]

    @model_validator(mode="after")
    def validate_protocol(self) -> Stage7EvaluationProtocol:
        if self.approved_at.tzinfo is None or self.approved_at.utcoffset() is None:
            raise ValueError("approved_at must include a timezone")
        if set(self.baselines) != {"keyword", "tfidf", "embedding"}:
            raise ValueError("stage 7 must evaluate all three baselines")
        if len(self.ablations) != 7 or len(set(self.ablations)) != 7:
            raise ValueError("stage 7 must define seven unique hybrid ablations")
        if len(set(self.stability_pair_ids)) != 5:
            raise ValueError("stage 7 stability pair identifiers must be unique")
        if self.metrics.minimum_accuracy != Decimal("0.70"):
            raise ValueError("stage 7 minimum accuracy must remain 0.70")
        if self.metrics.minimum_macro_f1 != Decimal("0.60"):
            raise ValueError("stage 7 minimum macro F1 must remain 0.60")
        expected_identity = {
            "five-role-runtime-v1": (
                "stage7-five-role-frozen-evaluation-v1",
                "stage7-five-role-test-v1",
                Decimal("1"),
                Decimal("0.95"),
            ),
            "five-role-runtime-v2": (
                "stage7-five-role-runtime-v2-frozen-evaluation-v1",
                "stage7-five-role-runtime-v2-test-v1",
                Decimal("0.80"),
                Decimal("1"),
            ),
        }[self.runtime_configuration_set_id]
        protocol_id, test_dataset_id, needs_review_recall, valid_output_rate = expected_identity
        if self.protocol_id != protocol_id or self.test_dataset_id != test_dataset_id:
            raise ValueError("stage 7 protocol identity does not match its runtime")
        if self.metrics.minimum_needs_review_recall != needs_review_recall:
            raise ValueError("stage 7 Needs Review recall differs from the approved protocol")
        if self.metrics.minimum_requirement_status_accuracy != Decimal("0.95"):
            raise ValueError("stage 7 requirement accuracy must remain 0.95")
        if self.metrics.maximum_criterion_mae != Decimal("3"):
            raise ValueError("stage 7 criterion MAE must remain at most 3")
        if self.metrics.maximum_total_score_mae != Decimal("12"):
            raise ValueError("stage 7 total score MAE must remain at most 12")
        if self.metrics.maximum_review_rate != Decimal("0.80"):
            raise ValueError("stage 7 review rate must remain at most 0.80")
        if self.metrics.minimum_valid_output_rate != valid_output_rate:
            raise ValueError("stage 7 valid output rate differs from the approved protocol")
        if self.metrics.minimum_stability_route_agreement != Decimal("1"):
            raise ValueError("stage 7 stability route agreement must remain 1")
        return self


class Stage7HumanReviewRecord(ContractModel):
    schema_version: Literal["1.0.0"]
    dataset_id: Literal["stage7-five-role-test-v1", "stage7-five-role-runtime-v2-test-v1"]
    dataset_version: Literal["1.0.0", "1.0.1"]
    review_mode: Literal["two_person_consensus_panel"]
    reviewer_references: Annotated[tuple[Identifier, Identifier], Field(min_length=2, max_length=2)]
    reviewed_at: datetime
    approved_pair_count: Literal[50]
    approved_correction_pair_ids: tuple[Identifier, ...]
    approval_statement: NonEmptyText

    @model_validator(mode="after")
    def validate_review(self) -> Self:
        if len(set(self.reviewer_references)) != 2:
            raise ValueError("stage 7 consensus review requires two unique reviewers")
        if self.reviewed_at.tzinfo is None or self.reviewed_at.utcoffset() is None:
            raise ValueError("reviewed_at must include a timezone")
        return self


class Stage7FrozenManifest(ContractModel):
    schema_version: Literal["1.0.0"]
    dataset_id: Literal["stage7-five-role-test-v1", "stage7-five-role-runtime-v2-test-v1"]
    dataset_version: Literal["1.0.0", "1.0.1"]
    status: Literal["human_reviewed_gold_locked"]
    frozen_at: datetime
    runtime_configuration_set_id: Literal["five-role-runtime-v1", "five-role-runtime-v2"]
    runtime_manifest_path: NonEmptyText
    runtime_manifest_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    source_directory: Literal[
        "data/to_review/stage7_test_v1",
        "data/to_review/stage7_runtime_v2_test_v1",
    ]
    source_manifest_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    review_record_path: Literal["review_record.json"]
    review_record_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    review_mode: Literal["two_person_consensus_panel"]
    reviewer_references: Annotated[tuple[Identifier, Identifier], Field(min_length=2, max_length=2)]
    reviewed_pair_count: Literal[50]
    pair_count: Literal[50]
    dataset_tier: Literal[DatasetTier.GOLD]
    ground_truth_status: Literal["human_reviewed_gold"]
    locked_for_evaluation: Literal[True]
    classifier_results_generated_before_lock: Literal[False]
    llm_requests_made_before_lock: Literal[False]
    final_label_counts: dict[ClassificationDecision, int]
    files: Annotated[tuple[Stage7FileDigest, ...], Field(min_length=4, max_length=4)]

    @model_validator(mode="after")
    def validate_frozen_manifest(self) -> Self:
        if self.frozen_at.tzinfo is None or self.frozen_at.utcoffset() is None:
            raise ValueError("frozen_at must include a timezone")
        if len(set(self.reviewer_references)) != 2:
            raise ValueError("frozen Stage 7 data requires two unique reviewers")
        expected_labels = {
            ClassificationDecision.PASS: 10,
            ClassificationDecision.WAITLIST: 10,
            ClassificationDecision.REJECT: 5,
            ClassificationDecision.NEEDS_REVIEW: 25,
        }
        if self.final_label_counts != expected_labels:
            raise ValueError("stage 7 final label distribution is invalid")
        if len({item.path for item in self.files}) != len(self.files):
            raise ValueError("frozen Stage 7 file paths must be unique")
        expected = {
            "stage7-five-role-test-v1": (
                "1.0.1",
                "five-role-runtime-v1",
                "data/to_review/stage7_test_v1",
            ),
            "stage7-five-role-runtime-v2-test-v1": (
                "1.0.0",
                "five-role-runtime-v2",
                "data/to_review/stage7_runtime_v2_test_v1",
            ),
        }[self.dataset_id]
        if (
            self.dataset_version,
            self.runtime_configuration_set_id,
            self.source_directory,
        ) != expected:
            raise ValueError("frozen Stage 7 manifest identity is inconsistent")
        return self


def expected_stage7_decision(
    annotation: SyntheticPairAnnotation,
    waitlist_minimum: Decimal = Decimal("70"),
    pass_minimum: Decimal = Decimal("85"),
    lower_review_band: tuple[Decimal, Decimal] = (Decimal("68"), Decimal("72")),
    upper_review_band: tuple[Decimal, Decimal] = (Decimal("83"), Decimal("87")),
) -> ClassificationDecision:
    statuses = {
        assessment.evidence_status for assessment in annotation.critical_requirement_assessments
    }
    score = annotation.total_score
    if (
        EvidenceStatus.MISSING in statuses
        or EvidenceStatus.CONFLICTING in statuses
        or lower_review_band[0] <= score <= lower_review_band[1]
        or upper_review_band[0] <= score <= upper_review_band[1]
        or EvidenceStatus.UNSATISFIED in statuses
        and score >= waitlist_minimum
        or score < waitlist_minimum
        and EvidenceStatus.UNSATISFIED not in statuses
    ):
        return ClassificationDecision.NEEDS_REVIEW
    if EvidenceStatus.UNSATISFIED in statuses:
        if score < waitlist_minimum:
            return ClassificationDecision.REJECT
        return ClassificationDecision.NEEDS_REVIEW
    if score >= pass_minimum:
        return ClassificationDecision.PASS
    if score >= waitlist_minimum:
        return ClassificationDecision.WAITLIST
    return ClassificationDecision.NEEDS_REVIEW


def _normalized_text(value: str) -> str:
    return " ".join(re.findall(r"\w+", value.casefold(), flags=re.UNICODE))


def _profile_text(profile: CVProfile) -> str:
    values: list[str] = []
    if profile.summary is not None:
        values.append(profile.summary)
    values.extend(evidence.text for evidence in profile.evidence)
    return _normalized_text(" ".join(values))


def _token_jaccard(left: str, right: str) -> Decimal:
    left_tokens = set(left.split())
    right_tokens = set(right.split())
    union = left_tokens.union(right_tokens)
    if not union:
        return Decimal("1")
    return Decimal(len(left_tokens.intersection(right_tokens))) / Decimal(len(union))


def _field_names(value: object) -> set[str]:
    if isinstance(value, dict):
        mapping = cast(dict[object, object], value)
        names = {str(key) for key in mapping}
        for nested in mapping.values():
            names.update(_field_names(nested))
        return names
    if isinstance(value, list):
        names: set[str] = set()
        for nested in cast(list[object], value):
            names.update(_field_names(nested))
        return names
    return set()


def _load_json_lines(path: Path, model_type: type[ContractModel]) -> tuple[ContractModel, ...]:
    return tuple(
        model_type.model_validate_json(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


def _empty_report(message: str) -> Stage7QualityReport:
    return Stage7QualityReport(
        schema_version="1.0.0",
        dataset_id="stage7-five-role-test-invalid",
        candidate_count=0,
        job_profile_count=0,
        rubric_count=0,
        pair_count=0,
        role_pair_counts={},
        scenario_pair_counts={},
        draft_label_counts={},
        prior_candidate_overlap_count=0,
        prior_profile_id_overlap_count=0,
        prior_exact_evidence_overlap_count=0,
        maximum_prior_cv_token_jaccard=Decimal("0"),
        classifier_results_generated=False,
        errors=(message,),
        warnings=(),
    )


def validate_stage7_test_set(
    repository_root: Path,
    dataset_directory: Path,
) -> Stage7QualityReport:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        manifest = Stage7TestManifest.model_validate_json(
            (dataset_directory / "manifest.json").read_text(encoding="utf-8")
        )
        profiles = cast(
            tuple[CVProfile, ...],
            _load_json_lines(dataset_directory / "cv_profiles.jsonl", CVProfile),
        )
        jobs = cast(
            tuple[JobProfile, ...],
            _load_json_lines(dataset_directory / "job_profiles.jsonl", JobProfile),
        )
        rubrics = cast(
            tuple[ScoringRubric, ...],
            _load_json_lines(dataset_directory / "rubrics.jsonl", ScoringRubric),
        )
        annotations = cast(
            tuple[SyntheticPairAnnotation, ...],
            _load_json_lines(
                dataset_directory / "pairs.jsonl",
                SyntheticPairAnnotation,
            ),
        )
    except (OSError, UnicodeError, ValueError) as error:
        return _empty_report(f"Stage 7 dataset loading failed: {error}")

    for digest in manifest.files:
        path = dataset_directory / digest.path
        if not path.is_file() or file_sha256(path) != digest.sha256:
            errors.append(f"Stage 7 file digest mismatch: {digest.path}")
    runtime_manifest_path = repository_root / manifest.runtime_manifest_path
    if (
        not runtime_manifest_path.is_file()
        or file_sha256(runtime_manifest_path) != manifest.runtime_manifest_sha256
    ):
        errors.append("Frozen runtime manifest digest mismatch")

    profile_by_id = {profile.cv_profile_id: profile for profile in profiles}
    job_by_id = {job.job_profile_id: job for job in jobs}
    rubric_by_id = {rubric.rubric_id: rubric for rubric in rubrics}
    if len(profile_by_id) != len(profiles):
        errors.append("Stage 7 CV profile identifiers must be unique")
    if len({profile.candidate_reference for profile in profiles}) != len(profiles):
        errors.append("Stage 7 candidate references must be unique")
    if len(job_by_id) != len(jobs):
        errors.append("Stage 7 job profile identifiers must be unique")
    if len(rubric_by_id) != len(rubrics):
        errors.append("Stage 7 rubric identifiers must be unique")
    if len({annotation.pair_id for annotation in annotations}) != len(annotations):
        errors.append("Stage 7 pair identifiers must be unique")

    role_counts: Counter[DatasetRole] = Counter()
    scenario_counts: Counter[SyntheticScenario] = Counter()
    label_counts: Counter[ClassificationDecision] = Counter()
    role_scenarios: defaultdict[DatasetRole, set[SyntheticScenario]] = defaultdict(set)
    semantic_prerequisites = (
        (
            "be-rest-api",
            "be-python",
            {EvidenceStatus.MISSING, EvidenceStatus.UNSATISFIED},
        ),
        (
            "be-testing",
            "be-python",
            {EvidenceStatus.MISSING, EvidenceStatus.UNSATISFIED},
        ),
        (
            "fe-language",
            "fe-web-foundations",
            {EvidenceStatus.UNSATISFIED},
        ),
        (
            "fe-framework",
            "fe-language",
            {EvidenceStatus.MISSING, EvidenceStatus.UNSATISFIED},
        ),
        (
            "qa-test-cases",
            "qa-testing-foundations",
            {EvidenceStatus.MISSING, EvidenceStatus.UNSATISFIED},
        ),
        (
            "qa-automation-foundation",
            "qa-testing-foundations",
            {EvidenceStatus.MISSING, EvidenceStatus.UNSATISFIED},
        ),
    )
    for annotation in annotations:
        role_counts[annotation.role] += 1
        scenario_counts[annotation.scenario] += 1
        label_counts[annotation.draft_label] += 1
        role_scenarios[annotation.role].add(annotation.scenario)
        profile = profile_by_id.get(annotation.cv_profile_id)
        job = job_by_id.get(annotation.job_profile_id)
        rubric = rubric_by_id.get(annotation.rubric_id)
        if profile is None or job is None or rubric is None:
            errors.append(f"Unknown Stage 7 pair reference: {annotation.pair_id}")
            continue
        if profile.candidate_reference != annotation.candidate_reference:
            errors.append(f"Candidate reference mismatch: {annotation.pair_id}")
        if rubric.job_profile_id != job.job_profile_id:
            errors.append(f"Job and rubric mismatch: {annotation.pair_id}")
        critical_ids = tuple(
            requirement.requirement_id
            for requirement in job.requirements
            if requirement.is_critical
        )
        assessment_ids = tuple(
            assessment.requirement_id for assessment in annotation.critical_requirement_assessments
        )
        if critical_ids != rubric.critical_requirement_ids or critical_ids != assessment_ids:
            errors.append(f"Critical requirement coverage mismatch: {annotation.pair_id}")
        status_by_requirement = {
            assessment.requirement_id: assessment.evidence_status
            for assessment in annotation.critical_requirement_assessments
        }
        for dependent_id, prerequisite_id, forbidden_statuses in semantic_prerequisites:
            if (
                status_by_requirement.get(dependent_id) is EvidenceStatus.SATISFIED
                and status_by_requirement.get(prerequisite_id) in forbidden_statuses
            ):
                errors.append(f"Cross-requirement evidence contradiction: {annotation.pair_id}")
        criterion_ids = tuple(criterion.criterion_id for criterion in rubric.criteria)
        assessment_criterion_ids = tuple(
            assessment.criterion_id for assessment in annotation.criterion_assessments
        )
        if criterion_ids != assessment_criterion_ids:
            errors.append(f"Criterion coverage mismatch: {annotation.pair_id}")
        known_evidence_ids = {evidence.evidence_id for evidence in profile.evidence}
        referenced_evidence_ids = {
            evidence_id
            for assessment in annotation.critical_requirement_assessments
            for evidence_id in assessment.evidence_ids
        }
        referenced_evidence_ids.update(
            evidence_id
            for assessment in annotation.criterion_assessments
            for evidence_id in assessment.evidence_ids
        )
        if not referenced_evidence_ids.issubset(known_evidence_ids):
            errors.append(f"Unknown evidence reference: {annotation.pair_id}")
        if manifest.runtime_configuration_set_id == "five-role-runtime-v2":
            expected_decision = expected_stage7_decision(
                annotation,
                waitlist_minimum=Decimal("67"),
                pass_minimum=Decimal("82"),
                lower_review_band=(Decimal("65"), Decimal("69")),
                upper_review_band=(Decimal("80"), Decimal("84")),
            )
        else:
            expected_decision = expected_stage7_decision(annotation)
        if annotation.draft_label is not expected_decision:
            errors.append(f"Draft decision policy mismatch: {annotation.pair_id}")
        if annotation.dataset_tier is not DatasetTier.BRONZE:
            errors.append(f"Stage 7 draft pair is not Bronze: {annotation.pair_id}")
        if not isinstance(annotation.review, PendingDatasetReview):
            errors.append(f"Stage 7 draft pair contains a human review: {annotation.pair_id}")
        if annotation.partition != "unassigned":
            errors.append(f"Stage 7 draft pair has an assigned partition: {annotation.pair_id}")
        opaque_values = (
            annotation.pair_id,
            annotation.cv_profile_id,
            annotation.candidate_reference,
        )
        if any(annotation.scenario.value in value for value in opaque_values):
            errors.append(f"Scenario leaked through an identifier: {annotation.pair_id}")

    expected_scenarios = set(SyntheticScenario)
    for role in DatasetRole:
        if role_scenarios[role] != expected_scenarios:
            errors.append(f"Scenario coverage is incomplete for role {role.value}")

    try:
        runtime_directory = (repository_root / manifest.runtime_manifest_path).parent
        loader = RepositoryConfigurationLoader(repository_root, runtime_directory)
        runtime_manifest = loader.runtime_manifest
        if runtime_manifest is None or runtime_manifest.configuration_status != "frozen_for_stage7":
            errors.append("Stage 7 requires the frozen five-role runtime")
        runtime_jobs = {
            artifact.job_profile_id: artifact.to_contract()
            for artifact in loader.load_job_artifacts()
        }
        for job in jobs:
            if runtime_jobs.get(job.job_profile_id) != job:
                errors.append(f"Stage 7 job differs from frozen runtime: {job.job_profile_id}")
        for rubric in rubrics:
            loaded = loader.load_for_job(rubric.job_profile_id)
            if loaded.rubric != rubric:
                errors.append(f"Stage 7 rubric differs from frozen runtime: {rubric.rubric_id}")
    except (OSError, UnicodeError, ValueError) as error:
        errors.append(f"Frozen runtime validation failed: {error}")

    prior_profiles: list[CVProfile] = []
    for prior in manifest.prior_datasets:
        path = repository_root / prior.cv_profiles_path
        if not path.is_file() or file_sha256(path) != prior.cv_profiles_sha256:
            errors.append(f"Prior dataset digest mismatch: {prior.dataset_id}")
            continue
        try:
            prior_profiles.extend(cast(tuple[CVProfile, ...], _load_json_lines(path, CVProfile)))
        except (OSError, UnicodeError, ValueError) as error:
            errors.append(f"Prior dataset loading failed for {prior.dataset_id}: {error}")

    prior_candidate_references = {profile.candidate_reference for profile in prior_profiles}
    prior_profile_ids = {profile.cv_profile_id for profile in prior_profiles}
    candidate_overlaps = {
        profile.candidate_reference
        for profile in profiles
        if profile.candidate_reference in prior_candidate_references
    }
    profile_id_overlaps = {
        profile.cv_profile_id for profile in profiles if profile.cv_profile_id in prior_profile_ids
    }
    prior_evidence_texts = {
        _normalized_text(evidence.text)
        for profile in prior_profiles
        for evidence in profile.evidence
    }
    evidence_overlaps = {
        _normalized_text(evidence.text)
        for profile in profiles
        for evidence in profile.evidence
        if _normalized_text(evidence.text) in prior_evidence_texts
    }
    if candidate_overlaps:
        errors.append("Stage 7 candidate references overlap prior data")
    if profile_id_overlaps:
        errors.append("Stage 7 CV profile identifiers overlap prior data")
    if evidence_overlaps:
        errors.append("Stage 7 evidence text exactly overlaps prior data")

    prior_profile_texts = tuple(_profile_text(profile) for profile in prior_profiles)
    maximum_jaccard = Decimal("0")
    for profile in profiles:
        current_text = _profile_text(profile)
        for prior_text in prior_profile_texts:
            maximum_jaccard = max(maximum_jaccard, _token_jaccard(current_text, prior_text))
    if maximum_jaccard >= Decimal("0.82"):
        errors.append("Stage 7 CV text is too similar to a prior profile")

    for profile in profiles:
        payload = profile.model_dump(mode="json")
        if _field_names(payload).intersection(PROTECTED_FIELD_NAMES):
            errors.append(f"Protected field found in {profile.cv_profile_id}")
        serialized = json.dumps(payload, ensure_ascii=False)
        if any(pattern.search(serialized) for pattern in PII_PATTERNS):
            errors.append(f"PII pattern found in {profile.cv_profile_id}")

    if len(profiles) != manifest.candidate_count:
        errors.append("Stage 7 candidate count does not match manifest")
    if len(jobs) != manifest.job_profile_count:
        errors.append("Stage 7 job count does not match manifest")
    if len(rubrics) != manifest.rubric_count:
        errors.append("Stage 7 rubric count does not match manifest")
    if len(annotations) != manifest.pair_count:
        errors.append("Stage 7 pair count does not match manifest")
    if dict(role_counts) != manifest.role_pair_counts:
        errors.append("Stage 7 role counts do not match manifest")
    if dict(scenario_counts) != manifest.scenario_pair_counts:
        errors.append("Stage 7 scenario counts do not match manifest")
    if dict(label_counts) != manifest.draft_label_counts:
        errors.append("Stage 7 draft label counts do not match manifest")

    return Stage7QualityReport(
        schema_version="1.0.0",
        dataset_id=manifest.dataset_id,
        candidate_count=len(profiles),
        job_profile_count=len(jobs),
        rubric_count=len(rubrics),
        pair_count=len(annotations),
        role_pair_counts=dict(role_counts),
        scenario_pair_counts=dict(scenario_counts),
        draft_label_counts=dict(label_counts),
        prior_candidate_overlap_count=len(candidate_overlaps),
        prior_profile_id_overlap_count=len(profile_id_overlaps),
        prior_exact_evidence_overlap_count=len(evidence_overlaps),
        maximum_prior_cv_token_jaccard=maximum_jaccard.quantize(Decimal("0.0001")),
        classifier_results_generated=manifest.classifier_results_generated,
        errors=tuple(dict.fromkeys(errors)),
        warnings=tuple(dict.fromkeys(warnings)),
    )


def stage7_manifest_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_stage7_frozen_test_set(
    repository_root: Path,
    dataset_directory: Path,
) -> Stage7QualityReport:
    errors: list[str] = []
    try:
        manifest = Stage7FrozenManifest.model_validate_json(
            (dataset_directory / "manifest.json").read_text(encoding="utf-8")
        )
        source_directory = repository_root / manifest.source_directory
        source_report = validate_stage7_test_set(repository_root, source_directory)
        errors.extend(source_report.errors)
        review_record = Stage7HumanReviewRecord.model_validate_json(
            (dataset_directory / "review_record.json").read_text(encoding="utf-8")
        )
        frozen_annotations = cast(
            tuple[SyntheticPairAnnotation, ...],
            _load_json_lines(dataset_directory / "pairs.jsonl", SyntheticPairAnnotation),
        )
        source_annotations = cast(
            tuple[SyntheticPairAnnotation, ...],
            _load_json_lines(source_directory / "pairs.jsonl", SyntheticPairAnnotation),
        )
    except (OSError, UnicodeError, ValueError) as error:
        return _empty_report(f"Frozen Stage 7 dataset loading failed: {error}")
    if (
        review_record.dataset_id != manifest.dataset_id
        or review_record.dataset_version != manifest.dataset_version
    ):
        errors.append("Frozen Stage 7 review record identity does not match")
    source_manifest_path = source_directory / "manifest.json"
    if stage7_manifest_sha256(source_manifest_path) != manifest.source_manifest_sha256:
        errors.append("Frozen Stage 7 source manifest digest mismatch")
    runtime_manifest_path = repository_root / manifest.runtime_manifest_path
    if (
        not runtime_manifest_path.is_file()
        or stage7_manifest_sha256(runtime_manifest_path) != manifest.runtime_manifest_sha256
    ):
        errors.append("Frozen Stage 7 runtime manifest digest mismatch")
    review_record_path = dataset_directory / manifest.review_record_path
    if (
        not review_record_path.is_file()
        or stage7_manifest_sha256(review_record_path) != manifest.review_record_sha256
    ):
        errors.append("Frozen Stage 7 review record digest mismatch")
    if review_record.reviewer_references != manifest.reviewer_references:
        errors.append("Frozen Stage 7 reviewer references do not match")
    for digest in manifest.files:
        path = dataset_directory / digest.path
        if not path.is_file() or stage7_manifest_sha256(path) != digest.sha256:
            errors.append(f"Frozen Stage 7 file digest mismatch: {digest.path}")
    for name in ("cv_profiles.jsonl", "job_profiles.jsonl", "rubrics.jsonl"):
        if (dataset_directory / name).read_bytes() != (source_directory / name).read_bytes():
            errors.append(f"Frozen Stage 7 source artifact changed: {name}")
    if len(frozen_annotations) != len(source_annotations):
        errors.append("Frozen Stage 7 pair count differs from the reviewed source")
    else:
        for source, frozen in zip(source_annotations, frozen_annotations, strict=True):
            source_payload = source.model_dump(mode="json", exclude={"dataset_tier", "review"})
            frozen_payload = frozen.model_dump(mode="json", exclude={"dataset_tier", "review"})
            if source_payload != frozen_payload:
                errors.append(f"Frozen Stage 7 annotation changed: {source.pair_id}")
                continue
            if frozen.dataset_tier is not DatasetTier.GOLD:
                errors.append(f"Frozen Stage 7 annotation is not Gold: {frozen.pair_id}")
            if not isinstance(frozen.review, ApprovedDatasetReview):
                errors.append(f"Frozen Stage 7 annotation lacks approval: {frozen.pair_id}")
                continue
            if (
                frozen.review.human_review_count != 2
                or frozen.review.reviewer_references != manifest.reviewer_references
                or frozen.review.final_label is not frozen.draft_label
                or frozen.review.criterion_score_overrides
            ):
                errors.append(f"Frozen Stage 7 review metadata is invalid: {frozen.pair_id}")
    final_label_counts = Counter(
        annotation.review.final_label
        for annotation in frozen_annotations
        if isinstance(annotation.review, ApprovedDatasetReview)
    )
    if dict(final_label_counts) != manifest.final_label_counts:
        errors.append("Frozen Stage 7 final label counts do not match the manifest")
    return Stage7QualityReport(
        schema_version="1.0.0",
        dataset_id=manifest.dataset_id,
        candidate_count=source_report.candidate_count,
        job_profile_count=source_report.job_profile_count,
        rubric_count=source_report.rubric_count,
        pair_count=len(frozen_annotations),
        role_pair_counts=source_report.role_pair_counts,
        scenario_pair_counts=source_report.scenario_pair_counts,
        draft_label_counts=dict(final_label_counts),
        prior_candidate_overlap_count=source_report.prior_candidate_overlap_count,
        prior_profile_id_overlap_count=source_report.prior_profile_id_overlap_count,
        prior_exact_evidence_overlap_count=source_report.prior_exact_evidence_overlap_count,
        maximum_prior_cv_token_jaccard=source_report.maximum_prior_cv_token_jaccard,
        classifier_results_generated=False,
        errors=tuple(dict.fromkeys(errors)),
        warnings=source_report.warnings,
    )
