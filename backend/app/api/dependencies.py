from __future__ import annotations

from dataclasses import dataclass
from hmac import compare_digest
from typing import Annotated, cast

from fastapi import Header, HTTPException, Request, status
from pydantic import SecretStr

from backend.app.application.classify_candidate import ClassifyCandidate
from backend.app.application.review_decision import ReviewClassificationDecision


@dataclass(frozen=True, slots=True)
class ApplicationContainer:
    classify_candidate: ClassifyCandidate
    review_decision: ReviewClassificationDecision
    api_key: SecretStr | None


def get_container(request: Request) -> ApplicationContainer:
    return cast(ApplicationContainer, request.app.state.container)


def require_api_key(
    request: Request,
    supplied_api_key: Annotated[
        str | None,
        Header(alias="X-Classifier-API-Key"),
    ] = None,
) -> None:
    expected = get_container(request).api_key
    if expected is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API authentication is not configured.",
        )
    if supplied_api_key is None or not compare_digest(
        supplied_api_key,
        expected.get_secret_value(),
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )
