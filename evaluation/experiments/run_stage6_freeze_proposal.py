from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Annotated, Literal, Self, cast

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.app.contracts import (
    AggregationWeights,
    ClassificationDecision,
    DecisionThresholds,
)
from evaluation.experiments.stage6_config import (
    Stage6L2Matching,
    Stage6SelectionPolicy,
)
from evaluation.metrics import ClassificationMetrics, calculate_metrics

PROPOSAL_CONFIG_PATH = Path("evaluation/configs/stage6_freeze_proposal_v1.yaml")
PROPOSAL_REPORT_PATH = Path("evaluation/reports/stage6_freeze_proposal_v1.json")


class FreezeProposalError(ValueError):
    pass


class FreezeProposalModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class FreezeSourceReport(FreezeProposalModel):
    path: str = Field(min_length=1, max_length=512)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    report_id: Literal["stage6-live-llm-validation-v1"]


class FreezeLiveModelStrategy(FreezeProposalModel):
    experiment_id: Literal["stage6-live-llm-validation-v1"]
    experiment_version: Literal["1.3.0"]
    provider_identifier: Literal["google_ai_studio"]
    model_identifier: Literal["gemini-3.5-flash-lite"]
    prompt_version: Literal["l3-evidence-rubric-v3"]


class AutomaticPassGate(FreezeProposalModel):
    l3_minimum_score: Annotated[
        Decimal,
        Field(ge=Decimal("0"), le=Decimal("100")),
    ]
    fallback_decision: Literal[ClassificationDecision.NEEDS_REVIEW]
    reason_identifier: Literal["l3-below-automatic-pass-minimum"]


class FreezeCandidate(FreezeProposalModel):
    candidate_id: Literal["live-l3-automatic-pass-gate-v1"]
    description: str = Field(min_length=1, max_length=1000)
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
    automatic_pass_gate: AutomaticPassGate

    @model_validator(mode="after")
    def validate_boundaries(self) -> Self:
        if self.thresholds.waitlist_minimum < self.boundary_offset_points:
            raise ValueError("waitlist threshold cannot produce a negative boundary")
        if self.thresholds.pass_minimum + self.boundary_offset_points > Decimal("100"):
            raise ValueError("pass threshold cannot produce a boundary above 100")
        return self


class Stage6FreezeProposal(FreezeProposalModel):
    schema_version: Literal["1.0.0"]
    proposal_id: Literal["stage6-live-freeze-proposal-v1"]
    proposal_version: Literal["1.0.0"]
    proposal_status: Literal["provisional_pending_human_approval"]
    validation_partition_id: Literal["stage6-validation-v1"]
    source_report: FreezeSourceReport
    live_model_strategy: FreezeLiveModelStrategy
    source_candidate_id: Literal["approved-current-v1"]
    candidate: FreezeCandidate
    selection_policy: Stage6SelectionPolicy


