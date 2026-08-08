import "server-only";

import { NextResponse } from "next/server";

import { DemoExecutionMode } from "@/lib/contracts";

export class BackendApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "BackendApiError";
    this.status = status;
  }
}

export class RouteInputError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "RouteInputError";
  }
}

function requiredEnvironmentValue(name: string, fallback?: string): string {
  const value = process.env[name] ?? fallback;
  if (value === undefined || value.trim() === "") {
    throw new Error(`${name} chưa được cấu hình cho frontend server.`);
  }
  return value.trim();
}

function backendBaseUrl(executionMode: DemoExecutionMode): string {
  const configured =
    executionMode === "offline"
      ? requiredEnvironmentValue(
          "CLASSIFIER_OFFLINE_BACKEND_URL",
          process.env.CLASSIFIER_BACKEND_URL ?? "http://127.0.0.1:8000",
        )
      : requiredEnvironmentValue("CLASSIFIER_LLM_BACKEND_URL", "http://127.0.0.1:8001");
  const parsed = new URL(configured);
  if (parsed.protocol !== "http:" && parsed.protocol !== "https:") {
    throw new Error("Backend URL phải sử dụng HTTP hoặc HTTPS.");
  }
  return parsed.toString().replace(/\/$/, "");
}

function backendApiKey(executionMode: DemoExecutionMode): string {
  return executionMode === "offline"
    ? requiredEnvironmentValue(
        "CLASSIFIER_OFFLINE_BACKEND_API_KEY",
        process.env.CLASSIFIER_API_KEY,
      )
    : requiredEnvironmentValue(
        "CLASSIFIER_LLM_BACKEND_API_KEY",
        process.env.CLASSIFIER_API_KEY,
      );
}

function errorDetail(value: unknown, fallback: string): string {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    return fallback;
  }
  const detail = (value as Record<string, unknown>).detail;
  return typeof detail === "string" && detail.trim() !== "" ? detail : fallback;
}

export async function requestBackend(
  path: string,
  init?: RequestInit,
  executionMode: DemoExecutionMode = "offline",
): Promise<unknown> {
  const headers = new Headers(init?.headers);
  headers.set("Accept", "application/json");
  headers.set("X-Classifier-API-Key", backendApiKey(executionMode));
  if (init?.body !== undefined) {
    headers.set("Content-Type", "application/json");
  }
  const response = await fetch(`${backendBaseUrl(executionMode)}${path}`, {
    ...init,
    headers,
    cache: "no-store",
  });
  let payload: unknown = null;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }
  if (!response.ok) {
    throw new BackendApiError(
      response.status,
      errorDetail(payload, `Backend trả về HTTP ${response.status}.`),
    );
  }
  return payload;
}

export function routeErrorResponse(error: unknown): NextResponse {
  if (error instanceof BackendApiError) {
    return NextResponse.json({ detail: error.message }, { status: error.status });
  }
  if (error instanceof RouteInputError) {
    return NextResponse.json({ detail: error.message }, { status: 400 });
  }
  const message = error instanceof Error ? error.message : "Lỗi server không xác định.";
  return NextResponse.json({ detail: message }, { status: 500 });
}
