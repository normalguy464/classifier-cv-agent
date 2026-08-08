from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import cast

import pytest

from backend.app.contracts import ClassificationDecision
from evaluation.experiments.run_stage6_freeze_proposal import (
    PROPOSAL_REPORT_PATH,
    AutomaticPassGate,
    apply_automatic_pass_gate,
    load_freeze_proposal,
    run,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
GENERATED_AT = datetime.fromisoformat("2026-07-26T23:55:00+07:00")


def _gate() -> AutomaticPassGate:
    return AutomaticPassGate(
        l3_minimum_score=Decimal("95"),
        fallback_decision=ClassificationDecision.NEEDS_REVIEW,
        reason_identifier="l3-below-automatic-pass-minimum",
    )


def test_freeze_proposal_is_versioned_linked_and_not_frozen() -> None:
    proposal = load_freeze_proposal(REPOSITORY_ROOT)

    assert proposal.proposal_status == "provisional_pending_human_approval"
    assert proposal.live_model_strategy.model_identifier == "gemini-3.5-flash-lite"
    assert proposal.live_model_strategy.prompt_version == "l3-evidence-rubric-v3"
    assert proposal.candidate.thresholds.pass_minimum == Decimal("75")
    assert proposal.candidate.thresholds.waitlist_minimum == Decimal("60")
    assert proposal.candidate.automatic_pass_gate.l3_minimum_score == Decimal("95")
    assert (
        proposal.candidate.aggregation.l1_deterministic_rules
        + proposal.candidate.aggregation.l2_section_semantic_matching
        + proposal.candidate.aggregation.l3_evidence_grounded_reasoning
        == 1
    )


def test_automatic_pass_gate_covers_boundary_missing_and_non_pass_inputs() -> None:
    gate = _gate()

    assert apply_automatic_pass_gate(
        ClassificationDecision.PASS,
        Decimal("95"),
        gate,
    ) == (ClassificationDecision.PASS, None)
    assert apply_automatic_pass_gate(
        ClassificationDecision.PASS,
        Decimal("94.99"),
        gate,
    ) == (
        ClassificationDecision.NEEDS_REVIEW,
        "l3-below-automatic-pass-minimum",
    )
    assert apply_automatic_pass_gate(
        ClassificationDecision.PASS,
        None,
        gate,
    ) == (
        ClassificationDecision.NEEDS_REVIEW,
        "l3-below-automatic-pass-minimum",
    )
    assert apply_automatic_pass_gate(
        ClassificationDecision.WAITLIST,
        Decimal("20"),
        gate,
    ) == (ClassificationDecision.WAITLIST, None)


def test_freeze_proposal_meets_selection_policy_without_frozen_data() -> None:
    report = run(REPOSITORY_ROOT, GENERATED_AT)
    safety = cast(dict[str, object], report["safety"])
    recommendation = cast(dict[str, object], report["recommendation"])
    changed_cases = cast(list[dict[str, object]], report["changed_cases"])
    manifest = json.loads(
        (REPOSITORY_ROOT / "data" / "splits" / "stage6_split_manifest_v1.json").read_text(
            encoding="utf-8"
        )
    )
    frozen_ids = cast(list[str], manifest["frozen_test"]["cv_profile_ids"])
    serialized = json.dumps(report)

    assert safety["needs_review_recall"] == 1
    assert safety["false_reject_count"] == 0
    assert safety["unsafe_pass_count"] == 0
    assert safety["review_rate"] == 0.8
    assert recommendation["candidate_id"] == "live-l3-automatic-pass-gate-v1"
    assert recommendation["eligible_for_human_approval"] is True
    assert recommendation["configuration_frozen"] is False
    assert recommendation["gate_6_complete"] is False
    assert {item["cv_profile_id"] for item in changed_cases} == {
        "cv-s4-be-005",
        "cv-s4-be-014",
        "cv-s4-da-004",
        "cv-s4-da-014",
    }
    assert all(cv_profile_id not in serialized for cv_profile_id in frozen_ids)


def test_committed_freeze_proposal_report_is_reproducible() -> None:
    committed = json.loads((REPOSITORY_ROOT / PROPOSAL_REPORT_PATH).read_text(encoding="utf-8"))
    generated_at = datetime.fromisoformat(cast(str, committed["generated_at"]))

    assert committed == run(REPOSITORY_ROOT, generated_at)


def test_freeze_proposal_rejects_naive_generation_time() -> None:
    with pytest.raises(ValueError, match="timezone"):
        run(REPOSITORY_ROOT, datetime(2026, 7, 26, 23, 55))
