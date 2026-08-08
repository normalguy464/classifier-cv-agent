from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from backend.app.api.dependencies import (
    ApplicationContainer,
    get_container,
    require_api_key,
)
from backend.app.contracts import ClassificationRequest, ClassificationResult

router = APIRouter(
    prefix="/v1/classifications",
    tags=["classifications"],
    dependencies=[Depends(require_api_key)],
)


@router.post(
    "",
    response_model=ClassificationResult,
    status_code=status.HTTP_201_CREATED,
)
async def classify_candidate(
    request: ClassificationRequest,
    container: Annotated[ApplicationContainer, Depends(get_container)],
) -> ClassificationResult:
    return await container.classify_candidate.execute(request)


@router.get("/{classification_result_id}", response_model=ClassificationResult)
async def get_classification(
    classification_result_id: str,
    container: Annotated[ApplicationContainer, Depends(get_container)],
) -> ClassificationResult:
    return await container.review_decision.get_result(classification_result_id)
