from decimal import Decimal
from math import sqrt

import pytest

from backend.app.agents.classifier.scoring.l2 import score_l2_with_trace
from backend.app.agents.classifier.scoring.l2_policy import (
    L2CoverageConfiguration,
    build_query_coverage_l2_policy,
)
from backend.app.contracts import (
    CVProfile,
    Evidence,
    EvidenceLocation,
    EvidenceSection,
    EvidenceSourceType,
    EvidenceStatus,
    ExperienceRange,
    JobProfile,
    JobRequirement,
    RequirementPriority,
    RubricCriterion,
    ScoringRubric,
    SeniorityLevel,
)
from backend.app.domain import L2CriterionPolicy, L2Policy, L2ScoringMode, ScoringInputError


class StaticEmbeddingAdapter:
    def __init__(self, vectors: dict[str, tuple[float, ...]]) -> None:
        self._vectors = vectors

    def embed(self, texts: tuple[str, ...]) -> tuple[tuple[float, ...], ...]:
        return tuple(self._vectors[text] for text in texts)


class StaticScoreCalibrator:
    def __init__(self, scores: tuple[Decimal, ...] | None) -> None:
        self._scores = scores

    def calibrate(
        self,
        job_profile_id: str,
        criterion_scores: tuple[Decimal, ...],
    ) -> tuple[Decimal, ...]:
        if self._scores is None:
            raise RuntimeError("calibration unavailable")
        assert job_profile_id == "job-l2-coverage"
        assert criterion_scores == (Decimal("50.00"),)
        return self._scores


def _evidence(evidence_id: str, text: str, section: EvidenceSection) -> Evidence:
    return Evidence(
        evidence_id=evidence_id,
        source_type=EvidenceSourceType.MANUAL,
        section=section,
        text=text,
        location=EvidenceLocation(source_record_id=f"record-{evidence_id}"),
    )


def _single_criterion_rubric() -> ScoringRubric:
    return ScoringRubric(
        rubric_id="rubric-l2-coverage",
        rubric_version="1.0.0",
        job_profile_id="job-l2-coverage",
        criteria=(
            RubricCriterion(
                criterion_id="mandatory-requirements",
                title="Mandatory requirements",
                description="Coverage of requirements.",
                weight=Decimal("100"),
            ),
        ),
        critical_requirement_ids=("req-one",),
    )


def test_query_coverage_penalizes_an_uncovered_query_and_returns_trace() -> None:
    profile = CVProfile(
        cv_profile_id="cv-coverage",
        candidate_reference="candidate-coverage",
        evidence=(_evidence("ev-project", "project evidence", EvidenceSection.PROJECTS),),
    )
    policy = L2Policy(
        job_profile_id="job-l2-coverage",
        criteria=(
            L2CriterionPolicy(
                criterion_id="mandatory-requirements",
                query_text="query covered",
                additional_query_texts=("query missing",),
                evidence_sections=(EvidenceSection.PROJECTS,),
                similarity_floor=Decimal("0"),
                similarity_ceiling=Decimal("1"),
                scoring_mode=L2ScoringMode.QUERY_COVERAGE,
                minimum_query_score=Decimal("50"),
            ),
        ),
    )
    adapter = StaticEmbeddingAdapter(
        {
            "query covered": (1.0, 0.0),
            "query missing": (0.0, 1.0),
            "project evidence": (1.0, 0.0),
        }
    )

    result, trace = score_l2_with_trace(
        profile,
        _single_criterion_rubric(),
        policy,
        adapter,
    )

    assert result.score == Decimal("50.00")
    assert result.criterion_assessments[0].evidence_ids == ("ev-project",)
    assert trace is not None
    query_traces = trace.criteria[0].query_traces
    assert tuple(item.effective_score for item in query_traces) == (
        Decimal("100.00"),
        Decimal("0"),
    )
    assert tuple(item.meets_minimum for item in query_traces) == (True, False)


