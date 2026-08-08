from __future__ import annotations

from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass
from importlib import import_module
from typing import Protocol, cast

from backend.app.agents.classifier.routing import route_classification
from backend.app.agents.classifier.scoring import (
    EmbeddingAdapter,
    L2ScoreCalibrator,
    L3Provider,
    L3ProviderRequest,
    aggregate_level_scores,
    score_l1,
    score_l2,
    score_l3,
    select_result_criterion_assessments,
)
from backend.app.agents.classifier.state import ClassifierState
from backend.app.application.ports import Clock, IdentifierGenerator
from backend.app.contracts import (
    ClassificationRequest,
    ClassificationResult,
    CriterionAssessment as ContractCriterionAssessment,
    LevelScore,
    QualityGate,
    RunVersions,
    ScoreBreakdown,
)
from backend.app.domain import (
    AggregationResult,
    L1Policy,
    L2Policy,
    LevelAssessment,
    RoutingPolicy,
    RoutingResult,
)


class GraphInvoker(Protocol):
    def ainvoke(self, value: ClassifierState) -> Awaitable[ClassifierState]: ...


GraphNode = Callable[
    [ClassifierState],
    ClassifierState | Awaitable[ClassifierState],
]


class GraphBuilder(Protocol):
    def add_node(self, node: str, action: GraphNode) -> None: ...

    def add_edge(self, start_key: str | list[str], end_key: str) -> None: ...

    def compile(self) -> GraphInvoker: ...


class StateGraphFactory(Protocol):
    def __call__(self, state_schema: type[ClassifierState]) -> GraphBuilder: ...


_langgraph_module = import_module("langgraph.graph")
_state_graph_factory = cast(
    StateGraphFactory,
    getattr(_langgraph_module, "StateGraph"),
)
_graph_start = cast(str, getattr(_langgraph_module, "START"))
_graph_end = cast(str, getattr(_langgraph_module, "END"))


@dataclass(frozen=True, slots=True)
class ClassifierDependencies:
    l1_policy: L1Policy
    l2_policy: L2Policy
    routing_policy: RoutingPolicy
    embedding_adapter: EmbeddingAdapter
    l3_provider: L3Provider
    identifier_generator: IdentifierGenerator
    clock: Clock
    l2_score_calibrator: L2ScoreCalibrator | None = None


def _unique_text(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(value for value in values if value.strip()))


def _level_score(assessment: LevelAssessment) -> LevelScore:
    return LevelScore(
        value=assessment.score,
        status=assessment.status,
        reason=assessment.reason,
    )


def _request(state: ClassifierState) -> ClassificationRequest:
    value = state.get("request")
    if value is None:
        raise RuntimeError("classifier state is missing request")
    return value


def _l1(state: ClassifierState) -> LevelAssessment:
    value = state.get("l1")
    if value is None:
        raise RuntimeError("classifier state is missing L1 assessment")
    return value


def _l2(state: ClassifierState) -> LevelAssessment:
    value = state.get("l2")
    if value is None:
        raise RuntimeError("classifier state is missing L2 assessment")
    return value


def _l3(state: ClassifierState) -> LevelAssessment:
    value = state.get("l3")
    if value is None:
        raise RuntimeError("classifier state is missing L3 assessment")
    return value


def _aggregation(state: ClassifierState) -> AggregationResult:
    value = state.get("aggregation")
    if value is None:
        raise RuntimeError("classifier state is missing aggregation")
    return value


def _routing(state: ClassifierState) -> RoutingResult:
    value = state.get("routing")
    if value is None:
        raise RuntimeError("classifier state is missing routing result")
    return value


def _classification_result(state: ClassifierState) -> ClassificationResult:
    value = state.get("result")
    if value is None:
        raise RuntimeError("classifier state is missing classification result")
    return value


