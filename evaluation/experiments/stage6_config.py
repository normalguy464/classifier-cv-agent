from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Annotated, Literal, Self, cast

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.app.contracts import AggregationWeights, DecisionThresholds

CANDIDATE_CONFIG_PATH = Path("evaluation/configs/stage6_candidates_v1.yaml")


class Stage6ConfigModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class Stage6SelectionPolicy(Stage6ConfigModel):
    required_needs_review_recall: Annotated[
        Decimal,
        Field(ge=Decimal("0"), le=Decimal("1")),
    ]
    required_false_reject_count: int = Field(ge=0)
    required_unsafe_pass_count: int = Field(ge=0)
    maximum_review_rate: Annotated[
        Decimal,
        Field(ge=Decimal("0"), le=Decimal("1")),
    ]
    primary_metric: Literal["macro_f1"]
    secondary_metric: Literal["lower_review_rate"]


class Stage6ModelStrategy(Stage6ConfigModel):
    embedding_model_identifier: Annotated[str, Field(min_length=1, max_length=512)]
    embedding_configured_version: Annotated[str, Field(min_length=1, max_length=256)]
    embedding_resolved_revision: Annotated[
        str,
        Field(pattern=r"^[0-9a-f]{40}$"),
    ]
    l3_provider_identifier: Literal["deterministic_fake"]
    l3_model_identifier: Literal["deterministic-evidence-scorer-v1"]
    prompt_version: Literal["l3-evidence-rubric-v1"]


class Stage6L2Matching(Stage6ConfigModel):
    similarity_floor: Annotated[
        Decimal,
        Field(ge=Decimal("-1"), le=Decimal("1")),
    ]
    similarity_ceiling: Annotated[
        Decimal,
        Field(ge=Decimal("-1"), le=Decimal("1")),
    ]
    top_k: int = Field(ge=1, le=20)

    @model_validator(mode="after")
    def validate_similarity_range(self) -> Self:
        if self.similarity_floor >= self.similarity_ceiling:
            raise ValueError("L2 similarity floor must be below its ceiling")
        return self


class Stage6Candidate(Stage6ConfigModel):
    candidate_id: Annotated[str, Field(min_length=1, max_length=128)]
    description: Annotated[str, Field(min_length=1, max_length=1000)]
    l2_matching: Stage6L2Matching
    aggregation: AggregationWeights
    thresholds: DecisionThresholds
    disagreement_points: Annotated[
        Decimal,
        Field(ge=Decimal("0"), le=Decimal("100")),
    ]
    boundary_offset_points: Annotated[
        Decimal,
        Field(ge=Decimal("0"), le=Decimal("10")),
    ]

    @model_validator(mode="after")
    def validate_boundaries(self) -> Self:
        if self.thresholds.waitlist_minimum < self.boundary_offset_points:
            raise ValueError("waitlist threshold cannot produce a negative boundary")
        if self.thresholds.pass_minimum + self.boundary_offset_points > Decimal("100"):
            raise ValueError("pass threshold cannot produce a boundary above 100")
        return self


class Stage6CandidateSet(Stage6ConfigModel):
    schema_version: Literal["1.0.0"]
    candidate_set_id: Annotated[str, Field(min_length=1, max_length=128)]
    candidate_set_version: Annotated[str, Field(min_length=1, max_length=64)]
    source_configuration_version: Annotated[str, Field(min_length=1, max_length=64)]
    source_models_configuration_version: Annotated[
        str,
        Field(min_length=1, max_length=64),
    ]
    validation_partition_id: Literal["stage6-validation-v1"]
    candidate_protection_rules_fixed: Literal[True]
    model_strategy: Stage6ModelStrategy
    selection_policy: Stage6SelectionPolicy
    candidates: Annotated[tuple[Stage6Candidate, ...], Field(min_length=2)]

    @model_validator(mode="after")
    def validate_candidates(self) -> Self:
        identifiers = tuple(candidate.candidate_id for candidate in self.candidates)
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("Stage 6 candidate identifiers must be unique")
        return self


def load_stage6_candidate_set(repository_root: Path) -> Stage6CandidateSet:
    path = repository_root / CANDIDATE_CONFIG_PATH
    value = cast(object, yaml.safe_load(path.read_text(encoding="utf-8")))
    if not isinstance(value, dict):
        raise ValueError("Stage 6 candidate configuration must be a mapping")
    return Stage6CandidateSet.model_validate(cast(dict[str, object], value))
