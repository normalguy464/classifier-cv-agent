from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.api.dependencies import (
    ApplicationContainer,
    get_container,
    require_api_key,
)
from backend.app.contracts import ApprovedDecision

router = APIRouter(
    prefix="/v1/classifications",
    tags=["decisions"],
    dependencies=[Depends(require_api_key)],
)


@router.post(
    "/{classification_result_id}/decisions",
    response_model=ApprovedDecision,
    status_code=status.HTTP_201_CREATED,
)
async def record_decision(
    classification_result_id: str,
    decision: ApprovedDecision,
    container: Annotated[ApplicationContainer, Depends(get_container)],
) -> ApprovedDecision:
    if decision.classification_result_id != classification_result_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Path and decision classification_result_id must match.",
        )
    return await container.review_decision.record(decision)


@router.get(
    "/{classification_result_id}/decisions",
    response_model=list[ApprovedDecision],
)
async def list_decisions(
    classification_result_id: str,
    container: Annotated[ApplicationContainer, Depends(get_container)],
) -> tuple[ApprovedDecision, ...]:
    return await container.review_decision.history(classification_result_id)
