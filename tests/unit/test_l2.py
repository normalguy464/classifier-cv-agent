from decimal import Decimal

import pytest

from backend.app.agents.classifier.scoring.l2 import score_l2
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
from backend.app.domain import L2CriterionPolicy, L2Policy, ScoringInputError, ScoringLevel


def make_evidence(evidence_id: str, text: str, section: EvidenceSection) -> Evidence:
    return Evidence(
        evidence_id=evidence_id,
        source_type=EvidenceSourceType.MANUAL,
        section=section,
        text=text,
        location=EvidenceLocation(source_record_id=f"record-{evidence_id}"),
    )


def make_cv() -> CVProfile:
    return CVProfile(
        cv_profile_id="cv-l2-test",
        candidate_reference="candidate-l2-test",
        evidence=(
            make_evidence("ev-skill", "Python API", EvidenceSection.SKILLS),
            make_evidence("ev-project", "Sales dashboard", EvidenceSection.PROJECTS),
        ),
    )


def make_rubric() -> ScoringRubric:
    return ScoringRubric(
        rubric_id="rubric-l2-test",
        rubric_version="1.0.0",
        job_profile_id="job-l2-test",
        criteria=(
            RubricCriterion(
                criterion_id="technical-skill",
                title="Technical skill",
                description="Technical evidence.",
                weight=Decimal("60"),
            ),
            RubricCriterion(
                criterion_id="project-impact",
                title="Project impact",
                description="Project evidence.",
                weight=Decimal("40"),
            ),
        ),
        critical_requirement_ids=("req-python",),
    )


def make_policy(top_k: int = 1) -> L2Policy:
    return L2Policy(
        job_profile_id="job-l2-test",
        criteria=(
            L2CriterionPolicy(
                criterion_id="technical-skill",
                query_text="query technical",
                evidence_sections=(EvidenceSection.SKILLS,),
                similarity_floor=Decimal("0"),
                similarity_ceiling=Decimal("1"),
                top_k=top_k,
            ),
            L2CriterionPolicy(
                criterion_id="project-impact",
                query_text="query project",
                evidence_sections=(EvidenceSection.PROJECTS,),
                similarity_floor=Decimal("0"),
                similarity_ceiling=Decimal("1"),
            ),
        ),
    )


class StaticEmbeddingAdapter:
    def __init__(self, vectors: dict[str, tuple[float, ...]]) -> None:
        self.vectors = vectors
        self.calls: list[tuple[str, ...]] = []

    def embed(self, texts: tuple[str, ...]) -> tuple[tuple[float, ...], ...]:
        self.calls.append(texts)
        return tuple(self.vectors[text] for text in texts)


class FailingEmbeddingAdapter:
    def embed(self, texts: tuple[str, ...]) -> tuple[tuple[float, ...], ...]:
        raise RuntimeError(f"provider failed for {len(texts)} texts")


class InvalidEmbeddingAdapter:
    def __init__(self, output: object) -> None:
        self.output = output

    def embed(self, texts: tuple[str, ...]) -> object:
        return self.output


def test_l2_scores_each_section_independently_and_applies_rubric_weights() -> None:
    adapter = StaticEmbeddingAdapter(
        {
            "query technical": (1.0, 0.0),
            "query project": (0.0, 1.0),
            "Python API": (1.0, 0.0),
            "Sales dashboard": (0.0, 1.0),
        }
    )

    result = score_l2(make_cv(), make_rubric(), make_policy(), adapter)

    assert result.level is ScoringLevel.L2
    assert result.status is LevelScoreStatus.AVAILABLE
    assert result.score == Decimal("100.00")
    assert tuple(item.weighted_score for item in result.criterion_assessments) == (
        Decimal("60.00"),
        Decimal("40.00"),
    )
    assert adapter.calls == [
        (
            "query technical",
            "query project",
            "Python API",
            "Sales dashboard",
        )
    ]


def test_l2_does_not_use_evidence_from_an_unconfigured_section() -> None:
    rubric = ScoringRubric(
        rubric_id="rubric-section-test",
        rubric_version="1.0.0",
        job_profile_id="job-l2-test",
        criteria=(
            RubricCriterion(
                criterion_id="technical-skill",
                title="Technical skill",
                description="Technical evidence.",
                weight=Decimal("100"),
            ),
        ),
        critical_requirement_ids=("req-python",),
    )
    policy = L2Policy(
        job_profile_id="job-l2-test",
        criteria=(
            L2CriterionPolicy(
                criterion_id="technical-skill",
                query_text="query technical",
                evidence_sections=(EvidenceSection.PROJECTS,),
                similarity_floor=Decimal("0"),
                similarity_ceiling=Decimal("1"),
            ),
        ),
    )
    adapter = StaticEmbeddingAdapter(
        {
            "query technical": (1.0, 0.0),
            "Python API": (1.0, 0.0),
            "Sales dashboard": (0.0, 1.0),
        }
    )

    result = score_l2(make_cv(), rubric, policy, adapter)
    assessment = result.criterion_assessments[0]

    assert result.score == Decimal("0.00")
    assert assessment.evidence_status is EvidenceStatus.MISSING
    assert assessment.evidence_ids == ()
    assert adapter.calls == [("query technical", "Sales dashboard")]