def _timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError("generated_at must be an ISO 8601 timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("generated_at must include a timezone")
    return parsed


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def load_freeze_proposal(repository_root: Path) -> Stage6FreezeProposal:
    path = repository_root / PROPOSAL_CONFIG_PATH
    value = cast(object, yaml.safe_load(path.read_text(encoding="utf-8")))
    if not isinstance(value, dict):
        raise FreezeProposalError("Stage 6 freeze proposal must be a mapping")
    proposal = Stage6FreezeProposal.model_validate(cast(dict[str, object], value))
    source_path = repository_root / proposal.source_report.path
    if _sha256(source_path) != proposal.source_report.sha256:
        raise FreezeProposalError("Stage 6 live source report changed after proposal creation")
    return proposal


def apply_automatic_pass_gate(
    predicted: ClassificationDecision,
    l3_score: Decimal | None,
    gate: AutomaticPassGate,
) -> tuple[ClassificationDecision, str | None]:
    if predicted is not ClassificationDecision.PASS:
        return predicted, None
    if l3_score is not None and l3_score >= gate.l3_minimum_score:
        return predicted, None
    return gate.fallback_decision, gate.reason_identifier


def _mapping(value: object, field_name: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise FreezeProposalError(f"{field_name} must be an object")
    return cast(dict[str, object], value)


def _items(value: object, field_name: str) -> list[object]:
    if not isinstance(value, list):
        raise FreezeProposalError(f"{field_name} must be a list")
    return cast(list[object], value)


def _text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise FreezeProposalError(f"{field_name} must contain text")
    return value


def _decimal(value: object, field_name: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (Decimal, float, int, str)):
        raise FreezeProposalError(f"{field_name} must be numeric")
    result = Decimal(str(value))
    if not result.is_finite() or result < 0 or result > 100:
        raise FreezeProposalError(f"{field_name} must be between 0 and 100")
    return result


def _metrics_payload(metrics: ClassificationMetrics) -> dict[str, object]:
    return {
        "sample_count": metrics.sample_count,
        "accuracy": metrics.accuracy,
        "macro_f1": metrics.macro_f1,
        "cohen_kappa": metrics.cohen_kappa,
        "labels": {label: asdict(label_metrics) for label, label_metrics in metrics.labels.items()},
        "confusion_matrix": [list(row) for row in metrics.confusion_matrix],
    }


def _source_candidate(
    report: dict[str, object],
    source_candidate_id: str,
) -> dict[str, object]:
    for value in _items(report.get("candidate_results"), "candidate_results"):
        result = _mapping(value, "candidate result")
        candidate = _mapping(result.get("candidate"), "candidate")
        if candidate.get("candidate_id") == source_candidate_id:
            return result
    raise FreezeProposalError("source candidate is missing from the live report")


def _validate_source_links(
    report: dict[str, object],
    proposal: Stage6FreezeProposal,
) -> None:
    if report.get("report_id") != proposal.source_report.report_id:
        raise FreezeProposalError("source report identifier does not match the proposal")
    strategy = _mapping(report.get("execution_strategy"), "execution_strategy")
    experiment = _mapping(report.get("live_experiment"), "live_experiment")
    model = proposal.live_model_strategy
    if (
        experiment.get("experiment_id") != model.experiment_id
        or experiment.get("experiment_version") != model.experiment_version
        or strategy.get("l3_provider_identifier") != model.provider_identifier
        or strategy.get("l3_model_identifier") != model.model_identifier
        or strategy.get("prompt_version") != model.prompt_version
    ):
        raise FreezeProposalError("source live model strategy does not match the proposal")
    split = _mapping(report.get("split_traceability"), "split_traceability")
    if (
        split.get("validation_partition_id") != proposal.validation_partition_id
        or split.get("frozen_test_evaluated") is not False
        or split.get("frozen_test_results_generated") is not False
    ):
        raise FreezeProposalError("source report violates the Stage 6 validation-only policy")


def run(
    repository_root: Path,
    generated_at: datetime,
) -> dict[str, object]:
    if generated_at.tzinfo is None or generated_at.utcoffset() is None:
        raise ValueError("generated_at must include a timezone")
    proposal = load_freeze_proposal(repository_root)
    source_path = repository_root / proposal.source_report.path
    report_value = cast(object, json.loads(source_path.read_text(encoding="utf-8")))
    if not isinstance(report_value, dict):
        raise FreezeProposalError("source live report must be a JSON object")
    source_report = cast(dict[str, object], report_value)
    _validate_source_links(source_report, proposal)
    source_candidate = _source_candidate(source_report, proposal.source_candidate_id)
    cases = _items(source_candidate.get("cases"), "source candidate cases")
    expected: list[ClassificationDecision] = []
    predicted: list[ClassificationDecision] = []
    changed_cases: list[dict[str, object]] = []
    output_cases: list[dict[str, object]] = []
    for value in cases:
        case = _mapping(value, "source candidate case")
        cv_profile_id = _text(case.get("cv_profile_id"), "cv_profile_id")
        expected_label = ClassificationDecision(_text(case.get("expected_label"), "expected_label"))
        before = ClassificationDecision(_text(case.get("predicted_label"), "predicted_label"))
        level_scores = _mapping(case.get("level_scores"), "level_scores")
        l3_value = level_scores.get("l3")
        l3_score = _decimal(l3_value, "l3 score") if l3_value is not None else None
        after, added_reason = apply_automatic_pass_gate(
            before,
            l3_score,
            proposal.candidate.automatic_pass_gate,
        )
        expected.append(expected_label)
        predicted.append(after)
        output_case: dict[str, object] = {
            "cv_profile_id": cv_profile_id,
            "expected_label": expected_label.value,
            "source_predicted_label": before.value,
            "proposed_predicted_label": after.value,
            "l3_score": float(l3_score) if l3_score is not None else None,
            "added_review_reason": added_reason,
        }
        output_cases.append(output_case)
        if after is not before:
            changed_cases.append(output_case)
    metrics = calculate_metrics(tuple(expected), tuple(predicted))
    needs_review_indexes = tuple(
        index
        for index, label in enumerate(expected)
        if label is ClassificationDecision.NEEDS_REVIEW
    )
    needs_review_recall = sum(
        predicted[index] is ClassificationDecision.NEEDS_REVIEW for index in needs_review_indexes
    ) / len(needs_review_indexes)
    false_reject_ids = tuple(
        cast(str, output_cases[index]["cv_profile_id"])
        for index, (expected_label, predicted_label) in enumerate(
            zip(expected, predicted, strict=True)
        )
        if predicted_label is ClassificationDecision.REJECT
        and expected_label is not ClassificationDecision.REJECT
    )
    unsafe_pass_ids = tuple(
        cast(str, output_cases[index]["cv_profile_id"])
        for index, (expected_label, predicted_label) in enumerate(
            zip(expected, predicted, strict=True)
        )
        if predicted_label is ClassificationDecision.PASS
        and expected_label
        in {
            ClassificationDecision.REJECT,
            ClassificationDecision.NEEDS_REVIEW,
        }
    )
    review_rate = sum(label is ClassificationDecision.NEEDS_REVIEW for label in predicted) / len(
        predicted
    )
    policy = proposal.selection_policy
    eligible = (
        Decimal(str(needs_review_recall)) >= policy.required_needs_review_recall
        and len(false_reject_ids) <= policy.required_false_reject_count
        and len(unsafe_pass_ids) <= policy.required_unsafe_pass_count
        and Decimal(str(review_rate)) <= policy.maximum_review_rate
    )
    return {
        "report_schema_version": "1.0.0",
        "report_id": "stage6-freeze-proposal-v1",
        "report_scope": "stage6-validation-only-live-l3-routing-proposal",
        "is_final_performance": False,
        "generated_at": generated_at.isoformat(),
        "source_traceability": {
            "proposal_configuration_file": PROPOSAL_CONFIG_PATH.as_posix(),
            "proposal_configuration_sha256": _sha256(repository_root / PROPOSAL_CONFIG_PATH),
            "live_report_file": proposal.source_report.path,
            "live_report_sha256": proposal.source_report.sha256,
            "validation_partition_id": proposal.validation_partition_id,
            "frozen_test_evaluated": False,
            "frozen_test_results_generated": False,
        },
        "model_strategy": proposal.live_model_strategy.model_dump(mode="json"),
        "candidate": proposal.candidate.model_dump(mode="json"),
        "selection_policy": policy.model_dump(mode="json"),
        "source_candidate_metrics": source_candidate.get("metrics"),
        "proposed_candidate_metrics": _metrics_payload(metrics),
        "safety": {
            "needs_review_recall": needs_review_recall,
            "false_reject_count": len(false_reject_ids),
            "false_reject_case_ids": list(false_reject_ids),
            "unsafe_pass_count": len(unsafe_pass_ids),
            "unsafe_pass_case_ids": list(unsafe_pass_ids),
            "review_rate": review_rate,
        },
        "changed_case_count": len(changed_cases),
        "changed_cases": changed_cases,
        "cases": output_cases,
        "recommendation": {
            "candidate_id": proposal.candidate.candidate_id if eligible else None,
            "eligible_for_human_approval": eligible,
            "requires_human_approval": True,
            "configuration_frozen": False,
            "gate_6_complete": False,
        },
    }


def write_report(
    repository_root: Path,
    generated_at: datetime,
    output_path: Path = PROPOSAL_REPORT_PATH,
) -> Path:
    report = run(repository_root, generated_at)
    absolute_path = repository_root / output_path
    absolute_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return absolute_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--generated-at",
        default=datetime.now().astimezone().isoformat(timespec="seconds"),
    )
    parser.add_argument("--output", default=PROPOSAL_REPORT_PATH.as_posix())
    arguments = parser.parse_args()
    repository_root = Path(__file__).resolve().parents[2]
    write_report(
        repository_root,
        _timestamp(cast(str, arguments.generated_at)),
        Path(cast(str, arguments.output)),
    )


if __name__ == "__main__":
    main()
