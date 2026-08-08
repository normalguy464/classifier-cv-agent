from __future__ import annotations

import argparse
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Literal, Self, cast

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from evaluation.datasets.runtime_v2 import file_sha256
from evaluation.experiments.run_runtime_v2_hybrid_selection import (
    HybridCandidate,
    evaluate_hybrid_candidate,
    load_json_report,
    load_reviewed_pairs,
    partition_sources,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = Path("evaluation/configs/runtime_v2_hybrid_fresh_confirmation_v1.yaml")
REPORT_PATH = Path("evaluation/reports/runtime_v2_hybrid_fresh_confirmation_v1.json")


class FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class ConfirmationPolicy(FrozenModel):
    minimum_accuracy: Decimal = Field(ge=0, le=1)
    minimum_macro_f1: Decimal = Field(ge=0, le=1)
    minimum_needs_review_recall: Decimal = Field(ge=0, le=1)
    maximum_false_reject_count: int = Field(ge=0)
    maximum_unsafe_pass_count: int = Field(ge=0)
    maximum_review_rate: Decimal = Field(ge=0, le=1)


class HybridConfirmationConfiguration(FrozenModel):
    schema_version: Literal["1.0.0"]
    experiment_id: Literal[
        "runtime-v2-hybrid-fresh-confirmation-v1",
        "runtime-v2-hybrid-fresh-confirmation-v2",
    ]
    experiment_version: Literal["1.0.0", "2.0.0"]
    status: Literal["ready_after_development_selection"]
    reviewed_pairs_path: Path
    offline_report_path: Path
    fresh_l3_report_path: Path
    partition: Literal["development"]
    development_selection_allowed: Literal[False]
    validation_access_allowed: Literal[False]
    stage7_v1_test_allowed: Literal[False]
    llm_provider_calls_allowed: Literal[False]
    selected_candidate: HybridCandidate
    confirmation_policy: ConfirmationPolicy

    @model_validator(mode="after")
    def validate_configuration(self) -> Self:
        paths = (
            self.reviewed_pairs_path,
            self.offline_report_path,
            self.fresh_l3_report_path,
        )
        if any(path.is_absolute() or ".." in path.parts for path in paths):
            raise ValueError("hybrid confirmation paths must be repository-relative")
        expected_version = {
            "runtime-v2-hybrid-fresh-confirmation-v1": "1.0.0",
            "runtime-v2-hybrid-fresh-confirmation-v2": "2.0.0",
        }[self.experiment_id]
        if self.experiment_version != expected_version:
            raise ValueError("hybrid confirmation experiment version is inconsistent")
        return self


def load_configuration(
    repository_root: Path,
    configuration_path: Path = CONFIG_PATH,
) -> HybridConfirmationConfiguration:
    payload = yaml.safe_load((repository_root / configuration_path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("hybrid confirmation configuration must be a mapping")
    return HybridConfirmationConfiguration.model_validate(cast(dict[str, object], payload))


def _passes(result: dict[str, object], policy: ConfirmationPolicy) -> bool:
    return (
        cast(float, result["accuracy"]) >= float(policy.minimum_accuracy)
        and cast(float, result["macro_f1"]) >= float(policy.minimum_macro_f1)
        and cast(float, result["needs_review_recall"]) >= float(policy.minimum_needs_review_recall)
        and cast(int, result["false_reject_count"]) <= policy.maximum_false_reject_count
        and cast(int, result["unsafe_pass_count"]) <= policy.maximum_unsafe_pass_count
        and cast(float, result["review_rate"]) <= float(policy.maximum_review_rate)
    )


def build_report(
    repository_root: Path,
    generated_at: datetime,
    configuration_path: Path = CONFIG_PATH,
) -> dict[str, object]:
    configuration = load_configuration(repository_root, configuration_path)
    pairs = load_reviewed_pairs(repository_root / configuration.reviewed_pairs_path)
    offline = load_json_report(repository_root / configuration.offline_report_path)
    l3 = load_json_report(repository_root / configuration.fresh_l3_report_path)
    sources = partition_sources(offline, l3, configuration.partition)
    result = evaluate_hybrid_candidate(configuration.selected_candidate, pairs, *sources)
    passed = _passes(result, configuration.confirmation_policy)
    return {
        "schema_version": "1.0.0",
        "report_id": configuration.experiment_id,
        "generated_at": generated_at.isoformat(),
        "development_selection_performed": False,
        "validation_accessed": False,
        "llm_provider_calls_made": False,
        "stage7_v1_test_accessed": False,
        "selected_candidate_id": configuration.selected_candidate.candidate_id,
        "confirmation": result,
        "quality_gate": {"passed": passed},
        "traceability": {
            "configuration_sha256": file_sha256(repository_root / configuration_path),
            "reviewed_pairs_sha256": file_sha256(
                repository_root / configuration.reviewed_pairs_path
            ),
            "offline_report_sha256": file_sha256(
                repository_root / configuration.offline_report_path
            ),
            "fresh_l3_report_sha256": file_sha256(
                repository_root / configuration.fresh_l3_report_path
            ),
        },
    }


def _timestamp(value: str) -> datetime:
    timestamp = datetime.fromisoformat(value)
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("generated_at must include a timezone")
    return timestamp


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated-at", default="2026-08-08T22:30:00+07:00")
    parser.add_argument("--configuration-path", default=str(CONFIG_PATH))
    parser.add_argument("--output", default=str(REPORT_PATH))
    arguments = parser.parse_args()
    configuration_path = Path(cast(str, arguments.configuration_path))
    report = build_report(
        REPOSITORY_ROOT,
        _timestamp(cast(str, arguments.generated_at)),
        configuration_path,
    )
    output = REPOSITORY_ROOT / Path(cast(str, arguments.output))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
