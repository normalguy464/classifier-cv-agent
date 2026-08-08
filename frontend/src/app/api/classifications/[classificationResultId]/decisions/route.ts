import { randomUUID } from "node:crypto";

import { NextRequest, NextResponse } from "next/server";

import { requestBackend, RouteInputError, routeErrorResponse } from "@/lib/server/backend";
import { DemoExecutionMode, parseDemoExecutionMode } from "@/lib/contracts";

type RouteContext = {
  params: Promise<{ classificationResultId: string }>;
};

const resultIdentifierPattern = /^[a-z0-9][a-z0-9-]{2,63}$/;
const finalDecisions = new Set(["pass", "waitlist", "reject"]);

function resultIdentifier(value: string): string {
  if (!resultIdentifierPattern.test(value)) {
    throw new RouteInputError("classification_result_id không hợp lệ.");
  }
  return value;
}

function executionMode(request: NextRequest): DemoExecutionMode {
  try {
    return parseDemoExecutionMode(request.nextUrl.searchParams.get("execution_mode"));
  } catch (error) {
    throw new RouteInputError(
      error instanceof Error ? error.message : "execution_mode không hợp lệ.",
    );
  }
}

function asRecord(value: unknown, label: string): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new RouteInputError(`${label} không đúng cấu trúc.`);
  }
  return value as Record<string, unknown>;
}

function nonEmptyString(value: unknown, label: string): string {
  if (typeof value !== "string" || value.trim() === "") {
    throw new RouteInputError(`${label} không được để trống.`);
  }
  return value.trim();
}

function decisionPayload(
  input: unknown,
  classificationResultId: string,
  proposedDecision: string,
): Record<string, unknown> {
  const record = asRecord(input, "decision");
  const finalDecision = nonEmptyString(record.final_decision, "final_decision");
  if (!finalDecisions.has(finalDecision)) {
    throw new RouteInputError("final_decision không hợp lệ.");
  }
  const reviewerReference = nonEmptyString(record.reviewer_reference, "reviewer_reference");
  if (!resultIdentifierPattern.test(reviewerReference)) {
    throw new RouteInputError(
      "reviewer_reference chỉ được chứa chữ thường, số và dấu gạch ngang.",
    );
  }
  const decisionReason = nonEmptyString(record.decision_reason, "decision_reason");
  const isApproved = proposedDecision !== "needs_review" && finalDecision === proposedDecision;
  const overrideReason =
    record.override_reason === null || record.override_reason === undefined
      ? null
      : nonEmptyString(record.override_reason, "override_reason");
  if (!isApproved && overrideReason === null) {
    throw new RouteInputError("Phải nhập lý do khi thay đổi quyết định đề xuất.");
  }
  return {
    schema_version: "1.0.0",
    approved_decision_id: `approved-${randomUUID()}`,
    classification_result_id: classificationResultId,
    approval_status: isApproved ? "approved" : "overridden",
    proposed_decision: proposedDecision,
    final_decision: finalDecision,
    reviewer_reference: reviewerReference,
    decision_reason: decisionReason,
    override_reason: isApproved ? null : overrideReason,
    decided_at: new Date().toISOString(),
  };
}

export async function GET(
  request: NextRequest,
  context: RouteContext,
): Promise<NextResponse> {
  try {
    const { classificationResultId: rawResultId } = await context.params;
    const classificationResultId = resultIdentifier(rawResultId);
    const mode = executionMode(request);
    const payload = await requestBackend(
      `/v1/classifications/${encodeURIComponent(classificationResultId)}/decisions`,
      undefined,
      mode,
    );
    return NextResponse.json(payload);
  } catch (error) {
    return routeErrorResponse(error);
  }
}

export async function POST(
  request: NextRequest,
  context: RouteContext,
): Promise<NextResponse> {
  try {
    const { classificationResultId: rawResultId } = await context.params;
    const classificationResultId = resultIdentifier(rawResultId);
    const mode = executionMode(request);
    const storedResult = asRecord(
      await requestBackend(
        `/v1/classifications/${encodeURIComponent(classificationResultId)}`,
        undefined,
        mode,
      ),
      "classification result",
    );
    const proposedDecision = nonEmptyString(
      storedResult.proposed_decision,
      "proposed_decision",
    );
    const payload = await requestBackend(
      `/v1/classifications/${encodeURIComponent(classificationResultId)}/decisions`,
      {
        method: "POST",
        body: JSON.stringify(
          decisionPayload(
            await request.json(),
            classificationResultId,
            proposedDecision,
          ),
        ),
      },
      mode,
    );
    return NextResponse.json(payload, { status: 201 });
  } catch (error) {
    return routeErrorResponse(error);
  }
}
