import { NextRequest } from "next/server";
import { beforeEach, describe, expect, it, vi } from "vitest";

const { requestBackend } = vi.hoisted(() => ({ requestBackend: vi.fn() }));

vi.mock("@/lib/server/backend", async () => {
  const actual = await vi.importActual<typeof import("@/lib/server/backend")>(
    "@/lib/server/backend",
  );
  return { ...actual, requestBackend };
});

import { POST } from "@/app/api/classifications/route";

function classificationRequest(executionMode: unknown): NextRequest {
  return new NextRequest("http://frontend.test/api/classifications", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      demo_case_id: "stage8-data-analyst-strong",
      execution_mode: executionMode,
    }),
  });
}

beforeEach(() => {
  requestBackend.mockReset();
  process.env.CLASSIFIER_LLM_PROVIDER = "openai";
  process.env.CLASSIFIER_LLM_MODEL = "gpt-test-model";
});

describe("classification route", () => {
  it.each(["offline", "llm"] as const)(
    "routes %s without adding demo fields to the backend contract",
    async (executionMode) => {
      requestBackend.mockResolvedValue({ classification_result_id: "result-route-001" });

      const response = await POST(classificationRequest(executionMode));

      expect(response.status).toBe(201);
      expect(requestBackend).toHaveBeenCalledOnce();
      const [path, init, mode] = requestBackend.mock.calls[0] ?? [];
      const payload = JSON.parse(String((init as RequestInit).body)) as Record<string, unknown>;
      expect(path).toBe("/v1/classifications");
      expect(mode).toBe(executionMode);
      expect(payload).not.toHaveProperty("demo_case_id");
      expect(payload).not.toHaveProperty("execution_mode");
      const configuration = payload.configuration as Record<string, unknown>;
      const models = configuration.models as Record<string, unknown>;
      expect(models.llm_provider_identifier).toBe(
        executionMode === "llm" ? "openai" : "deterministic_fake",
      );
      expect(models.llm_model_identifier).toBe(
        executionMode === "llm" ? "gpt-test-model" : "deterministic-evidence-scorer-v1",
      );
    },
  );

  it("rejects unknown execution modes before contacting a backend", async () => {
    const response = await POST(classificationRequest("automatic"));

    expect(response.status).toBe(400);
    expect(requestBackend).not.toHaveBeenCalled();
  });
});