def _result_from_state(
    state: ClassifierState,
    dependencies: ClassifierDependencies,
) -> ClassificationResult:
    request = _request(state)
    l1 = _l1(state)
    l2 = _l2(state)
    l3 = _l3(state)
    routing = _routing(state)
    selected_criteria = select_result_criterion_assessments(
        (l1, l2, l3),
        request.rubric,
    )
    criterion_assessments = tuple(
        ContractCriterionAssessment(
            criterion_id=item.criterion_id,
            score=item.weighted_score,
            evidence_status=item.evidence_status,
            evidence_ids=item.evidence_ids,
            rationale=item.rationale,
        )
        for item in selected_criteria
    )
    reasons = routing.reasons
    strengths = _unique_text(item for level in (l1, l2, l3) for item in level.strengths)
    risks = _unique_text(item for level in (l1, l2, l3) for item in level.risks)
    warnings = _unique_text(item for level in (l1, l2, l3) for item in level.warnings)
    return ClassificationResult(
        classification_result_id=dependencies.identifier_generator.new_identifier("result"),
        request_id=request.request_id,
        cv_profile_id=request.cv_profile.cv_profile_id,
        job_profile_id=request.job_profile.job_profile_id,
        proposed_decision=routing.decision,
        scores=ScoreBreakdown(
            l1=_level_score(l1),
            l2=_level_score(l2),
            l3=_level_score(l3),
            final_score=routing.final_score,
        ),
        criterion_assessments=criterion_assessments,
        strengths=strengths,
        risks=risks,
        warnings=warnings,
        confidence=l3.confidence,
        quality_gate=QualityGate(
            requires_review=bool(reasons),
            reasons=reasons,
        ),
        versions=RunVersions(
            job_profile_artifact_version=request.configuration.job_profile_artifact_version,
            rubric_version=request.rubric.rubric_version,
            configuration_version=request.configuration.configuration_version,
            l1_rules_configuration_version=(request.configuration.l1_rules_configuration_version),
            models_configuration_version=request.configuration.models_configuration_version,
            embedding_model_identifier=(request.configuration.models.embedding_model_identifier),
            embedding_model_version=request.configuration.models.embedding_model_version,
            llm_provider_identifier=request.configuration.models.llm_provider_identifier,
            llm_model_identifier=request.configuration.models.llm_model_identifier,
            prompt_version=request.configuration.models.prompt_version,
        ),
        created_at=dependencies.clock.now(),
    )


def build_classifier_graph(dependencies: ClassifierDependencies) -> GraphInvoker:
    def l1_node(state: ClassifierState) -> ClassifierState:
        request = _request(state)
        return {
            "l1": score_l1(
                request.cv_profile,
                request.rubric,
                dependencies.l1_policy,
            )
        }

    def l2_node(state: ClassifierState) -> ClassifierState:
        request = _request(state)
        return {
            "l2": score_l2(
                request.cv_profile,
                request.rubric,
                dependencies.l2_policy,
                dependencies.embedding_adapter,
                dependencies.l2_score_calibrator,
            )
        }

    async def l3_node(state: ClassifierState) -> ClassifierState:
        request = _request(state)
        provider_request = L3ProviderRequest(
            cv_profile=request.cv_profile,
            job_profile=request.job_profile,
            rubric=request.rubric,
            prompt_version=request.configuration.models.prompt_version,
        )
        return {"l3": await score_l3(provider_request, dependencies.l3_provider)}

    def aggregate_node(state: ClassifierState) -> ClassifierState:
        return {
            "aggregation": aggregate_level_scores(
                (_l1(state), _l2(state), _l3(state)),
                _request(state).configuration.aggregation,
            )
        }

    def routing_node(state: ClassifierState) -> ClassifierState:
        return {
            "routing": route_classification(
                _aggregation(state),
                _l1(state).requirement_assessments,
                dependencies.routing_policy,
            )
        }

    def result_node(state: ClassifierState) -> ClassifierState:
        return {"result": _result_from_state(state, dependencies)}

    graph = _state_graph_factory(ClassifierState)
    graph.add_node("l1", l1_node)
    graph.add_node("l2", l2_node)
    graph.add_node("l3", l3_node)
    graph.add_node("aggregate", aggregate_node)
    graph.add_node("route", routing_node)
    graph.add_node("result", result_node)
    graph.add_edge(_graph_start, "l1")
    graph.add_edge(_graph_start, "l2")
    graph.add_edge(_graph_start, "l3")
    graph.add_edge(["l1", "l2", "l3"], "aggregate")
    graph.add_edge("aggregate", "route")
    graph.add_edge("route", "result")
    graph.add_edge("result", _graph_end)
    return graph.compile()


class LangGraphClassifierWorkflow:
    def __init__(self, dependencies: ClassifierDependencies) -> None:
        self._graph = build_classifier_graph(dependencies)

    async def classify(self, request: ClassificationRequest) -> ClassificationResult:
        state = await self._graph.ainvoke({"request": request})
        return _classification_result(state)
