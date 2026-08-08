from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from backend.app.agents.classifier.graph import (
    ClassifierDependencies,
    LangGraphClassifierWorkflow,
)
from backend.app.agents.classifier.scoring.l3 import L3ProviderRequest
from backend.app.contracts import (
    ClassificationDecision,
    EvidenceSection,
    EvidenceStatus,
    LevelScoreStatus,
)
from backend.app.domain import (
    BoundaryRule,
    L1Policy,
    L2CriterionPolicy,
    L2Policy,
    MatchMode,
    RequirementRule,
    RoutingPolicy,
)
from tests.contract.test_contracts import valid_request


class ConstantEmbeddingAdapter:
    def embed(self, texts: tuple[str, ...]) -> tuple[tuple[float, ...], ...]:
        return tuple((1.0, 0.0) for _ in texts)


class FullScoreProvider:
    async def evaluate(self, request: L3ProviderRequest) -> object:
        evidence_id = request.cv_profile.evidence[0].evidence_id
        requirement_assessments = [
            {
                "requirement_id": requirement_id,
                "evidence_status": EvidenceStatus.SATISFIED,
                "evidence_ids": [evidence_id],
                "rationale": "The configured evidence supports this requirement.",
            }
            for requirement_id in request.rubric.critical_requirement_ids
        ]
        criterion_assessments = [
            {
                "criterion_id": criterion.criterion_id,
                "score": criterion.weight,
                "evidence_status": EvidenceStatus.SATISFIED,
                "evidence_ids": [evidence_id],
                "rationale": "The configured evidence supports this criterion.",
            }
            for criterion in request.rubric.criteria
        ]
        return {
            "requirement_assessments": requirement_assessments,
            "criterion_assessments": criterion_assessments,
            "overall_score": Decimal("100"),
            "strengths": ["Evidence is explicit."],
            "risks": [],
            "warnings": [],
            "confidence": Decimal("0.90"),
        }


class UnavailableProvider:
    async def evaluate(self, request: L3ProviderRequest) -> object:
        raise RuntimeError(request.prompt_version)


class FixedIdentifierGenerator:
    def new_identifier(self, prefix: str) -> str:
        return f"{prefix}-graph-001"


class FixedClock:
    def now(self) -> datetime:
        return datetime(2026, 7, 26, 9, 0, tzinfo=UTC)


def l1_policy() -> L1Policy:
    return L1Policy(
        job_profile_id="junior-data-analyst-v1",
        rules=(
            RequirementRule(
                requirement_id="da-sql",
                evidence_sections=(EvidenceSection.SKILLS, EvidenceSection.PROJECTS),
                positive_terms=("SQL",),
                explicit_negative_terms=("no sql",),
                match_mode=MatchMode.ANY,
            ),
            RequirementRule(
                requirement_id="da-python",
                evidence_sections=(EvidenceSection.SKILLS, EvidenceSection.PROJECTS),
                positive_terms=("Python",),
                explicit_negative_terms=("no python",),
                match_mode=MatchMode.ANY,
            ),
        ),
    )


def l2_policy() -> L2Policy:
    request = valid_request()
    return L2Policy(
        job_profile_id=request.job_profile.job_profile_id,
        criteria=tuple(
            L2CriterionPolicy(
                criterion_id=criterion.criterion_id,
                query_text=criterion.description,
                evidence_sections=(
                    EvidenceSection.SKILLS,
                    EvidenceSection.PROJECTS,
                    EvidenceSection.WORK_EXPERIENCE,
                    EvidenceSection.EDUCATION,
                ),
                similarity_floor=Decimal("-1"),
                similarity_ceiling=Decimal("1"),
                top_k=1,
            )
            for criterion in request.rubric.criteria
        ),
    )


def routing_policy() -> RoutingPolicy:
    return RoutingPolicy(
        pass_minimum=Decimal("75"),
        waitlist_minimum=Decimal("60"),
        missing_critical_evidence=True,
        conflicting_critical_evidence=True,
        invalid_provider_output=True,
        disagreement_points=Decimal("25"),
        boundary_rules=(
            BoundaryRule(
                rule_id="lower-threshold-boundary",
                minimum=Decimal("58"),
                maximum=Decimal("62"),
            ),
            BoundaryRule(
                rule_id="upper-threshold-boundary",
                minimum=Decimal("73"),
                maximum=Decimal("77"),
            ),
        ),
        low_score_without_explicit_critical_unsatisfied=True,
        critical_unsatisfied_at_or_above_waitlist_threshold=True,
        reject_requires_explicit_unsatisfied_critical=True,
    )


def dependencies(provider: FullScoreProvider | UnavailableProvider) -> ClassifierDependencies:
    return ClassifierDependencies(
        l1_policy=l1_policy(),
        l2_policy=l2_policy(),
        routing_policy=routing_policy(),
        embedding_adapter=ConstantEmbeddingAdapter(),
        l3_provider=provider,
        identifier_generator=FixedIdentifierGenerator(),
        clock=FixedClock(),
    )


@pytest.mark.asyncio
async def test_langgraph_workflow_runs_all_levels_and_builds_result() -> None:
    workflow = LangGraphClassifierWorkflow(dependencies(FullScoreProvider()))

    result = await workflow.classify(valid_request())

    assert result.classification_result_id == "result-graph-001"
    assert result.proposed_decision is ClassificationDecision.PASS
    assert result.scores.l1.value == Decimal("100.00")
    assert result.scores.l2.value == Decimal("100.00")
    assert result.scores.l3.value == Decimal("100.00")
    assert result.scores.final_score == Decimal("100.00")
    assert result.confidence == Decimal("0.90")
    assert result.quality_gate.requires_review is False
    assert len(result.criterion_assessments) == 5


@pytest.mark.asyncio
async def test_langgraph_workflow_routes_provider_failure_to_review() -> None:
    workflow = LangGraphClassifierWorkflow(dependencies(UnavailableProvider()))

    result = await workflow.classify(valid_request())

    assert result.proposed_decision is ClassificationDecision.NEEDS_REVIEW
    assert result.scores.l3.status is LevelScoreStatus.UNAVAILABLE
    assert result.scores.final_score is None
    assert result.confidence is None
    assert "invalid-provider-output" in result.quality_gate.reasons
