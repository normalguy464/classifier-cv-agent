from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Annotated, Literal, Self, cast

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.app.contracts import EvidenceSection
from backend.app.agents.classifier.scoring.l2_policy import L2CoverageConfiguration

CONFIG_PATH = Path("evaluation/configs/synthetic_expansion_l2_candidates_v1.yaml")
REMEDIATED_CONFIG_PATH = Path("evaluation/configs/synthetic_expansion_l2_candidates_v2.yaml")
REMEDIATED_V2_3_CONFIG_PATH = Path("evaluation/configs/synthetic_expansion_l2_candidates_v3.yaml")
REMEDIATED_V2_3_1_CONFIG_PATH = Path("evaluation/configs/synthetic_expansion_l2_candidates_v4.yaml")


class L2CandidateModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class ExpansionL2SelectionPolicy(L2CandidateModel):
    maximum_exact_ceiling_rate: Annotated[
        Decimal,
        Field(ge=Decimal("0"), le=Decimal("1")),
    ]
    required_strong_over_hard_negative_roles: Literal[5]
    required_false_reject_count: Literal[0]
    required_unsafe_pass_count: Literal[0]


class ExpansionL2Candidate(L2CandidateModel):
    candidate_id: Annotated[str, Field(min_length=1, max_length=128)]
    similarity_floor: Annotated[Decimal, Field(ge=Decimal("-1"), le=Decimal("1"))]
    similarity_ceiling: Annotated[Decimal, Field(ge=Decimal("-1"), le=Decimal("1"))]
    top_k: int = Field(ge=1, le=20)
    minimum_query_score: Annotated[
        Decimal,
        Field(ge=Decimal("0"), le=Decimal("100")),
    ]

    @model_validator(mode="after")
    def validate_similarity_range(self) -> Self:
        if self.similarity_floor >= self.similarity_ceiling:
            raise ValueError("L2 candidate similarity floor must be below ceiling")
        return self


class ExpansionL2CandidateSet(L2CandidateModel):
    schema_version: Literal["1.0.0"]
    candidate_set_id: Literal[
        "synthetic-expansion-v2-l2-development-candidates-v1",
        "synthetic-expansion-v2-2-l2-development-candidates-v2",
        "synthetic-expansion-v2-3-l2-development-candidates-v3",
        "synthetic-expansion-v2-3-1-l2-development-candidates-v4",
    ]
    candidate_set_version: Literal["1.1.0", "1.2.0", "1.3.0", "1.3.1"]
    dataset_id: Literal["synthetic-cv-jd-expansion-v2-reviewed-silver"]
    dataset_version: Literal["2.1.0", "2.2.0", "2.3.0", "2.3.1"]
    reviewed_dataset_directory: Path = Path("data/synthetic_expansion/reviewed/v2")
    split_manifest_path: Path = Path(
        "data/synthetic_expansion/splits/v2_silver_split_manifest.json"
    )
    report_id: Literal[
        "synthetic-expansion-v2-l2-development-tuning-v1",
        "synthetic-expansion-v2-2-l2-development-tuning-v2",
        "synthetic-expansion-v2-3-l2-development-tuning-v3",
        "synthetic-expansion-v2-3-1-l2-development-tuning-v4",
    ] = "synthetic-expansion-v2-l2-development-tuning-v1"
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
    embedding_model_identifier: Literal["intfloat/multilingual-e5-base"]
    embedding_resolved_revision: Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]
    query_strategy_version: Literal["job-requirement-coverage-v1"]
    selection_policy: ExpansionL2SelectionPolicy
    candidates: Annotated[tuple[ExpansionL2Candidate, ...], Field(min_length=2)]
    section_weights: dict[EvidenceSection, Decimal]

    @model_validator(mode="after")
    def validate_candidate_set(self) -> Self:
        identifiers = tuple(item.candidate_id for item in self.candidates)
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("L2 candidate identifiers must be unique")
        required_sections = set(EvidenceSection)
        if set(self.section_weights) != required_sections:
            raise ValueError("L2 section weights must cover every evidence section")
        if any(
            not weight.is_finite() or weight <= Decimal("0") or weight > Decimal("1")
            for weight in self.section_weights.values()
        ):
            raise ValueError("L2 section weights must be above 0 and at most 1")
        expected = {
            "synthetic-expansion-v2-l2-development-candidates-v1": (
                "1.1.0",
                "2.1.0",
                Path("data/synthetic_expansion/reviewed/v2"),
                Path("data/synthetic_expansion/splits/v2_silver_split_manifest.json"),
                "synthetic-expansion-v2-l2-development-tuning-v1",
                "synthetic-expansion-v2-development-silver",
                "synthetic-expansion-v2-held-out-silver",
            ),
            "synthetic-expansion-v2-2-l2-development-candidates-v2": (
                "1.2.0",
                "2.2.0",
                Path("data/synthetic_expansion/reviewed/v2_2"),
                Path("data/synthetic_expansion/splits/v2_2_silver_split_manifest.json"),
                "synthetic-expansion-v2-2-l2-development-tuning-v2",
                "synthetic-expansion-v2-2-development-silver",
                "synthetic-expansion-v2-2-held-out-silver",
            ),
            "synthetic-expansion-v2-3-l2-development-candidates-v3": (
                "1.3.0",
                "2.3.0",
                Path("data/synthetic_expansion/reviewed/v2_3"),
                Path("data/synthetic_expansion/splits/v2_3_silver_split_manifest.json"),
                "synthetic-expansion-v2-3-l2-development-tuning-v3",
                "synthetic-expansion-v2-3-development-silver",
                "synthetic-expansion-v2-3-held-out-silver",
            ),
            "synthetic-expansion-v2-3-1-l2-development-candidates-v4": (
                "1.3.1",
                "2.3.1",
                Path("data/synthetic_expansion/reviewed/v2_3_1"),
                Path("data/synthetic_expansion/splits/v2_3_1_silver_split_manifest.json"),
                "synthetic-expansion-v2-3-1-l2-development-tuning-v4",
                "synthetic-expansion-v2-3-1-development-silver",
                "synthetic-expansion-v2-3-1-held-out-silver",
            ),
        }[self.candidate_set_id]
        actual = (
            self.candidate_set_version,
            self.dataset_version,
            self.reviewed_dataset_directory,
            self.split_manifest_path,
            self.report_id,
            self.development_partition_id,
            self.held_out_partition_id,
        )
        if actual != expected:
            raise ValueError("L2 candidate set does not match its dataset lineage")
        return self

    def coverage_configuration(
        self,
        candidate: ExpansionL2Candidate,
    ) -> L2CoverageConfiguration:
        return L2CoverageConfiguration(
            similarity_floor=candidate.similarity_floor,
            similarity_ceiling=candidate.similarity_ceiling,
            top_k=candidate.top_k,
            minimum_query_score=candidate.minimum_query_score,
            section_weights=tuple(self.section_weights.items()),
        )


def load_expansion_l2_candidate_set(
    repository_root: Path,
    configuration_path: Path = CONFIG_PATH,
) -> ExpansionL2CandidateSet:
    path = repository_root / configuration_path
    value = cast(object, yaml.safe_load(path.read_text(encoding="utf-8")))
    if not isinstance(value, dict):
        raise ValueError("L2 candidate configuration must be a mapping")
    return ExpansionL2CandidateSet.model_validate(cast(dict[str, object], value))
