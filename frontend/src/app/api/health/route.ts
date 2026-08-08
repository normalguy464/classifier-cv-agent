import { NextRequest, NextResponse } from "next/server";

import { requestBackend, RouteInputError, routeErrorResponse } from "@/lib/server/backend";
import { DemoExecutionMode, parseDemoExecutionMode } from "@/lib/contracts";

export async function GET(request: NextRequest): Promise<NextResponse> {
  try {
    let executionMode: DemoExecutionMode;
    try {
      executionMode = parseDemoExecutionMode(
        request.nextUrl.searchParams.get("execution_mode"),
      );
    } catch (error) {
      throw new RouteInputError(
        error instanceof Error ? error.message : "execution_mode không hợp lệ.",
      );
    }
    const payload = await requestBackend("/health", undefined, executionMode);
    return NextResponse.json(payload);
  } catch (error) {
    return routeErrorResponse(error);
  }
}
