from __future__ import annotations

from backend.app.agents.classifier.scoring import score_l1
from backend.app.contracts import (
    CVProfile,
    ClassificationDecision,
    DecisionThresholds,
    EvidenceStatus,
    ScoringRubric,
)
from backend.app.domain import L1Policy
from evaluation.baselines.models import BaselinePrediction, threshold_decision


class KeywordRuleBaseline:
    def __init__(self, policy: L1Policy) -> None:
        self._policy = policy

    def predict(
        self,
        cv_profile: CVProfile,
        rubric: ScoringRubric,
        thresholds: DecisionThresholds,
    ) -> BaselinePrediction:
        assessment = score_l1(cv_profile, rubric, self._policy)
        if assessment.score is None:
            raise ValueError("L1 baseline requires an available score")
        statuses = {item.evidence_status for item in assessment.requirement_assessments}
        decision = threshold_decision(assessment.score, thresholds)
        if EvidenceStatus.MISSING in statuses or EvidenceStatus.CONFLICTING in statuses:
            decision = ClassificationDecision.NEEDS_REVIEW
        if EvidenceStatus.UNSATISFIED in statuses:
            if assessment.score < thresholds.waitlist_minimum:
                decision = ClassificationDecision.REJECT
            else:
                decision = ClassificationDecision.NEEDS_REVIEW
        return BaselinePrediction(
            score=assessment.score,
            decision=decision,
            baseline_identifier="keyword-rule-v1",
        )
