"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

import {
  ApprovedDecision,
  ClassificationDecision,
  ClassificationResult,
  DemoCaseSummary,
  DemoExecutionMode,
  FinalDecision,
  formatScore,
  parseApprovedDecisions,
  parseClassificationResult,
  parseDemoCases,
} from "@/lib/contracts";

const decisionLabels: Record<ClassificationDecision, string> = {
  pass: "Đạt",
  waitlist: "Danh sách chờ",
  reject: "Không đạt",
  needs_review: "Cần xem xét",
};

const finalDecisionLabels: Record<FinalDecision, string> = {
  pass: "Đạt",
  waitlist: "Danh sách chờ",
  reject: "Không đạt",
};

const evidenceStatusLabels = {
  satisfied: "Đáp ứng",
  unsatisfied: "Không đáp ứng",
  missing: "Thiếu thông tin",
  conflicting: "Mâu thuẫn",
};

const reasonLabels: Record<string, string> = {
  "missing-critical-evidence": "Thiếu thông tin cho yêu cầu bắt buộc",
  "conflicting-critical-evidence": "Thông tin về yêu cầu bắt buộc bị mâu thuẫn",
  "low-score-without-explicit-critical-unsatisfied":
    "Điểm thấp nhưng chưa có thông tin xác nhận không đáp ứng yêu cầu bắt buộc",
  "critical-unsatisfied-at-or-above-waitlist-threshold":
    "Có yêu cầu bắt buộc không đạt nhưng điểm tổng vẫn cao",
  "invalid-provider-output": "Một tầng đánh giá không cung cấp output hợp lệ",
  "large-level-disagreement": "Điểm giữa các tầng chênh lệch lớn",
  "lower-threshold-boundary": "Điểm nằm sát ngưỡng danh sách chờ",
  "upper-threshold-boundary": "Điểm nằm sát ngưỡng đạt",
};

async function responsePayload(response: Response): Promise<unknown> {
  const payload: unknown = await response.json();
  if (!response.ok) {
    if (typeof payload === "object" && payload !== null && !Array.isArray(payload)) {
      const detail = (payload as Record<string, unknown>).detail;
      if (typeof detail === "string") {
        throw new Error(detail);
      }
    }
    throw new Error(`Yêu cầu thất bại với HTTP ${response.status}.`);
  }
  return payload;
}

function initialFinalDecision(result: ClassificationResult): FinalDecision {
  return result.proposed_decision === "needs_review" ? "waitlist" : result.proposed_decision;
}

function criterionTitle(demoCase: DemoCaseSummary, criterionId: string): string {
  return (
    demoCase.criteria.find((criterion) => criterion.criterion_id === criterionId)?.title ??
    criterionId
  );
}