def test_l2_calibrator_updates_level_criteria_and_trace_consistently() -> None:
    profile = CVProfile(
        cv_profile_id="cv-calibrated",
        candidate_reference="candidate-calibrated",
        evidence=(_evidence("ev-project", "project evidence", EvidenceSection.PROJECTS),),
    )
    policy = L2Policy(
        job_profile_id="job-l2-coverage",
        criteria=(
            L2CriterionPolicy(
                criterion_id="mandatory-requirements",
                query_text="query covered",
                additional_query_texts=("query missing",),
                evidence_sections=(EvidenceSection.PROJECTS,),
                similarity_floor=Decimal("0"),
                similarity_ceiling=Decimal("1"),
                scoring_mode=L2ScoringMode.QUERY_COVERAGE,
                minimum_query_score=Decimal("50"),
            ),
        ),
    )
    adapter = StaticEmbeddingAdapter(
        {
            "query covered": (1.0, 0.0),
            "query missing": (0.0, 1.0),
            "project evidence": (1.0, 0.0),
        }
    )

    result, trace = score_l2_with_trace(
        profile,
        _single_criterion_rubric(),
        policy,
        adapter,
        StaticScoreCalibrator((Decimal("75"),)),
    )

    assert result.score == Decimal("75.00")
    assert result.criterion_assessments[0].weighted_score == Decimal("75.00")
    assert "Calibrated" in result.criterion_assessments[0].rationale
    assert trace is not None
    assert trace.criteria[0].weighted_score == Decimal("75.00")


@pytest.mark.parametrize(
    ("scores", "expected_status"),
    [
        (None, "unavailable"),
        ((Decimal("120"),), "invalid"),
        ((Decimal("10"), Decimal("20")), "invalid"),
    ],
)
def test_l2_calibrator_failure_is_explicit(
    scores: tuple[Decimal, ...] | None,
    expected_status: str,
) -> None:
    profile = CVProfile(
        cv_profile_id="cv-calibration-failure",
        candidate_reference="candidate-calibration-failure",
        evidence=(_evidence("ev-project", "project evidence", EvidenceSection.PROJECTS),),
    )
    policy = L2Policy(
        job_profile_id="job-l2-coverage",
        criteria=(
            L2CriterionPolicy(
                criterion_id="mandatory-requirements",
                query_text="query",
                evidence_sections=(EvidenceSection.PROJECTS,),
                similarity_floor=Decimal("0"),
                similarity_ceiling=Decimal("1"),
            ),
        ),
    )
    adapter = StaticEmbeddingAdapter({"query": (1.0, 0.0), "project evidence": (0.5, sqrt(0.75))})

    result, trace = score_l2_with_trace(
        profile,
        _single_criterion_rubric(),
        policy,
        adapter,
        StaticScoreCalibrator(scores),
    )

    assert result.status.value == expected_status
    assert result.score is None
    assert trace is None


def test_section_weight_can_rank_specific_project_above_skills_only_match() -> None:
    profile = CVProfile(
        cv_profile_id="cv-section-weight",
        candidate_reference="candidate-section-weight",
        evidence=(
            _evidence("ev-skill", "skill evidence", EvidenceSection.SKILLS),
            _evidence("ev-project", "project evidence", EvidenceSection.PROJECTS),
        ),
    )
    policy = L2Policy(
        job_profile_id="job-l2-coverage",
        criteria=(
            L2CriterionPolicy(
                criterion_id="mandatory-requirements",
                query_text="query",
                evidence_sections=(EvidenceSection.SKILLS, EvidenceSection.PROJECTS),
                similarity_floor=Decimal("0"),
                similarity_ceiling=Decimal("1"),
                scoring_mode=L2ScoringMode.QUERY_COVERAGE,
                minimum_query_score=Decimal("1"),
                section_weights=(
                    (EvidenceSection.SKILLS, Decimal("0.50")),
                    (EvidenceSection.PROJECTS, Decimal("1")),
                ),
            ),
        ),
    )
    adapter = StaticEmbeddingAdapter(
        {
            "query": (1.0, 0.0),
            "skill evidence": (1.0, 0.0),
            "project evidence": (0.8, 0.6),
        }
    )

    result, trace = score_l2_with_trace(
        profile,
        _single_criterion_rubric(),
        policy,
        adapter,
    )

    assert result.score == Decimal("80.00")
    assert result.criterion_assessments[0].evidence_ids == ("ev-project",)
    assert trace is not None
    selected = trace.criteria[0].query_traces[0].selected_matches[0]
    assert selected.evidence_id == "ev-project"
    assert selected.raw_similarity == Decimal("0.8")
    assert selected.adjusted_score == Decimal("80.00")


