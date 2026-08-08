from __future__ import annotations

from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from backend.app.contracts.common import (
    ContractModel,
    Evidence,
    Identifier,
    NonEmptyText,
    QualityWarning,
)

EvidenceId = Identifier


class Skill(ContractModel):
    name: NonEmptyText
    evidence_ids: Annotated[tuple[EvidenceId, ...], Field(min_length=1)]


class WorkExperience(ContractModel):
    experience_id: Identifier
    title: NonEmptyText
    organization_reference: NonEmptyText | None = None
    duration_months: int = Field(ge=0, le=600)
    summary: NonEmptyText
    technologies: tuple[NonEmptyText, ...] = ()
    evidence_ids: Annotated[tuple[EvidenceId, ...], Field(min_length=1)]


class EducationRecord(ContractModel):
    education_id: Identifier
    degree: NonEmptyText
    field_of_study: NonEmptyText | None = None
    institution_reference: NonEmptyText | None = None
    evidence_ids: Annotated[tuple[EvidenceId, ...], Field(min_length=1)]


class Project(ContractModel):
    project_id: Identifier
    title: NonEmptyText
    summary: NonEmptyText
    technologies: tuple[NonEmptyText, ...] = ()
    evidence_ids: Annotated[tuple[EvidenceId, ...], Field(min_length=1)]


class Certification(ContractModel):
    certification_id: Identifier
    name: NonEmptyText
    issuer_reference: NonEmptyText | None = None
    evidence_ids: Annotated[tuple[EvidenceId, ...], Field(min_length=1)]


class CVProfile(ContractModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    cv_profile_id: Identifier
    candidate_reference: Identifier
    summary: NonEmptyText | None = None
    skills: tuple[Skill, ...] = ()
    work_experiences: tuple[WorkExperience, ...] = ()
    education: tuple[EducationRecord, ...] = ()
    projects: tuple[Project, ...] = ()
    certifications: tuple[Certification, ...] = ()
    evidence: Annotated[tuple[Evidence, ...], Field(min_length=1)]
    quality_warnings: tuple[QualityWarning, ...] = ()

    @model_validator(mode="after")
    def validate_evidence_references(self) -> Self:
        evidence_ids = tuple(item.evidence_id for item in self.evidence)
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("evidence identifiers must be unique")
        referenced_ids = {evidence_id for item in self.skills for evidence_id in item.evidence_ids}
        referenced_ids.update(
            evidence_id for item in self.work_experiences for evidence_id in item.evidence_ids
        )
        referenced_ids.update(
            evidence_id for item in self.education for evidence_id in item.evidence_ids
        )
        referenced_ids.update(
            evidence_id for item in self.projects for evidence_id in item.evidence_ids
        )
        referenced_ids.update(
            evidence_id for item in self.certifications for evidence_id in item.evidence_ids
        )
        unknown_ids = referenced_ids.difference(evidence_ids)
        if unknown_ids:
            raise ValueError(f"unknown evidence identifiers: {sorted(unknown_ids)}")
        return self
