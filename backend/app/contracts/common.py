from __future__ import annotations

from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

Identifier = Annotated[
    str,
    Field(min_length=3, max_length=64, pattern=r"^[a-z0-9][a-z0-9-]{2,63}$"),
]
NonEmptyText = Annotated[str, Field(min_length=1, max_length=4000)]
Score = Annotated[
    Decimal, Field(ge=Decimal("0"), le=Decimal("100"), max_digits=5, decimal_places=2)
]
Confidence = Annotated[
    Decimal, Field(ge=Decimal("0"), le=Decimal("1"), max_digits=3, decimal_places=2)
]


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class EvidenceSourceType(StrEnum):
    PARSER = "parser"
    MANUAL = "manual"
    REVIEWER = "reviewer"
    CANDIDATE = "candidate"


class EvidenceSection(StrEnum):
    SKILLS = "skills"
    WORK_EXPERIENCE = "work_experience"
    PROJECTS = "projects"
    EDUCATION = "education"
    CERTIFICATIONS = "certifications"
    OTHER = "other"


class EvidenceStatus(StrEnum):
    SATISFIED = "satisfied"
    UNSATISFIED = "unsatisfied"
    MISSING = "missing"
    CONFLICTING = "conflicting"


class WarningSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class EvidenceLocation(ContractModel):
    source_record_id: Identifier
    page_number: int | None = Field(default=None, ge=1)
    character_start: int | None = Field(default=None, ge=0)
    character_end: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_character_range(self) -> Self:
        if (
            self.character_start is not None
            and self.character_end is not None
            and self.character_end < self.character_start
        ):
            raise ValueError("character_end must be greater than or equal to character_start")
        return self


class Evidence(ContractModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    evidence_id: Identifier
    source_type: EvidenceSourceType
    section: EvidenceSection
    text: NonEmptyText
    location: EvidenceLocation
    extraction_confidence: Confidence | None = None
    is_verified: bool = False


class QualityWarning(ContractModel):
    code: Identifier
    severity: WarningSeverity
    message: NonEmptyText
