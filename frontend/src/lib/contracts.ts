export type ClassificationDecision = "pass" | "waitlist" | "reject" | "needs_review";
export type FinalDecision = "pass" | "waitlist" | "reject";
export type EvidenceStatus = "satisfied" | "unsatisfied" | "missing" | "conflicting";
export type DemoExecutionMode = "offline" | "llm";
export type ScoreValue = number | string;

export interface DemoEvidence {
  evidence_id: string;
  section: string;
  text: string;
  is_verified: boolean;
}

export interface DemoCriterion {
  criterion_id: string;
  title: string;
  weight: ScoreValue;
}

export interface DemoCaseSummary {
  demo_case_id: string;
  role: string;
  scenario: string;
  candidate_reference: string;
  cv_profile_id: string;
  cv_summary: string | null;
  job_profile_id: string;
  job_title: string;
  evidence: DemoEvidence[];
  criteria: DemoCriterion[];
}

export interface LevelScore {
  value: ScoreValue | null;
  status: "available" | "unavailable" | "invalid";
  reason: string | null;
}

export interface CriterionAssessment {
  criterion_id: string;
  score: ScoreValue;
  evidence_status: EvidenceStatus;
  evidence_ids: string[];
  rationale: string;
}

export interface ClassificationResult {
  schema_version: string;
  classification_result_id: string;
  request_id: string;
  cv_profile_id: string;
  job_profile_id: string;
  proposed_decision: ClassificationDecision;
  scores: {
    l1: LevelScore;
    l2: LevelScore;
    l3: LevelScore;
    final_score: ScoreValue | null;
  };
  criterion_assessments: CriterionAssessment[];
  strengths: string[];
  risks: string[];
  warnings: string[];
  confidence: ScoreValue | null;
  quality_gate: {
    requires_review: boolean;
    reasons: string[];
  };
  versions: Record<string, string>;
  created_at: string;
}

export interface ApprovedDecision {
  schema_version: string;
  approved_decision_id: string;
  classification_result_id: string;
  approval_status: "approved" | "overridden";
  proposed_decision: ClassificationDecision;
  final_decision: FinalDecision;
  reviewer_reference: string;
  decision_reason: string;
  override_reason: string | null;
  decided_at: string;
}

export interface DecisionSubmission {
  final_decision: FinalDecision;
  reviewer_reference: string;
  decision_reason: string;
  override_reason: string | null;
}

const classificationDecisions = new Set<ClassificationDecision>([
  "pass",
  "waitlist",
  "reject",
  "needs_review",
]);
const finalDecisions = new Set<FinalDecision>(["pass", "waitlist", "reject"]);
const evidenceStatuses = new Set<EvidenceStatus>([
  "satisfied",
  "unsatisfied",
  "missing",
  "conflicting",
]);

export function parseDemoExecutionMode(value: unknown): DemoExecutionMode {
  if (value !== "offline" && value !== "llm") {
    throw new Error("execution_mode phải là offline hoặc llm.");
  }
  return value;
}

function asRecord(value: unknown, label: string): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new Error(`${label} không đúng cấu trúc.`);
  }
  return value as Record<string, unknown>;
}

function asString(value: unknown, label: string): string {
  if (typeof value !== "string" || value.trim().length === 0) {
    throw new Error(`${label} phải là chuỗi không rỗng.`);
  }
  return value;
}

function asNullableString(value: unknown, label: string): string | null {
  return value === null ? null : asString(value, label);
}

function asBoolean(value: unknown, label: string): boolean {
  if (typeof value !== "boolean") {
    throw new Error(`${label} phải là boolean.`);
  }
  return value;
}

function asScore(value: unknown, label: string): ScoreValue {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === "string" && value.trim() !== "" && Number.isFinite(Number(value))) {
    return value;
  }
  throw new Error(`${label} phải là điểm số hợp lệ.`);
}

function asNullableScore(value: unknown, label: string): ScoreValue | null {
  return value === null ? null : asScore(value, label);
}

function asStringArray(value: unknown, label: string): string[] {
  if (!Array.isArray(value)) {
    throw new Error(`${label} phải là danh sách.`);
  }
  return value.map((item, index) => asString(item, `${label}[${index}]`));
}

