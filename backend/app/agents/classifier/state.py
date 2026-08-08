from __future__ import annotations

from typing import TypedDict

from backend.app.contracts import ClassificationRequest, ClassificationResult
from backend.app.domain import AggregationResult, LevelAssessment, RoutingResult


class ClassifierState(TypedDict, total=False):
    request: ClassificationRequest
    l1: LevelAssessment
    l2: LevelAssessment
    l3: LevelAssessment
    aggregation: AggregationResult
    routing: RoutingResult
    result: ClassificationResult
