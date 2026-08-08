from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from backend.app.contracts import ClassificationDecision, DecisionThresholds


@dataclass(frozen=True, slots=True)
class BaselinePrediction:
    score: Decimal
    decision: ClassificationDecision
    baseline_identifier: str


def threshold_decision(
    score: Decimal,
    thresholds: DecisionThresholds,
) -> ClassificationDecision:
    if score >= thresholds.pass_minimum:
        return ClassificationDecision.PASS
    if score >= thresholds.waitlist_minimum:
        return ClassificationDecision.WAITLIST
    return ClassificationDecision.NEEDS_REVIEW
