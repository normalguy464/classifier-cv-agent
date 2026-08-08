from __future__ import annotations

import argparse
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Literal, Self, cast

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.app.agents.classifier.scoring.l2_policy import (
    L2CoverageConfiguration,
    build_query_coverage_l2_policy,
)
from backend.app.contracts import EvidenceSection, JobProfile, ScoringRubric
from evaluation.datasets.runtime_v2 import file_sha256
from evaluation.experiments.run_runtime_v2_offline_l1_l2 import (
    CONFIG_PATH as OFFLINE_CONFIG_PATH,
    OfflineEmbeddingRuntime,
    OfflinePolicySet,
    build_offline_policy_set,
    build_partition_summary,
    build_precomputed_bridges,
    default_embedding_runtime,
    evaluate_offline_cases,
    evaluate_quality_checks,
    load_offline_data,
    load_offline_configuration,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = Path("evaluation/configs/runtime_v2_l2_candidates_v1.yaml")
REPORT_PATH = Path("evaluation/reports/runtime_v2_l2_tuning_v1.json")


class FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class L2Candidate(FrozenModel):
    candidate_id: str = Field(min_length=1)
    similarity_floor: Decimal = Field(ge=-1, le=1)
    similarity_ceiling: Decimal = Field(ge=-1, le=1)
    minimum_query_score: Decimal = Field(ge=0, le=100)
    query_profile: Literal["coverage-v1", "rubric-signals-v2", "rubric-quality-v3"] = "coverage-v1"

    @model_validator(mode="after")
    def validate_interval(self) -> Self:
        if self.similarity_ceiling <= self.similarity_floor:
            raise ValueError("similarity_ceiling must be greater than similarity_floor")
        return self


class SectionWeight(FrozenModel):
    section: EvidenceSection
    weight: Decimal = Field(ge=0, le=1)


class SelectionConfiguration(FrozenModel):
    require_all_offline_checks: Literal[True]
    rank_by: tuple[
        Literal[
            "failed_check_count_ascending",
            "validation_total_score_mae_ascending",
            "validation_score_correlation_descending",
        ],
        ...,
    ]


class L2TuningConfiguration(FrozenModel):
    schema_version: Literal["1.0.0"]
    experiment_id: Literal["runtime-v2-l2-candidates-v1"]
    experiment_version: Literal["1.0.0"]
    status: Literal["approved_for_offline_tuning"]
    stage7_v1_test_allowed: Literal[False]
    llm_provider_calls_allowed: Literal[False]
    candidates: tuple[L2Candidate, ...]
    top_k: int = Field(ge=1)
    section_weights: tuple[SectionWeight, ...]
    selection: SelectionConfiguration

    @model_validator(mode="after")
    def validate_unique_values(self) -> Self:
        candidate_ids = tuple(item.candidate_id for item in self.candidates)
        if not candidate_ids or len(candidate_ids) != len(set(candidate_ids)):
            raise ValueError("candidates must contain unique identifiers")
        sections = tuple(item.section for item in self.section_weights)
        if len(sections) != len(set(sections)):
            raise ValueError("section_weights must contain unique sections")
        if not self.selection.rank_by:
            raise ValueError("selection rank_by must not be empty")
        return self


def load_tuning_configuration(
    repository_root: Path,
    configuration_path: Path = CONFIG_PATH,
) -> L2TuningConfiguration:
    payload = yaml.safe_load((repository_root / configuration_path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("L2 tuning configuration must be a mapping")
    return L2TuningConfiguration.model_validate(cast(dict[str, object], payload))


def _timestamp(value: str) -> datetime:
    try:
        timestamp = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError("generated_at must be an ISO 8601 timestamp") from error
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("generated_at must include a timezone")
    return timestamp


def _candidate_policy_set(
    candidate: L2Candidate,
    base_policy_set: OfflinePolicySet,
    jobs: dict[str, JobProfile],
    rubrics: dict[str, ScoringRubric],
    configuration: L2TuningConfiguration,
) -> OfflinePolicySet:
    rubrics_by_job = {item.job_profile_id: item for item in rubrics.values()}
    coverage = L2CoverageConfiguration(
        similarity_floor=candidate.similarity_floor,
        similarity_ceiling=candidate.similarity_ceiling,
        top_k=configuration.top_k,
        minimum_query_score=candidate.minimum_query_score,
        section_weights=tuple(
            (item.section, item.weight) for item in configuration.section_weights
        ),
        query_profile=candidate.query_profile,
    )
    return OfflinePolicySet(
        candidate_id=candidate.candidate_id,
        runtime_directory=base_policy_set.runtime_directory,
        l1_by_job=base_policy_set.l1_by_job,
        l2_by_job={
            job_id: build_query_coverage_l2_policy(
                job,
                rubrics_by_job[job_id],
                coverage,
            )
            for job_id, job in jobs.items()
        },
    )


def _ranking_key(result: dict[str, object]) -> tuple[int, float, float]:
    quality_gate = cast(dict[str, object], result["quality_gate"])
    checks = cast(dict[str, bool], quality_gate["checks"])
    validation = cast(dict[str, object], result["validation"])
    l2 = cast(dict[str, object], validation["l2"])
    return (
        sum(not value for value in checks.values()),
        float(cast(float, l2["total_score_mae"])),
        -float(cast(float, l2["score_correlation"])),
    )


def run_l2_tuning(
    repository_root: Path,
    generated_at: datetime,
    embedding_runtime: OfflineEmbeddingRuntime | None = None,
    configuration_path: Path = CONFIG_PATH,
) -> dict[str, object]:
    if generated_at.tzinfo is None or generated_at.utcoffset() is None:
        raise ValueError("generated_at must include a timezone")
    tuning = load_tuning_configuration(repository_root, configuration_path)
    offline = load_offline_configuration(repository_root)
    pairs, profiles, jobs, rubrics, manifest, split = load_offline_data(repository_root, offline)
    base_policy_set = build_offline_policy_set(
        repository_root,
        offline.candidate_runtime_directory,
        "runtime-v2-l2-tuning-base",
        jobs,
        rubrics,
        True,
    )
    runtime = embedding_runtime or default_embedding_runtime(
        repository_root,
        offline.candidate_runtime_directory,
        next(iter(jobs)),
        True,
    )
    bridge_policy_set = _candidate_policy_set(
        tuning.candidates[0], base_policy_set, jobs, rubrics, tuning
    )
    bridges = build_precomputed_bridges(pairs, profiles, bridge_policy_set, runtime)
    results: list[dict[str, object]] = []
    for candidate in tuning.candidates:
        policy_set = _candidate_policy_set(candidate, base_policy_set, jobs, rubrics, tuning)
        cases = evaluate_offline_cases(pairs, profiles, rubrics, policy_set, bridges)
        cases_by_id = {item.pair_id: item for item in cases}
        development = build_partition_summary(
            tuple(cases_by_id[pair_id] for pair_id in split.development.pair_ids)
        )
        validation = build_partition_summary(
            tuple(cases_by_id[pair_id] for pair_id in split.validation.pair_ids)
        )
        checks = evaluate_quality_checks(development, validation, offline)
        results.append(
            {
                "candidate": candidate.model_dump(mode="json"),
                "development": development,
                "validation": validation,
                "quality_gate": {"passed": all(checks.values()), "checks": checks},
            }
        )
    ranked = sorted(results, key=_ranking_key)
    selected = ranked[0]
    selected_gate = cast(dict[str, object], selected["quality_gate"])
    selected_candidate = cast(dict[str, object], selected["candidate"])
    return {
        "schema_version": "1.0.0",
        "report_id": f"{tuning.experiment_id}-report",
        "generated_at": generated_at.isoformat(),
        "llm_provider_calls_made": False,
        "stage7_v1_test_accessed": False,
        "configured_embedding_model_executed": runtime.configured_model_executed,
        "selected_candidate_id": selected_candidate["candidate_id"],
        "selection_passed": bool(selected_gate["passed"]),
        "candidate_results": ranked,
        "traceability": {
            "configuration_path": configuration_path.as_posix(),
            "configuration_sha256": file_sha256(repository_root / configuration_path),
            "offline_configuration_path": OFFLINE_CONFIG_PATH.as_posix(),
            "offline_configuration_sha256": file_sha256(repository_root / OFFLINE_CONFIG_PATH),
            "reviewed_dataset_manifest_sha256": file_sha256(
                repository_root / offline.reviewed_dataset_directory / "manifest.json"
            ),
            "split_manifest_sha256": file_sha256(repository_root / offline.split_manifest_path),
            "l1_rules_sha256": file_sha256(
                repository_root / offline.candidate_runtime_directory / "l1_rules.yaml"
            ),
            "dataset_id": manifest.dataset_id,
            "embedding_model_identifier": runtime.model_identifier,
            "embedding_model_version": runtime.model_version,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated-at", required=True)
    parser.add_argument("--configuration-path")
    parser.add_argument("--report-path")
    arguments = parser.parse_args()
    generated_at = _timestamp(cast(str, arguments.generated_at))
    configuration_path = (
        Path(cast(str, arguments.configuration_path))
        if arguments.configuration_path
        else CONFIG_PATH
    )
    report = run_l2_tuning(REPOSITORY_ROOT, generated_at, configuration_path=configuration_path)
    report_path = Path(cast(str, arguments.report_path)) if arguments.report_path else REPORT_PATH
    output_path = REPOSITORY_ROOT / report_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(output_path)


if __name__ == "__main__":
    main()
