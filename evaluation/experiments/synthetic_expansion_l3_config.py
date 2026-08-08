from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Annotated, Literal, Self, cast

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.app.contracts import AggregationWeights, DecisionThresholds

CONFIG_PATH = Path("evaluation/configs/synthetic_expansion_l3_openrouter_v1.yaml")
NEMOTRON_CONFIG_PATH = Path("evaluation/configs/synthetic_expansion_l3_openrouter_v2.yaml")
GPT_OSS_CONFIG_PATH = Path("evaluation/configs/synthetic_expansion_l3_openrouter_v3.yaml")
GPT_OSS_HEALED_CONFIG_PATH = Path("evaluation/configs/synthetic_expansion_l3_openrouter_v4.yaml")
GPT_OSS_120B_CONFIG_PATH = Path("evaluation/configs/synthetic_expansion_l3_openrouter_v5.yaml")
NEMOTRON_NANO_CONFIG_PATH = Path("evaluation/configs/synthetic_expansion_l3_openrouter_v6.yaml")
NEMOTRON_NANO_HEALED_CONFIG_PATH = Path(
    "evaluation/configs/synthetic_expansion_l3_openrouter_v7.yaml"
)
GPT_OSS_120B_HEALED_CONFIG_PATH = Path(
    "evaluation/configs/synthetic_expansion_l3_openrouter_v8.yaml"
)
NEMOTRON_ULTRA_CONFIG_PATH = Path("evaluation/configs/synthetic_expansion_l3_openrouter_v9.yaml")
NEMOTRON_ULTRA_NATIVE_CONFIG_PATH = Path(
    "evaluation/configs/synthetic_expansion_l3_openrouter_v10.yaml"
)
GEMMA_3_CONFIG_PATH = Path("evaluation/configs/synthetic_expansion_l3_openrouter_v11.yaml")
GEMMA_3_NATIVE_CONFIG_PATH = Path("evaluation/configs/synthetic_expansion_l3_openrouter_v12.yaml")
QWEN3_NEXT_CONFIG_PATH = Path("evaluation/configs/synthetic_expansion_l3_openrouter_v13.yaml")
QWEN3_NEXT_NATIVE_CONFIG_PATH = Path(
    "evaluation/configs/synthetic_expansion_l3_openrouter_v14.yaml"
)
QWEN3_NEXT_SNAPSHOT_CONFIG_PATH = Path(
    "evaluation/configs/synthetic_expansion_l3_openrouter_v15.yaml"
)
GOOGLE_AI_STUDIO_CONFIG_PATH = Path(
    "evaluation/configs/synthetic_expansion_l3_google_ai_studio_v1.yaml"
)
GOOGLE_AI_STUDIO_CALIBRATED_CONFIG_PATH = Path(
    "evaluation/configs/synthetic_expansion_l3_google_ai_studio_v2.yaml"
)
GOOGLE_AI_STUDIO_SCOPED_CONFIG_PATH = Path(
    "evaluation/configs/synthetic_expansion_l3_google_ai_studio_v3.yaml"
)
GOOGLE_AI_STUDIO_QA_REMEDIATED_CONFIG_PATH = Path(
    "evaluation/configs/synthetic_expansion_l3_google_ai_studio_v4.yaml"
)
GOOGLE_AI_STUDIO_STRICT_SCOPED_CONFIG_PATH = Path(
    "evaluation/configs/synthetic_expansion_l3_google_ai_studio_v5.yaml"
)
GOOGLE_AI_STUDIO_HARD_SCOPED_CONFIG_PATH = Path(
    "evaluation/configs/synthetic_expansion_l3_google_ai_studio_v6.yaml"
)
GOOGLE_AI_STUDIO_EXACT_NEGATIVE_CONFIG_PATH = Path(
    "evaluation/configs/synthetic_expansion_l3_google_ai_studio_v7.yaml"
)
OPENAI_GPT_5_4_MINI_CONFIG_PATH = Path(
    "evaluation/configs/synthetic_expansion_l3_openai_gpt_5_4_mini_v1.yaml"
)
OPENAI_GPT_5_4_MINI_NORMALIZED_CONFIG_PATH = Path(
    "evaluation/configs/synthetic_expansion_l3_openai_gpt_5_4_mini_v2.yaml"
)
OPENAI_GPT_5_4_MINI_VALIDATED_CONFIG_PATH = Path(
    "evaluation/configs/synthetic_expansion_l3_openai_gpt_5_4_mini_v3.yaml"
)
OPENAI_GPT_5_4_MINI_DYNAMIC_SCHEMA_CONFIG_PATH = Path(
    "evaluation/configs/synthetic_expansion_l3_openai_gpt_5_4_mini_v4.yaml"
)
OPENAI_GPT_5_4_MINI_ROLE_CALIBRATED_CONFIG_PATH = Path(
    "evaluation/configs/synthetic_expansion_l3_openai_gpt_5_4_mini_v5.yaml"
)
OPENAI_GPT_5_4_MINI_REQUIREMENT_GUARDED_CONFIG_PATH = Path(
    "evaluation/configs/synthetic_expansion_l3_openai_gpt_5_4_mini_v6.yaml"
)
OPENAI_GPT_5_4_MINI_SAFETY_GATED_CONFIG_PATH = Path(
    "evaluation/configs/synthetic_expansion_l3_openai_gpt_5_4_mini_v7.yaml"
)
OPENAI_GPT_5_4_MINI_HYBRID_TUNED_CONFIG_PATH = Path(
    "evaluation/configs/synthetic_expansion_l3_openai_gpt_5_4_mini_v8.yaml"
)


