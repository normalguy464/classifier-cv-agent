from __future__ import annotations

from datetime import UTC, datetime

import httpx
import pytest
from pydantic import SecretStr

from backend.app.api.app import create_app
from backend.app.api.dependencies import ApplicationContainer
from backend.app.application.classify_candidate import ClassifyCandidate
from backend.app.application.review_decision import ReviewClassificationDecision
from backend.app.contracts import ClassificationRequest, ClassificationResult
from backend.app.infrastructure.persistence.memory import InMemoryClassifierRepository
from tests.contract.test_contracts import valid_request, valid_result

API_KEY = "integration-test-key"
API_HEADERS = {"X-Classifier-API-Key": API_KEY}


class FixedWorkflow:
    def __init__(self, result: ClassificationResult) -> None:
        self._result = result

    async def classify(self, request: ClassificationRequest) -> ClassificationResult:
        return self._result


def build_test_client(
    api_key: SecretStr | None = SecretStr(API_KEY),
) -> httpx.AsyncClient:
    repository = InMemoryClassifierRepository()
    container = ApplicationContainer(
        classify_candidate=ClassifyCandidate(FixedWorkflow(valid_result()), repository),
        review_decision=ReviewClassificationDecision(repository),
        api_key=api_key,
    )
    application = create_app(container)
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=application),
        base_url="http://classifier.test",
    )


def approved_decision_payload() -> dict[str, object]:
    return {
        "schema_version": "1.0.0",
        "approved_decision_id": "approved-api-001",
        "classification_result_id": "result-001",
        "approval_status": "approved",
        "proposed_decision": "pass",
        "final_decision": "pass",
        "reviewer_reference": "reviewer-001",
        "decision_reason": "The reviewer confirmed the classification.",
        "override_reason": None,
        "decided_at": datetime.now(UTC).isoformat(),
    }


@pytest.mark.asyncio
async def test_health_endpoint_is_available_without_authentication() -> None:
    async with build_test_client() as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_classify_get_approve_and_retrieve_audit_history() -> None:
    async with build_test_client() as client:
        classify_response = await client.post(
            "/v1/classifications",
            headers=API_HEADERS,
            json=valid_request().model_dump(mode="json"),
        )

        assert classify_response.status_code == 201
        assert classify_response.json()["schema_version"] == "1.1.0"
        assert classify_response.json()["proposed_decision"] == "pass"

        get_response = await client.get(
            "/v1/classifications/result-001",
            headers=API_HEADERS,
        )
        decision_response = await client.post(
            "/v1/classifications/result-001/decisions",
            headers=API_HEADERS,
            json=approved_decision_payload(),
        )
        history_response = await client.get(
            "/v1/classifications/result-001/decisions",
            headers=API_HEADERS,
        )

    assert get_response.status_code == 200
    assert decision_response.status_code == 201
    assert history_response.status_code == 200
    assert len(history_response.json()) == 1
    assert history_response.json()[0]["approved_decision_id"] == "approved-api-001"


@pytest.mark.asyncio
async def test_api_rejects_missing_and_invalid_authentication() -> None:
    async with build_test_client() as client:
        payload = valid_request().model_dump(mode="json")

        missing_response = await client.post("/v1/classifications", json=payload)
        invalid_response = await client.post(
            "/v1/classifications",
            headers={"X-Classifier-API-Key": "wrong"},
            json=payload,
        )

    assert missing_response.status_code == 401
    assert invalid_response.status_code == 401


@pytest.mark.asyncio
async def test_api_returns_service_unavailable_when_authentication_is_not_configured() -> None:
    async with build_test_client(api_key=None) as client:
        response = await client.post(
            "/v1/classifications",
            headers=API_HEADERS,
            json=valid_request().model_dump(mode="json"),
        )

    assert response.status_code == 503


@pytest.mark.asyncio
async def test_api_rejects_contract_payload_with_protected_field() -> None:
    payload = valid_request().model_dump(mode="json")
    payload["cv_profile"]["age"] = 22

    async with build_test_client() as client:
        response = await client.post(
            "/v1/classifications",
            headers=API_HEADERS,
            json=payload,
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_api_maps_missing_result_and_duplicate_persistence_errors() -> None:
    async with build_test_client() as client:
        missing_response = await client.get(
            "/v1/classifications/result-missing",
            headers=API_HEADERS,
        )
        payload = valid_request().model_dump(mode="json")
        first_response = await client.post(
            "/v1/classifications",
            headers=API_HEADERS,
            json=payload,
        )
        duplicate_response = await client.post(
            "/v1/classifications",
            headers=API_HEADERS,
            json=payload,
        )

    assert missing_response.status_code == 404
    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409


@pytest.mark.asyncio
async def test_api_rejects_decision_with_mismatched_path_identifier() -> None:
    async with build_test_client() as client:
        await client.post(
            "/v1/classifications",
            headers=API_HEADERS,
            json=valid_request().model_dump(mode="json"),
        )

        response = await client.post(
            "/v1/classifications/result-other/decisions",
            headers=API_HEADERS,
            json=approved_decision_payload(),
        )

    assert response.status_code == 422