def test_l2_top_k_uses_mean_similarity_and_rounds_weighted_points() -> None:
    cv_profile = CVProfile(
        cv_profile_id="cv-top-k",
        candidate_reference="candidate-top-k",
        evidence=(
            make_evidence("ev-first", "First project", EvidenceSection.PROJECTS),
            make_evidence("ev-second", "Second project", EvidenceSection.PROJECTS),
        ),
    )
    rubric = ScoringRubric(
        rubric_id="rubric-top-k",
        rubric_version="1.0.0",
        job_profile_id="job-l2-test",
        criteria=(
            RubricCriterion(
                criterion_id="project-impact",
                title="Project impact",
                description="Project evidence.",
                weight=Decimal("100"),
            ),
        ),
        critical_requirement_ids=("req-project",),
    )
    policy = L2Policy(
        job_profile_id="job-l2-test",
        criteria=(
            L2CriterionPolicy(
                criterion_id="project-impact",
                query_text="query project",
                evidence_sections=(EvidenceSection.PROJECTS,),
                similarity_floor=Decimal("0"),
                similarity_ceiling=Decimal("1"),
                top_k=2,
            ),
        ),
    )
    adapter = StaticEmbeddingAdapter(
        {
            "query project": (1.0, 0.0),
            "First project": (1.0, 0.0),
            "Second project": (0.0, 1.0),
        }
    )

    result = score_l2(cv_profile, rubric, policy, adapter)

    assert result.score == Decimal("50.00")
    assert result.criterion_assessments[0].evidence_ids == ("ev-first", "ev-second")


def test_l2_provider_exception_routes_to_unavailable_without_leaking_error() -> None:
    result = score_l2(make_cv(), make_rubric(), make_policy(), FailingEmbeddingAdapter())

    assert result.status is LevelScoreStatus.UNAVAILABLE
    assert result.score is None
    assert result.reason == "L2 embedding provider is unavailable."
    assert "provider failed" not in result.reason


@pytest.mark.parametrize(
    "output",
    [
        [],
        ((1.0, 0.0),),
        ((1.0, 0.0), (0.0,), (1.0, 0.0), (0.0, 1.0)),
        ((1.0, 0.0), (0.0, 1.0), (float("nan"), 0.0), (0.0, 1.0)),
        ((1.0, 0.0), (0.0, 1.0), (0.0, 0.0), (0.0, 1.0)),
        ((1.0, 0.0), (0.0, 1.0), ("bad", 0.0), (0.0, 1.0)),
    ],
)
def test_l2_invalid_embedding_output_is_reported_as_invalid(output: object) -> None:
    result = score_l2(
        make_cv(),
        make_rubric(),
        make_policy(),
        InvalidEmbeddingAdapter(output),
    )

    assert result.status is LevelScoreStatus.INVALID
    assert result.score is None
    assert result.reason == "L2 embedding provider returned invalid vectors."


def test_l2_rejects_missing_extra_or_wrong_job_policy_criteria() -> None:
    rubric = make_rubric()
    missing_criterion = L2Policy(
        job_profile_id="job-l2-test",
        criteria=(make_policy().criteria[0],),
    )
    wrong_job = L2Policy(job_profile_id="other-job", criteria=make_policy().criteria)
    adapter = StaticEmbeddingAdapter({})

    with pytest.raises(ScoringInputError, match="exactly match"):
        score_l2(make_cv(), rubric, missing_criterion, adapter)
    with pytest.raises(ScoringInputError, match="job_profile_id"):
        score_l2(make_cv(), rubric, wrong_job, adapter)


def test_l2_policy_rejects_invalid_similarity_bounds_top_k_and_duplicates() -> None:
    criterion = make_policy().criteria[0]

    with pytest.raises(ScoringInputError):
        L2CriterionPolicy(
            criterion_id="technical-skill",
            query_text="query",
            evidence_sections=(EvidenceSection.SKILLS,),
            similarity_floor=Decimal("0.5"),
            similarity_ceiling=Decimal("0.5"),
        )
    with pytest.raises(ScoringInputError):
        L2CriterionPolicy(
            criterion_id="technical-skill",
            query_text="query",
            evidence_sections=(EvidenceSection.SKILLS,),
            similarity_floor=Decimal("0"),
            similarity_ceiling=Decimal("1"),
            top_k=0,
        )
    with pytest.raises(ScoringInputError, match="unique"):
        L2Policy(job_profile_id="job-l2-test", criteria=(criterion, criterion))