@pytest.mark.parametrize(
    ("similarity", "minimum", "expected_score", "expected_status"),
    [
        (0.5, Decimal("50"), Decimal("50.00"), EvidenceStatus.SATISFIED),
        (0.49, Decimal("50"), Decimal("0.00"), EvidenceStatus.MISSING),
    ],
)
def test_query_minimum_boundary_is_inclusive(
    similarity: float,
    minimum: Decimal,
    expected_score: Decimal,
    expected_status: EvidenceStatus,
) -> None:
    profile = CVProfile(
        cv_profile_id="cv-minimum-boundary",
        candidate_reference="candidate-minimum-boundary",
        evidence=(_evidence("ev-boundary", "boundary evidence", EvidenceSection.PROJECTS),),
    )
    policy = L2Policy(
        job_profile_id="job-l2-coverage",
        criteria=(
            L2CriterionPolicy(
                criterion_id="mandatory-requirements",
                query_text="query",
                evidence_sections=(EvidenceSection.PROJECTS,),
                similarity_floor=Decimal("0"),
                similarity_ceiling=Decimal("1"),
                scoring_mode=L2ScoringMode.QUERY_COVERAGE,
                minimum_query_score=minimum,
            ),
        ),
    )
    adapter = StaticEmbeddingAdapter(
        {
            "query": (1.0, 0.0),
            "boundary evidence": (similarity, sqrt(1 - similarity**2)),
        }
    )

    result, _ = score_l2_with_trace(
        profile,
        _single_criterion_rubric(),
        policy,
        adapter,
    )

    assert result.score == expected_score
    assert result.criterion_assessments[0].evidence_status is expected_status


def _job_and_rubric() -> tuple[JobProfile, ScoringRubric]:
    job = JobProfile(
        job_profile_id="job-query-builder",
        title="Junior Test Role",
        seniority=SeniorityLevel.JUNIOR,
        experience_range=ExperienceRange(
            minimum_years=0,
            maximum_years=2,
            formal_work_experience_required=False,
        ),
        responsibilities=("Build a service", "Validate its output"),
        requirements=(
            JobRequirement(
                requirement_id="req-one",
                title="Python",
                description="Use Python in a project.",
                priority=RequirementPriority.REQUIRED,
                is_critical=True,
                accepted_evidence=("Project implementation",),
                missing_evidence_policy="Missing is not failure.",
                explicit_failure_policy="Explicitly no Python.",
            ),
            JobRequirement(
                requirement_id="req-two",
                title="SQL",
                description="Use SQL in a project.",
                priority=RequirementPriority.REQUIRED,
                is_critical=True,
                accepted_evidence=("Project query",),
                missing_evidence_policy="Missing is not failure.",
                explicit_failure_policy="Explicitly no SQL.",
            ),
            JobRequirement(
                requirement_id="req-three",
                title="Testing",
                description="Write automated tests.",
                priority=RequirementPriority.PREFERRED,
                accepted_evidence=("Test suite",),
                missing_evidence_policy="Preferred information may be missing.",
                explicit_failure_policy="Preferred failure is not critical.",
            ),
        ),
    )
    rubric = ScoringRubric(
        rubric_id="rubric-query-builder",
        rubric_version="1.0.0",
        job_profile_id=job.job_profile_id,
        criteria=tuple(
            RubricCriterion(
                criterion_id=criterion_id,
                title=title,
                description=f"Assess {title}.",
                weight=weight,
            )
            for criterion_id, title, weight in (
                ("mandatory-requirements", "Mandatory", Decimal("30")),
                ("technical", "Technical", Decimal("25")),
                ("role", "Role", Decimal("20")),
                ("projects-and-impact", "Projects", Decimal("15")),
                ("communication-and-evidence-quality", "Clarity", Decimal("10")),
            )
        ),
        critical_requirement_ids=("req-one", "req-two"),
    )
    return job, rubric


