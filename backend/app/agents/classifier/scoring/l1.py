from __future__ import annotations

import re
import unicodedata
from decimal import Decimal, ROUND_HALF_UP
from typing import Final

from backend.app.contracts import (
    CVProfile,
    Evidence,
    EvidenceStatus,
    LevelScoreStatus,
    ScoringRubric,
)
from backend.app.domain import (
    L1Policy,
    LevelAssessment,
    MatchMode,
    RequirementAssessment,
    RequirementRule,
    ScoringInputError,
    ScoringLevel,
)

SCORE_QUANTUM: Final[Decimal] = Decimal("0.01")


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(normalized.split())


def _contains_term(text: str, term: str) -> bool:
    normalized_term = _normalize_text(term)
    return re.search(rf"(?<!\w){re.escape(normalized_term)}(?!\w)", text) is not None


def _matched_terms(text: str, terms: tuple[str, ...]) -> set[str]:
    return {term for term in terms if _contains_term(text, term)}


def _eligible_evidence(cv_profile: CVProfile, rule: RequirementRule) -> tuple[Evidence, ...]:
    allowed_sections = set(rule.evidence_sections)
    return tuple(item for item in cv_profile.evidence if item.section in allowed_sections)


def _assess_requirement(cv_profile: CVProfile, rule: RequirementRule) -> RequirementAssessment:
    evidence = _eligible_evidence(cv_profile, rule)
    positive_sections = set(rule.effective_positive_evidence_sections)
    positive_evidence_ids: set[str] = set()
    negative_evidence_ids: set[str] = set()
    all_positive_matches: set[str] = set()

    for item in evidence:
        normalized_text = _normalize_text(item.text)
        negative_matches = _matched_terms(normalized_text, rule.explicit_negative_terms)
        if negative_matches:
            negative_evidence_ids.add(item.evidence_id)
            continue
        positive_matches: set[str] = (
            _matched_terms(normalized_text, rule.positive_terms)
            if item.section in positive_sections
            else set()
        )
        if positive_matches:
            positive_evidence_ids.add(item.evidence_id)
            all_positive_matches.update(positive_matches)

    positive_terms = {_normalize_text(term) for term in rule.positive_terms}
    normalized_matches = {_normalize_text(term) for term in all_positive_matches}
    if rule.positive_term_groups:
        normalized_groups = tuple(
            {_normalize_text(term) for term in group} for group in rule.positive_term_groups
        )
        has_positive = any(group.issubset(normalized_matches) for group in normalized_groups)
    else:
        has_positive = bool(positive_evidence_ids)
    if not rule.positive_term_groups and rule.match_mode is MatchMode.ALL:
        has_positive = normalized_matches == positive_terms
    has_negative = bool(negative_evidence_ids)

    if has_positive and has_negative:
        evidence_ids = tuple(sorted(positive_evidence_ids | negative_evidence_ids))
        return RequirementAssessment(
            requirement_id=rule.requirement_id,
            evidence_status=EvidenceStatus.CONFLICTING,
            evidence_ids=evidence_ids,
            rationale="Positive and explicit negative signals appear in separate CV evidence.",
        )
    if has_negative:
        return RequirementAssessment(
            requirement_id=rule.requirement_id,
            evidence_status=EvidenceStatus.UNSATISFIED,
            evidence_ids=tuple(sorted(negative_evidence_ids)),
            rationale="The CV contains an explicit negative signal for this requirement.",
        )
    if has_positive:
        return RequirementAssessment(
            requirement_id=rule.requirement_id,
            evidence_status=EvidenceStatus.SATISFIED,
            evidence_ids=tuple(sorted(positive_evidence_ids)),
            rationale="The CV contains the configured positive signals for this requirement.",
        )
    return RequirementAssessment(
        requirement_id=rule.requirement_id,
        evidence_status=EvidenceStatus.MISSING,
        evidence_ids=(),
        rationale="The CV contains neither a configured positive nor explicit negative signal.",
    )


def _validate_policy(rubric: ScoringRubric, policy: L1Policy) -> dict[str, RequirementRule]:
    if policy.job_profile_id != rubric.job_profile_id:
        raise ScoringInputError("L1 policy job_profile_id must match the rubric")
    rules_by_id = {rule.requirement_id: rule for rule in policy.rules}
    missing_rule_ids = set(rubric.critical_requirement_ids).difference(rules_by_id)
    if missing_rule_ids:
        raise ScoringInputError(
            f"L1 policy is missing critical requirement rules: {sorted(missing_rule_ids)}"
        )
    return rules_by_id


def score_l1(
    cv_profile: CVProfile,
    rubric: ScoringRubric,
    policy: L1Policy,
) -> LevelAssessment:
    rules_by_id = _validate_policy(rubric, policy)
    assessments = tuple(
        _assess_requirement(cv_profile, rules_by_id[requirement_id])
        for requirement_id in rubric.critical_requirement_ids
    )
    satisfied_count = sum(
        assessment.evidence_status is EvidenceStatus.SATISFIED for assessment in assessments
    )
    score = (
        Decimal(satisfied_count) / Decimal(len(rubric.critical_requirement_ids)) * Decimal("100")
    ).quantize(SCORE_QUANTUM, rounding=ROUND_HALF_UP)
    return LevelAssessment(
        level=ScoringLevel.L1,
        status=LevelScoreStatus.AVAILABLE,
        score=score,
        requirement_assessments=assessments,
    )
