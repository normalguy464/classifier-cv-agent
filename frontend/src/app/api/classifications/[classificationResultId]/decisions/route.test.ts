import { NextRequest } from "next/server";
import { beforeEach, describe, expect, it, vi } from "vitest";

const { requestBackend } = vi.hoisted(() => ({ requestBackend: vi.fn() }));

vi.mock("@/lib/server/backend", async () => {
  const actual = await vi.importActual<typeof import("@/lib/server/backend")>(
    "@/lib/server/backend",
  );
  return { ...actual, requestBackend };
});

import { POST } from "@/app/api/classifications/[classificationResultId]/decisions/route";

function context(resultId = "result-route-001") {
  return { params: Promise.resolve({ classificationResultId: resultId }) };
}

function decisionRequest(
  payload: Record<string, unknown>,
  executionMode = "offline",
): NextRequest {
  return new NextRequest(
    `http://frontend.test/api/classifications/result-route-001/decisions?execution_mode=${executionMode}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    },
  );
}

beforeEach(() => {
  requestBackend.mockReset();
});

describe("decision route", () => {
  it("builds an approval contract from the stored proposed decision", async () => {
    requestBackend
      .mockResolvedValueOnce({ proposed_decision: "pass" })
      .mockResolvedValueOnce({ approved_decision_id: "approved-route-001" });

    const response = await POST(
      decisionRequest({
        final_decision: "pass",
        reviewer_reference: "reviewer-route-001",
        decision_reason: "Đã kiểm tra đầy đủ.",
        override_reason: null,
      }),
      context(),
    );

    expect(response.status).toBe(201);
    const secondCall = requestBackend.mock.calls[1];
    const init = secondCall?.[1] as RequestInit;
    const payload = JSON.parse(String(init.body)) as Record<string, unknown>;
    expect(payload.approval_status).toBe("approved");
    expect(payload.proposed_decision).toBe("pass");
    expect(payload.final_decision).toBe("pass");
    expect(payload.override_reason).toBeNull();
    expect(requestBackend.mock.calls[0]?.[2]).toBe("offline");
    expect(requestBackend.mock.calls[1]?.[2]).toBe("offline");
  });

  it("requires an override reason for Needs Review and rejects malformed identifiers", async () => {
    requestBackend.mockResolvedValueOnce({ proposed_decision: "needs_review" });

    const missingReasonResponse = await POST(
      decisionRequest({
        final_decision: "waitlist",
        reviewer_reference: "reviewer-route-001",
        decision_reason: "Cần quyết định cuối.",
        override_reason: null,
      }),
      context(),
    );
    const malformedIdResponse = await POST(
      decisionRequest({
        final_decision: "waitlist",
        reviewer_reference: "reviewer-route-001",
        decision_reason: "Cần quyết định cuối.",
        override_reason: "Đã xem xét thủ công.",
      }),
      context("invalid/id"),
    );

    expect(missingReasonResponse.status).toBe(400);
    expect(await missingReasonResponse.json()).toEqual({
      detail: "Phải nhập lý do khi thay đổi quyết định đề xuất.",
    });
    expect(malformedIdResponse.status).toBe(400);
  });

  it("keeps result lookup and decision persistence on the selected LLM backend", async () => {
    requestBackend
      .mockResolvedValueOnce({ proposed_decision: "pass" })
      .mockResolvedValueOnce({ approved_decision_id: "approved-route-llm" });

    const response = await POST(
      decisionRequest(
        {
          final_decision: "pass",
          reviewer_reference: "reviewer-route-llm",
          decision_reason: "Đã kiểm tra kết quả LLM.",
          override_reason: null,
        },
        "llm",
      ),
      context(),
    );

    expect(response.status).toBe(201);
    expect(requestBackend.mock.calls[0]?.[2]).toBe("llm");
    expect(requestBackend.mock.calls[1]?.[2]).toBe("llm");
  });
});
