from __future__ import annotations

import hashlib
import re
from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
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
from backend.app.contracts.common import ContractModel, Identifier, NonEmptyText, Score


class DatasetRole(StrEnum):
    DATA_ANALYST = "data_analyst"
    PYTHON_BACKEND = "python_backend"
    FRONTEND = "frontend"
    QA_ENGINEER = "qa_engineer"
    DATA_ENGINEER = "data_engineer"


class JobVariant(StrEnum):
    MINIMUM = "minimum"
    STANDARD = "standard"
    PREFERRED_HEAVY = "preferred_heavy"
    AMBIGUOUS = "ambiguous"
    PROJECT_EQUIVALENT = "project_equivalent"


class SyntheticScenario(StrEnum):
    STRONG = "strong"
    SOLID = "solid"
    MODERATE = "moderate"
    MISSING_CRITICAL = "missing_critical"
    CONFLICTING_CRITICAL = "conflicting_critical"
    EXPLICIT_FAILURE = "explicit_failure"
    LOWER_BOUNDARY = "lower_boundary"
    UPPER_BOUNDARY = "upper_boundary"
    TRANSFERABLE = "transferable"
    HARD_NEGATIVE = "hard_negative"


class DatasetTier(StrEnum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"


class RequirementDraftAssessment(ContractModel):
    requirement_id: Identifier
    evidence_status: EvidenceStatus
    evidence_ids: tuple[Identifier, ...] = ()
    rationale: NonEmptyText


class CriterionDraftAssessment(ContractModel):
    criterion_id: Identifier
    awarded_points: Score
    maximum_points: Score
    evidence_ids: tuple[Identifier, ...] = ()
    rationale: NonEmptyText

    @model_validator(mode="after")
    def validate_points(self) -> Self:
        if self.awarded_points > self.maximum_points:
            raise ValueError("awarded points must not exceed maximum points")
        return self


class PendingDatasetReview(ContractModel):
    status: Literal["pending"] = "pending"
    human_review_count: Literal[0] = 0
    label_finalized: Literal[False] = False
    reviewer_references: tuple[Identifier, ...] = ()
    final_label: None = None


class CriterionScoreOverride(ContractModel):
    criterion_id: Identifier
    draft_points: Score
    final_points: Score
    rationale: NonEmptyText


class ApprovedDatasetReview(ContractModel):
    status: Literal["approved"] = "approved"
    human_review_count: int = Field(ge=1)
    label_finalized: Literal[True] = True
    reviewer_references: Annotated[tuple[Identifier, ...], Field(min_length=1)]
    final_label: ClassificationDecision
    criterion_score_overrides: tuple[CriterionScoreOverride, ...] = ()
    notes: NonEmptyText
    reviewed_at: datetime

    @model_validator(mode="after")
    def validate_review(self) -> Self:
        if self.reviewed_at.tzinfo is None or self.reviewed_at.utcoffset() is None:
            raise ValueError("reviewed_at must include a timezone")
        if len(set(self.reviewer_references)) != len(self.reviewer_references):
            raise ValueError("reviewer references must be unique")
        if self.human_review_count != len(self.reviewer_references):
            raise ValueError("human review count must match reviewer references")
        override_ids = tuple(item.criterion_id for item in self.criterion_score_overrides)
        if len(set(override_ids)) != len(override_ids):
            raise ValueError("criterion score override identifiers must be unique")
        return self


class SyntheticPairAnnotation(ContractModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    pair_id: Identifier
    cv_profile_id: Identifier
    candidate_reference: Identifier
    job_profile_id: Identifier
    rubric_id: Identifier
    role: DatasetRole
    job_variant: JobVariant
    scenario: SyntheticScenario
    source_type: Literal["synthetic"] = "synthetic"
    source_license: None = None
    dataset_tier: DatasetTier = DatasetTier.BRONZE
    partition: Literal["unassigned"] = "unassigned"
    critical_requirement_assessments: Annotated[
        tuple[RequirementDraftAssessment, ...], Field(min_length=1)
    ]
    criterion_assessments: Annotated[tuple[CriterionDraftAssessment, ...], Field(min_length=1)]
    total_score: Score
    draft_label: ClassificationDecision
    review_reasons: tuple[Identifier, ...] = ()
    overall_rationale: NonEmptyText
    review: PendingDatasetReview | ApprovedDatasetReview

    @model_validator(mode="after")
    def validate_annotation(self) -> Self:
        total = sum(
            (assessment.awarded_points for assessment in self.criterion_assessments),
            Decimal("0"),
        )
        if total != self.total_score:
            raise ValueError("total score must equal the criterion score sum")
        if self.draft_label is ClassificationDecision.NEEDS_REVIEW and not self.review_reasons:
            raise ValueError("needs_review draft labels require review reasons")
        if self.draft_label is not ClassificationDecision.NEEDS_REVIEW and self.review_reasons:
            raise ValueError("non-review draft labels must not include review reasons")
        if self.dataset_tier is DatasetTier.BRONZE and not isinstance(
            self.review, PendingDatasetReview
        ):
            raise ValueError("bronze annotations must retain pending review")
        if self.dataset_tier is DatasetTier.SILVER and not isinstance(
            self.review, ApprovedDatasetReview
        ):
            raise ValueError("silver annotations require an approved review")
        if self.dataset_tier is DatasetTier.GOLD:
            if not isinstance(self.review, ApprovedDatasetReview):
                raise ValueError("gold annotations require an approved review")
            if self.review.human_review_count < 2:
                raise ValueError("gold annotations require at least two human reviews")
        if isinstance(self.review, ApprovedDatasetReview):
            criterion_ids = {assessment.criterion_id for assessment in self.criterion_assessments}
            override_ids = {
                override.criterion_id for override in self.review.criterion_score_overrides
            }
            if not override_ids.issubset(criterion_ids):
                raise ValueError("criterion score overrides must reference known criteria")
        return self


class FileDigest(ContractModel):
    path: NonEmptyText
    sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    record_count: int = Field(ge=1)


class SyntheticExpansionManifest(ContractModel):
    schema_version: Literal["1.0.0", "1.1.0", "1.2.0"] = "1.0.0"
    dataset_id: Identifier
    dataset_version: NonEmptyText
    status: Literal["draft_for_human_review", "human_reviewed_silver"]
    generated_at: NonEmptyText
    cv_schema_version: Literal["1.0.0"]
    job_profile_schema_version: Literal["1.0.0"]
    rubric_schema_version: Literal["1.0.0"]
    configuration_version: Literal["1.1.0"]
    roles: Annotated[tuple[DatasetRole, ...], Field(min_length=1)]
    job_variants: Annotated[tuple[JobVariant, ...], Field(min_length=1)]
    scenarios: Annotated[tuple[SyntheticScenario, ...], Field(min_length=1)]
    cv_profile_count: int = Field(ge=1)
    job_profile_count: int = Field(ge=1)
    rubric_count: int = Field(ge=1)
    pair_count: int = Field(ge=1)
    tier_counts: dict[DatasetTier, int]
    human_reviewed_pair_count: int = Field(ge=0)
    split_status: Literal["unassigned"]
    frozen_test_created: Literal[False]
    market_reference_version: NonEmptyText | None = None
    reviewer_references: tuple[Identifier, ...] = ()
    reviewed_at: datetime | None = None
    source_dataset_id: Identifier | None = None
    source_dataset_version: NonEmptyText | None = None
    source_manifest_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")] | None = None
    provenance: Annotated[tuple[NonEmptyText, ...], Field(min_length=1)]
    files: Annotated[tuple[FileDigest, ...], Field(min_length=1)]

    @model_validator(mode="after")
    def validate_market_reference(self) -> Self:
        if self.schema_version in {"1.1.0", "1.2.0"} and self.market_reference_version is None:
            raise ValueError("schema 1.1.0 and later manifests require a market reference version")
        if self.status == "draft_for_human_review":
            if self.human_reviewed_pair_count != 0:
                raise ValueError("draft manifests cannot contain reviewed pairs")
            if self.reviewer_references or self.reviewed_at is not None:
                raise ValueError("draft manifests cannot contain reviewer metadata")
            if any(
                value is not None
                for value in (
                    self.source_dataset_id,
                    self.source_dataset_version,
                    self.source_manifest_sha256,
                )
            ):
                raise ValueError("draft manifests cannot reference a reviewed source")
            if self.tier_counts != {DatasetTier.BRONZE: self.pair_count}:
                raise ValueError("draft manifests must contain only bronze pairs")
        if self.status == "human_reviewed_silver":
            if self.schema_version != "1.2.0":
                raise ValueError("reviewed silver manifests require schema 1.2.0")
            if self.human_reviewed_pair_count != self.pair_count:
                raise ValueError("reviewed silver manifests must cover every pair")
            if self.tier_counts != {DatasetTier.SILVER: self.pair_count}:
                raise ValueError("reviewed silver manifests must contain only silver pairs")
            if not self.reviewer_references or self.reviewed_at is None:
                raise ValueError("reviewed silver manifests require reviewer metadata")
            if any(
                value is None
                for value in (
                    self.source_dataset_id,
                    self.source_dataset_version,
                    self.source_manifest_sha256,
                )
            ):
                raise ValueError("reviewed silver manifests require source traceability")
            if self.reviewed_at.tzinfo is None or self.reviewed_at.utcoffset() is None:
                raise ValueError("manifest reviewed_at must include a timezone")
        return self


class DatasetQualityReport(ContractModel):
    dataset_id: Identifier
    cv_profile_count: int = Field(ge=0)
    job_profile_count: int = Field(ge=0)
    rubric_count: int = Field(ge=0)
    pair_count: int = Field(ge=0)
    role_pair_counts: dict[DatasetRole, int]
    label_counts: dict[ClassificationDecision, int]
    tier_counts: dict[DatasetTier, int]
    errors: tuple[NonEmptyText, ...]
    warnings: tuple[NonEmptyText, ...]

    @property
    def passed(self) -> bool:
        return not self.errors


class SyntheticExpansionPartition(ContractModel):
    partition_id: Identifier
    intended_use: Literal["development_validation", "held_out_diagnostic"]
    tuning_allowed: bool
    final_performance_allowed: Literal[False] = False
    classifier_results_generated: Literal[False] = False
    candidate_count: int = Field(ge=1)
    pair_count: int = Field(ge=1)
    role_candidate_counts: dict[DatasetRole, int]
    label_pair_counts: dict[ClassificationDecision, int]
    candidate_references: Annotated[tuple[Identifier, ...], Field(min_length=1)]
    pair_ids: Annotated[tuple[Identifier, ...], Field(min_length=1)]

    @model_validator(mode="after")
    def validate_counts(self) -> Self:
        if self.candidate_count != len(self.candidate_references):
            raise ValueError("partition candidate count does not match references")
        if self.pair_count != len(self.pair_ids):
            raise ValueError("partition pair count does not match identifiers")
        if self.candidate_count != sum(self.role_candidate_counts.values()):
            raise ValueError("partition role counts do not match candidate count")
        if self.pair_count != sum(self.label_pair_counts.values()):
            raise ValueError("partition label counts do not match pair count")
        if len(set(self.candidate_references)) != len(self.candidate_references):
            raise ValueError("partition candidate references must be unique")
        if len(set(self.pair_ids)) != len(self.pair_ids):
            raise ValueError("partition pair identifiers must be unique")
        return self


class SyntheticExpansionSilverSplitManifest(ContractModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    split_manifest_id: Identifier
    split_policy_version: Literal["1.0.0"]
    selection_method: Literal["role-grouped-candidate-sha256-ranking"]
    split_seed_identifier: Identifier
    created_at: datetime
    source_dataset_id: Identifier
    source_dataset_version: NonEmptyText
    source_dataset_tier: Literal[DatasetTier.SILVER]
    source_directory: NonEmptyText
    source_manifest_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    frozen_test_created: Literal[False]
    gold_review_required_for_final_evaluation: Literal[True]
    development: SyntheticExpansionPartition
    held_out: SyntheticExpansionPartition

    @model_validator(mode="after")
    def validate_split(self) -> Self:
        if self.created_at.tzinfo is None or self.created_at.utcoffset() is None:
            raise ValueError("split created_at must include a timezone")
        if self.development.tuning_allowed is not True:
            raise ValueError("development partition must allow tuning")
        if self.held_out.tuning_allowed is not False:
            raise ValueError("held-out partition must disallow tuning")
        development_candidates = set(self.development.candidate_references)
        held_out_candidates = set(self.held_out.candidate_references)
        development_pairs = set(self.development.pair_ids)
        held_out_pairs = set(self.held_out.pair_ids)
        if development_candidates.intersection(held_out_candidates):
            raise ValueError("candidate references must not cross partitions")
        if development_pairs.intersection(held_out_pairs):
            raise ValueError("pair identifiers must not cross partitions")
        if self.development.candidate_count != 30 or self.held_out.candidate_count != 20:
            raise ValueError("silver split must contain 30 and 20 candidates")
        if self.development.pair_count != 150 or self.held_out.pair_count != 100:
            raise ValueError("silver split must contain 150 and 100 pairs")
        if self.development.role_candidate_counts != {role: 6 for role in DatasetRole}:
            raise ValueError("development must contain six candidates per role")
        if self.held_out.role_candidate_counts != {role: 4 for role in DatasetRole}:
            raise ValueError("held-out must contain four candidates per role")
        if set(self.development.label_pair_counts) != set(ClassificationDecision):
            raise ValueError("development must represent every classification label")
        if set(self.held_out.label_pair_counts) != set(ClassificationDecision):
            raise ValueError("held-out must represent every classification label")
        return self


PII_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    re.compile(r"(?<!\d)(?:\+84|0)(?:3|5|7|8|9)\d{8}(?!\d)"),
    re.compile(r"\b\d{9}|\d{12}\b"),
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
EXPECTED_CRITERION_MAXIMUMS = (
    Decimal("30"),
    Decimal("25"),
    Decimal("20"),
    Decimal("15"),
    Decimal("10"),
)


def load_json_lines(path: Path, model_type: type[ContractModel]) -> tuple[ContractModel, ...]:
    return tuple(
        model_type.model_validate_json(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expected_decision(annotation: SyntheticPairAnnotation) -> ClassificationDecision:
    statuses = {
        assessment.evidence_status for assessment in annotation.critical_requirement_assessments
    }
    if annotation.review_reasons:
        return ClassificationDecision.NEEDS_REVIEW
    if EvidenceStatus.UNSATISFIED in statuses:
        if annotation.total_score < Decimal("60"):
            return ClassificationDecision.REJECT
        return ClassificationDecision.NEEDS_REVIEW
    if annotation.total_score >= Decimal("75"):
        return ClassificationDecision.PASS
    if annotation.total_score >= Decimal("60"):
        return ClassificationDecision.WAITLIST
    return ClassificationDecision.NEEDS_REVIEW


def _field_names(value: object) -> set[str]:
    if isinstance(value, dict):
        mapping = cast(dict[object, object], value)
        names = {str(key) for key in mapping}
        for nested in mapping.values():
            names.update(_field_names(nested))
        return names
    if isinstance(value, list):
        sequence = cast(list[object], value)
        names: set[str] = set()
        for nested in sequence:
            names.update(_field_names(nested))
        return names
    return set()


def _append_unique_error(errors: list[str], message: str) -> None:
    if message not in errors:
        errors.append(message)


def validate_synthetic_expansion(dataset_directory: Path) -> DatasetQualityReport:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        profiles = tuple(
            CVProfile.model_validate_json(line)
            for line in (dataset_directory / "cv_profiles.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        )
        jobs = tuple(
            JobProfile.model_validate_json(line)
            for line in (dataset_directory / "job_profiles.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        )
        rubrics = tuple(
            ScoringRubric.model_validate_json(line)
            for line in (dataset_directory / "rubrics.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        )
        annotations = tuple(
            SyntheticPairAnnotation.model_validate_json(line)
            for line in (dataset_directory / "pairs.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
        manifest = SyntheticExpansionManifest.model_validate_json(
            (dataset_directory / "manifest.json").read_text(encoding="utf-8")
        )
    except (OSError, UnicodeError, ValueError) as error:
        return DatasetQualityReport(
            dataset_id="synthetic-expansion-invalid",
            cv_profile_count=0,
            job_profile_count=0,
            rubric_count=0,
            pair_count=0,
            role_pair_counts={},
            label_counts={},
            tier_counts={},
            errors=(f"Dataset loading failed: {error}",),
            warnings=(),
        )

    profile_by_id = {profile.cv_profile_id: profile for profile in profiles}
    job_by_id = {job.job_profile_id: job for job in jobs}
    rubric_by_id = {rubric.rubric_id: rubric for rubric in rubrics}
    if len(profile_by_id) != len(profiles):
        errors.append("CV profile identifiers must be unique")
    if len(job_by_id) != len(jobs):
        errors.append("Job profile identifiers must be unique")
    if len(rubric_by_id) != len(rubrics):
        errors.append("Rubric identifiers must be unique")
    if len({annotation.pair_id for annotation in annotations}) != len(annotations):
        errors.append("Pair identifiers must be unique")
    if len({profile.candidate_reference for profile in profiles}) != len(profiles):
        errors.append("Candidate references must be unique")

    combinations: set[tuple[str, str]] = set()
    candidate_partitions: dict[str, set[str]] = defaultdict(set)
    role_pairs: Counter[DatasetRole] = Counter()
    label_counts: Counter[ClassificationDecision] = Counter()
    tier_counts: Counter[DatasetTier] = Counter()
    approved_review_count = 0
    reviewer_references: set[str] = set()
    for annotation in annotations:
        profile = profile_by_id.get(annotation.cv_profile_id)
        job = job_by_id.get(annotation.job_profile_id)
        rubric = rubric_by_id.get(annotation.rubric_id)
        if profile is None:
            errors.append(f"Unknown CV profile in {annotation.pair_id}")
            continue
        if job is None:
            errors.append(f"Unknown job profile in {annotation.pair_id}")
            continue
        if rubric is None:
            errors.append(f"Unknown rubric in {annotation.pair_id}")
            continue
        if profile.candidate_reference != annotation.candidate_reference:
            errors.append(f"Candidate reference mismatch in {annotation.pair_id}")
        if rubric.job_profile_id != job.job_profile_id:
            errors.append(f"Rubric and job link mismatch in {annotation.pair_id}")
        required_ids = {
            requirement.requirement_id
            for requirement in job.requirements
            if requirement.is_critical
        }
        assessment_ids = {
            assessment.requirement_id for assessment in annotation.critical_requirement_assessments
        }
        if required_ids != set(rubric.critical_requirement_ids) or required_ids != assessment_ids:
            errors.append(f"Critical requirement coverage mismatch in {annotation.pair_id}")
        criterion_ids = tuple(criterion.criterion_id for criterion in rubric.criteria)
        assessment_criterion_ids = tuple(
            assessment.criterion_id for assessment in annotation.criterion_assessments
        )
        maximums = tuple(
            assessment.maximum_points for assessment in annotation.criterion_assessments
        )
        if criterion_ids != assessment_criterion_ids:
            errors.append(f"Criterion order mismatch in {annotation.pair_id}")
        if maximums != EXPECTED_CRITERION_MAXIMUMS:
            errors.append(f"Criterion maximums mismatch in {annotation.pair_id}")
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
            errors.append(f"Unknown evidence reference in {annotation.pair_id}")
        if annotation.draft_label is not expected_decision(annotation):
            errors.append(f"Draft decision policy mismatch in {annotation.pair_id}")
        combination = (annotation.cv_profile_id, annotation.job_profile_id)
        if combination in combinations:
            errors.append(f"Duplicate CV-JD combination in {annotation.pair_id}")
        combinations.add(combination)
        candidate_partitions[annotation.candidate_reference].add(annotation.partition)
        role_pairs.update((annotation.role,))
        effective_label = annotation.draft_label
        if isinstance(annotation.review, ApprovedDatasetReview):
            approved_review_count += 1
            reviewer_references.update(annotation.review.reviewer_references)
            effective_label = annotation.review.final_label
        label_counts.update((effective_label,))
        tier_counts.update((DatasetTier(annotation.dataset_tier),))

    for candidate_reference, partitions in candidate_partitions.items():
        if len(partitions) != 1:
            errors.append(f"Candidate {candidate_reference} appears in multiple partitions")

    for profile in profiles:
        payload = profile.model_dump(mode="json")
        if PROTECTED_FIELD_NAMES.intersection(_field_names(payload)):
            errors.append(f"Protected field detected in {profile.cv_profile_id}")
        serialized = profile.model_dump_json()
        if any(pattern.search(serialized) for pattern in PII_PATTERNS):
            errors.append(f"Potential PII detected in {profile.cv_profile_id}")

    expected_files = {
        "cv_profiles.jsonl": len(profiles),
        "job_profiles.jsonl": len(jobs),
        "rubrics.jsonl": len(rubrics),
        "pairs.jsonl": len(annotations),
    }
    digest_by_path = {digest.path: digest for digest in manifest.files}
    for relative_path, record_count in expected_files.items():
        digest = digest_by_path.get(relative_path)
        if digest is None:
            errors.append(f"Missing manifest digest for {relative_path}")
            continue
        if digest.record_count != record_count:
            errors.append(f"Manifest count mismatch for {relative_path}")
        if digest.sha256 != file_sha256(dataset_directory / relative_path):
            errors.append(f"Manifest hash mismatch for {relative_path}")

    manifest_counts = (
        manifest.cv_profile_count,
        manifest.job_profile_count,
        manifest.rubric_count,
        manifest.pair_count,
    )
    actual_counts = (len(profiles), len(jobs), len(rubrics), len(annotations))
    if manifest_counts != actual_counts:
        errors.append("Manifest aggregate counts do not match dataset files")
    if dict(tier_counts) != manifest.tier_counts:
        errors.append("Manifest tier counts do not match pair annotations")
    if approved_review_count != manifest.human_reviewed_pair_count:
        errors.append("Manifest reviewed-pair count does not match pair annotations")
    if reviewer_references != set(manifest.reviewer_references):
        errors.append("Manifest reviewer references do not match pair annotations")
    if set(label_counts) != set(ClassificationDecision):
        warnings.append("Not every classifier decision is represented")
    if any(count != 50 for count in role_pairs.values()) or len(role_pairs) != 5:
        errors.append("Each of the five roles must contain exactly 50 CV-JD pairs")

    for role in DatasetRole:
        role_profiles = {
            annotation.cv_profile_id for annotation in annotations if annotation.role is role
        }
        role_jobs = {
            annotation.job_profile_id for annotation in annotations if annotation.role is role
        }
        role_combinations = {
            (annotation.cv_profile_id, annotation.job_profile_id)
            for annotation in annotations
            if annotation.role is role
        }
        if len(role_profiles) != 10 or len(role_jobs) != 5 or len(role_combinations) != 50:
            _append_unique_error(errors, f"Incomplete cross-product for role {role.value}")

    return DatasetQualityReport(
        dataset_id=manifest.dataset_id,
        cv_profile_count=len(profiles),
        job_profile_count=len(jobs),
        rubric_count=len(rubrics),
        pair_count=len(annotations),
        role_pair_counts=dict(role_pairs),
        label_counts=dict(label_counts),
        tier_counts=dict(tier_counts),
        errors=tuple(errors),
        warnings=tuple(warnings),
    )