function parseLevelScore(value: unknown, label: string): LevelScore {
  const record = asRecord(value, label);
  const status = asString(record.status, `${label}.status`);
  if (status !== "available" && status !== "unavailable" && status !== "invalid") {
    throw new Error(`${label}.status không hợp lệ.`);
  }
  return {
    value: asNullableScore(record.value, `${label}.value`),
    status,
    reason: asNullableString(record.reason, `${label}.reason`),
  };
}

function parseCriterionAssessment(value: unknown, index: number): CriterionAssessment {
  const record = asRecord(value, `criterion_assessments[${index}]`);
  const evidenceStatus = asString(
    record.evidence_status,
    `criterion_assessments[${index}].evidence_status`,
  );
  if (!evidenceStatuses.has(evidenceStatus as EvidenceStatus)) {
    throw new Error(`criterion_assessments[${index}].evidence_status không hợp lệ.`);
  }
  return {
    criterion_id: asString(record.criterion_id, `criterion_assessments[${index}].criterion_id`),
    score: asScore(record.score, `criterion_assessments[${index}].score`),
    evidence_status: evidenceStatus as EvidenceStatus,
    evidence_ids: asStringArray(
      record.evidence_ids,
      `criterion_assessments[${index}].evidence_ids`,
    ),
    rationale: asString(record.rationale, `criterion_assessments[${index}].rationale`),
  };
}

function parseVersions(value: unknown): Record<string, string> {
  const record = asRecord(value, "versions");
  return Object.fromEntries(
    Object.entries(record).map(([key, item]) => [key, asString(item, `versions.${key}`)]),
  );
}

export function parseClassificationResult(value: unknown): ClassificationResult {
  const record = asRecord(value, "classification result");
  const decision = asString(record.proposed_decision, "proposed_decision");
  if (!classificationDecisions.has(decision as ClassificationDecision)) {
    throw new Error("proposed_decision không hợp lệ.");
  }
  const scores = asRecord(record.scores, "scores");
  const qualityGate = asRecord(record.quality_gate, "quality_gate");
  if (!Array.isArray(record.criterion_assessments)) {
    throw new Error("criterion_assessments phải là danh sách.");
  }
  return {
    schema_version: asString(record.schema_version, "schema_version"),
    classification_result_id: asString(
      record.classification_result_id,
      "classification_result_id",
    ),
    request_id: asString(record.request_id, "request_id"),
    cv_profile_id: asString(record.cv_profile_id, "cv_profile_id"),
    job_profile_id: asString(record.job_profile_id, "job_profile_id"),
    proposed_decision: decision as ClassificationDecision,
    scores: {
      l1: parseLevelScore(scores.l1, "scores.l1"),
      l2: parseLevelScore(scores.l2, "scores.l2"),
      l3: parseLevelScore(scores.l3, "scores.l3"),
      final_score: asNullableScore(scores.final_score, "scores.final_score"),
    },
    criterion_assessments: record.criterion_assessments.map(parseCriterionAssessment),
    strengths: asStringArray(record.strengths, "strengths"),
    risks: asStringArray(record.risks, "risks"),
    warnings: asStringArray(record.warnings, "warnings"),
    confidence: asNullableScore(record.confidence, "confidence"),
    quality_gate: {
      requires_review: asBoolean(qualityGate.requires_review, "quality_gate.requires_review"),
      reasons: asStringArray(qualityGate.reasons, "quality_gate.reasons"),
    },
    versions: parseVersions(record.versions),
    created_at: asString(record.created_at, "created_at"),
  };
}

function parseDemoEvidence(value: unknown, index: number): DemoEvidence {
  const record = asRecord(value, `evidence[${index}]`);
  return {
    evidence_id: asString(record.evidence_id, `evidence[${index}].evidence_id`),
    section: asString(record.section, `evidence[${index}].section`),
    text: asString(record.text, `evidence[${index}].text`),
    is_verified: asBoolean(record.is_verified, `evidence[${index}].is_verified`),
  };
}

