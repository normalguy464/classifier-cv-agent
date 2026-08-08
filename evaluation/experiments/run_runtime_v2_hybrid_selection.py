from __future__ import annotations

import argparse
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Annotated, Literal, Self, cast

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.app.agents.classifier.routing import route_classification
from backend.app.agents.classifier.scoring import aggregate_level_scores
from backend.app.contracts import (
    AggregationWeights,
    ClassificationDecision,
    LevelScoreStatus,
)
from backend.app.domain import (
    BoundaryRule,
    LevelAssessment,
    RequirementAssessment,
    RoutingPolicy,
    ScoringLevel,
)
from evaluation.datasets.runtime_v2 import file_sha256
from evaluation.datasets.synthetic_expansion import SyntheticPairAnnotation
from evaluation.metrics import calculate_metrics

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = Path("evaluation/configs/runtime_v2_hybrid_selection_v1.yaml")
REPORT_PATH = Path("evaluation/reports/runtime_v2_hybrid_selection_v1.json")


class FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class HybridCandidate(FrozenModel):
    candidate_id: str
    l1_weight: Decimal = Field(ge=0, le=1)
    l2_weight: Decimal = Field(ge=0, le=1)
    l3_weight: Decimal = Field(ge=0, le=1)
    l3_score_offset: Decimal = Field(default=Decimal("0"), ge=0, le=15)
    waitlist_minimum: Decimal = Field(ge=0, le=100)
    pass_minimum: Decimal = Field(ge=0, le=100)
    disagreement_points: Decimal = Field(ge=0, le=100)
    lower_boundary_minimum: Decimal = Field(ge=0, le=100)
    lower_boundary_maximum: Decimal = Field(ge=0, le=100)
    upper_boundary_minimum: Decimal = Field(ge=0, le=100)
    upper_boundary_maximum: Decimal = Field(ge=0, le=100)

    @model_validator(mode="after")
    def validate_candidate(self) -> Self:
        if self.l1_weight + self.l2_weight + self.l3_weight != Decimal("1"):
            raise ValueError("hybrid weights must total one")
        if self.waitlist_minimum >= self.pass_minimum:
            raise ValueError("hybrid thresholds must be increasing")
        if self.lower_boundary_minimum > self.lower_boundary_maximum:
            raise ValueError("lower boundary is invalid")
        if self.upper_boundary_minimum > self.upper_boundary_maximum:
            raise ValueError("upper boundary is invalid")
        return self


class SelectionPolicy(FrozenModel):
    development_selects_candidate: Literal[True]
    validation_selects_candidate: Literal[False]
    minimum_accuracy: Decimal = Field(ge=0, le=1)
    minimum_macro_f1: Decimal = Field(ge=0, le=1)
    minimum_needs_review_recall: Decimal = Field(ge=0, le=1)
    maximum_false_reject_count: int = Field(ge=0)
    maximum_unsafe_pass_count: int = Field(ge=0)
    maximum_review_rate: Decimal = Field(ge=0, le=1)


class HybridSelectionConfiguration(FrozenModel):
    schema_version: Literal["1.0.0"]
    experiment_id: Literal[
        "runtime-v2-hybrid-selection-v1",
        "runtime-v2-hybrid-development-tuning-v2",
        "runtime-v2-hybrid-threshold-tuning-v3",
        "runtime-v2-hybrid-offset-tuning-v4",
        "runtime-v2-hybrid-expanded-development-v5",
        "runtime-v2-hybrid-waitlist-tuning-v6",
    ]
    experiment_version: Literal["1.0.0", "2.0.0", "3.0.0", "4.0.0", "5.0.0", "6.0.0"]
    status: Literal["ready_after_l3_validation"]
    reviewed_pairs_path: Path
    offline_report_path: Path
    development_l3_report_path: Path
    additional_development_l3_report_paths: tuple[Path, ...] = ()
    validation_l3_report_path: Path
    validation_evaluation_allowed: bool = True
    stage7_v1_test_allowed: Literal[False]
    llm_provider_calls_allowed: Literal[False]
    candidates: Annotated[tuple[HybridCandidate, ...], Field(min_length=2, max_length=6)]
    selection_policy: SelectionPolicy

    @model_validator(mode="after")
    def validate_configuration(self) -> Self:
        paths = (
            self.reviewed_pairs_path,
            self.offline_report_path,
            self.development_l3_report_path,
            self.validation_l3_report_path,
            *self.additional_development_l3_report_paths,
        )
        if any(path.is_absolute() or ".." in path.parts for path in paths):
            raise ValueError("hybrid selection paths must be repository-relative")
        candidate_ids = tuple(item.candidate_id for item in self.candidates)
        if len(candidate_ids) != len(set(candidate_ids)):
            raise ValueError("hybrid candidate identifiers must be unique")
        expected = {
            "runtime-v2-hybrid-selection-v1": ("1.0.0", True),
            "runtime-v2-hybrid-development-tuning-v2": ("2.0.0", False),
            "runtime-v2-hybrid-threshold-tuning-v3": ("3.0.0", False),
            "runtime-v2-hybrid-offset-tuning-v4": ("4.0.0", False),
            "runtime-v2-hybrid-expanded-development-v5": ("5.0.0", False),
            "runtime-v2-hybrid-waitlist-tuning-v6": ("6.0.0", False),
        }[self.experiment_id]
        if (self.experiment_version, self.validation_evaluation_allowed) != expected:
            raise ValueError("hybrid experiment version and data policy are inconsistent")
        return self