class ExpansionL3ConfigModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class ExpansionL3DataPolicy(ExpansionL3ConfigModel):
    development_only: Literal[True]
    held_out_allowed: Literal[False]
    original_frozen_test_allowed: Literal[False]
    raw_provider_response_persisted: Literal[False]


class ExpansionL3RequestPolicy(ExpansionL3ConfigModel):
    hard_request_cap: int = Field(ge=30, le=40)
    prior_series_request_count: int = Field(default=0, ge=0, le=100)
    series_hard_request_cap: int | None = Field(default=None, ge=30, le=100)
    development_panel_pair_count: int = Field(default=0, ge=0, le=25)
    require_development_panel_pass_before_batch: bool = False
    minimum_request_interval_seconds: float = Field(ge=1, le=60)
    request_timeout_seconds: float = Field(default=60, ge=30, le=120)
    maximum_invalid_retries_per_attempt: Literal[1]
    maximum_unavailable_retries_per_attempt: Literal[1] = 1
    maximum_total_retries_per_attempt: Literal[1] = 1
    require_supported_parameters: bool = False
    response_healing_enabled: bool = False
    include_temperature_parameter: bool = True
    max_completion_tokens: int | None = Field(default=None, ge=1, le=128000)
    reasoning_effort: Literal["none", "low", "medium", "high", "xhigh"] | None = None

    @model_validator(mode="after")
    def validate_series_request_cap(self) -> Self:
        if (
            self.require_development_panel_pass_before_batch
            and not self.development_panel_pair_count
        ):
            raise ValueError("required L3 development panel must contain at least one pair")
        if (
            not self.require_development_panel_pass_before_batch
            and self.development_panel_pair_count
        ):
            raise ValueError("optional L3 development panel pair count must be zero")
        if self.series_hard_request_cap is None:
            if self.prior_series_request_count:
                raise ValueError("prior L3 series requests require a series request cap")
            return self
        if self.prior_series_request_count + self.hard_request_cap > self.series_hard_request_cap:
            raise ValueError("L3 experiment request budget exceeds the series request cap")
        return self


class ExpansionL3CostPolicy(ExpansionL3ConfigModel):
    input_usd_per_million_tokens: Decimal = Field(ge=Decimal("0"))
    cached_input_usd_per_million_tokens: Decimal = Field(ge=Decimal("0"))
    output_usd_per_million_tokens: Decimal = Field(ge=Decimal("0"))
    assumed_max_input_tokens_per_request: int = Field(ge=1, le=400000)
    maximum_estimated_experiment_cost_usd: Decimal = Field(gt=Decimal("0"), le=Decimal("10"))


class ExpansionL3StabilityPolicy(ExpansionL3ConfigModel):
    pair_ids: Annotated[tuple[str, ...], Field(min_length=5, max_length=5)]
    total_attempts_per_pair: Literal[2]

    @model_validator(mode="after")
    def validate_unique_pair_ids(self) -> Self:
        if len(self.pair_ids) != len(set(self.pair_ids)):
            raise ValueError("L3 stability pair identifiers must be unique")
        return self


class ExpansionL3QualityPolicy(ExpansionL3ConfigModel):
    required_primary_valid_output_rate: Annotated[
        Decimal,
        Field(ge=Decimal("0"), le=Decimal("1")),
    ]
    required_requirement_status_match_rate: Annotated[
        Decimal,
        Field(ge=Decimal("0"), le=Decimal("1")),
    ]
    maximum_stability_score_range: Annotated[
        Decimal,
        Field(ge=Decimal("0"), le=Decimal("100")),
    ]
    required_stability_requirement_agreement_rate: Annotated[
        Decimal,
        Field(ge=Decimal("0"), le=Decimal("1")),
    ]
    required_stability_requirement_route_agreement_rate: Annotated[
        Decimal,
        Field(ge=Decimal("0"), le=Decimal("1")),
    ] = Decimal("1")
    maximum_endpoint_score_rate: Annotated[
        Decimal,
        Field(ge=Decimal("0"), le=Decimal("1")),
    ] = Decimal("1")
    maximum_criterion_mean_absolute_error: Annotated[
        Decimal,
        Field(ge=Decimal("0"), le=Decimal("100")),
    ] = Decimal("100")
    maximum_total_score_mean_absolute_error: Annotated[
        Decimal,
        Field(ge=Decimal("0"), le=Decimal("100")),
    ] = Decimal("100")
    maximum_unsafe_requirement_status_mismatch_count: int = Field(default=0, ge=0, le=120)

    @model_validator(mode="after")
    def validate_complete_primary_output_requirement(self) -> Self:
        if self.required_primary_valid_output_rate != Decimal("1"):
            raise ValueError("L3 primary valid output rate policy must be 1")
        return self