function parseDemoCriterion(value: unknown, index: number): DemoCriterion {
  const record = asRecord(value, `criteria[${index}]`);
  return {
    criterion_id: asString(record.criterion_id, `criteria[${index}].criterion_id`),
    title: asString(record.title, `criteria[${index}].title`),
    weight: asScore(record.weight, `criteria[${index}].weight`),
  };
}

export function parseDemoCases(value: unknown): DemoCaseSummary[] {
  if (!Array.isArray(value)) {
    throw new Error("Danh sách demo case không đúng cấu trúc.");
  }
  return value.map((item, index) => {
    const record = asRecord(item, `demo_cases[${index}]`);
    if (!Array.isArray(record.evidence) || !Array.isArray(record.criteria)) {
      throw new Error(`demo_cases[${index}] thiếu evidence hoặc criteria.`);
    }
    return {
      demo_case_id: asString(record.demo_case_id, `demo_cases[${index}].demo_case_id`),
      role: asString(record.role, `demo_cases[${index}].role`),
      scenario: asString(record.scenario, `demo_cases[${index}].scenario`),
      candidate_reference: asString(
        record.candidate_reference,
        `demo_cases[${index}].candidate_reference`,
      ),
      cv_profile_id: asString(record.cv_profile_id, `demo_cases[${index}].cv_profile_id`),
      cv_summary: asNullableString(record.cv_summary, `demo_cases[${index}].cv_summary`),
      job_profile_id: asString(
        record.job_profile_id,
        `demo_cases[${index}].job_profile_id`,
      ),
      job_title: asString(record.job_title, `demo_cases[${index}].job_title`),
      evidence: record.evidence.map(parseDemoEvidence),
      criteria: record.criteria.map(parseDemoCriterion),
    };
  });
}

function parseApprovedDecision(value: unknown, index: number): ApprovedDecision {
  const record = asRecord(value, `decisions[${index}]`);
  const proposedDecision = asString(
    record.proposed_decision,
    `decisions[${index}].proposed_decision`,
  );
  const finalDecision = asString(record.final_decision, `decisions[${index}].final_decision`);
  const approvalStatus = asString(
    record.approval_status,
    `decisions[${index}].approval_status`,
  );
  if (!classificationDecisions.has(proposedDecision as ClassificationDecision)) {
    throw new Error(`decisions[${index}].proposed_decision không hợp lệ.`);
  }
  if (!finalDecisions.has(finalDecision as FinalDecision)) {
    throw new Error(`decisions[${index}].final_decision không hợp lệ.`);
  }
  if (approvalStatus !== "approved" && approvalStatus !== "overridden") {
    throw new Error(`decisions[${index}].approval_status không hợp lệ.`);
  }
  return {
    schema_version: asString(record.schema_version, `decisions[${index}].schema_version`),
    approved_decision_id: asString(
      record.approved_decision_id,
      `decisions[${index}].approved_decision_id`,
    ),
    classification_result_id: asString(
      record.classification_result_id,
      `decisions[${index}].classification_result_id`,
    ),
    approval_status: approvalStatus,
    proposed_decision: proposedDecision as ClassificationDecision,
    final_decision: finalDecision as FinalDecision,
    reviewer_reference: asString(
      record.reviewer_reference,
      `decisions[${index}].reviewer_reference`,
    ),
    decision_reason: asString(
      record.decision_reason,
      `decisions[${index}].decision_reason`,
    ),
    override_reason: asNullableString(
      record.override_reason,
      `decisions[${index}].override_reason`,
    ),
    decided_at: asString(record.decided_at, `decisions[${index}].decided_at`),
  };
}

export function parseApprovedDecisions(value: unknown): ApprovedDecision[] {
  if (!Array.isArray(value)) {
    throw new Error("Lịch sử quyết định không đúng cấu trúc.");
  }
  return value.map(parseApprovedDecision);
}

export function formatScore(value: ScoreValue | null): string {
  if (value === null) {
    return "Không có";
  }
  const numeric = Number(value);
  return Number.isInteger(numeric) ? numeric.toFixed(0) : numeric.toFixed(2);
}
