from __future__ import annotations

import hashlib
import json
from datetime import date
from decimal import Decimal
from pathlib import Path, PurePosixPath
from typing import Annotated, Literal, Self, cast

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator


class RuntimeManifestError(ValueError):
    pass


class RuntimeManifestModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class HashedArtifact(RuntimeManifestModel):
    path: Annotated[str, Field(min_length=1, max_length=512)]
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_path(self) -> Self:
        path = PurePosixPath(self.path)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("artifact path must remain inside the configuration directory")
        return self


class SourceArtifact(HashedArtifact):
    report_id: str | None = Field(default=None, min_length=1, max_length=256)


class RuntimeScoringStrategy(RuntimeManifestModel):
    scoring_configuration_version: Literal["2.0.0", "3.0.0"]
    models_configuration_version: Literal["2.0.0", "3.0.0"]
    l1_rules_configuration_version: Literal["2.0.0", "3.0.0"]
    l2_candidate_id: Literal[
        "coverage-70-95-v1",
        "rubric-quality-v3-extra-trees-leaf3-v1",
    ]
    prompt_version: Literal["l3-evidence-rubric-v12", "l3-evidence-rubric-v15"]
    l3_score_mapping_version: Literal[
        "l3-deterministic-level-mapping-v1",
        "l3-deterministic-level-mapping-v3",
    ]
    provider_identifier: Literal["openai"]
    model_identifier: Literal["gpt-5.4-mini-2026-03-17"]
    aggregation: tuple[Decimal, Decimal, Decimal]
    thresholds: tuple[Decimal, Decimal]
    disagreement_points: Decimal
    boundary_offset_points: Decimal

    @model_validator(mode="after")
    def validate_strategy(self) -> Self:
        if sum(self.aggregation, Decimal("0")) != Decimal("1"):
            raise ValueError("runtime aggregation weights must total 1")
        strategy_key = (
            self.scoring_configuration_version,
            self.models_configuration_version,
            self.l1_rules_configuration_version,
            self.l2_candidate_id,
            self.prompt_version,
            self.l3_score_mapping_version,
        )
        expected = {
            (
                "2.0.0",
                "2.0.0",
                "2.0.0",
                "coverage-70-95-v1",
                "l3-evidence-rubric-v12",
                "l3-deterministic-level-mapping-v1",
            ): (
                (Decimal("0.40"), Decimal("0.20"), Decimal("0.40")),
                (Decimal("70"), Decimal("85")),
                Decimal("35"),
            ),
            (
                "3.0.0",
                "3.0.0",
                "3.0.0",
                "rubric-quality-v3-extra-trees-leaf3-v1",
                "l3-evidence-rubric-v15",
                "l3-deterministic-level-mapping-v3",
            ): (
                (Decimal("0.20"), Decimal("0.30"), Decimal("0.50")),
                (Decimal("67"), Decimal("82")),
                Decimal("45"),
            ),
        }.get(strategy_key)
        if expected is None:
            raise ValueError("runtime strategy versions are not an approved combination")
        expected_aggregation, expected_thresholds, expected_disagreement = expected
        if self.aggregation != expected_aggregation:
            raise ValueError("runtime aggregation does not match its versioned strategy")
        if self.thresholds != expected_thresholds:
            raise ValueError("runtime thresholds do not match their versioned strategy")
        if self.disagreement_points != expected_disagreement:
            raise ValueError("runtime disagreement threshold does not match its versioned strategy")
        if self.boundary_offset_points != Decimal("2"):
            raise ValueError("runtime boundary offset must match approved v8")
        return self


class RuntimeDataPolicy(RuntimeManifestModel):
    development_report_only: Literal[True]
    held_out_evaluated: Literal[False]
    original_frozen_test_evaluated: Literal[False]
    raw_provider_response_persisted: Literal[False]


class RuntimeConfigurationManifest(RuntimeManifestModel):
    schema_version: Literal["1.0.0"]
    artifact_kind: Literal["classifier_runtime_configuration_manifest"]
    configuration_set_id: Literal[
        "five-role-runtime-v1",
        "five-role-runtime-v2-development-candidate",
        "five-role-runtime-v2",
    ]
    manifest_version: Literal["1.0.0", "2.0.0"]
    configuration_status: Literal[
        "approved_v8_pending_gate6_freeze",
        "frozen_for_stage7",
        "development_candidate_pending_review",
    ]
    user_approval_date: date | None
    approved_experiment_id: str = Field(min_length=1, max_length=256)
    source_report: SourceArtifact
    source_experiment_configuration: SourceArtifact
    supported_job_profile_ids: Annotated[tuple[str, ...], Field(min_length=1)]
    runtime_artifacts: Annotated[tuple[HashedArtifact, ...], Field(min_length=1)]
    strategy: RuntimeScoringStrategy
    data_policy: RuntimeDataPolicy

    @model_validator(mode="after")
    def validate_uniqueness(self) -> Self:
        if len(self.supported_job_profile_ids) != len(set(self.supported_job_profile_ids)):
            raise ValueError("runtime job profile identifiers must be unique")
        paths = tuple(item.path for item in self.runtime_artifacts)
        if len(paths) != len(set(paths)):
            raise ValueError("runtime artifact paths must be unique")
        return self


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def load_runtime_manifest(
    repository_root: Path,
    configuration_directory: Path,
) -> RuntimeConfigurationManifest | None:
    manifest_path = configuration_directory / "runtime_manifest.yaml"
    if not manifest_path.is_file():
        return None
    try:
        payload = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as error:
        raise RuntimeManifestError("cannot load runtime configuration manifest") from error
    if not isinstance(payload, dict):
        raise RuntimeManifestError("runtime configuration manifest must be a mapping")
    manifest = RuntimeConfigurationManifest.model_validate(cast(dict[str, object], payload))
    for artifact in manifest.runtime_artifacts:
        path = (configuration_directory / artifact.path).resolve()
        try:
            path.relative_to(configuration_directory.resolve())
        except ValueError as error:
            raise RuntimeManifestError(
                "runtime artifact escaped configuration directory"
            ) from error
        if not path.is_file() or _sha256(path) != artifact.sha256:
            raise RuntimeManifestError(f"runtime artifact hash mismatch: {artifact.path}")
    for source in (manifest.source_report, manifest.source_experiment_configuration):
        path = (repository_root / source.path).resolve()
        try:
            path.relative_to(repository_root.resolve())
        except ValueError as error:
            raise RuntimeManifestError("runtime source artifact escaped repository") from error
        if not path.is_file() or _sha256(path) != source.sha256:
            raise RuntimeManifestError(f"runtime source artifact hash mismatch: {source.path}")
    report_payload = json.loads(
        (repository_root / manifest.source_report.path).read_text(encoding="utf-8")
    )
    report = cast(dict[str, object], report_payload) if isinstance(report_payload, dict) else None
    if report is None:
        raise RuntimeManifestError("runtime source report must be a JSON object")
    quality_gate = report.get("quality_gate")
    nested_gate_passed = (
        isinstance(quality_gate, dict)
        and cast(dict[str, object], quality_gate).get("passed") is True
    )
    if report.get("report_id") != manifest.source_report.report_id or not (
        report.get("quality_gate_passed") is True or nested_gate_passed
    ):
        raise RuntimeManifestError("runtime source report is not the approved passing report")
    return manifest
