from __future__ import annotations

import hashlib
import re
from collections import Counter
from pathlib import Path
from datetime import datetime
from typing import Annotated, Literal, Self, TypeVar, cast

from pydantic import Field, model_validator

from backend.app.contracts import CVProfile, ClassificationDecision, JobProfile, ScoringRubric
from backend.app.contracts.common import ContractModel, Identifier, NonEmptyText
from evaluation.datasets.synthetic_expansion import (
    ApprovedDatasetReview,
    DatasetRole,
    DatasetTier,
    SyntheticPairAnnotation,
)


class RuntimeV2PriorReference(ContractModel):
    dataset_id: Identifier
    directory: NonEmptyText


class RuntimeV2FileDigest(ContractModel):
    path: NonEmptyText
    sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    record_count: int = Field(ge=1)


class RuntimeV2DevelopmentManifest(ContractModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    dataset_id: Literal["five-role-runtime-v2-development-v1"]
    dataset_version: Literal["1.0.0"]
    status: Literal["draft_for_human_review"]
    generated_at: NonEmptyText
    source_runtime_configuration_set_id: Literal["five-role-runtime-v1"]
    intended_runtime_configuration_set_id: Literal["five-role-runtime-v2"]
    roles: Annotated[tuple[DatasetRole, ...], Field(min_length=5, max_length=5)]
    cv_profile_count: Literal[75]
    job_profile_count: Literal[5]
    rubric_count: Literal[5]
    pair_count: Literal[75]
    pair_count_per_role: Literal[15]
    tier: Literal[DatasetTier.BRONZE]
    ground_truth_status: Literal["pending_human_review"]
    tuning_allowed: Literal[False]
    classifier_results_generated: Literal[False]
    llm_requests_made: Literal[False]
    prior_references: Annotated[tuple[RuntimeV2PriorReference, ...], Field(min_length=1)]
    provenance: Annotated[tuple[NonEmptyText, ...], Field(min_length=1)]
    files: Annotated[tuple[RuntimeV2FileDigest, ...], Field(min_length=4)]

    @model_validator(mode="after")
    def validate_roles(self) -> Self:
        if set(self.roles) != set(DatasetRole):
            raise ValueError("runtime v2 development must cover all five roles")
        file_paths = tuple(item.path for item in self.files)
        if len(file_paths) != len(set(file_paths)):
            raise ValueError("manifest file paths must be unique")
        return self


class RuntimeV2DevelopmentQualityReport(ContractModel):
    dataset_id: Identifier
    cv_profile_count: int = Field(ge=0)
    pair_count: int = Field(ge=0)
    role_pair_counts: dict[DatasetRole, int]
    label_counts: dict[ClassificationDecision, int]
    exact_prior_evidence_overlap_count: int = Field(ge=0)
    maximum_prior_cv_token_jaccard: float = Field(ge=0, le=1)
    errors: tuple[NonEmptyText, ...]
    warnings: tuple[NonEmptyText, ...]

    @property
    def passed(self) -> bool:
        return not self.errors


class RuntimeV2HumanReviewRecord(ContractModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    dataset_id: Literal["five-role-runtime-v2-development-v1"]
    review_status: Literal["approved_unchanged"]
    reviewer_reference: Identifier
    reviewed_at: datetime
    approved_pair_count: Literal[75]
    approval_scope: Annotated[tuple[NonEmptyText, ...], Field(min_length=4, max_length=4)]
    user_statement: NonEmptyText

    @model_validator(mode="after")
    def validate_timestamp(self) -> Self:
        if self.reviewed_at.tzinfo is None or self.reviewed_at.utcoffset() is None:
            raise ValueError("reviewed_at must include a timezone")
        return self


class RuntimeV2ReviewedManifest(ContractModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    dataset_id: Literal["five-role-runtime-v2-development-v1-reviewed-silver"]
    dataset_version: Literal["1.1.0"]
    status: Literal["human_reviewed_silver"]
    reviewed_at: datetime
    source_dataset_id: Literal["five-role-runtime-v2-development-v1"]
    source_dataset_version: Literal["1.0.0"]
    source_manifest_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    reviewer_references: Annotated[tuple[Identifier, ...], Field(min_length=1)]
    roles: Annotated[tuple[DatasetRole, ...], Field(min_length=5, max_length=5)]
    cv_profile_count: Literal[75]
    job_profile_count: Literal[5]
    rubric_count: Literal[5]
    pair_count: Literal[75]
    tier: Literal[DatasetTier.SILVER]
    ground_truth_status: Literal["human_reviewed_silver"]
    split_status: Literal["unassigned"]
    classifier_results_generated: Literal[False]
    llm_requests_made: Literal[False]
    provenance: Annotated[tuple[NonEmptyText, ...], Field(min_length=1)]
    files: Annotated[tuple[RuntimeV2FileDigest, ...], Field(min_length=5)]

    @model_validator(mode="after")
    def validate_reviewed_manifest(self) -> Self:
        if self.reviewed_at.tzinfo is None or self.reviewed_at.utcoffset() is None:
            raise ValueError("reviewed_at must include a timezone")
        if set(self.roles) != set(DatasetRole):
            raise ValueError("reviewed runtime v2 development must cover all five roles")
        return self


class RuntimeV2Partition(ContractModel):
    partition_id: Identifier
    intended_use: Literal["rule_and_policy_development", "configuration_validation"]
    tuning_allowed: Literal[True]
    final_performance_reporting_allowed: Literal[False]
    pair_count: int = Field(ge=1)
    role_pair_counts: dict[DatasetRole, int]
    label_pair_counts: dict[ClassificationDecision, int]
    candidate_references: Annotated[tuple[Identifier, ...], Field(min_length=1)]
    pair_ids: Annotated[tuple[Identifier, ...], Field(min_length=1)]

    @model_validator(mode="after")
    def validate_partition(self) -> Self:
        if self.pair_count != len(self.pair_ids):
            raise ValueError("partition pair count does not match pair identifiers")
        if self.pair_count != len(self.candidate_references):
            raise ValueError("runtime v2 partitions require one pair per candidate")
        if self.pair_count != sum(self.role_pair_counts.values()):
            raise ValueError("partition role counts do not match pair count")
        if self.pair_count != sum(self.label_pair_counts.values()):
            raise ValueError("partition label counts do not match pair count")
        if len(set(self.pair_ids)) != len(self.pair_ids):
            raise ValueError("partition pair identifiers must be unique")
        if len(set(self.candidate_references)) != len(self.candidate_references):
            raise ValueError("partition candidate references must be unique")
        return self


class RuntimeV2SplitManifest(ContractModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    split_manifest_id: Literal["five-role-runtime-v2-development-split-v1"]
    split_policy_version: Literal["1.0.0"]
    selection_method: Literal["role-label-stratified-candidate-sha256-v1"]
    split_seed_identifier: Identifier
    created_at: datetime
    source_dataset_id: Literal["five-role-runtime-v2-development-v1-reviewed-silver"]
    source_dataset_version: Literal["1.1.0"]
    source_manifest_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    frozen_test_created: Literal[False]
    stage7_v1_test_excluded: Literal[True]
    development: RuntimeV2Partition
    validation: RuntimeV2Partition

    @model_validator(mode="after")
    def validate_split(self) -> Self:
        if self.created_at.tzinfo is None or self.created_at.utcoffset() is None:
            raise ValueError("created_at must include a timezone")
        development_candidates = set(self.development.candidate_references)
        validation_candidates = set(self.validation.candidate_references)
        if development_candidates.intersection(validation_candidates):
            raise ValueError("candidate references must not cross partitions")
        if set(self.development.pair_ids).intersection(self.validation.pair_ids):
            raise ValueError("pair identifiers must not cross partitions")
        if self.development.pair_count != 50 or self.validation.pair_count != 25:
            raise ValueError("runtime v2 split must contain 50 development and 25 validation pairs")
        if self.development.role_pair_counts != {role: 10 for role in DatasetRole}:
            raise ValueError("development must contain ten pairs per role")
        if self.validation.role_pair_counts != {role: 5 for role in DatasetRole}:
            raise ValueError("validation must contain five pairs per role")
        expected_development_labels = {
            ClassificationDecision.PASS: 10,
            ClassificationDecision.WAITLIST: 5,
            ClassificationDecision.REJECT: 5,
            ClassificationDecision.NEEDS_REVIEW: 30,
        }
        expected_validation_labels = {
            ClassificationDecision.PASS: 5,
            ClassificationDecision.WAITLIST: 5,
            ClassificationDecision.REJECT: 5,
            ClassificationDecision.NEEDS_REVIEW: 10,
        }
        if self.development.label_pair_counts != expected_development_labels:
            raise ValueError("development label distribution is invalid")
        if self.validation.label_pair_counts != expected_validation_labels:
            raise ValueError("validation label distribution is invalid")
        return self


PII_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    re.compile(r"(?<!\d)(?:\+84|0)(?:3|5|7|8|9)\d{8}(?!\d)"),
    re.compile(r"\b(?:\d{9}|\d{12})\b"),
)
PROTECTED_FIELD_NAMES = {
    "age",
    "date_of_birth",
    "disability",
    "ethnicity",
    "gender",
    "hometown",
    "marital_status",
    "religion",
}
EXPECTED_CRITERION_MAXIMUMS = (30, 25, 20, 15, 10)
ContractType = TypeVar("ContractType", bound=ContractModel)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_lines(path: Path, model_type: type[ContractType]) -> tuple[ContractType, ...]:
    return tuple(
        model_type.model_validate_json(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


def _field_names(value: object) -> set[str]:
    if isinstance(value, dict):
        mapping = cast(dict[object, object], value)
        names = {str(key) for key in mapping}
        for item in mapping.values():
            names.update(_field_names(item))
        return names
    if isinstance(value, list | tuple):
        sequence = cast(list[object] | tuple[object, ...], value)
        names: set[str] = set()
        for item in sequence:
            names.update(_field_names(item))
        return names
    return set()


def _normalized_tokens(value: str) -> set[str]:
    return set(re.findall(r"[\w+#.-]+", value.casefold()))


def _profile_text(profile: CVProfile) -> str:
    return " ".join(item.text for item in profile.evidence)


def _token_jaccard(left: str, right: str) -> float:
    left_tokens = _normalized_tokens(left)
    right_tokens = _normalized_tokens(right)
    union = left_tokens | right_tokens
    if not union:
        return 0.0
    return len(left_tokens & right_tokens) / len(union)


def _prior_profiles(references: tuple[RuntimeV2PriorReference, ...]) -> tuple[CVProfile, ...]:
    profiles: list[CVProfile] = []
    for reference in references:
        path = Path(reference.directory) / "cv_profiles.jsonl"
        profiles.extend(_load_lines(path, CVProfile))
    return tuple(profiles)


def validate_runtime_v2_development(
    dataset_directory: Path,
    repository_root: Path,
) -> RuntimeV2DevelopmentQualityReport:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        profiles = _load_lines(dataset_directory / "cv_profiles.jsonl", CVProfile)
        jobs = _load_lines(dataset_directory / "job_profiles.jsonl", JobProfile)
        rubrics = _load_lines(dataset_directory / "rubrics.jsonl", ScoringRubric)
        pairs = _load_lines(dataset_directory / "pairs.jsonl", SyntheticPairAnnotation)
        manifest = RuntimeV2DevelopmentManifest.model_validate_json(
            (dataset_directory / "manifest.json").read_text(encoding="utf-8")
        )
    except (OSError, UnicodeError, ValueError) as error:
        return RuntimeV2DevelopmentQualityReport(
            dataset_id="five-role-runtime-v2-development-invalid",
            cv_profile_count=0,
            pair_count=0,
            role_pair_counts={},
            label_counts={},
            exact_prior_evidence_overlap_count=0,
            maximum_prior_cv_token_jaccard=0,
            errors=(f"Dataset loading failed: {error}",),
            warnings=(),
        )

    typed_profiles = tuple(CVProfile.model_validate(item) for item in profiles)
    typed_jobs = tuple(JobProfile.model_validate(item) for item in jobs)
    typed_rubrics = tuple(ScoringRubric.model_validate(item) for item in rubrics)
    typed_pairs = tuple(SyntheticPairAnnotation.model_validate(item) for item in pairs)
    profile_by_id = {item.cv_profile_id: item for item in typed_profiles}
    job_by_id = {item.job_profile_id: item for item in typed_jobs}
    rubric_by_id = {item.rubric_id: item for item in typed_rubrics}
    role_counts: Counter[DatasetRole] = Counter()
    label_counts: Counter[ClassificationDecision] = Counter()

    if len(profile_by_id) != len(typed_profiles):
        errors.append("CV profile identifiers must be unique")
    if len({item.candidate_reference for item in typed_profiles}) != len(typed_profiles):
        errors.append("Candidate references must be unique")
    if len({item.pair_id for item in typed_pairs}) != len(typed_pairs):
        errors.append("Pair identifiers must be unique")

    for pair in typed_pairs:
        role_counts[pair.role] += 1
        label_counts[pair.draft_label] += 1
        profile = profile_by_id.get(pair.cv_profile_id)
        job = job_by_id.get(pair.job_profile_id)
        rubric = rubric_by_id.get(pair.rubric_id)
        if profile is None or job is None or rubric is None:
            errors.append(f"Unknown profile, job or rubric in {pair.pair_id}")
            continue
        if profile.candidate_reference != pair.candidate_reference:
            errors.append(f"Candidate reference mismatch in {pair.pair_id}")
        if rubric.job_profile_id != job.job_profile_id:
            errors.append(f"Job and rubric link mismatch in {pair.pair_id}")
        critical_ids = {item.requirement_id for item in job.requirements if item.is_critical}
        assessment_ids = {item.requirement_id for item in pair.critical_requirement_assessments}
        if critical_ids != assessment_ids or critical_ids != set(rubric.critical_requirement_ids):
            errors.append(f"Critical requirement coverage mismatch in {pair.pair_id}")
        maximums = tuple(int(item.maximum_points) for item in pair.criterion_assessments)
        if maximums != EXPECTED_CRITERION_MAXIMUMS:
            errors.append(f"Criterion maximums mismatch in {pair.pair_id}")
        known_evidence = {item.evidence_id for item in profile.evidence}
        referenced_evidence = {
            evidence_id
            for assessment in pair.critical_requirement_assessments
            for evidence_id in assessment.evidence_ids
        }
        referenced_evidence.update(
            evidence_id
            for assessment in pair.criterion_assessments
            for evidence_id in assessment.evidence_ids
        )
        if not referenced_evidence.issubset(known_evidence):
            errors.append(f"Unknown evidence reference in {pair.pair_id}")
        if pair.dataset_tier is not DatasetTier.BRONZE or pair.review.status != "pending":
            errors.append(f"Unreviewed pair is not Bronze and pending in {pair.pair_id}")

    expected_role_counts = {role: 15 for role in DatasetRole}
    if dict(role_counts) != expected_role_counts:
        errors.append("Each role must contain exactly 15 development pairs")
    if set(label_counts) != set(ClassificationDecision):
        errors.append("Every classifier decision must be represented")
    if (len(typed_profiles), len(typed_jobs), len(typed_rubrics), len(typed_pairs)) != (
        manifest.cv_profile_count,
        manifest.job_profile_count,
        manifest.rubric_count,
        manifest.pair_count,
    ):
        errors.append("Manifest counts do not match dataset files")

    digest_by_path = {item.path: item for item in manifest.files}
    for relative_path, count in {
        "cv_profiles.jsonl": len(typed_profiles),
        "job_profiles.jsonl": len(typed_jobs),
        "rubrics.jsonl": len(typed_rubrics),
        "pairs.jsonl": len(typed_pairs),
    }.items():
        digest = digest_by_path.get(relative_path)
        path = dataset_directory / relative_path
        if digest is None:
            errors.append(f"Missing manifest digest for {relative_path}")
        elif digest.record_count != count or digest.sha256 != file_sha256(path):
            errors.append(f"Manifest digest mismatch for {relative_path}")

    for profile in typed_profiles:
        payload = profile.model_dump(mode="json")
        if PROTECTED_FIELD_NAMES.intersection(_field_names(payload)):
            errors.append(f"Protected field detected in {profile.cv_profile_id}")
        serialized = profile.model_dump_json()
        if any(pattern.search(serialized) for pattern in PII_PATTERNS):
            errors.append(f"Potential PII detected in {profile.cv_profile_id}")

    resolved_references = tuple(
        RuntimeV2PriorReference(
            dataset_id=item.dataset_id,
            directory=str(repository_root / item.directory),
        )
        for item in manifest.prior_references
    )
    try:
        prior_profiles = _prior_profiles(resolved_references)
    except (OSError, UnicodeError, ValueError) as error:
        errors.append(f"Prior dataset loading failed: {error}")
        prior_profiles = ()
    prior_evidence = {
        item.text.casefold().strip() for profile in prior_profiles for item in profile.evidence
    }
    current_evidence = {
        item.text.casefold().strip() for profile in typed_profiles for item in profile.evidence
    }
    exact_overlap_count = len(prior_evidence & current_evidence)
    if exact_overlap_count:
        errors.append("Exact evidence text overlaps a prior dataset")
    maximum_jaccard = max(
        (
            _token_jaccard(_profile_text(current), _profile_text(prior))
            for current in typed_profiles
            for prior in prior_profiles
        ),
        default=0.0,
    )
    if maximum_jaccard >= 0.82:
        errors.append("Maximum prior CV token Jaccard must remain below 0.82")

    return RuntimeV2DevelopmentQualityReport(
        dataset_id=manifest.dataset_id,
        cv_profile_count=len(typed_profiles),
        pair_count=len(typed_pairs),
        role_pair_counts=dict(role_counts),
        label_counts=dict(label_counts),
        exact_prior_evidence_overlap_count=exact_overlap_count,
        maximum_prior_cv_token_jaccard=maximum_jaccard,
        errors=tuple(dict.fromkeys(errors)),
        warnings=tuple(dict.fromkeys(warnings)),
    )


def validate_runtime_v2_reviewed(
    dataset_directory: Path,
    source_directory: Path,
    repository_root: Path,
) -> RuntimeV2DevelopmentQualityReport:
    source_report = validate_runtime_v2_development(source_directory, repository_root)
    errors = list(source_report.errors)
    warnings = list(source_report.warnings)
    try:
        manifest = RuntimeV2ReviewedManifest.model_validate_json(
            (dataset_directory / "manifest.json").read_text(encoding="utf-8")
        )
        review_record = RuntimeV2HumanReviewRecord.model_validate_json(
            (dataset_directory / "review_record.json").read_text(encoding="utf-8")
        )
        profiles = _load_lines(dataset_directory / "cv_profiles.jsonl", CVProfile)
        jobs = _load_lines(dataset_directory / "job_profiles.jsonl", JobProfile)
        rubrics = _load_lines(dataset_directory / "rubrics.jsonl", ScoringRubric)
        pairs = _load_lines(dataset_directory / "pairs.jsonl", SyntheticPairAnnotation)
        source_pairs = _load_lines(source_directory / "pairs.jsonl", SyntheticPairAnnotation)
    except (OSError, UnicodeError, ValueError) as error:
        errors.append(f"Reviewed dataset loading failed: {error}")
        return RuntimeV2DevelopmentQualityReport(
            dataset_id="five-role-runtime-v2-development-reviewed-invalid",
            cv_profile_count=0,
            pair_count=0,
            role_pair_counts={},
            label_counts={},
            exact_prior_evidence_overlap_count=source_report.exact_prior_evidence_overlap_count,
            maximum_prior_cv_token_jaccard=source_report.maximum_prior_cv_token_jaccard,
            errors=tuple(dict.fromkeys(errors)),
            warnings=tuple(dict.fromkeys(warnings)),
        )

    source_manifest_path = source_directory / "manifest.json"
    if manifest.source_manifest_sha256 != file_sha256(source_manifest_path):
        errors.append("Reviewed manifest source hash mismatch")
    if review_record.reviewer_reference not in manifest.reviewer_references:
        errors.append("Review record reviewer is absent from reviewed manifest")
    if review_record.reviewed_at != manifest.reviewed_at:
        errors.append("Review record timestamp does not match reviewed manifest")
    if (len(profiles), len(jobs), len(rubrics), len(pairs)) != (
        manifest.cv_profile_count,
        manifest.job_profile_count,
        manifest.rubric_count,
        manifest.pair_count,
    ):
        errors.append("Reviewed manifest counts do not match dataset files")

    for name in ("cv_profiles.jsonl", "job_profiles.jsonl", "rubrics.jsonl"):
        if file_sha256(dataset_directory / name) != file_sha256(source_directory / name):
            errors.append(f"Reviewed {name} must be byte-identical to the Bronze source")

    digest_by_path = {item.path: item for item in manifest.files}
    record_counts = {
        "cv_profiles.jsonl": len(profiles),
        "job_profiles.jsonl": len(jobs),
        "rubrics.jsonl": len(rubrics),
        "pairs.jsonl": len(pairs),
        "review_record.json": 1,
    }
    for relative_path, count in record_counts.items():
        digest = digest_by_path.get(relative_path)
        path = dataset_directory / relative_path
        if digest is None:
            errors.append(f"Missing reviewed manifest digest for {relative_path}")
        elif digest.record_count != count or digest.sha256 != file_sha256(path):
            errors.append(f"Reviewed manifest digest mismatch for {relative_path}")

    source_by_id = {item.pair_id: item for item in source_pairs}
    role_counts: Counter[DatasetRole] = Counter()
    label_counts: Counter[ClassificationDecision] = Counter()
    for pair in pairs:
        role_counts[pair.role] += 1
        source_pair = source_by_id.get(pair.pair_id)
        if source_pair is None:
            errors.append(f"Reviewed pair has no Bronze source: {pair.pair_id}")
            continue
        source_payload = source_pair.model_dump(mode="json")
        reviewed_payload = pair.model_dump(mode="json")
        source_payload.pop("dataset_tier")
        source_payload.pop("review")
        reviewed_payload.pop("dataset_tier")
        reviewed_payload.pop("review")
        if source_payload != reviewed_payload:
            errors.append(f"Reviewed pair changed approved content: {pair.pair_id}")
        if pair.dataset_tier is not DatasetTier.SILVER:
            errors.append(f"Reviewed pair is not Silver: {pair.pair_id}")
        if not isinstance(pair.review, ApprovedDatasetReview):
            errors.append(f"Reviewed pair lacks approved review: {pair.pair_id}")
            continue
        if pair.review.reviewer_references != manifest.reviewer_references:
            errors.append(f"Reviewer references mismatch in {pair.pair_id}")
        if pair.review.final_label is not pair.draft_label:
            errors.append(f"Final label differs from approved draft in {pair.pair_id}")
        label_counts[pair.review.final_label] += 1

    if set(source_by_id) != {item.pair_id for item in pairs}:
        errors.append("Reviewed pair identifiers do not exactly match the Bronze source")

    return RuntimeV2DevelopmentQualityReport(
        dataset_id=manifest.dataset_id,
        cv_profile_count=len(profiles),
        pair_count=len(pairs),
        role_pair_counts=dict(role_counts),
        label_counts=dict(label_counts),
        exact_prior_evidence_overlap_count=source_report.exact_prior_evidence_overlap_count,
        maximum_prior_cv_token_jaccard=source_report.maximum_prior_cv_token_jaccard,
        errors=tuple(dict.fromkeys(errors)),
        warnings=tuple(dict.fromkeys(warnings)),
    )
