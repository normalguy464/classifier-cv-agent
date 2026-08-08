import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { requestBackend } from "@/lib/server/backend";

function jsonResponse(value: unknown): Response {
  return new Response(JSON.stringify(value), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}

const originalEnvironment = { ...process.env };

beforeEach(() => {
  process.env = { ...originalEnvironment };
  process.env.CLASSIFIER_OFFLINE_BACKEND_URL = "http://offline.test:8000";
  process.env.CLASSIFIER_OFFLINE_BACKEND_API_KEY = "offline-key";
  process.env.CLASSIFIER_LLM_BACKEND_URL = "http://llm.test:8001";
  process.env.CLASSIFIER_LLM_BACKEND_API_KEY = "llm-key";
});

afterEach(() => {
  process.env = { ...originalEnvironment };
  vi.unstubAllGlobals();
});

describe("requestBackend", () => {
  it.each([
    ["offline", "http://offline.test:8000/health", "offline-key"],
    ["llm", "http://llm.test:8001/health", "llm-key"],
  ] as const)("routes %s mode to its isolated backend", async (mode, url, apiKey) => {
    const fetchMock = vi.fn(
      async (input: string | URL | Request, init?: RequestInit) => {
        void input;
        void init;
        return jsonResponse({ status: "ok" });
      },
    );
    vi.stubGlobal("fetch", fetchMock);

    await requestBackend("/health", undefined, mode);

    const [calledUrl, init] = fetchMock.mock.calls[0] ?? [];
    expect(calledUrl).toBe(url);
    expect(new Headers(init?.headers).get("X-Classifier-API-Key")).toBe(apiKey);
  });

  it("does not silently fall back to offline when LLM configuration is missing", async () => {
    delete process.env.CLASSIFIER_LLM_BACKEND_URL;
    delete process.env.CLASSIFIER_LLM_BACKEND_API_KEY;
    delete process.env.CLASSIFIER_API_KEY;
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);

    await expect(requestBackend("/health", undefined, "llm")).rejects.toThrow(
      "CLASSIFIER_LLM_BACKEND_API_KEY",
    );
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("uses the shared backend API key for LLM mode when no override is configured", async () => {
    delete process.env.CLASSIFIER_LLM_BACKEND_API_KEY;
    process.env.CLASSIFIER_API_KEY = "shared-backend-key";
    const fetchMock = vi.fn(async () => jsonResponse({ status: "ok" }));
    vi.stubGlobal("fetch", fetchMock);

    await requestBackend("/health", undefined, "llm");

    const [, init] = fetchMock.mock.calls[0] ?? [];
    expect(new Headers(init?.headers).get("X-Classifier-API-Key")).toBe(
      "shared-backend-key",
    );
  });
});
