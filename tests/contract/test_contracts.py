from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from backend.app.contracts import (
    AggregationWeights,
    ApprovalStatus,
    ApprovedDecision,
    CVProfile,
    ClassificationConfig,
    ClassificationDecision,
    ClassificationRequest,
    ClassificationResult,
    CriterionAssessment,
    DecisionThresholds,
    Evidence,
    EvidenceLocation,
    EvidenceSection,
    EvidenceSourceType,
    EvidenceStatus,
    ExperienceRange,
    FinalDecision,
    JobProfile,
    JobRequirement,
    LevelScore,
    LevelScoreStatus,
    ModelMetadata,
    NeedsReviewPolicy,
    Project,
    QualityGate,
    RequirementPriority,
    ReviewBand,
    RubricCriterion,
    RunVersions,
    ScoreBreakdown,
    ScoringRubric,
    SeniorityLevel,
    Skill,
)


def valid_evidence() -> tuple[Evidence, ...]:
    return (
        Evidence(
            evidence_id="ev-sql",
            source_type=EvidenceSourceType.PARSER,
            section=EvidenceSection.SKILLS,
            text="SQL: joined, aggregated and filtered sales data.",
            location=EvidenceLocation(source_record_id="record-skills", page_number=1),
            extraction_confidence=Decimal("0.95"),
        ),
        Evidence(
            evidence_id="ev-python",
            source_type=EvidenceSourceType.PARSER,
            section=EvidenceSection.SKILLS,
            text="Python with pandas for data cleaning and analysis.",
            location=EvidenceLocation(source_record_id="record-skills", page_number=1),
            extraction_confidence=Decimal("0.95"),
        ),
        Evidence(
            evidence_id="ev-project",
            source_type=EvidenceSourceType.PARSER,
            section=EvidenceSection.PROJECTS,
            text="Built a sales dashboard from cleaned transaction data.",
            location=EvidenceLocation(source_record_id="record-project", page_number=2),
            extraction_confidence=Decimal("0.90"),
        ),
    )


def valid_cv_profile() -> CVProfile:
    return CVProfile(
        cv_profile_id="cv-001",
        candidate_reference="candidate-001",
        skills=(
            Skill(name="SQL", evidence_ids=("ev-sql",)),
            Skill(name="Python", evidence_ids=("ev-python",)),
        ),
        projects=(
            Project(
                project_id="project-sales-dashboard",
                title="Sales dashboard",
                summary="Cleaned data and presented weekly sales trends.",
                technologies=("Python", "SQL", "Power BI"),
                evidence_ids=("ev-project", "ev-sql", "ev-python"),
            ),
        ),
        evidence=valid_evidence(),
    )


def valid_job_profile() -> JobProfile:
    return JobProfile(
        job_profile_id="junior-data-analyst-v1",
        title="Junior Data Analyst",
        seniority=SeniorityLevel.JUNIOR,
        experience_range=ExperienceRange(minimum_years=0, maximum_years=2),
        responsibilities=("Analyze structured data for business questions.",),
        requirements=(
            JobRequirement(
                requirement_id="da-sql",
                title="SQL",
                description="Use SQL for querying and aggregation.",
                priority=RequirementPriority.REQUIRED,
                is_critical=True,
                accepted_evidence=("Project or work evidence using SQL.",),
                missing_evidence_policy="Mark missing evidence for review.",
                explicit_failure_policy="Require explicit evidence before marking unsatisfied.",
            ),
            JobRequirement(
                requirement_id="da-python",
                title="Python or R",
                description="Use Python or R for analysis.",
                priority=RequirementPriority.REQUIRED,
                is_critical=True,
                accepted_evidence=("Project or work evidence using Python or R.",),
                missing_evidence_policy="Mark missing evidence for review.",
                explicit_failure_policy="Require explicit evidence before marking unsatisfied.",
            ),
            JobRequirement(
                requirement_id="da-bi",
                title="Business intelligence",
                description="Use dashboard tools when relevant.",
                priority=RequirementPriority.PREFERRED,
                accepted_evidence=("Dashboard project evidence.",),
                missing_evidence_policy="Do not treat missing evidence as unsatisfied.",
                explicit_failure_policy="Only explicit contrary evidence is unsatisfied.",
            ),
        ),
    )


def valid_rubric() -> ScoringRubric:
    return ScoringRubric(
        rubric_id="junior-data-analyst-rubric-v1",
        rubric_version="1.0.0",
        job_profile_id="junior-data-analyst-v1",
        criteria=(
            RubricCriterion(
                criterion_id="mandatory-requirements",
                title="Mandatory requirements",
                description="Evaluate critical requirements.",
                weight=Decimal("30"),
            ),
            RubricCriterion(
                criterion_id="technical-analysis",
                title="Technical analysis",
                description="Evaluate technical analysis ability.",
                weight=Decimal("25"),
            ),
            RubricCriterion(
                criterion_id="analytical-reasoning",
                title="Analytical reasoning",
                description="Evaluate analytical reasoning.",
                weight=Decimal("20"),
            ),
            RubricCriterion(
                criterion_id="projects-and-impact",
                title="Projects and impact",
                description="Evaluate projects and impact.",
                weight=Decimal("15"),
            ),
            RubricCriterion(
                criterion_id="communication-and-evidence-quality",
                title="Communication and evidence",
                description="Evaluate communication quality.",
                weight=Decimal("10"),
            ),
        ),
        critical_requirement_ids=("da-sql", "da-python"),
    )


