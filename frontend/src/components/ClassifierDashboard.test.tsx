import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ClassifierDashboard } from "@/components/ClassifierDashboard";

const demoCases = [
  {
    demo_case_id: "stage8-data-analyst-strong",
    role: "data_analyst",
    scenario: "strong",
    candidate_reference: "candidate-demo-001",
    cv_profile_id: "cv-demo-001",
    cv_summary: "Hồ sơ phân tích dữ liệu có dự án thực hành.",
    job_profile_id: "job-demo-001",
    job_title: "Junior Data Analyst",
    evidence: [
      {
        evidence_id: "evidence-demo-001",
        section: "projects",
        text: "Xây dashboard Power BI và kiểm tra số liệu bằng SQL.",
        is_verified: false,
      },
    ],
    criteria: [
      {
        criterion_id: "mandatory-requirements",
        title: "Yêu cầu bắt buộc",
        weight: "30",
      },
    ],
  },
];

const classificationResult = {
  schema_version: "1.1.0",
  classification_result_id: "result-demo-001",
  request_id: "request-demo-001",
  cv_profile_id: "cv-demo-001",
  job_profile_id: "job-demo-001",
  proposed_decision: "pass",
  scores: {
    l1: { value: "90", status: "available", reason: null },
    l2: { value: "82", status: "available", reason: null },
    l3: { value: "88", status: "available", reason: null },
    final_score: "87.60",
  },
  criterion_assessments: [
    {
      criterion_id: "mandatory-requirements",
      score: "28",
      evidence_status: "satisfied",
      evidence_ids: ["evidence-demo-001"],
      rationale: "Có thông tin trực tiếp cho yêu cầu bắt buộc.",
    },
  ],
  strengths: ["Có dự án phù hợp."],
  risks: [],
  warnings: [],
  confidence: "0.90",
  quality_gate: { requires_review: false, reasons: [] },
  versions: {
    configuration_version: "3.0.0",
    prompt_version: "prompt-v15",
    llm_provider_identifier: "openai",
    llm_model_identifier: "gpt-5.4-mini-2026-03-17",
  },
  created_at: "2026-08-08T10:00:00+07:00",
};

const approvedDecision = {
  schema_version: "1.0.0",
  approved_decision_id: "approved-demo-001",
  classification_result_id: "result-demo-001",
  approval_status: "approved",
  proposed_decision: "pass",
  final_decision: "pass",
  reviewer_reference: "reviewer-stage-eight",
  decision_reason: "Người duyệt đã kiểm tra kết quả.",
  override_reason: null,
  decided_at: "2026-08-08T10:05:00+07:00",
};

