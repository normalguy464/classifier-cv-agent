from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from backend.app.agents.classifier.scoring.l1 import score_l1
from backend.app.contracts import (
    CVProfile,
    Evidence,
    EvidenceLocation,
    EvidenceSection,
    EvidenceSourceType,
    EvidenceStatus,
    LevelScoreStatus,
    RubricCriterion,
    ScoringRubric,
)
from backend.app.domain import (
    L1Policy,
    MatchMode,
    RequirementRule,
    ScoringInputError,
    ScoringLevel,
)


def make_evidence(
    evidence_id: str,
    text: str,
    section: EvidenceSection = EvidenceSection.SKILLS,
) -> Evidence:
    return Evidence(
        evidence_id=evidence_id,
        source_type=EvidenceSourceType.MANUAL,
        section=section,
        text=text,
        location=EvidenceLocation(source_record_id=f"record-{evidence_id}"),
    )


def make_cv(*evidence: Evidence) -> CVProfile:
    return CVProfile(
        cv_profile_id="cv-l1-test",
        candidate_reference="candidate-l1-test",
        evidence=evidence,
    )


def make_rubric(*requirement_ids: str) -> ScoringRubric:
    return ScoringRubric(
        rubric_id="rubric-l1-test",
        rubric_version="1.0.0",
        job_profile_id="job-l1-test",
        criteria=(
            RubricCriterion(
                criterion_id="mandatory-requirements",
                title="Mandatory requirements",
                description="Critical requirements.",
                weight=Decimal("100"),
            ),
        ),
        critical_requirement_ids=requirement_ids,
    )


def make_rule(
    requirement_id: str,
    positive_terms: tuple[str, ...],
    explicit_negative_terms: tuple[str, ...],
    match_mode: MatchMode = MatchMode.ANY,
) -> RequirementRule:
    return RequirementRule(
        requirement_id=requirement_id,
        evidence_sections=(EvidenceSection.SKILLS, EvidenceSection.PROJECTS),
        positive_terms=positive_terms,
        explicit_negative_terms=explicit_negative_terms,
        match_mode=match_mode,
    )


def test_l1_scores_satisfied_unsatisfied_and_missing_requirements() -> None:
    cv_profile = make_cv(
        make_evidence("ev-python", "Built services with Python."),
        make_evidence("ev-sql-gap", "I have never used SQL."),
    )
    rubric = make_rubric("req-python", "req-sql", "req-git")
    policy = L1Policy(
        job_profile_id="job-l1-test",
        rules=(
            make_rule("req-python", ("Python",), ("never used Python",)),
            make_rule("req-sql", ("SQL",), ("never used SQL",)),
            make_rule("req-git", ("Git",), ("never used Git",)),
        ),
    )

    result = score_l1(cv_profile, rubric, policy)
    statuses = {
        item.requirement_id: item.evidence_status for item in result.requirement_assessments
    }

    assert result.level is ScoringLevel.L1
    assert result.status is LevelScoreStatus.AVAILABLE
    assert result.score == Decimal("33.33")
    assert statuses == {
        "req-python": EvidenceStatus.SATISFIED,
        "req-sql": EvidenceStatus.UNSATISFIED,
        "req-git": EvidenceStatus.MISSING,
    }


def test_l1_negative_phrase_takes_precedence_inside_the_same_evidence() -> None:
    cv_profile = make_cv(make_evidence("ev-python-gap", "Chưa từng sử dụng Python."))
    rubric = make_rubric("req-python")
    policy = L1Policy(
        job_profile_id="job-l1-test",
        rules=(
            make_rule(
                "req-python",
                ("Python",),
                ("Chưa từng sử dụng Python",),
            ),
        ),
    )

    assessment = score_l1(cv_profile, rubric, policy).requirement_assessments[0]

    assert assessment.evidence_status is EvidenceStatus.UNSATISFIED
    assert assessment.evidence_ids == ("ev-python-gap",)


def test_l1_separate_positive_and_negative_evidence_is_conflicting() -> None:
    cv_profile = make_cv(
        make_evidence("ev-python-positive", "Python backend project."),
        make_evidence("ev-python-negative", "I have never used Python."),
    )
    rubric = make_rubric("req-python")
    policy = L1Policy(
        job_profile_id="job-l1-test",
        rules=(make_rule("req-python", ("Python",), ("never used Python",)),),
    )

    assessment = score_l1(cv_profile, rubric, policy).requirement_assessments[0]

    assert assessment.evidence_status is EvidenceStatus.CONFLICTING
    assert assessment.evidence_ids == ("ev-python-negative", "ev-python-positive")


def test_l1_all_match_mode_requires_every_positive_term() -> None:
    rubric = make_rubric("req-api")
    policy = L1Policy(
        job_profile_id="job-l1-test",
        rules=(
            make_rule(
                "req-api",
                ("Python", "FastAPI"),
                ("no backend experience",),
                MatchMode.ALL,
            ),
        ),
    )
    partial = make_cv(make_evidence("ev-python-only", "Python project."))
    complete = make_cv(
        make_evidence("ev-python", "Python project."),
        make_evidence("ev-fastapi", "FastAPI endpoint.", EvidenceSection.PROJECTS),
    )

    partial_result = score_l1(partial, rubric, policy)
    complete_result = score_l1(complete, rubric, policy)

    assert partial_result.requirement_assessments[0].evidence_status is EvidenceStatus.MISSING
    assert partial_result.score == Decimal("0.00")
    assert complete_result.requirement_assessments[0].evidence_status is EvidenceStatus.SATISFIED
    assert complete_result.score == Decimal("100.00")