def valid_config() -> ClassificationConfig:
    return ClassificationConfig(
        configuration_id="scoring-config-v1",
        configuration_version="1.1.0",
        job_profile_artifact_version="1.0.0",
        l1_rules_configuration_version="1.0.0",
        models_configuration_version="1.1.0",
        aggregation=AggregationWeights(
            l1_deterministic_rules=Decimal("0.45"),
            l2_section_semantic_matching=Decimal("0.25"),
            l3_evidence_grounded_reasoning=Decimal("0.30"),
        ),
        thresholds=DecisionThresholds(
            pass_minimum=Decimal("75"),
            waitlist_minimum=Decimal("60"),
        ),
        needs_review_policy=NeedsReviewPolicy(
            missing_critical_evidence=True,
            conflicting_critical_evidence=True,
            invalid_provider_output=True,
            disagreement_points=Decimal("25"),
            boundary_score_bands=(
                ReviewBand(minimum=Decimal("58"), maximum=Decimal("62")),
                ReviewBand(minimum=Decimal("73"), maximum=Decimal("77")),
            ),
        ),
        models=ModelMetadata(
            embedding_model_identifier="intfloat/multilingual-e5-base",
            embedding_model_version="multilingual-e5-base",
            llm_provider_identifier="environment-configured",
            llm_model_identifier="configured-at-runtime",
            prompt_version="l3-evidence-rubric-v1",
        ),
    )


def valid_request() -> ClassificationRequest:
    return ClassificationRequest(
        request_id="request-001",
        cv_profile=valid_cv_profile(),
        job_profile=valid_job_profile(),
        rubric=valid_rubric(),
        configuration=valid_config(),
    )


def available_score(value: str) -> LevelScore:
    return LevelScore(value=Decimal(value), status=LevelScoreStatus.AVAILABLE)


def valid_result() -> ClassificationResult:
    return ClassificationResult(
        classification_result_id="result-001",
        request_id="request-001",
        cv_profile_id="cv-001",
        job_profile_id="junior-data-analyst-v1",
        proposed_decision=ClassificationDecision.PASS,
        scores=ScoreBreakdown(
            l1=available_score("80"),
            l2=available_score("78"),
            l3=available_score("82"),
            final_score=Decimal("80.10"),
        ),
        criterion_assessments=(
            CriterionAssessment(
                criterion_id="mandatory-requirements",
                score=Decimal("28"),
                evidence_status=EvidenceStatus.SATISFIED,
                evidence_ids=("ev-sql", "ev-python"),
                rationale="The supplied evidence supports the required skills.",
            ),
        ),
        strengths=("SQL and Python project evidence is explicit.",),
        risks=(),
        warnings=(),
        confidence=Decimal("0.82"),
        quality_gate=QualityGate(requires_review=False),
        versions=RunVersions(
            job_profile_artifact_version="1.0.0",
            rubric_version="1.0.0",
            configuration_version="1.1.0",
            l1_rules_configuration_version="1.0.0",
            models_configuration_version="1.1.0",
            embedding_model_identifier="intfloat/multilingual-e5-base",
            embedding_model_version="multilingual-e5-base",
            llm_provider_identifier="environment-configured",
            llm_model_identifier="configured-at-runtime",
            prompt_version="l3-evidence-rubric-v1",
        ),
        created_at=datetime.now(UTC),
    )


def test_valid_request_and_result_are_serializable() -> None:
    request = valid_request()
    result = valid_result()

    assert request.schema_version == "1.1.0"
    assert request.configuration.schema_version == "1.1.0"
    assert result.schema_version == "1.1.0"
    assert request.rubric.job_profile_id == request.job_profile.job_profile_id
    assert result.model_dump(mode="json")["proposed_decision"] == "pass"
    assert result.scores.final_score == Decimal("80.10")
    assert result.versions.l1_rules_configuration_version == "1.0.0"
    assert result.versions.models_configuration_version == "1.1.0"


def test_cv_profile_rejects_unknown_evidence_reference() -> None:
    with pytest.raises(ValidationError):
        CVProfile(
            cv_profile_id="cv-002",
            candidate_reference="candidate-002",
            skills=(Skill(name="SQL", evidence_ids=("ev-missing",)),),
            evidence=valid_evidence(),
        )


def test_cv_profile_rejects_protected_attribute_field() -> None:
    payload = valid_cv_profile().model_dump()
    payload["age"] = 22

    with pytest.raises(ValidationError):
        CVProfile.model_validate(payload)


def test_contract_rejects_unsupported_schema_version() -> None:
    payload = valid_cv_profile().model_dump()
    payload["schema_version"] = "2.0.0"

    with pytest.raises(ValidationError):
        CVProfile.model_validate(payload)


