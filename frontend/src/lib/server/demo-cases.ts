import "server-only";

import { randomUUID } from "node:crypto";

import dataAnalystStrong from "@/data/demo-cases/stage8-data-analyst-strong.json";
import dataEngineerConflict from "@/data/demo-cases/stage8-data-engineer-conflict.json";
import frontendModerate from "@/data/demo-cases/stage8-frontend-moderate.json";
import pythonBackendMissing from "@/data/demo-cases/stage8-python-backend-missing.json";
import qaExplicitFailure from "@/data/demo-cases/stage8-qa-explicit-failure.json";
import { DemoExecutionMode } from "@/lib/contracts";
import { RouteInputError } from "@/lib/server/backend";

type JsonRecord = Record<string, unknown>;

interface DemoCaseRecord {
  demo_case_id: string;
  role: string;
  scenario: string;
  request: JsonRecord;
}

function asRecord(value: unknown, label: string): JsonRecord {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new Error(`${label} không đúng cấu trúc.`);
  }
  return value as JsonRecord;
}

function asString(value: unknown, label: string): string {
  if (typeof value !== "string" || value.trim() === "") {
    throw new Error(`${label} phải là chuỗi không rỗng.`);
  }
  return value;
}

function parseDemoCase(value: unknown): DemoCaseRecord {
  const record = asRecord(value, "demo case");
  return {
    demo_case_id: asString(record.demo_case_id, "demo_case_id"),
    role: asString(record.role, "role"),
    scenario: asString(record.scenario, "scenario"),
    request: asRecord(record.request, "request"),
  };
}

const demoCases = [
  dataAnalystStrong,
  pythonBackendMissing,
  frontendModerate,
  qaExplicitFailure,
  dataEngineerConflict,
].map(parseDemoCase);

const demoCasesById = new Map(demoCases.map((item) => [item.demo_case_id, item]));

export function listDemoCases(): JsonRecord[] {
  return demoCases.map((item) => {
    const cvProfile = asRecord(item.request.cv_profile, "cv_profile");
    const jobProfile = asRecord(item.request.job_profile, "job_profile");
    const rubric = asRecord(item.request.rubric, "rubric");
    const rawEvidence = cvProfile.evidence;
    const rawCriteria = rubric.criteria;
    if (!Array.isArray(rawEvidence) || !Array.isArray(rawCriteria)) {
      throw new Error("Demo case thiếu evidence hoặc criteria.");
    }
    return {
      demo_case_id: item.demo_case_id,
      role: item.role,
      scenario: item.scenario,
      candidate_reference: asString(cvProfile.candidate_reference, "candidate_reference"),
      cv_profile_id: asString(cvProfile.cv_profile_id, "cv_profile_id"),
      cv_summary:
        cvProfile.summary === null ? null : asString(cvProfile.summary, "cv_profile.summary"),
      job_profile_id: asString(jobProfile.job_profile_id, "job_profile_id"),
      job_title: asString(jobProfile.title, "job_profile.title"),
      evidence: rawEvidence.map((value) => {
        const evidence = asRecord(value, "evidence");
        return {
          evidence_id: asString(evidence.evidence_id, "evidence_id"),
          section: asString(evidence.section, "evidence.section"),
          text: asString(evidence.text, "evidence.text"),
          is_verified: evidence.is_verified === true,
        };
      }),
      criteria: rawCriteria.map((value) => {
        const criterion = asRecord(value, "criterion");
        return {
          criterion_id: asString(criterion.criterion_id, "criterion_id"),
          title: asString(criterion.title, "criterion.title"),
          weight: criterion.weight,
        };
      }),
    };
  });
}

function requiredRuntimeEnvironmentValue(name: string): string {
  const value = process.env[name];
  if (value === undefined || value.trim() === "") {
    throw new Error(`${name} chưa được cấu hình cho frontend server.`);
  }
  return value.trim();
}

function selectLlmRuntime(request: JsonRecord): void {
  const configuration = asRecord(request.configuration, "configuration");
  const models = asRecord(configuration.models, "configuration.models");
  models.llm_provider_identifier = requiredRuntimeEnvironmentValue(
    "CLASSIFIER_LLM_PROVIDER",
  );
  models.llm_model_identifier = requiredRuntimeEnvironmentValue("CLASSIFIER_LLM_MODEL");
}

export function createDemoClassificationRequest(
  demoCaseId: string,
  executionMode: DemoExecutionMode = "offline",
): JsonRecord {
  const demoCase = demoCasesById.get(demoCaseId);
  if (demoCase === undefined) {
    throw new RouteInputError(`Không tìm thấy demo case: ${demoCaseId}`);
  }
  const request = structuredClone(demoCase.request);
  request.request_id = `request-${randomUUID()}`;
  if (executionMode === "llm") {
    selectLlmRuntime(request);
  }
  return request;
}
