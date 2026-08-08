import { describe, expect, it } from "vitest";

import {
  formatScore,
  parseApprovedDecisions,
  parseClassificationResult,
  parseDemoCases,
  parseDemoExecutionMode,
} from "@/lib/contracts";

function validResult(): Record<string, unknown> {
  return {
    schema_version: "1.1.0",
    classification_result_id: "result-test-001",
    request_id: "request-test-001",
    cv_profile_id: "cv-test-001",
    job_profile_id: "job-test-001",
    proposed_decision: "needs_review",
    scores: {
      l1: { value: "78", status: "available", reason: null },
      l2: { value: 64.5, status: "available", reason: null },
      l3: { value: null, status: "unavailable", reason: "Provider unavailable" },
      final_score: "70.25",
    },
    criterion_assessments: [
      {
        criterion_id: "mandatory-requirements",
        score: "24",
        evidence_status: "missing",
        evidence_ids: [],
        rationale: "Thiếu thông tin trực tiếp.",
      },
    ],
    strengths: ["Có dự án liên quan."],
    risks: ["Thiếu thông tin bắt buộc."],
    warnings: [],
    confidence: "0.80",
    quality_gate: { requires_review: true, reasons: ["missing-critical-evidence"] },
    versions: { configuration_version: "3.0.0", prompt_version: "prompt-v15" },
    created_at: "2026-08-08T10:00:00+07:00",
  };
}

describe("contract parsers", () => {
  it("parses valid classifier output with numeric strings and unavailable levels", () => {
    const result = parseClassificationResult(validResult());

    expect(result.proposed_decision).toBe("needs_review");
    expect(result.scores.l2.value).toBe(64.5);
    expect(result.scores.l3.status).toBe("unavailable");
    expect(formatScore(result.scores.final_score)).toBe("70.25");
    expect(formatScore(null)).toBe("Không có");
  });

  it("rejects invalid decisions, score values and malformed lists", () => {
    expect(() =>
      parseClassificationResult({ ...validResult(), proposed_decision: "unknown" }),
    ).toThrow("proposed_decision không hợp lệ");
    const invalidScore = validResult();
    invalidScore.scores = {
      ...(invalidScore.scores as Record<string, unknown>),
      final_score: "not-a-number",
    };
    expect(() => parseClassificationResult(invalidScore)).toThrow("điểm số hợp lệ");
    expect(() => parseDemoCases({})).toThrow("không đúng cấu trúc");
    expect(() => parseApprovedDecisions({})).toThrow("không đúng cấu trúc");
  });
  it("accepts only the two explicit demo execution modes", () => {
    expect(parseDemoExecutionMode("offline")).toBe("offline");
    expect(parseDemoExecutionMode("llm")).toBe("llm");
    expect(() => parseDemoExecutionMode("automatic")).toThrow("execution_mode");
    expect(() => parseDemoExecutionMode(null)).toThrow("execution_mode");
  });
});
