from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Annotated, Literal, Self, cast

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

LIVE_CONFIG_PATH = Path("evaluation/configs/stage6_live_llm_v1.yaml")


class Stage6LiveConfigModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class Stage6LiveDataPolicy(Stage6LiveConfigModel):
    validation_only: Literal[True]
    frozen_test_allowed: Literal[False]
    raw_provider_response_persisted: Literal[False]


class Stage6LiveProviderRequestPolicy(Stage6LiveConfigModel):
    maximum_invalid_retries_per_attempt: int = Field(ge=0, le=5)


class Stage6LiveStabilityPolicy(Stage6LiveConfigModel):
    case_ids: Annotated[tuple[str, ...], Field(min_length=1)]
    total_attempts_per_case: int = Field(ge=2, le=10)

    @model_validator(mode="after")
    def validate_unique_case_ids(self) -> Self:
        if len(self.case_ids) != len(set(self.case_ids)):
            raise ValueError("Stage 6 live stability case identifiers must be unique")
        return self


class Stage6LiveQualityPolicy(Stage6LiveConfigModel):
    required_primary_valid_output_rate: Annotated[
        Decimal,
        Field(ge=Decimal("0"), le=Decimal("1")),
    ]
    maximum_stability_score_range: Annotated[
        Decimal,
        Field(ge=Decimal("0"), le=Decimal("100")),
    ]
    required_requirement_status_agreement_rate: Annotated[
        Decimal,
        Field(ge=Decimal("0"), le=Decimal("1")),
    ]


class Stage6LiveConfiguration(Stage6LiveConfigModel):
    schema_version: Literal["1.0.0"]
    experiment_id: Literal["stage6-live-llm-validation-v1"]
    experiment_version: Literal["1.3.0"]
    candidate_set_id: Literal["stage6-validation-candidates-v1"]
    candidate_set_version: Literal["1.2.0"]
    validation_partition_id: Literal["stage6-validation-v1"]
    provider_identifier: Annotated[str, Field(min_length=1, max_length=128)]
    model_identifier: Annotated[str, Field(min_length=1, max_length=256)]
    prompt_version: Literal["l3-evidence-rubric-v3"]
    billing_tier_assumption: Literal["free_tier_user_reported"]
    data_policy: Stage6LiveDataPolicy
    provider_request_policy: Stage6LiveProviderRequestPolicy
    stability: Stage6LiveStabilityPolicy
    quality_policy: Stage6LiveQualityPolicy


def load_stage6_live_configuration(repository_root: Path) -> Stage6LiveConfiguration:
    path = repository_root / LIVE_CONFIG_PATH
    value = cast(object, yaml.safe_load(path.read_text(encoding="utf-8")))
    if not isinstance(value, dict):
        raise ValueError("Stage 6 live LLM configuration must be a mapping")
    return Stage6LiveConfiguration.model_validate(cast(dict[str, object], value))
