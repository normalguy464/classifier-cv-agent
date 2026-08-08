import { expect, test } from "@playwright/test";

const demoCases = [
  {
    demo_case_id: "stage8-data-analyst-strong",
    role: "data_analyst",
    scenario: "strong",
    candidate_reference: "candidate-e2e-001",
    cv_profile_id: "cv-e2e-001",
    cv_summary: "Hồ sơ demo cho kiểm thử trình duyệt.",
    job_profile_id: "job-e2e-001",
    job_title: "Junior Data Analyst",
    evidence: [
      {
        evidence_id: "evidence-e2e-001",
        section: "projects",
        text: "Dùng SQL và Power BI để kiểm tra chỉ số vận hành.",
        is_verified: false,
      },
    ],
    criteria: [
      { criterion_id: "mandatory-requirements", title: "Yêu cầu bắt buộc", weight: "30" },
    ],
  },
];

function result(proposedDecision: "pass" | "needs_review") {
  return {
    schema_version: "1.1.0",
    classification_result_id: `result-e2e-${proposedDecision.replace("_", "-")}`,
    request_id: "request-e2e-001",
    cv_profile_id: "cv-e2e-001",
    job_profile_id: "job-e2e-001",
    proposed_decision: proposedDecision,
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
        evidence_ids: ["evidence-e2e-001"],
        rationale: "Có thông tin trực tiếp cho yêu cầu bắt buộc.",
      },
    ],
    strengths: [],
    risks: [],
    warnings: [],
    confidence: "0.90",
    quality_gate: {
      requires_review: proposedDecision === "needs_review",
      reasons: proposedDecision === "needs_review" ? ["large-level-disagreement"] : [],
    },
    versions: { configuration_version: "3.0.0" },
    created_at: "2026-08-08T10:00:00+07:00",
  };
}

test("classify, inspect evidence, approve, override and retrieve audit history", async ({
  page,
}) => {
  let run = 0;
  const decisions: Record<string, unknown>[] = [];
  await page.route("**/api/demo-cases", (route) => route.fulfill({ json: demoCases }));
  await page.route("**/api/health?*", (route) => route.fulfill({ json: { status: "ok" } }));
  await page.route("**/api/classifications", async (route) => {
    if (route.request().method() !== "POST") {
      await route.fallback();
      return;
    }
    const proposedDecision = run === 0 ? "pass" : "needs_review";
    run += 1;
    await route.fulfill({ status: 201, json: result(proposedDecision) });
  });
  await page.route("**/api/classifications/*/decisions?*", async (route) => {
    if (route.request().method() === "POST") {
      const input = route.request().postDataJSON() as Record<string, unknown>;
      const isOverride = input.override_reason !== null;
      decisions.push({
        schema_version: "1.0.0",
        approved_decision_id: `approved-e2e-${decisions.length + 1}`,
        classification_result_id: run === 1 ? "result-e2e-pass" : "result-e2e-needs-review",
        approval_status: isOverride ? "overridden" : "approved",
        proposed_decision: isOverride ? "needs_review" : "pass",
        final_decision: input.final_decision,
        reviewer_reference: input.reviewer_reference,
        decision_reason: input.decision_reason,
        override_reason: input.override_reason,
        decided_at: "2026-08-08T10:05:00+07:00",
      });
      await route.fulfill({ status: 201, json: decisions.at(-1) });
      return;
    }
    await route.fulfill({ json: decisions.slice(-1) });
  });

  await page.goto("/");
  await expect(page.getByText("Backend: Đang hoạt động")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Chọn hồ sơ demo" })).toHaveCSS(
    "font-family",
    "Arial, Helvetica, sans-serif",
  );
  await expect(page.getByRole("heading", { name: "Kết quả phân loại" })).toHaveCSS(
    "font-family",
    "Arial, Helvetica, sans-serif",
  );
  await page.getByRole("button", { name: "Chạy phân loại offline" }).click();
  await expect(page.getByText("87.60")).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Human review và lịch sử quyết định" }),
  ).toHaveCSS("font-family", "Arial, Helvetica, sans-serif");
  await expect(page.getByText("Dùng SQL và Power BI để kiểm tra chỉ số vận hành.").first()).toBeAttached();
  await page.getByRole("button", { name: "Phê duyệt đề xuất" }).click();
  await expect(page.getByText("Đã phê duyệt")).toBeVisible();

  await page.getByRole("button", { name: "Chạy phân loại offline" }).click();
  await expect(page.getByText("Cần xem xét", { exact: true })).toBeVisible();
  await page.getByLabel("Lý do thay đổi đề xuất").fill("Đã kiểm tra mâu thuẫn thủ công.");
  await page.getByRole("button", { name: "Lưu quyết định thay đổi" }).click();
  await expect(page.getByText("Đã thay đổi")).toBeVisible();
  await expect(page.getByText("Lý do thay đổi: Đã kiểm tra mâu thuẫn thủ công.")).toBeVisible();
});
