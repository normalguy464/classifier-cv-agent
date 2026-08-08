import { NextRequest, NextResponse } from "next/server";

import { requestBackend, RouteInputError, routeErrorResponse } from "@/lib/server/backend";
import { createDemoClassificationRequest } from "@/lib/server/demo-cases";
import { DemoExecutionMode, parseDemoExecutionMode } from "@/lib/contracts";

type DemoClassificationInput = {
  demoCaseId: string;
  executionMode: DemoExecutionMode;
};

function demoClassificationInput(value: unknown): DemoClassificationInput {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new RouteInputError("Request phân loại không đúng cấu trúc.");
  }
  const record = value as Record<string, unknown>;
  const demoCaseId = record.demo_case_id;
  if (typeof demoCaseId !== "string" || !/^stage8-[a-z0-9-]+$/.test(demoCaseId)) {
    throw new RouteInputError("demo_case_id không hợp lệ.");
  }
  try {
    return {
      demoCaseId,
      executionMode: parseDemoExecutionMode(record.execution_mode),
    };
  } catch (error) {
    throw new RouteInputError(error instanceof Error ? error.message : "execution_mode không hợp lệ.");
  }
}

export async function POST(request: NextRequest): Promise<NextResponse> {
  try {
    const input = demoClassificationInput(await request.json());
    const payload = await requestBackend(
      "/v1/classifications",
      {
        method: "POST",
        body: JSON.stringify(
          createDemoClassificationRequest(input.demoCaseId, input.executionMode),
        ),
      },
      input.executionMode,
    );
    return NextResponse.json(payload, { status: 201 });
  } catch (error) {
    return routeErrorResponse(error);
  }
}