def load_configuration(
    repository_root: Path,
    configuration_path: Path = CONFIG_PATH,
) -> HybridSelectionConfiguration:
    payload = yaml.safe_load((repository_root / configuration_path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("hybrid selection configuration must be a mapping")
    return HybridSelectionConfiguration.model_validate(cast(dict[str, object], payload))


def load_json_report(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"report must be a JSON object: {path.name}")
    return cast(dict[str, object], payload)


def load_reviewed_pairs(path: Path) -> dict[str, SyntheticPairAnnotation]:
    return {
        item.pair_id: item
        for item in (
            SyntheticPairAnnotation.model_validate_json(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }


def _routing_policy(candidate: HybridCandidate) -> RoutingPolicy:
    return RoutingPolicy(
        pass_minimum=candidate.pass_minimum,
        waitlist_minimum=candidate.waitlist_minimum,
        missing_critical_evidence=True,
        conflicting_critical_evidence=True,
        invalid_provider_output=True,
        disagreement_points=candidate.disagreement_points,
        boundary_rules=(
            BoundaryRule(
                rule_id="lower-threshold-boundary",
                minimum=candidate.lower_boundary_minimum,
                maximum=candidate.lower_boundary_maximum,
            ),
            BoundaryRule(
                rule_id="upper-threshold-boundary",
                minimum=candidate.upper_boundary_minimum,
                maximum=candidate.upper_boundary_maximum,
            ),
        ),
        low_score_without_explicit_critical_unsatisfied=True,
        critical_unsatisfied_at_or_above_waitlist_threshold=True,
        reject_requires_explicit_unsatisfied_critical=True,
    )


def _weights(candidate: HybridCandidate) -> AggregationWeights:
    return AggregationWeights(
        l1_deterministic_rules=candidate.l1_weight,
        l2_section_semantic_matching=candidate.l2_weight,
        l3_evidence_grounded_reasoning=candidate.l3_weight,
    )


def _requirement_assessments(
    pair: SyntheticPairAnnotation,
) -> tuple[RequirementAssessment, ...]:
    return tuple(
        RequirementAssessment(
            requirement_id=item.requirement_id,
            evidence_status=item.evidence_status,
            evidence_ids=item.evidence_ids,
            rationale=item.rationale,
        )
        for item in pair.critical_requirement_assessments
    )


def partition_sources(
    offline_report: dict[str, object],
    l3_report: dict[str, object],
    partition: str,
) -> tuple[dict[str, dict[str, object]], dict[str, dict[str, object]]]:
    offline_partition = cast(dict[str, object], offline_report[partition])
    offline_cases = {
        cast(str, item["pair_id"]): item
        for item in cast(list[dict[str, object]], offline_partition["cases"])
    }
    l3_cases = {
        cast(str, item["pair_id"]): item
        for item in cast(list[dict[str, object]], l3_report["cases"])
    }
    if set(l3_cases).difference(offline_cases):
        raise ValueError("L3 report contains cases outside the offline partition")
    return offline_cases, l3_cases


def evaluate_hybrid_candidate(
    candidate: HybridCandidate,
    pairs: dict[str, SyntheticPairAnnotation],
    offline_cases: dict[str, dict[str, object]],
    l3_cases: dict[str, dict[str, object]],
) -> dict[str, object]:
    expected: list[ClassificationDecision] = []
    predicted: list[ClassificationDecision] = []
    cases: list[dict[str, object]] = []
    false_rejects: list[str] = []
    unsafe_passes: list[str] = []
    for pair_id in sorted(l3_cases):
        offline = offline_cases[pair_id]
        l3 = l3_cases[pair_id]
        pair = pairs[pair_id]
        requirements = _requirement_assessments(pair)
        levels = tuple(
            LevelAssessment(
                level=level,
                status=LevelScoreStatus.AVAILABLE,
                score=Decimal(str(score)),
                requirement_assessments=requirements if level is ScoringLevel.L1 else (),
            )
            for level, score in (
                (ScoringLevel.L1, offline["l1_score"]),
                (ScoringLevel.L2, offline["l2_score"]),
                (
                    ScoringLevel.L3,
                    min(
                        Decimal("100"),
                        Decimal(str(l3["l3_total_score"])) + candidate.l3_score_offset,
                    ),
                ),
            )
        )
        aggregation = aggregate_level_scores(levels, _weights(candidate))
        routing = route_classification(aggregation, requirements, _routing_policy(candidate))
        expected_label = ClassificationDecision(cast(str, offline["expected_label"]))
        expected.append(expected_label)
        predicted.append(routing.decision)
        if (
            routing.decision is ClassificationDecision.REJECT
            and expected_label is not routing.decision
        ):
            false_rejects.append(pair_id)
        if (
            routing.decision is ClassificationDecision.PASS
            and expected_label is not routing.decision
        ):
            unsafe_passes.append(pair_id)
        cases.append(
            {
                "pair_id": pair_id,
                "expected_label": expected_label.value,
                "predicted_label": routing.decision.value,
                "final_score": float(cast(Decimal, routing.final_score)),
                "review_reasons": list(routing.reasons),
            }
        )
    metrics = calculate_metrics(tuple(expected), tuple(predicted))
    review_count = sum(item is ClassificationDecision.NEEDS_REVIEW for item in predicted)
    needs_review = metrics.labels[ClassificationDecision.NEEDS_REVIEW.value]
    return {
        "candidate_id": candidate.candidate_id,
        "sample_count": metrics.sample_count,
        "accuracy": metrics.accuracy,
        "macro_f1": metrics.macro_f1,
        "cohen_kappa": metrics.cohen_kappa,
        "needs_review_recall": needs_review.recall,
        "review_rate": review_count / metrics.sample_count,
        "false_reject_count": len(false_rejects),
        "false_reject_case_ids": false_rejects,
        "unsafe_pass_count": len(unsafe_passes),
        "unsafe_pass_case_ids": unsafe_passes,
        "confusion_matrix": [list(row) for row in metrics.confusion_matrix],
        "cases": cases,
    }


def _passes(result: dict[str, object], policy: SelectionPolicy) -> bool:
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
    development_l3 = load_json_report(repository_root / configuration.development_l3_report_path)
    development_sources = partition_sources(offline, development_l3, "development")
    development_offline_cases, development_l3_cases = development_sources
    for additional_path in configuration.additional_development_l3_report_paths:
        additional_report = load_json_report(repository_root / additional_path)
        additional_offline, additional_l3 = partition_sources(
            offline,
            additional_report,
            "development",
        )
        if set(additional_l3).intersection(development_l3_cases):
            raise ValueError("development L3 reports must contain disjoint cases")
        development_offline_cases.update(additional_offline)
        development_l3_cases.update(additional_l3)
    development_results = [
        evaluate_hybrid_candidate(candidate, pairs, *development_sources)
        for candidate in configuration.candidates
    ]
    eligible = [
        result for result in development_results if _passes(result, configuration.selection_policy)
    ]
    if not eligible:
        selected = max(
            development_results,
            key=lambda item: (cast(float, item["macro_f1"]), cast(float, item["accuracy"])),
        )
        selected_passed = False
    else:
        selected = max(
            eligible,
            key=lambda item: (cast(float, item["macro_f1"]), cast(float, item["accuracy"])),
        )
        selected_passed = True
    candidate_by_id = {item.candidate_id: item for item in configuration.candidates}
    selected_id = cast(str, selected["candidate_id"])
    validation_result: dict[str, object] | None = None
    validation_passed = True
    if configuration.validation_evaluation_allowed:
        validation_l3 = load_json_report(repository_root / configuration.validation_l3_report_path)
        validation_sources = partition_sources(offline, validation_l3, "validation")
        validation_result = evaluate_hybrid_candidate(
            candidate_by_id[selected_id],
            pairs,
            *validation_sources,
        )
        validation_passed = _passes(validation_result, configuration.selection_policy)
    return {
        "schema_version": "1.0.0",
        "report_id": configuration.experiment_id,
        "generated_at": generated_at.isoformat(),
        "llm_provider_calls_made": False,
        "stage7_v1_test_accessed": False,
        "development_candidates": development_results,
        "selected_candidate_id": selected_id,
        "development_selection_passed": selected_passed,
        "validation": validation_result,
        "quality_gate": {"passed": selected_passed and validation_passed},
        "traceability": {
            "configuration_sha256": file_sha256(repository_root / configuration_path),
            "reviewed_pairs_sha256": file_sha256(
                repository_root / configuration.reviewed_pairs_path
            ),
            "offline_report_sha256": file_sha256(
                repository_root / configuration.offline_report_path
            ),
            "development_l3_report_sha256": file_sha256(
                repository_root / configuration.development_l3_report_path
            ),
            "additional_development_l3_report_sha256": [
                file_sha256(repository_root / path)
                for path in configuration.additional_development_l3_report_paths
            ],
            "validation_l3_report_sha256": (
                file_sha256(repository_root / configuration.validation_l3_report_path)
                if configuration.validation_evaluation_allowed
                else None
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
    parser.add_argument("--generated-at", default="2026-08-08T21:00:00+07:00")
    parser.add_argument("--configuration-path", default=str(CONFIG_PATH))
    parser.add_argument("--output", default=str(REPORT_PATH))
    arguments = parser.parse_args()
    report = build_report(
        REPOSITORY_ROOT,
        _timestamp(cast(str, arguments.generated_at)),
        Path(cast(str, arguments.configuration_path)),
    )
    output = REPOSITORY_ROOT / Path(cast(str, arguments.output))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