function jsonResponse(value: unknown, status = 200): Response {
  return new Response(JSON.stringify(value), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function requestUrl(input: string | URL | Request): string {
  if (typeof input === "string") {
    return input;
  }
  return input instanceof URL ? input.toString() : input.url;
}

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("ClassifierDashboard", () => {
  it("classifies, displays evidence, approves and retrieves audit history", async () => {
    let decisionSaved = false;
    const fetchMock = vi.fn(async (input: string | URL | Request, init?: RequestInit) => {
      const url = requestUrl(input);
      if (url === "/api/demo-cases") {
        return jsonResponse(demoCases);
      }
      if (url === "/api/health?execution_mode=offline") {
        return jsonResponse({ status: "ok" });
      }
      if (url === "/api/classifications" && init?.method === "POST") {
        return jsonResponse(classificationResult, 201);
      }
      if (url.includes("/decisions?execution_mode=offline") && init?.method === "POST") {
        decisionSaved = true;
        return jsonResponse(approvedDecision, 201);
      }
      if (url.includes("/decisions?execution_mode=offline")) {
        return jsonResponse(decisionSaved ? [approvedDecision] : []);
      }
      throw new Error(`Unexpected request: ${url}`);
    });
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();

    render(<ClassifierDashboard />);

    expect(screen.queryByText("Bản nghiên cứu có human review.")).not.toBeInTheDocument();
    expect(screen.queryByLabelText("Giới hạn hệ thống")).not.toBeInTheDocument();
    expect(await screen.findByText("Backend: Đang hoạt động")).toBeInTheDocument();
    expect(screen.getByText("Junior Data Analyst")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Chạy phân loại offline" }));

    expect(await screen.findByText("87.60")).toBeInTheDocument();
    expect(screen.getByText("Có thông tin trực tiếp cho yêu cầu bắt buộc.")).toBeInTheDocument();
    expect(
      screen.getAllByText("Xây dashboard Power BI và kiểm tra số liệu bằng SQL.").length,
    ).toBeGreaterThan(0);
    expect(screen.getByRole("button", { name: "Phê duyệt đề xuất" })).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Phê duyệt đề xuất" }));

    expect(await screen.findByText("Đã phê duyệt")).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/classifications/result-demo-001/decisions?execution_mode=offline",
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("shows backend errors and leaves the review panel closed", async () => {
    const fetchMock = vi.fn(async (input: string | URL | Request, init?: RequestInit) => {
      const url = requestUrl(input);
      if (url === "/api/demo-cases") {
        return jsonResponse(demoCases);
      }
      if (url === "/api/health?execution_mode=offline") {
        return jsonResponse({ status: "ok" });
      }
      if (url === "/api/classifications" && init?.method === "POST") {
        return jsonResponse({ detail: "Classifier tạm thời không hoạt động." }, 503);
      }
      throw new Error(`Unexpected request: ${url}`);
    });
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();

    render(<ClassifierDashboard />);
    await screen.findByText("Backend: Đang hoạt động");
    await user.click(screen.getByRole("button", { name: "Chạy phân loại offline" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Classifier tạm thời không hoạt động.",
    );
    expect(screen.queryByText("Human review và lịch sử quyết định")).not.toBeInTheDocument();
  });

  it("keeps demo evidence visible when the backend health check fails", async () => {
    const fetchMock = vi.fn(async (input: string | URL | Request) => {
      const url = requestUrl(input);
      if (url === "/api/demo-cases") {
        return jsonResponse(demoCases);
      }
      if (url === "/api/health?execution_mode=offline") {
        return jsonResponse({ detail: "Backend chưa được cấu hình." }, 500);
      }
      throw new Error(`Unexpected request: ${url}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<ClassifierDashboard />);

    expect(await screen.findByText("Backend: Mất kết nối")).toBeInTheDocument();
    expect(
      screen.getByRole("option", { name: /candidate-demo-001/ }),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Xây dashboard Power BI và kiểm tra số liệu bằng SQL."),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Chạy phân loại offline" })).toBeDisabled();
  });

  it("requires cost confirmation and routes a real LLM run explicitly", async () => {
    const fetchMock = vi.fn(async (input: string | URL | Request, init?: RequestInit) => {
      const url = requestUrl(input);
      if (url === "/api/demo-cases") {
        return jsonResponse(demoCases);
      }
      if (url === "/api/health?execution_mode=offline") {
        return jsonResponse({ status: "ok" });
      }
      if (url === "/api/health?execution_mode=llm") {
        return jsonResponse({ status: "ok" });
      }
      if (url === "/api/classifications" && init?.method === "POST") {
        return jsonResponse(classificationResult, 201);
      }
      if (url.includes("/decisions?execution_mode=llm")) {
        return jsonResponse([]);
      }
      throw new Error(`Unexpected request: ${url}`);
    });
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();

    render(<ClassifierDashboard />);
    await screen.findByText("Backend: Đang hoạt động");
    await user.selectOptions(screen.getByLabelText("Chế độ L3"), "llm");
    await screen.findByText("Tôi xác nhận lần chạy này có thể phát sinh phí API.");
    const runButton = screen.getByRole("button", { name: "Chạy bằng LLM thật" });
    expect(runButton).toBeDisabled();

    await user.click(screen.getByLabelText("Tôi xác nhận lần chạy này có thể phát sinh phí API."));
    expect(runButton).toBeEnabled();
    await user.click(runButton);

    expect(await screen.findByText("gpt-5.4-mini-2026-03-17", { exact: false })).toBeInTheDocument();
    const classificationCall = fetchMock.mock.calls.find(
      ([input]) => requestUrl(input) === "/api/classifications",
    );
    const requestBody = JSON.parse(String(classificationCall?.[1]?.body)) as Record<
      string,
      unknown
    >;
    expect(requestBody.execution_mode).toBe("llm");
  });
});
