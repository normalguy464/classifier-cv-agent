import { NextRequest } from "next/server";
import { beforeEach, describe, expect, it, vi } from "vitest";

const { requestBackend } = vi.hoisted(() => ({ requestBackend: vi.fn() }));

vi.mock("@/lib/server/backend", async () => {
  const actual = await vi.importActual<typeof import("@/lib/server/backend")>(
    "@/lib/server/backend",
  );
  return { ...actual, requestBackend };
});

import { GET } from "@/app/api/health/route";

beforeEach(() => {
  requestBackend.mockReset();
});

describe("health route", () => {
  it.each(["offline", "llm"] as const)("checks the selected %s backend", async (mode) => {
    requestBackend.mockResolvedValue({ status: "ok" });
    const request = new NextRequest(
      `http://frontend.test/api/health?execution_mode=${mode}`,
    );

    const response = await GET(request);

    expect(response.status).toBe(200);
    expect(requestBackend).toHaveBeenCalledWith("/health", undefined, mode);
  });

  it("rejects a missing mode instead of guessing a backend", async () => {
    const response = await GET(new NextRequest("http://frontend.test/api/health"));

    expect(response.status).toBe(400);
    expect(requestBackend).not.toHaveBeenCalled();
  });
});