class ExpansionL3HybridPolicy(ExpansionL3ConfigModel):
    candidate_id: Literal["openai-role-calibrated-hybrid-v1"]
    l2_candidate_id: Literal["coverage-70-95-v1"]
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


class ExpansionL3Configuration(ExpansionL3ConfigModel):
    schema_version: Literal["1.0.0"]
    experiment_id: Literal[
        "synthetic-expansion-v2-openrouter-l3-validation-v1",
        "synthetic-expansion-v2-openrouter-l3-validation-v2",
        "synthetic-expansion-v2-openrouter-l3-validation-v3",
        "synthetic-expansion-v2-openrouter-l3-validation-v4",
        "synthetic-expansion-v2-openrouter-l3-validation-v5",
        "synthetic-expansion-v2-openrouter-l3-validation-v6",
        "synthetic-expansion-v2-openrouter-l3-validation-v7",
        "synthetic-expansion-v2-openrouter-l3-validation-v8",
        "synthetic-expansion-v2-openrouter-l3-validation-v9",
        "synthetic-expansion-v2-openrouter-l3-validation-v10",
        "synthetic-expansion-v2-openrouter-l3-validation-v11",
        "synthetic-expansion-v2-openrouter-l3-validation-v12",
        "synthetic-expansion-v2-openrouter-l3-validation-v13",
        "synthetic-expansion-v2-openrouter-l3-validation-v14",
        "synthetic-expansion-v2-openrouter-l3-validation-v15",
        "synthetic-expansion-v2-google-ai-studio-l3-validation-v1",
        "synthetic-expansion-v2-google-ai-studio-l3-validation-v2",
        "synthetic-expansion-v2-google-ai-studio-l3-validation-v3",
        "synthetic-expansion-v2-google-ai-studio-l3-validation-v4",
        "synthetic-expansion-v2-google-ai-studio-l3-validation-v5",
        "synthetic-expansion-v2-google-ai-studio-l3-validation-v6",
        "synthetic-expansion-v2-google-ai-studio-l3-validation-v7",
        "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v1",
        "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v2",
        "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v3",
        "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v4",
        "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v5",
        "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v6",
        "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v7",
        "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v8",
    ]
    experiment_version: Literal[
        "1.0.0",
        "2.0.0",
        "3.0.0",
        "4.0.0",
        "5.0.0",
        "6.0.0",
        "7.0.0",
        "8.0.0",
        "9.0.0",
        "10.0.0",
        "11.0.0",
        "12.0.0",
        "13.0.0",
        "14.0.0",
        "15.0.0",
        "16.0.0",
        "17.0.0",
        "18.0.0",
        "19.0.0",
        "20.0.0",
        "21.0.0",
        "22.0.0",
        "23.0.0",
        "24.0.0",
        "25.0.0",
        "26.0.0",
        "27.0.0",
        "28.0.0",
        "29.0.0",
        "30.0.0",
    ]
    dataset_id: Literal["synthetic-cv-jd-expansion-v2-reviewed-silver"]
    dataset_version: Literal["2.1.0", "2.2.0", "2.3.0", "2.3.1"]
    reviewed_dataset_directory: Path = Path("data/synthetic_expansion/reviewed/v2")
    split_manifest_path: Path = Path(
        "data/synthetic_expansion/splits/v2_silver_split_manifest.json"
    )
    development_partition_id: Literal[
        "synthetic-expansion-v2-development-silver",
        "synthetic-expansion-v2-2-development-silver",
        "synthetic-expansion-v2-3-development-silver",
        "synthetic-expansion-v2-3-1-development-silver",
    ]
    held_out_partition_id: Literal[
        "synthetic-expansion-v2-held-out-silver",
        "synthetic-expansion-v2-2-held-out-silver",
        "synthetic-expansion-v2-3-held-out-silver",
        "synthetic-expansion-v2-3-1-held-out-silver",
    ]
    provider_identifier: Literal["openrouter", "google_ai_studio", "openai"]
    model_identifier: Literal[
        "google/gemma-4-26b-a4b-it:free",
        "nvidia/nemotron-3-super-120b-a12b:free",
        "openai/gpt-oss-20b:free",
        "openai/gpt-oss-120b:free",
        "nvidia/nemotron-3-nano-30b-a3b:free",
        "nvidia/nemotron-3-ultra-550b-a55b:free",
        "google/gemma-3-27b-it:free",
        "qwen/qwen3-next-80b-a3b-instruct:free",
        "qwen/qwen3-next-80b-a3b-instruct-2509:free",
        "gemini-3.5-flash-lite",
        "gpt-5.4-mini-2026-03-17",
    ]
    prompt_version: Literal[
        "l3-evidence-rubric-v3",
        "l3-evidence-rubric-v5",
        "l3-evidence-rubric-v6",
        "l3-evidence-rubric-v7",
        "l3-evidence-rubric-v8",
        "l3-evidence-rubric-v9",
        "l3-evidence-rubric-v10",
        "l3-evidence-rubric-v11",
        "l3-evidence-rubric-v12",
    ]
    l2_configuration_path: Path = Path(
        "evaluation/configs/synthetic_expansion_l2_candidates_v1.yaml"
    )
    l2_candidate_set_id: Literal[
        "synthetic-expansion-v2-l2-development-candidates-v1",
        "synthetic-expansion-v2-2-l2-development-candidates-v2",
        "synthetic-expansion-v2-3-l2-development-candidates-v3",
        "synthetic-expansion-v2-3-1-l2-development-candidates-v4",
    ]
    l2_candidate_set_version: Literal["1.1.0", "1.2.0", "1.3.0", "1.3.1"]
    l2_candidate_id: Literal["coverage-70-95-v1"]
    l3_score_mapping_version: Literal[
        "provider-weighted-points-v1",
        "l3-deterministic-level-mapping-v1",
    ] = "provider-weighted-points-v1"
    billing_tier_assumption: Literal["free_variant", "free_tier_user_reported", "paid_tier_1"]
    data_policy: ExpansionL3DataPolicy
    request_policy: ExpansionL3RequestPolicy
    cost_policy: ExpansionL3CostPolicy | None = None
    primary_pair_ids: Annotated[tuple[str, ...], Field(min_length=25, max_length=25)]
    stability: ExpansionL3StabilityPolicy
    quality_policy: ExpansionL3QualityPolicy
    hybrid_policy: ExpansionL3HybridPolicy | None = None

    @model_validator(mode="after")
    def validate_sample_and_budget(self) -> Self:
        if len(self.primary_pair_ids) != len(set(self.primary_pair_ids)):
            raise ValueError("L3 primary pair identifiers must be unique")
        if not set(self.stability.pair_ids).issubset(self.primary_pair_ids):
            raise ValueError("L3 stability pairs must be primary sample pairs")
        required_attempts = len(self.primary_pair_ids) + len(self.stability.pair_ids)
        if self.request_policy.hard_request_cap < required_attempts:
            raise ValueError("L3 hard request cap must cover required valid attempts")
        expected = {
            "synthetic-expansion-v2-openrouter-l3-validation-v1": (
                "1.0.0",
                "google/gemma-4-26b-a4b-it:free",
                "openrouter",
                False,
                False,
                True,
            ),
            "synthetic-expansion-v2-openrouter-l3-validation-v2": (
                "2.0.0",
                "nvidia/nemotron-3-super-120b-a12b:free",
                "openrouter",
                True,
                False,
                True,
            ),
            "synthetic-expansion-v2-openrouter-l3-validation-v3": (
                "3.0.0",
                "openai/gpt-oss-20b:free",
                "openrouter",
                True,
                False,
                True,
            ),
            "synthetic-expansion-v2-openrouter-l3-validation-v4": (
                "4.0.0",
                "openai/gpt-oss-20b:free",
                "openrouter",
                True,
                True,
                True,
            ),
            "synthetic-expansion-v2-openrouter-l3-validation-v5": (
                "5.0.0",
                "openai/gpt-oss-120b:free",
                "openrouter",
                True,
                True,
                True,
            ),
            "synthetic-expansion-v2-openrouter-l3-validation-v6": (
                "6.0.0",
                "nvidia/nemotron-3-nano-30b-a3b:free",
                "openrouter",
                True,
                True,
                True,
            ),
            "synthetic-expansion-v2-openrouter-l3-validation-v7": (
                "7.0.0",
                "nvidia/nemotron-3-nano-30b-a3b:free",
                "openrouter",
                False,
                True,
                True,
            ),
            "synthetic-expansion-v2-openrouter-l3-validation-v8": (
                "8.0.0",
                "openai/gpt-oss-120b:free",
                "openrouter",
                False,
                True,
                True,
            ),
            "synthetic-expansion-v2-openrouter-l3-validation-v9": (
                "9.0.0",
                "nvidia/nemotron-3-ultra-550b-a55b:free",
                "openrouter",
                False,
                True,
                True,
            ),
            "synthetic-expansion-v2-openrouter-l3-validation-v10": (
                "10.0.0",
                "nvidia/nemotron-3-ultra-550b-a55b:free",
                "openrouter",
                False,
                False,
                True,
            ),
            "synthetic-expansion-v2-openrouter-l3-validation-v11": (
                "11.0.0",
                "google/gemma-3-27b-it:free",
                "openrouter",
                True,
                False,
                True,
            ),
            "synthetic-expansion-v2-openrouter-l3-validation-v12": (
                "12.0.0",
                "google/gemma-3-27b-it:free",
                "openrouter",
                False,
                False,
                True,
            ),
            "synthetic-expansion-v2-openrouter-l3-validation-v13": (
                "13.0.0",
                "qwen/qwen3-next-80b-a3b-instruct:free",
                "openrouter",
                True,
                False,
                True,
            ),
            "synthetic-expansion-v2-openrouter-l3-validation-v14": (
                "14.0.0",
                "qwen/qwen3-next-80b-a3b-instruct:free",
                "openrouter",
                False,
                False,
                True,
            ),
            "synthetic-expansion-v2-openrouter-l3-validation-v15": (
                "15.0.0",
                "qwen/qwen3-next-80b-a3b-instruct-2509:free",
                "openrouter",
                True,
                False,
                True,
            ),
            "synthetic-expansion-v2-google-ai-studio-l3-validation-v1": (
                "16.0.0",
                "gemini-3.5-flash-lite",
                "google_ai_studio",
                False,
                False,
                False,
            ),
            "synthetic-expansion-v2-google-ai-studio-l3-validation-v2": (
                "17.0.0",
                "gemini-3.5-flash-lite",
                "google_ai_studio",
                False,
                False,
                False,
            ),
            "synthetic-expansion-v2-google-ai-studio-l3-validation-v3": (
                "18.0.0",
                "gemini-3.5-flash-lite",
                "google_ai_studio",
                False,
                False,
                False,
            ),
            "synthetic-expansion-v2-google-ai-studio-l3-validation-v4": (
                "19.0.0",
                "gemini-3.5-flash-lite",
                "google_ai_studio",
                False,
                False,
                False,
            ),
            "synthetic-expansion-v2-google-ai-studio-l3-validation-v5": (
                "20.0.0",
                "gemini-3.5-flash-lite",
                "google_ai_studio",
                False,
                False,
                False,
            ),
            "synthetic-expansion-v2-google-ai-studio-l3-validation-v6": (
                "21.0.0",
                "gemini-3.5-flash-lite",
                "google_ai_studio",
                False,
                False,
                False,
            ),
            "synthetic-expansion-v2-google-ai-studio-l3-validation-v7": (
                "22.0.0",
                "gemini-3.5-flash-lite",
                "google_ai_studio",
                False,
                False,
                False,
            ),
            "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v1": (
                "23.0.0",
                "gpt-5.4-mini-2026-03-17",
                "openai",
                False,
                False,
                False,
            ),
            "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v2": (
                "24.0.0",
                "gpt-5.4-mini-2026-03-17",
                "openai",
                False,
                False,
                False,
            ),
            "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v3": (
                "25.0.0",
                "gpt-5.4-mini-2026-03-17",
                "openai",
                False,
                False,
                False,
            ),
            "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v4": (
                "26.0.0",
                "gpt-5.4-mini-2026-03-17",
                "openai",
                False,
                False,
                False,
            ),
            "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v5": (
                "27.0.0",
                "gpt-5.4-mini-2026-03-17",
                "openai",
                False,
                False,
                False,
            ),
            "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v6": (
                "28.0.0",
                "gpt-5.4-mini-2026-03-17",
                "openai",
                False,
                False,
                False,
            ),
            "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v7": (
                "29.0.0",
                "gpt-5.4-mini-2026-03-17",
                "openai",
                False,
                False,
                False,
            ),
            "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v8": (
                "30.0.0",
                "gpt-5.4-mini-2026-03-17",
                "openai",
                False,
                False,
                False,
            ),
        }[self.experiment_id]
        actual = (
            self.experiment_version,
            self.model_identifier,
            self.provider_identifier,
            self.request_policy.require_supported_parameters,
            self.request_policy.response_healing_enabled,
            self.request_policy.include_temperature_parameter,
        )
        if actual != expected:
            raise ValueError("L3 experiment version, model and provider policy do not match")
        if self.experiment_id in {
            "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v4",
            "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v5",
            "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v6",
            "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v7",
            "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v8",
        }:
            dynamic_schema_request_policy = (
                self.request_policy.hard_request_cap,
                self.request_policy.prior_series_request_count,
                self.request_policy.series_hard_request_cap,
                self.request_policy.development_panel_pair_count,
                self.request_policy.require_development_panel_pass_before_batch,
            )
            expected_dynamic_schema_request_policy = {
                "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v4": (
                    32,
                    13,
                    45,
                    5,
                    True,
                ),
                "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v5": (
                    32,
                    18,
                    50,
                    5,
                    True,
                ),
                "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v6": (
                    32,
                    23,
                    55,
                    5,
                    True,
                ),
                "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v7": (
                    32,
                    23,
                    55,
                    5,
                    True,
                ),
                "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v8": (
                    32,
                    23,
                    55,
                    5,
                    True,
                ),
            }[self.experiment_id]
            if dynamic_schema_request_policy != expected_dynamic_schema_request_policy:
                raise ValueError(
                    "OpenAI dynamic-schema panel and series request policy do not match"
                )
        expected_prompt_version = {
            "synthetic-expansion-v2-google-ai-studio-l3-validation-v2": ("l3-evidence-rubric-v5"),
            "synthetic-expansion-v2-google-ai-studio-l3-validation-v3": ("l3-evidence-rubric-v6"),
            "synthetic-expansion-v2-google-ai-studio-l3-validation-v4": ("l3-evidence-rubric-v6"),
            "synthetic-expansion-v2-google-ai-studio-l3-validation-v5": ("l3-evidence-rubric-v7"),
            "synthetic-expansion-v2-google-ai-studio-l3-validation-v6": ("l3-evidence-rubric-v8"),
            "synthetic-expansion-v2-google-ai-studio-l3-validation-v7": ("l3-evidence-rubric-v8"),
            "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v1": (
                "l3-evidence-rubric-v9"
            ),
            "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v2": (
                "l3-evidence-rubric-v9"
            ),
            "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v3": (
                "l3-evidence-rubric-v10"
            ),
            "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v4": (
                "l3-evidence-rubric-v10"
            ),
            "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v5": (
                "l3-evidence-rubric-v11"
            ),
            "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v6": (
                "l3-evidence-rubric-v12"
            ),
            "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v7": (
                "l3-evidence-rubric-v12"
            ),
            "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v8": (
                "l3-evidence-rubric-v12"
            ),
        }.get(self.experiment_id, "l3-evidence-rubric-v3")
        if self.prompt_version != expected_prompt_version:
            raise ValueError("L3 experiment and prompt version do not match")
        expected_lineage = {
            "synthetic-expansion-v2-google-ai-studio-l3-validation-v3": (
                "2.2.0",
                Path("data/synthetic_expansion/reviewed/v2_2"),
                Path("data/synthetic_expansion/splits/v2_2_silver_split_manifest.json"),
                "synthetic-expansion-v2-2-development-silver",
                "synthetic-expansion-v2-2-held-out-silver",
                Path("evaluation/configs/synthetic_expansion_l2_candidates_v2.yaml"),
                "synthetic-expansion-v2-2-l2-development-candidates-v2",
                "1.2.0",
            ),
            "synthetic-expansion-v2-google-ai-studio-l3-validation-v4": (
                "2.3.0",
                Path("data/synthetic_expansion/reviewed/v2_3"),
                Path("data/synthetic_expansion/splits/v2_3_silver_split_manifest.json"),
                "synthetic-expansion-v2-3-development-silver",
                "synthetic-expansion-v2-3-held-out-silver",
                Path("evaluation/configs/synthetic_expansion_l2_candidates_v3.yaml"),
                "synthetic-expansion-v2-3-l2-development-candidates-v3",
                "1.3.0",
            ),
            "synthetic-expansion-v2-google-ai-studio-l3-validation-v5": (
                "2.3.0",
                Path("data/synthetic_expansion/reviewed/v2_3"),
                Path("data/synthetic_expansion/splits/v2_3_silver_split_manifest.json"),
                "synthetic-expansion-v2-3-development-silver",
                "synthetic-expansion-v2-3-held-out-silver",
                Path("evaluation/configs/synthetic_expansion_l2_candidates_v3.yaml"),
                "synthetic-expansion-v2-3-l2-development-candidates-v3",
                "1.3.0",
            ),
            "synthetic-expansion-v2-google-ai-studio-l3-validation-v6": (
                "2.3.0",
                Path("data/synthetic_expansion/reviewed/v2_3"),
                Path("data/synthetic_expansion/splits/v2_3_silver_split_manifest.json"),
                "synthetic-expansion-v2-3-development-silver",
                "synthetic-expansion-v2-3-held-out-silver",
                Path("evaluation/configs/synthetic_expansion_l2_candidates_v3.yaml"),
                "synthetic-expansion-v2-3-l2-development-candidates-v3",
                "1.3.0",
            ),
            "synthetic-expansion-v2-google-ai-studio-l3-validation-v7": (
                "2.3.1",
                Path("data/synthetic_expansion/reviewed/v2_3_1"),
                Path("data/synthetic_expansion/splits/v2_3_1_silver_split_manifest.json"),
                "synthetic-expansion-v2-3-1-development-silver",
                "synthetic-expansion-v2-3-1-held-out-silver",
                Path("evaluation/configs/synthetic_expansion_l2_candidates_v4.yaml"),
                "synthetic-expansion-v2-3-1-l2-development-candidates-v4",
                "1.3.1",
            ),
            "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v1": (
                "2.3.1",
                Path("data/synthetic_expansion/reviewed/v2_3_1"),
                Path("data/synthetic_expansion/splits/v2_3_1_silver_split_manifest.json"),
                "synthetic-expansion-v2-3-1-development-silver",
                "synthetic-expansion-v2-3-1-held-out-silver",
                Path("evaluation/configs/synthetic_expansion_l2_candidates_v4.yaml"),
                "synthetic-expansion-v2-3-1-l2-development-candidates-v4",
                "1.3.1",
            ),
            "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v2": (
                "2.3.1",
                Path("data/synthetic_expansion/reviewed/v2_3_1"),
                Path("data/synthetic_expansion/splits/v2_3_1_silver_split_manifest.json"),
                "synthetic-expansion-v2-3-1-development-silver",
                "synthetic-expansion-v2-3-1-held-out-silver",
                Path("evaluation/configs/synthetic_expansion_l2_candidates_v4.yaml"),
                "synthetic-expansion-v2-3-1-l2-development-candidates-v4",
                "1.3.1",
            ),
            "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v3": (
                "2.3.1",
                Path("data/synthetic_expansion/reviewed/v2_3_1"),
                Path("data/synthetic_expansion/splits/v2_3_1_silver_split_manifest.json"),
                "synthetic-expansion-v2-3-1-development-silver",
                "synthetic-expansion-v2-3-1-held-out-silver",
                Path("evaluation/configs/synthetic_expansion_l2_candidates_v4.yaml"),
                "synthetic-expansion-v2-3-1-l2-development-candidates-v4",
                "1.3.1",
            ),
            "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v4": (
                "2.3.1",
                Path("data/synthetic_expansion/reviewed/v2_3_1"),
                Path("data/synthetic_expansion/splits/v2_3_1_silver_split_manifest.json"),
                "synthetic-expansion-v2-3-1-development-silver",
                "synthetic-expansion-v2-3-1-held-out-silver",
                Path("evaluation/configs/synthetic_expansion_l2_candidates_v4.yaml"),
                "synthetic-expansion-v2-3-1-l2-development-candidates-v4",
                "1.3.1",
            ),
            "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v5": (
                "2.3.1",
                Path("data/synthetic_expansion/reviewed/v2_3_1"),
                Path("data/synthetic_expansion/splits/v2_3_1_silver_split_manifest.json"),
                "synthetic-expansion-v2-3-1-development-silver",
                "synthetic-expansion-v2-3-1-held-out-silver",
                Path("evaluation/configs/synthetic_expansion_l2_candidates_v4.yaml"),
                "synthetic-expansion-v2-3-1-l2-development-candidates-v4",
                "1.3.1",
            ),
            "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v6": (
                "2.3.1",
                Path("data/synthetic_expansion/reviewed/v2_3_1"),
                Path("data/synthetic_expansion/splits/v2_3_1_silver_split_manifest.json"),
                "synthetic-expansion-v2-3-1-development-silver",
                "synthetic-expansion-v2-3-1-held-out-silver",
                Path("evaluation/configs/synthetic_expansion_l2_candidates_v4.yaml"),
                "synthetic-expansion-v2-3-1-l2-development-candidates-v4",
                "1.3.1",
            ),
            "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v7": (
                "2.3.1",
                Path("data/synthetic_expansion/reviewed/v2_3_1"),
                Path("data/synthetic_expansion/splits/v2_3_1_silver_split_manifest.json"),
                "synthetic-expansion-v2-3-1-development-silver",
                "synthetic-expansion-v2-3-1-held-out-silver",
                Path("evaluation/configs/synthetic_expansion_l2_candidates_v4.yaml"),
                "synthetic-expansion-v2-3-1-l2-development-candidates-v4",
                "1.3.1",
            ),
            "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v8": (
                "2.3.1",
                Path("data/synthetic_expansion/reviewed/v2_3_1"),
                Path("data/synthetic_expansion/splits/v2_3_1_silver_split_manifest.json"),
                "synthetic-expansion-v2-3-1-development-silver",
                "synthetic-expansion-v2-3-1-held-out-silver",
                Path("evaluation/configs/synthetic_expansion_l2_candidates_v4.yaml"),
                "synthetic-expansion-v2-3-1-l2-development-candidates-v4",
                "1.3.1",
            ),
        }.get(self.experiment_id)
        if expected_lineage is not None:
            actual_lineage = (
                self.dataset_version,
                self.reviewed_dataset_directory,
                self.split_manifest_path,
                self.development_partition_id,
                self.held_out_partition_id,
                self.l2_configuration_path,
                self.l2_candidate_set_id,
                self.l2_candidate_set_version,
            )
            if actual_lineage != expected_lineage:
                raise ValueError("L3 experiment does not match remediated dataset lineage")
        elif (
            self.dataset_version != "2.1.0"
            or self.reviewed_dataset_directory != Path("data/synthetic_expansion/reviewed/v2")
            or self.split_manifest_path
            != Path("data/synthetic_expansion/splits/v2_silver_split_manifest.json")
            or self.development_partition_id != "synthetic-expansion-v2-development-silver"
            or self.held_out_partition_id != "synthetic-expansion-v2-held-out-silver"
            or self.l2_configuration_path
            != Path("evaluation/configs/synthetic_expansion_l2_candidates_v1.yaml")
            or self.l2_candidate_set_id != "synthetic-expansion-v2-l2-development-candidates-v1"
            or self.l2_candidate_set_version != "1.1.0"
        ):
            raise ValueError("historical L3 experiment lineage must remain unchanged")
        if self.provider_identifier == "openai":
            if self.cost_policy is None:
                raise ValueError("paid L3 experiment requires a cost policy")
            expected_cost_policy = (
                Decimal("0.75"),
                Decimal("0.075"),
                Decimal("4.50"),
                12000,
                Decimal("1.00"),
            )
            actual_cost_policy = (
                self.cost_policy.input_usd_per_million_tokens,
                self.cost_policy.cached_input_usd_per_million_tokens,
                self.cost_policy.output_usd_per_million_tokens,
                self.cost_policy.assumed_max_input_tokens_per_request,
                self.cost_policy.maximum_estimated_experiment_cost_usd,
            )
            if actual_cost_policy != expected_cost_policy:
                raise ValueError("OpenAI L3 pricing and cost policy do not match")
            if (
                self.request_policy.max_completion_tokens != 4096
                or self.request_policy.reasoning_effort != "none"
                or self.billing_tier_assumption != "paid_tier_1"
            ):
                raise ValueError("OpenAI L3 token, reasoning and billing policy do not match")
            worst_case_cost = (
                Decimal(self.request_policy.hard_request_cap)
                * (
                    Decimal(self.cost_policy.assumed_max_input_tokens_per_request)
                    * self.cost_policy.input_usd_per_million_tokens
                    + Decimal(self.request_policy.max_completion_tokens)
                    * self.cost_policy.output_usd_per_million_tokens
                )
                / Decimal("1000000")
            )
            if worst_case_cost > self.cost_policy.maximum_estimated_experiment_cost_usd:
                raise ValueError("OpenAI L3 worst-case estimated cost exceeds the budget")
        elif self.cost_policy is not None:
            raise ValueError("free L3 experiment must not declare a paid cost policy")
        expected_score_mapping_version = (
            "l3-deterministic-level-mapping-v1"
            if self.experiment_id
            in {
                "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v5",
                "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v6",
                "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v7",
                "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v8",
            }
            else "provider-weighted-points-v1"
        )
        if self.l3_score_mapping_version != expected_score_mapping_version:
            raise ValueError("L3 experiment and score mapping version do not match")
        safety_gated_experiment = self.experiment_id in {
            "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v7",
            "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v8",
        }
        expected_requirement_status_rate = (
            Decimal("0.95") if safety_gated_experiment else Decimal("1")
        )
        if (
            self.quality_policy.required_requirement_status_match_rate
            != expected_requirement_status_rate
            or self.quality_policy.maximum_unsafe_requirement_status_mismatch_count != 0
        ):
            raise ValueError("L3 requirement-status safety gate does not match experiment")
        hybrid_tuned_experiment = (
            self.experiment_id == "synthetic-expansion-v2-openai-gpt-5-4-mini-l3-validation-v8"
        )
        expected_stability_status_rate = Decimal("0.8") if hybrid_tuned_experiment else Decimal("1")
        if (
            self.quality_policy.required_stability_requirement_agreement_rate
            != expected_stability_status_rate
            or self.quality_policy.required_stability_requirement_route_agreement_rate
            != Decimal("1")
        ):
            raise ValueError("L3 stability safety gate does not match experiment")
        expected_hybrid_policy = (
            (
                "openai-role-calibrated-hybrid-v1",
                "coverage-70-95-v1",
                Decimal("0.40"),
                Decimal("0.20"),
                Decimal("0.40"),
                Decimal("70"),
                Decimal("85"),
                Decimal("35"),
                Decimal("2"),
            )
            if hybrid_tuned_experiment
            else None
        )
        actual_hybrid_policy = (
            None
            if self.hybrid_policy is None
            else (
                self.hybrid_policy.candidate_id,
                self.hybrid_policy.l2_candidate_id,
                self.hybrid_policy.aggregation.l1_deterministic_rules,
                self.hybrid_policy.aggregation.l2_section_semantic_matching,
                self.hybrid_policy.aggregation.l3_evidence_grounded_reasoning,
                self.hybrid_policy.thresholds.waitlist_minimum,
                self.hybrid_policy.thresholds.pass_minimum,
                self.hybrid_policy.disagreement_points,
                self.hybrid_policy.boundary_offset_points,
            )
        )
        if actual_hybrid_policy != expected_hybrid_policy:
            raise ValueError("L3 hybrid tuning policy does not match experiment")
        return self

    @property
    def required_valid_attempt_count(self) -> int:
        return len(self.primary_pair_ids) + len(self.stability.pair_ids)


def load_expansion_l3_configuration(
    repository_root: Path,
    configuration_path: Path = CONFIG_PATH,
) -> ExpansionL3Configuration:
    path = repository_root / configuration_path
    value = cast(object, yaml.safe_load(path.read_text(encoding="utf-8")))
    if not isinstance(value, dict):
        raise ValueError("expansion L3 configuration must be a mapping")
    return ExpansionL3Configuration.model_validate(cast(dict[str, object], value))