def test_l1_only_reads_configured_evidence_sections() -> None:
    cv_profile = make_cv(make_evidence("ev-python-education", "Python", EvidenceSection.EDUCATION))
    rubric = make_rubric("req-python")
    policy = L1Policy(
        job_profile_id="job-l1-test",
        rules=(make_rule("req-python", ("Python",), ("never used Python",)),),
    )

    assessment = score_l1(cv_profile, rubric, policy).requirement_assessments[0]

    assert assessment.evidence_status is EvidenceStatus.MISSING


def test_l1_positive_sections_exclude_context_only_mentions() -> None:
    rubric = make_rubric("req-python")
    rule = RequirementRule(
        requirement_id="req-python",
        evidence_sections=(EvidenceSection.PROJECTS, EvidenceSection.OTHER),
        positive_evidence_sections=(EvidenceSection.PROJECTS,),
        positive_terms=("Python",),
        explicit_negative_terms=("chưa từng dùng Python",),
    )
    policy = L1Policy(job_profile_id="job-l1-test", rules=(rule,))
    context_only = make_cv(
        make_evidence(
            "ev-context",
            "Đã đọc source Python nhưng không xác định phần mã tự thực hiện.",
            EvidenceSection.OTHER,
        )
    )
    applied = make_cv(
        make_evidence(
            "ev-applied",
            "Viết service Python xử lý dữ liệu đầu vào.",
            EvidenceSection.PROJECTS,
        )
    )

    context_result = score_l1(context_only, rubric, policy)
    applied_result = score_l1(applied, rubric, policy)

    assert context_result.requirement_assessments[0].evidence_status is EvidenceStatus.MISSING
    assert applied_result.requirement_assessments[0].evidence_status is EvidenceStatus.SATISFIED


def test_l1_positive_term_groups_support_alternative_compound_signals() -> None:
    rubric = make_rubric("req-delivery")
    rule = RequirementRule(
        requirement_id="req-delivery",
        evidence_sections=(EvidenceSection.SKILLS, EvidenceSection.PROJECTS),
        positive_terms=("Git", "Docker", "pull request", "Dockerfile"),
        explicit_negative_terms=("không có Git hoặc Docker",),
        positive_term_groups=(("Git", "Docker"), ("pull request", "Dockerfile")),
    )
    policy = L1Policy(job_profile_id="job-l1-test", rules=(rule,))
    partial = make_cv(make_evidence("ev-git", "Dùng Git cho source."))
    alternative = make_cv(
        make_evidence(
            "ev-delivery",
            "Mở pull request và viết Dockerfile để bàn giao.",
            EvidenceSection.PROJECTS,
        )
    )

    partial_result = score_l1(partial, rubric, policy)
    alternative_result = score_l1(alternative, rubric, policy)

    assert partial_result.requirement_assessments[0].evidence_status is EvidenceStatus.MISSING
    assert alternative_result.requirement_assessments[0].evidence_status is EvidenceStatus.SATISFIED


def test_l1_rejects_policy_with_missing_critical_rule_or_wrong_job() -> None:
    cv_profile = make_cv(make_evidence("ev-python", "Python"))
    rubric = make_rubric("req-python", "req-sql")
    incomplete_policy = L1Policy(
        job_profile_id="job-l1-test",
        rules=(make_rule("req-python", ("Python",), ()),),
    )
    wrong_job_policy = L1Policy(
        job_profile_id="other-job",
        rules=(
            make_rule("req-python", ("Python",), ()),
            make_rule("req-sql", ("SQL",), ()),
        ),
    )

    with pytest.raises(ScoringInputError, match="missing critical"):
        score_l1(cv_profile, rubric, incomplete_policy)
    with pytest.raises(ScoringInputError, match="job_profile_id"):
        score_l1(cv_profile, rubric, wrong_job_policy)


@pytest.mark.parametrize(
    "rule",
    [
        {
            "requirement_id": "req-python",
            "evidence_sections": (),
            "positive_terms": ("Python",),
            "explicit_negative_terms": (),
        },
        {
            "requirement_id": "req-python",
            "evidence_sections": (EvidenceSection.SKILLS,),
            "positive_terms": (),
            "explicit_negative_terms": (),
        },
        {
            "requirement_id": "req-python",
            "evidence_sections": (EvidenceSection.SKILLS,),
            "positive_terms": ("Python", "python"),
            "explicit_negative_terms": (),
        },
        {
            "requirement_id": "req-python",
            "evidence_sections": (EvidenceSection.SKILLS,),
            "positive_terms": ("Python",),
            "explicit_negative_terms": ("",),
        },
        {
            "requirement_id": "req-python",
            "evidence_sections": (EvidenceSection.SKILLS,),
            "positive_terms": ("Python",),
            "explicit_negative_terms": (),
            "positive_term_groups": (("FastAPI",),),
        },
        {
            "requirement_id": "req-python",
            "evidence_sections": (EvidenceSection.SKILLS,),
            "positive_terms": ("Python",),
            "explicit_negative_terms": (),
            "positive_evidence_sections": (EvidenceSection.PROJECTS,),
        },
    ],
)
def test_l1_rejects_malformed_requirement_rules(rule: dict[str, object]) -> None:
    with pytest.raises(ScoringInputError):
        RequirementRule(**rule)


def test_l1_policy_is_immutable_and_rejects_duplicate_rules() -> None:
    rule = make_rule("req-python", ("Python",), ())
    policy = L1Policy(job_profile_id="job-l1-test", rules=(rule,))

    with pytest.raises(FrozenInstanceError):
        policy.job_profile_id = "changed-job"
    with pytest.raises(ScoringInputError, match="unique"):
        L1Policy(job_profile_id="job-l1-test", rules=(rule, rule))
