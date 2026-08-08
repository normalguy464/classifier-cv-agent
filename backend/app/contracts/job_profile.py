from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from backend.app.contracts.common import ContractModel, Identifier, NonEmptyText


class RequirementPriority(StrEnum):
    REQUIRED = "required"
    PREFERRED = "preferred"


class SeniorityLevel(StrEnum):
    INTERN = "intern"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"


class ExperienceRange(ContractModel):
    minimum_years: int = Field(ge=0, le=40)
    maximum_years: int = Field(ge=0, le=40)
    formal_work_experience_required: bool = False

    @model_validator(mode="after")
    def validate_range(self) -> Self:
        if self.maximum_years < self.minimum_years:
            raise ValueError("maximum_years must be greater than or equal to minimum_years")
        return self


class JobRequirement(ContractModel):
    requirement_id: Identifier
    title: NonEmptyText
    description: NonEmptyText
    priority: RequirementPriority
    is_critical: bool = False
    accepted_evidence: Annotated[tuple[NonEmptyText, ...], Field(min_length=1)]
    missing_evidence_policy: NonEmptyText
    explicit_failure_policy: NonEmptyText

    @model_validator(mode="after")
    def validate_critical_requirement(self) -> Self:
        if self.is_critical and self.priority is not RequirementPriority.REQUIRED:
            raise ValueError("critical requirements must have required priority")
        return self


class JobProfile(ContractModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    job_profile_id: Identifier
    title: NonEmptyText
    language: str = "vi"
    seniority: SeniorityLevel
    experience_range: ExperienceRange
    responsibilities: Annotated[tuple[NonEmptyText, ...], Field(min_length=1)]
    requirements: Annotated[tuple[JobRequirement, ...], Field(min_length=1)]

    @model_validator(mode="after")
    def validate_requirements(self) -> Self:
        requirement_ids = tuple(item.requirement_id for item in self.requirements)
        if len(requirement_ids) != len(set(requirement_ids)):
            raise ValueError("requirement identifiers must be unique")
        if not any(item.priority is RequirementPriority.REQUIRED for item in self.requirements):
            raise ValueError("a job profile must have at least one required requirement")
        return self
