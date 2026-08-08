from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import cast
from uuid import uuid4

import httpx
import pytest
from pydantic import SecretStr

from backend.app.contracts import ClassificationDecision, FinalDecision
from backend.app.core.settings import RuntimeSettings, StorageBackend
from backend.app.infrastructure.bootstrap import build_application

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEMO_CASE_PATH = (
    REPOSITORY_ROOT / "frontend" / "src" / "data" / "demo-cases" / "stage8-data-analyst-strong.json"
)
API_KEY = "stage-eight-integration-key"
API_HEADERS = {"X-Classifier-API-Key": API_KEY}


@pytest.mark.asyncio
async def test_stage8_demo_classifies_reviews_and_retrieves_audit_history() -> None:
    settings = RuntimeSettings(
        classifier_api_key=SecretStr(API_KEY),
        classifier_storage_backend=StorageBackend.MEMORY,
        classifier_config_directory=REPOSITORY_ROOT / "configs" / "runtime" / "five_role_v2",
        classifier_llm_adapter="deterministic_fake",
    )
    application = build_application(settings)
    raw_case = cast(
        dict[str, object],
        json.loads(DEMO_CASE_PATH.read_text(encoding="utf-8")),
    )
    request_payload = cast(dict[str, object], raw_case["request"])
    request_payload["request_id"] = f"request-{uuid4()}"

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=application),
        base_url="http://classifier.test",
    ) as client:
        classification_response = await client.post(
            "/v1/classifications",
            headers=API_HEADERS,
            json=request_payload,
        )

        assert classification_response.status_code == 201
        result = cast(dict[str, object], classification_response.json())
        result_id = cast(str, result["classification_result_id"])
        proposed_decision = ClassificationDecision(cast(str, result["proposed_decision"]))
        if proposed_decision is ClassificationDecision.NEEDS_REVIEW:
            approval_status = "overridden"
            final_decision = FinalDecision.WAITLIST
            override_reason: str | None = "Người duyệt đã xử lý điều kiện cần xem xét."
        else:
            approval_status = "approved"
            final_decision = FinalDecision(proposed_decision.value)
            override_reason = None
        decision_payload = {
            "schema_version": "1.0.0",
            "approved_decision_id": f"approved-{uuid4()}",
            "classification_result_id": result_id,
            "approval_status": approval_status,
            "proposed_decision": proposed_decision.value,
            "final_decision": final_decision.value,
            "reviewer_reference": "reviewer-stage-eight",
            "decision_reason": "Người duyệt đã kiểm tra kết quả phân loại.",
            "override_reason": override_reason,
            "decided_at": datetime.now(UTC).isoformat(),
        }
        decision_response = await client.post(
            f"/v1/classifications/{result_id}/decisions",
            headers=API_HEADERS,
            json=decision_payload,
        )
        history_response = await client.get(
            f"/v1/classifications/{result_id}/decisions",
            headers=API_HEADERS,
        )

    assert decision_response.status_code == 201
    assert history_response.status_code == 200
    history = cast(list[dict[str, object]], history_response.json())
    assert len(history) == 1
    assert history[0]["classification_result_id"] == result_id
    assert history[0]["final_decision"] == final_decision.value