def test_query_policy_builder_covers_requirements_and_uses_section_specific_scope() -> None:
    job, rubric = _job_and_rubric()
    configuration = L2CoverageConfiguration(
        similarity_floor=Decimal("0.80"),
        similarity_ceiling=Decimal("0.95"),
        top_k=1,
        minimum_query_score=Decimal("20"),
        section_weights=tuple((section, Decimal("1")) for section in EvidenceSection),
    )

    policy = build_query_coverage_l2_policy(job, rubric, configuration)

    assert policy.query_count == 9
    assert tuple(len(item.query_texts) for item in policy.criteria) == (2, 3, 2, 1, 1)
    assert EvidenceSection.SKILLS in policy.criteria[0].evidence_sections
    assert EvidenceSection.SKILLS not in policy.criteria[3].evidence_sections
    assert EvidenceSection.SKILLS not in policy.criteria[4].evidence_sections
    assert all(item.scoring_mode is L2ScoringMode.QUERY_COVERAGE for item in policy.criteria)


def test_rubric_signals_query_profile_adds_quality_and_depth_queries() -> None:
    job, rubric = _job_and_rubric()
    configuration = L2CoverageConfiguration(
        similarity_floor=Decimal("0.80"),
        similarity_ceiling=Decimal("0.95"),
        top_k=1,
        minimum_query_score=Decimal("20"),
        section_weights=tuple((section, Decimal("1")) for section in EvidenceSection),
        query_profile="rubric-signals-v2",
    )

    policy = build_query_coverage_l2_policy(job, rubric, configuration)

    assert policy.query_count == 14
    assert tuple(len(item.query_texts) for item in policy.criteria) == (2, 3, 3, 3, 3)
    assert "trade-off" in policy.criteria[2].query_texts[1]
    assert "tái tạo" in policy.criteria[3].query_texts[2]


def test_rubric_quality_query_profile_removes_role_title_dilution() -> None:
    job, rubric = _job_and_rubric()
    configuration = L2CoverageConfiguration(
        similarity_floor=Decimal("0.80"),
        similarity_ceiling=Decimal("0.95"),
        top_k=1,
        minimum_query_score=Decimal("20"),
        section_weights=tuple((section, Decimal("1")) for section in EvidenceSection),
        query_profile="rubric-quality-v3",
    )

    policy = build_query_coverage_l2_policy(job, rubric, configuration)

    assert policy.query_count == 11
    assert tuple(len(item.query_texts) for item in policy.criteria) == (2, 3, 2, 2, 2)
    assert all(job.title not in query for item in policy.criteria[2:] for query in item.query_texts)


def test_query_coverage_policy_rejects_duplicate_queries_and_invalid_section_weights() -> None:
    with pytest.raises(ScoringInputError, match="query texts"):
        L2CriterionPolicy(
            criterion_id="criterion",
            query_text="duplicate",
            additional_query_texts=("duplicate",),
            evidence_sections=(EvidenceSection.PROJECTS,),
            similarity_floor=Decimal("0"),
            similarity_ceiling=Decimal("1"),
            scoring_mode=L2ScoringMode.QUERY_COVERAGE,
        )
    with pytest.raises(ScoringInputError, match="section weights"):
        L2CriterionPolicy(
            criterion_id="criterion",
            query_text="query",
            evidence_sections=(EvidenceSection.PROJECTS,),
            similarity_floor=Decimal("0"),
            similarity_ceiling=Decimal("1"),
            scoring_mode=L2ScoringMode.QUERY_COVERAGE,
            section_weights=((EvidenceSection.SKILLS, Decimal("1")),),
        )