def test_classification_request_rejects_pre_traceability_schema() -> None:
    payload = valid_request().model_dump()
    payload["schema_version"] = "1.0.0"

    with pytest.raises(ValidationError):
        ClassificationRequest.model_validate(payload)


def test_job_profile_rejects_critical_preferred_requirement() -> None:
    with pytest.raises(ValidationError):
        JobRequirement(
            requirement_id="da-invalid",
            title="Invalid",
            description="A critical preferred requirement is invalid.",
            priority=RequirementPriority.PREFERRED,
            is_critical=True,
            accepted_evidence=("Evidence.",),
            missing_evidence_policy="Review.",
            explicit_failure_policy="Explicit evidence only.",
        )


def test_rubric_rejects_abnormal_weight_total() -> None:
    criteria = valid_rubric().criteria
    invalid_criteria = (
        criteria[0],
        criteria[1],
        criteria[2],
        criteria[3],
        RubricCriterion(
            criterion_id="communication-and-evidence-quality",
            title="Communication and evidence",
            description="Evaluate communication quality.",
            weight=Decimal("11"),
        ),
    )

    with pytest.raises(ValidationError):
        ScoringRubric(
            rubric_id="junior-data-analyst-rubric-v2",
            rubric_version="1.0.0",
            job_profile_id="junior-data-analyst-v1",
            criteria=invalid_criteria,
            critical_requirement_ids=("da-sql", "da-python"),
        )


def test_configuration_rejects_invalid_aggregation_and_thresholds() -> None:
    with pytest.raises(ValidationError):
        AggregationWeights(
            l1_deterministic_rules=Decimal("0.50"),
            l2_section_semantic_matching=Decimal("0.25"),
            l3_evidence_grounded_reasoning=Decimal("0.30"),
        )

    with pytest.raises(ValidationError):
        DecisionThresholds(pass_minimum=Decimal("60"), waitlist_minimum=Decimal("60"))


@pytest.mark.parametrize(
    "field_name",
    (
        "job_profile_artifact_version",
        "l1_rules_configuration_version",
        "models_configuration_version",
    ),
)
def test_configuration_requires_policy_traceability_versions(field_name: str) -> None:
    payload = valid_config().model_dump()
    payload.pop(field_name)

    with pytest.raises(ValidationError):
        ClassificationConfig.model_validate(payload)


def test_request_rejects_unknown_critical_requirement() -> None:
    rubric = valid_rubric().model_copy(update={"critical_requirement_ids": ("da-unknown",)})

    with pytest.raises(ValidationError):
        ClassificationRequest(
            request_id="request-002",
            cv_profile=valid_cv_profile(),
            job_profile=valid_job_profile(),
            rubric=rubric,
            configuration=valid_config(),
        )


def test_needs_review_result_accepts_unavailable_l3_without_final_score() -> None:
    result = ClassificationResult(
        classification_result_id="result-002",
        request_id="request-001",
        cv_profile_id="cv-001",
        job_profile_id="junior-data-analyst-v1",
        proposed_decision=ClassificationDecision.NEEDS_REVIEW,
        scores=ScoreBreakdown(
            l1=available_score("80"),
            l2=available_score("78"),
            l3=LevelScore(
                value=None,
                status=LevelScoreStatus.UNAVAILABLE,
                reason="Provider timeout.",
            ),
            final_score=None,
        ),
        criterion_assessments=(
            CriterionAssessment(
                criterion_id="mandatory-requirements",
                score=Decimal("28"),
                evidence_status=EvidenceStatus.SATISFIED,
                evidence_ids=("ev-sql", "ev-python"),
                rationale="The supplied evidence supports the required skills.",
            ),
        ),
        confidence=None,
        quality_gate=QualityGate(requires_review=True, reasons=("L3 provider unavailable.",)),
        versions=valid_result().versions,
        created_at=datetime.now(UTC),
    )

    assert result.proposed_decision is ClassificationDecision.NEEDS_REVIEW
    assert result.scores.final_score is None


def test_approved_decision_requires_consistent_human_action() -> None:
    approved = ApprovedDecision(
        approved_decision_id="approved-001",
        classification_result_id="result-001",
        approval_status=ApprovalStatus.APPROVED,
        proposed_decision=ClassificationDecision.PASS,
        final_decision=FinalDecision.PASS,
        reviewer_reference="reviewer-001",
        decision_reason="Evidence and proposed decision were reviewed.",
        decided_at=datetime.now(UTC),
    )

    assert approved.final_decision is FinalDecision.PASS

    with pytest.raises(ValidationError):
        ApprovedDecision(
            approved_decision_id="approved-002",
            classification_result_id="result-001",
            approval_status=ApprovalStatus.OVERRIDDEN,
            proposed_decision=ClassificationDecision.PASS,
            final_decision=FinalDecision.REJECT,
            reviewer_reference="reviewer-001",
            decision_reason="The reviewer changed the decision.",
            decided_at=datetime.now(UTC),
        )