export function ClassifierDashboard() {
  const [demoCases, setDemoCases] = useState<DemoCaseSummary[]>([]);
  const [selectedCaseId, setSelectedCaseId] = useState("");
  const [executionMode, setExecutionMode] = useState<DemoExecutionMode>("offline");
  const [llmCostConfirmed, setLlmCostConfirmed] = useState(false);
  const [result, setResult] = useState<ClassificationResult | null>(null);
  const [history, setHistory] = useState<ApprovedDecision[]>([]);
  const [backendStatus, setBackendStatus] = useState<"checking" | "online" | "offline">(
    "checking",
  );
  const [loading, setLoading] = useState(false);
  const [submittingDecision, setSubmittingDecision] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reviewerReference, setReviewerReference] = useState("reviewer-stage-eight");
  const [decisionReason, setDecisionReason] = useState(
    "Người duyệt đã kiểm tra điểm, thông tin hỗ trợ và điều kiện cần xem xét.",
  );
  const [finalDecision, setFinalDecision] = useState<FinalDecision>("waitlist");
  const [overrideReason, setOverrideReason] = useState("");

  const selectedCase = useMemo(
    () => demoCases.find((item) => item.demo_case_id === selectedCaseId) ?? null,
    [demoCases, selectedCaseId],
  );
  const isApproval =
    result !== null &&
    result.proposed_decision !== "needs_review" &&
    finalDecision === result.proposed_decision;

  useEffect(() => {
    let active = true;
    async function loadDemoCases() {
      try {
        const casesResponse = await fetch("/api/demo-cases");
        const cases = parseDemoCases(await responsePayload(casesResponse));
        if (active) {
          setDemoCases(cases);
          setSelectedCaseId(cases[0]?.demo_case_id ?? "");
        }
      } catch (loadError) {
        if (active) {
          setError(loadError instanceof Error ? loadError.message : "Không thể tải dữ liệu demo.");
        }
      }
    }
    void loadDemoCases();
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;
    async function checkBackend() {
      setBackendStatus("checking");
      try {
        const healthResponse = await fetch(`/api/health?execution_mode=${executionMode}`);
        await responsePayload(healthResponse);
        if (active) {
          setBackendStatus("online");
          setError(null);
        }
      } catch (healthError) {
        if (active) {
          setBackendStatus("offline");
          setError(
            healthError instanceof Error ? healthError.message : "Không thể kết nối backend.",
          );
        }
      }
    }
    void checkBackend();
    return () => {
      active = false;
    };
  }, [executionMode]);

  async function loadHistory(classificationResultId: string): Promise<void> {
    const response = await fetch(
      `/api/classifications/${encodeURIComponent(classificationResultId)}/decisions?execution_mode=${executionMode}`,
    );
    setHistory(parseApprovedDecisions(await responsePayload(response)));
  }

  async function classify(): Promise<void> {
    if (selectedCaseId === "") {
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    setHistory([]);
    try {
      const response = await fetch("/api/classifications", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          demo_case_id: selectedCaseId,
          execution_mode: executionMode,
        }),
      });
      const classificationResult = parseClassificationResult(await responsePayload(response));
      setResult(classificationResult);
      setFinalDecision(initialFinalDecision(classificationResult));
      setOverrideReason("");
      await loadHistory(classificationResult.classification_result_id);
    } catch (classificationError) {
      setError(
        classificationError instanceof Error
          ? classificationError.message
          : "Không thể phân loại hồ sơ.",
      );
    } finally {
      setLoading(false);
    }
  }

  async function submitDecision(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (result === null) {
      return;
    }
    setSubmittingDecision(true);
    setError(null);
    try {
      const response = await fetch(
        `/api/classifications/${encodeURIComponent(result.classification_result_id)}/decisions?execution_mode=${executionMode}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            final_decision: finalDecision,
            reviewer_reference: reviewerReference,
            decision_reason: decisionReason,
            override_reason: isApproval ? null : overrideReason,
          }),
        },
      );
      await responsePayload(response);
      await loadHistory(result.classification_result_id);
    } catch (decisionError) {
      setError(
        decisionError instanceof Error ? decisionError.message : "Không thể lưu quyết định.",
      );
    } finally {
      setSubmittingDecision(false);
    }
  }

  return (
    <main className="page-shell">
      <header className="page-header">
        <div>
          <p className="eyebrow">AI Recruitment System</p>
          <h1>Classifier Agent</h1>
          <p className="subtitle">
            Đánh giá mức phù hợp của hồ sơ và chuyển quyết định cuối cho người duyệt.
          </p>
        </div>
        <div className={`service-status service-status-${backendStatus}`} role="status">
          Backend: {backendStatus === "online" ? "Đang hoạt động" : backendStatus === "offline" ? "Mất kết nối" : "Đang kiểm tra"}
        </div>
      </header>

      {error !== null ? (
        <div className="error-message" role="alert">
          {error}
        </div>
      ) : null}

      <div className="dashboard-grid">
        <section className="panel input-panel" aria-labelledby="input-heading">
          <div className="section-heading">
            <p className="section-index">Bước 1</p>
            <h2 id="input-heading">Chọn hồ sơ demo</h2>
          </div>
          <label htmlFor="execution-mode">Chế độ L3</label>
          <select
            id="execution-mode"
            value={executionMode}
            onChange={(event) => {
              setExecutionMode(event.target.value as DemoExecutionMode);
              setLlmCostConfirmed(false);
              setResult(null);
              setHistory([]);
              setError(null);
            }}
            disabled={loading || submittingDecision}
          >
            <option value="offline">Offline - L3 mô phỏng</option>
            <option value="llm">LLM thật - có thể phát sinh phí</option>
          </select>

          <div className={`mode-description mode-description-${executionMode}`}>
            <strong>
              {executionMode === "offline" ? "Offline - L3 mô phỏng" : "LLM thật"}
            </strong>
            <span>
              {executionMode === "offline"
                ? "L3 dùng quy tắc độ phủ thông tin; không gửi request tới provider."
                : "L3 gọi provider đã cấu hình; kết quả có thể phát sinh phí và độ trễ."}
            </span>
          </div>

          {executionMode === "llm" ? (
            <label className="confirmation-label" htmlFor="llm-cost-confirmed">
              <input
                id="llm-cost-confirmed"
                type="checkbox"
                checked={llmCostConfirmed}
                onChange={(event) => setLlmCostConfirmed(event.target.checked)}
              />
              <span>Tôi xác nhận lần chạy này có thể phát sinh phí API.</span>
            </label>
          ) : null}

          <label htmlFor="demo-case">Hồ sơ và vị trí tuyển dụng</label>
          <select
            id="demo-case"
            value={selectedCaseId}
            onChange={(event) => {
              setSelectedCaseId(event.target.value);
              setResult(null);
              setHistory([]);
              setError(null);
            }}
            disabled={demoCases.length === 0 || loading}
          >
            {demoCases.map((demoCase) => (
              <option key={demoCase.demo_case_id} value={demoCase.demo_case_id}>
                {demoCase.job_title} - {demoCase.candidate_reference}
              </option>
            ))}
          </select>

          {selectedCase !== null ? (
            <div className="candidate-summary">
              <p>
                <span>Mã hồ sơ</span>
                <strong>{selectedCase.cv_profile_id}</strong>
              </p>
              <p>
                <span>Vị trí</span>
                <strong>{selectedCase.job_title}</strong>
              </p>
              <p className="summary-text">{selectedCase.cv_summary}</p>
            </div>
          ) : (
            <p className="empty-state">Chưa tải được hồ sơ demo.</p>
          )}

          <button
            className="primary-button"
            type="button"
            onClick={() => void classify()}
            disabled={
              selectedCase === null ||
              loading ||
              backendStatus !== "online" ||
              (executionMode === "llm" && !llmCostConfirmed)
            }
          >
            {loading
              ? "Đang phân loại"
              : executionMode === "llm"
                ? "Chạy bằng LLM thật"
                : "Chạy phân loại offline"}
          </button>

          {selectedCase !== null ? (
            <details className="evidence-preview">
              <summary>Xem thông tin trong CV</summary>
              <div className="evidence-list">
                {selectedCase.evidence.map((evidence) => (
                  <article key={evidence.evidence_id}>
                    <div>
                      <span>{evidence.section}</span>
                      <code>{evidence.evidence_id}</code>
                    </div>
                    <p>{evidence.text}</p>
                  </article>
                ))}
              </div>
            </details>
          ) : null}
        </section>

        <section className="panel result-panel" aria-labelledby="result-heading">
          <div className="section-heading">
            <p className="section-index">Bước 2</p>
            <h2 id="result-heading">Kết quả phân loại</h2>
          </div>
          {result === null || selectedCase === null ? (
            <div className="result-placeholder">
              <p>Kết quả sẽ xuất hiện sau khi chạy phân loại.</p>
            </div>
          ) : (
            <div className="result-content">
              <div className={`result-mode result-mode-${executionMode}`}>
                <strong>
                  {executionMode === "offline" ? "Offline - L3 mô phỏng" : "LLM thật"}
                </strong>
                <span>
                  {executionMode === "offline"
                    ? "Điểm L3 được tính bằng quy tắc xác định."
                    : `${result.versions.llm_provider_identifier ?? "Provider đã cấu hình"} - ${result.versions.llm_model_identifier ?? "Model đã cấu hình"}`}
                </span>
              </div>
              <div className="decision-summary">
                <div>
                  <span>Đề xuất</span>
                  <strong className={`decision decision-${result.proposed_decision}`}>
                    {decisionLabels[result.proposed_decision]}
                  </strong>
                </div>
                <div>
                  <span>Điểm tổng</span>
                  <strong>{formatScore(result.scores.final_score)}</strong>
                </div>
                <div>
                  <span>Độ tin cậy L3</span>
                  <strong>{formatScore(result.confidence)}</strong>
                </div>
              </div>

              <div className="level-scores" aria-label="Điểm theo tầng">
                {(["l1", "l2", "l3"] as const).map((level) => (
                  <div key={level}>
                    <span>{level.toUpperCase()}</span>
                    <strong>{formatScore(result.scores[level].value)}</strong>
                    <small>{result.scores[level].status}</small>
                  </div>
                ))}
              </div>

              {result.quality_gate.requires_review ? (
                <div className="review-reasons">
                  <h3>Lý do cần xem xét</h3>
                  <ul>
                    {result.quality_gate.reasons.map((reason) => (
                      <li key={reason}>{reasonLabels[reason] ?? reason}</li>
                    ))}
                  </ul>
                </div>
              ) : null}

              <div className="criterion-list">
                <h3>Năm nhóm tiêu chí</h3>
                {result.criterion_assessments.map((assessment) => {
                  const evidenceItems = selectedCase.evidence.filter((evidence) =>
                    assessment.evidence_ids.includes(evidence.evidence_id),
                  );
                  return (
                    <article key={assessment.criterion_id} className="criterion-card">
                      <div className="criterion-heading">
                        <div>
                          <h4>{criterionTitle(selectedCase, assessment.criterion_id)}</h4>
                          <span>{evidenceStatusLabels[assessment.evidence_status]}</span>
                        </div>
                        <strong>{formatScore(assessment.score)}</strong>
                      </div>
                      <p>{assessment.rationale}</p>
                      {evidenceItems.length > 0 ? (
                        <details>
                          <summary>
                            {executionMode === "offline"
                              ? "Thông tin được adapter offline sử dụng"
                              : "Thông tin hỗ trợ"}{" "}
                            ({evidenceItems.length})
                          </summary>
                          <ul>
                            {evidenceItems.map((evidence) => (
                              <li key={evidence.evidence_id}>{evidence.text}</li>
                            ))}
                          </ul>
                        </details>
                      ) : (
                        <p className="muted">Không có thông tin hỗ trợ được dẫn chiếu.</p>
                      )}
                    </article>
                  );
                })}
              </div>

              {result.risks.length > 0 || result.warnings.length > 0 ? (
                <div className="risk-list">
                  <h3>Rủi ro và cảnh báo</h3>
                  <ul>
                    {[...result.risks, ...result.warnings].map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              ) : null}
            </div>
          )}
        </section>
      </div>

      {result !== null ? (
        <section className="panel review-panel" aria-labelledby="review-heading">
          <div className="section-heading">
            <p className="section-index">Bước 3</p>
            <h2 id="review-heading">Human review và lịch sử quyết định</h2>
          </div>
          <div className="review-grid">
            <form onSubmit={(event) => void submitDecision(event)}>
              <label htmlFor="reviewer-reference">Mã người duyệt</label>
              <input
                id="reviewer-reference"
                value={reviewerReference}
                onChange={(event) => setReviewerReference(event.target.value)}
                pattern="[a-z0-9][a-z0-9-]{2,63}"
                required
              />

              <label htmlFor="final-decision">Quyết định cuối</label>
              <select
                id="final-decision"
                value={finalDecision}
                onChange={(event) => setFinalDecision(event.target.value as FinalDecision)}
              >
                {Object.entries(finalDecisionLabels).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>

              <label htmlFor="decision-reason">Lý do quyết định</label>
              <textarea
                id="decision-reason"
                value={decisionReason}
                onChange={(event) => setDecisionReason(event.target.value)}
                required
              />

              {!isApproval ? (
                <>
                  <label htmlFor="override-reason">Lý do thay đổi đề xuất</label>
                  <textarea
                    id="override-reason"
                    value={overrideReason}
                    onChange={(event) => setOverrideReason(event.target.value)}
                    required
                  />
                </>
              ) : null}

              <button className="primary-button" type="submit" disabled={submittingDecision}>
                {submittingDecision
                  ? "Đang lưu quyết định"
                  : isApproval
                    ? "Phê duyệt đề xuất"
                    : "Lưu quyết định thay đổi"}
              </button>
            </form>

            <div className="history" aria-live="polite">
              <h3>Lịch sử audit</h3>
              {history.length === 0 ? (
                <p className="empty-state">Chưa có quyết định được ghi nhận.</p>
              ) : (
                <ol>
                  {history.map((decision) => (
                    <li key={decision.approved_decision_id}>
                      <div>
                        <strong>
                          {decision.approval_status === "approved"
                            ? "Đã phê duyệt"
                            : "Đã thay đổi"}
                        </strong>
                        <span>{finalDecisionLabels[decision.final_decision]}</span>
                      </div>
                      <p>{decision.decision_reason}</p>
                      {decision.override_reason !== null ? (
                        <p>Lý do thay đổi: {decision.override_reason}</p>
                      ) : null}
                      <small>
                        {decision.reviewer_reference} - {new Date(decision.decided_at).toLocaleString("vi-VN")}
                      </small>
                    </li>
                  ))}
                </ol>
              )}
            </div>
          </div>
        </section>
      ) : null}
    </main>
  );
}
