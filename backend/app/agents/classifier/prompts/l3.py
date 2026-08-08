from __future__ import annotations

import json
from collections.abc import Sequence
from typing import TypedDict, cast

from backend.app.contracts import Evidence, EvidenceSection, JobProfile, ScoringRubric
from backend.app.domain import RequirementAssessment

PROMPT_VERSION = "l3-evidence-rubric-v1"
LIVE_PROMPT_VERSION = "l3-evidence-rubric-v3"
ANCHORED_PROMPT_VERSION = "l3-evidence-rubric-v4"
CALIBRATED_PROMPT_VERSION = "l3-evidence-rubric-v5"
SCOPED_PROMPT_VERSION = "l3-evidence-rubric-v6"
STRICT_SCOPED_PROMPT_VERSION = "l3-evidence-rubric-v7"
HARD_SCOPED_PROMPT_VERSION = "l3-evidence-rubric-v8"
GPT_5_4_MINI_PROMPT_VERSION = "l3-evidence-rubric-v9"
VALIDATED_PROMPT_VERSION = "l3-evidence-rubric-v10"
ROLE_CALIBRATED_PROMPT_VERSION = "l3-evidence-rubric-v11"
REQUIREMENT_GUARDED_PROMPT_VERSION = "l3-evidence-rubric-v12"
CONFLICT_AUDITED_PROMPT_VERSION = "l3-evidence-rubric-v13"
AUTHORITATIVE_REQUIREMENTS_PROMPT_VERSION = "l3-evidence-rubric-v14"
CRITERION_STATUS_PROMPT_VERSION = "l3-evidence-rubric-v15"

SYSTEM_PROMPT = (
    "Bạn đánh giá mức độ phù hợp của hồ sơ theo đúng rubric được cung cấp. "
    "Chỉ sử dụng các đoạn thông tin có evidence_id trong đầu vào. "
    "Không suy diễn kỹ năng, kinh nghiệm, học vấn, tác động hoặc thuộc tính không được nêu. "
    "Thiếu thông tin phải giữ là missing, không tự đổi thành unsatisfied. "
    "Mỗi điểm tiêu chí là weighted points và không được vượt quá weight của tiêu chí. "
    "Trả về duy nhất một JSON object tuân thủ schema structured output."
)

LIVE_SYSTEM_PROMPT = (
    "Bạn đánh giá mức độ phù hợp của hồ sơ theo đúng rubric được cung cấp. "
    "Chỉ sử dụng các đoạn thông tin có evidence_id trong đầu vào. "
    "Không suy diễn kỹ năng, kinh nghiệm, học vấn, tác động hoặc thuộc tính không được nêu. "
    "Thiếu thông tin phải giữ là missing, không tự đổi thành unsatisfied. "
    "Requirement assessments phải chứa chính xác requirement_id được liệt kê trong "
    "output_constraints, không thêm hoặc bỏ ID. "
    "Criterion assessments phải chứa chính xác criterion_id được liệt kê, mỗi điểm là "
    "weighted points và không vượt maximum_weighted_points tương ứng. "
    "Chỉ tham chiếu evidence_id nằm trong allowed_evidence_ids. "
    "Nếu evidence_status là satisfied hoặc unsatisfied thì evidence_ids phải có ít nhất "
    "một ID; missing thì evidence_ids phải rỗng; conflicting thì phải có ít nhất hai ID "
    "khác nhau. "
    "overall_score phải bằng tổng điểm của criterion_assessments. "
    "Trả về duy nhất một JSON object tuân thủ schema structured output."
)

ANCHORED_SYSTEM_PROMPT = LIVE_SYSTEM_PROMPT + (
    "Chấm từng tiêu chí theo scoring_anchors trong output_constraints và chọn mức thấp hơn "
    "khi thông tin nằm giữa hai mức. Không mặc định cho điểm tối đa chỉ vì yêu cầu bắt buộc "
    "được đáp ứng hoặc nhiều kỹ năng được liệt kê. "
)

CALIBRATED_SYSTEM_PROMPT = LIVE_SYSTEM_PROMPT + (
    "Đánh giá requirement trước, sau đó chấm riêng từng tiêu chí theo calibration_protocol. "
    "Đọc toàn bộ nội dung của mỗi evidence, bao gồm câu phủ định, giới hạn phạm vi, thiếu "
    "ownership, thiếu outcome hoặc chỉ là bản minh họa; các giới hạn này không được bỏ qua "
    "vì cùng evidence có nhiều từ khóa phù hợp. "
    "Một kỹ năng chỉ được liệt kê, một học phần hoặc một mô tả chung không tương đương với "
    "năng lực đã được áp dụng. "
    "Dùng mốc thấp hơn khi thông tin nằm giữa hai mức và chỉ dùng điểm tối đa trong trường "
    "hợp hiếm khi mọi thành phần của tiêu chí đều có thông tin trực tiếp, sâu và kiểm tra được. "
    "Sau khi cộng điểm, đối chiếu overall_score với overall_score_bands; nếu band điểm cao hơn "
    "chất lượng thông tin thực tế thì phải hạ các điểm tiêu chí liên quan. "
)

SCOPED_SYSTEM_PROMPT = CALIBRATED_SYSTEM_PROMPT + (
    "Đánh giá độc lập từng requirement_id. Một câu phủ định, thiếu sót hoặc mâu thuẫn chỉ "
    "được đổi evidence_status của requirement mà câu đó nêu đích danh hoặc phủ định trực "
    "tiếp. Không lan trạng thái unsatisfied hay conflicting sang requirement khác chỉ vì "
    "chúng cùng xuất hiện trong một dự án hoặc hồ sơ. Thông tin giới hạn chung vẫn được dùng "
    "để giảm điểm tiêu chí liên quan nhưng không tự tạo mâu thuẫn cho mọi requirement. "
)

STRICT_SCOPED_SYSTEM_PROMPT = SCOPED_SYSTEM_PROMPT + (
    "Với mỗi requirement, phân loại từng evidence thành direct_positive, exact_negative hoặc "
    "context_only trước khi chọn trạng thái. Coursework, tên chương trình học, danh sách kỹ "
    "năng và mục tiêu nghề nghiệp luôn là context_only. Câu giới hạn chung không nêu đích "
    "danh năng lực cũng là context_only đối với requirement. Chỉ chọn conflicting khi có cả "
    "direct_positive và exact_negative cho chính cùng một năng lực. "
)

HARD_SCOPED_SYSTEM_PROMPT = (
    "Bất biến bắt buộc: evidence thuộc education không bao giờ là direct positive cho "
    "requirement; câu phủ định không nêu chính xác năng lực không bao giờ là exact negative; "
    "không được dùng context_only_evidence_ids để tạo satisfied hoặc conflicting. "
    + STRICT_SCOPED_SYSTEM_PROMPT
)

GPT_5_4_MINI_SYSTEM_PROMPT = (
    "Goal: score this junior candidate against the supplied job and rubric using only input "
    "evidence that has an evidence_id. Follow output_constraints exactly. First assess every "
    "requirement_id independently. Education, coursework, skill lists, aspirations, and unnamed "
    "limitations are context_only. A concrete action, artifact, technical detail, or outcome for "
    "the exact capability is direct_positive. An explicit denial, absence, inability, or failed "
    "application that names the exact capability is exact_negative. Set satisfied only from "
    "direct_positive, unsatisfied only from exact_negative, conflicting only when both exist for "
    "the same capability, and missing when neither exists. Never cite context_only evidence in a "
    "requirement assessment. Then score each criterion in weighted points using the calibration "
    "anchors and caps; choose the lower anchor when evidence falls between levels. Do not infer "
    "skills, ownership, impact, or verification. Preserve missing as distinct from unsatisfied. "
    "Each criterion score must stay within its maximum and overall_score must equal their sum. "
    "Return only one JSON object that satisfies the structured-output schema."
)

VALIDATED_SYSTEM_PROMPT = GPT_5_4_MINI_SYSTEM_PROMPT + (
    " Before returning, run this output checklist: requirement_assessments and "
    "criterion_assessments must each use every requested ID exactly once; satisfied and "
    "unsatisfied require at least one allowed evidence_id; missing requires an empty evidence_ids "
    "array; conflicting requires at least two distinct allowed evidence_ids. For criteria, use "
    "missing only when no relevant evidence is cited, and never attach evidence_ids to missing. "
    "After choosing all five criterion scores, calculate their arithmetic sum and set "
    "overall_score to that exact sum."
)

ROLE_CALIBRATED_SYSTEM_PROMPT = (
    "Assess this junior candidate using only evidence IDs supplied in the request. Evaluate each "
    "critical requirement independently with the exact status algorithm and never infer a skill, "
    "outcome, ownership, or impact. For each criterion, select one qualitative calibration_level "
    "from the allowed levels using the role_calibration_profile and the full evidence text. Do not "
    "produce numeric criterion scores or an overall score. Deterministic application code maps the "
    "selected levels and critical requirement statuses to weighted points. Use every requested ID "
    "exactly once, obey evidence cardinality, cite only allowed evidence IDs, and return only one "
    "JSON object satisfying the structured-output schema."
)

REQUIREMENT_GUARDED_SYSTEM_PROMPT = ROLE_CALIBRATED_SYSTEM_PROMPT + (
    " For requirement statuses, exact capability boundaries are mandatory: a related tool, "
    "workflow, framework, or outcome never proves a named technology unless the evidence text "
    "states that technology or an explicitly accepted alternative. Apply a negative statement "
    "only to the capability atom it names, even when another requirement appears in the same "
    "project or broader skill family. When uncertain whether two capabilities are equivalent, "
    "treat the evidence as context_only for that requirement."
)

CONFLICT_AUDITED_SYSTEM_PROMPT = REQUIREMENT_GUARDED_SYSTEM_PROMPT + (
    " Before finalizing each requirement, scan every evidence section for both direct_positive "
    "and exact_negative statements about that capability. Evidence in other or summary sections "
    "can be exact_negative when it explicitly denies the capability. A stronger, newer, or more "
    "detailed positive statement never overrides an exact_negative; when both exist, return "
    "conflicting and cite at least one evidence ID from each side."
)

AUTHORITATIVE_REQUIREMENTS_SYSTEM_PROMPT = CONFLICT_AUDITED_SYSTEM_PROMPT + (
    " Requirement statuses and their evidence IDs in authoritative_requirement_assessments "
    "were produced by the validated deterministic requirement engine. Copy those assessments "
    "exactly; do not reinterpret, weaken, or override them. Use the remaining evidence to choose "
    "qualitative criterion levels and explain strengths, risks, and warnings."
)

CRITERION_STATUS_SYSTEM_PROMPT = AUTHORITATIVE_REQUIREMENTS_SYSTEM_PROMPT + (
    " Criterion evidence_status describes whether criterion-related information exists, not "
    "whether the candidate is strong. Explicit limitations, failures, non-ownership, absent "
    "artifacts, and context_only requirement evidence are still relevant criterion evidence: "
    "use unsatisfied and cite those IDs. Use missing for a criterion only when no supplied "
    "evidence is related to that criterion at all."
)

ROLE_CALIBRATION_PROFILES: dict[str, dict[str, str]] = {
    "junior-data-analyst-": {
        "technical_specialization": (
            "SQL query depth, data-quality checks, Python or R analysis, BI data modeling, KPI "
            "definitions, statistics, and reproducibility"
        ),
        "role_capability": (
            "turning a business question into validated analysis, choosing useful metrics, "
            "explaining limitations, and making actionable recommendations"
        ),
        "projects_and_impact": (
            "end-to-end analysis ownership from source inspection through dashboard or report, "
            "with a credible decision, outcome, or measurable operational use"
        ),
        "communication_and_evidence_quality": (
            "clear scope, query or notebook details, KPI definitions, artifacts, outcomes, and "
            "explicit analytical limitations"
        ),
    },
    "junior-python-backend-": {
        "technical_specialization": (
            "structured Python, API validation and error handling, relational schema, migrations, "
            "transactions, tests, containers, and observable delivery"
        ),
        "role_capability": (
            "API and data-flow design decisions, failure-path reasoning, integration ownership, "
            "security boundaries, and maintainable delivery workflow"
        ),
        "projects_and_impact": (
            "an end-to-end backend service with credible consumers, deployment or container "
            "evidence, tested failure paths, and a concrete operational outcome"
        ),
        "communication_and_evidence_quality": (
            "precise endpoint, schema, test, deployment, incident, and limitation details rather "
            "than a framework or technology list"
        ),
    },
    "junior-frontend-": {
        "technical_specialization": (
            "semantic HTML, responsive CSS, TypeScript, component design, API integration, "
            "authentication states, accessibility, testing, and runtime error handling"
        ),
        "role_capability": (
            "user-flow ownership, state and form decisions, loading and failure behavior, "
            "accessibility reasoning, and collaboration through Git"
        ),
        "projects_and_impact": (
            "a delivered user-facing flow with tested interactions, measurable usability or "
            "performance outcome, and clear ownership"
        ),
        "communication_and_evidence_quality": (
            "specific components, states, accessibility checks, test artifacts, outcomes, and "
            "known browser or product limitations"
        ),
    },
    "junior-qa-engineer-": {
        "technical_specialization": (
            "test design techniques, functional and regression coverage, API and SQL checks, bug "
            "lifecycle, automation foundation, and reproducible test artifacts"
        ),
        "role_capability": (
            "risk analysis, coverage decisions, defect investigation, acceptance clarification, "
            "prioritization, and communication with developers or product stakeholders"
        ),
        "projects_and_impact": (
            "an end-to-end quality workflow with traceable cases, defects, regression evidence, "
            "automation or data checks, and a credible release outcome"
        ),
        "communication_and_evidence_quality": (
            "precise test scope, technique, environment, defect evidence, coverage result, and "
            "explicit untested or unresolved areas"
        ),
    },
    "junior-data-engineer-": {
        "technical_specialization": (
            "Python and SQL pipelines, data modeling, incremental loading, orchestration, data "
            "quality, tests, containers, lineage, and warehouse or lake delivery"
        ),
        "role_capability": (
            "source-to-target design, reliability and recovery decisions, schema evolution, data "
            "quality ownership, observability, and delivery tradeoffs"
        ),
        "projects_and_impact": (
            "an end-to-end pipeline with multiple stages, validated data outputs, credible users, "
            "operational reliability, and measurable delivery impact"
        ),
        "communication_and_evidence_quality": (
            "specific sources, transformations, models, quality rules, run behavior, artifacts, "
            "outcomes, and operational limitations"
        ),
    },
}


class ChatMessage(TypedDict):
    role: str
    content: str


def build_l3_messages(
    job_profile: JobProfile,
    rubric: ScoringRubric,
    evidence: Sequence[Evidence],
    prompt_version: str,
    authoritative_requirement_assessments: Sequence[RequirementAssessment] = (),
) -> tuple[ChatMessage, ChatMessage]:
    if prompt_version not in {
        PROMPT_VERSION,
        LIVE_PROMPT_VERSION,
        ANCHORED_PROMPT_VERSION,
        CALIBRATED_PROMPT_VERSION,
        SCOPED_PROMPT_VERSION,
        STRICT_SCOPED_PROMPT_VERSION,
        HARD_SCOPED_PROMPT_VERSION,
        GPT_5_4_MINI_PROMPT_VERSION,
        VALIDATED_PROMPT_VERSION,
        ROLE_CALIBRATED_PROMPT_VERSION,
        REQUIREMENT_GUARDED_PROMPT_VERSION,
        CONFLICT_AUDITED_PROMPT_VERSION,
        AUTHORITATIVE_REQUIREMENTS_PROMPT_VERSION,
        CRITERION_STATUS_PROMPT_VERSION,
    }:
        raise ValueError("unsupported L3 prompt version")
    payload: dict[str, object] = {
        "prompt_version": prompt_version,
        "job_profile": job_profile.model_dump(mode="json"),
        "rubric": rubric.model_dump(mode="json"),
        "evidence": [item.model_dump(mode="json") for item in evidence],
    }
    system_prompt = SYSTEM_PROMPT
    if prompt_version in {
        LIVE_PROMPT_VERSION,
        ANCHORED_PROMPT_VERSION,
        CALIBRATED_PROMPT_VERSION,
        SCOPED_PROMPT_VERSION,
        STRICT_SCOPED_PROMPT_VERSION,
        HARD_SCOPED_PROMPT_VERSION,
        GPT_5_4_MINI_PROMPT_VERSION,
        VALIDATED_PROMPT_VERSION,
        ROLE_CALIBRATED_PROMPT_VERSION,
        REQUIREMENT_GUARDED_PROMPT_VERSION,
        CONFLICT_AUDITED_PROMPT_VERSION,
        AUTHORITATIVE_REQUIREMENTS_PROMPT_VERSION,
        CRITERION_STATUS_PROMPT_VERSION,
    }:
        payload["output_constraints"] = {
            "requirement_ids_exactly": list(rubric.critical_requirement_ids),
            "criteria_exactly": [
                {
                    "criterion_id": criterion.criterion_id,
                    "maximum_weighted_points": float(criterion.weight),
                }
                for criterion in rubric.criteria
            ],
            "allowed_evidence_ids": [item.evidence_id for item in evidence],
            "evidence_status_rules": {
                "satisfied": "evidence_ids must contain at least one allowed ID",
                "unsatisfied": "evidence_ids must contain at least one allowed ID",
                "missing": "evidence_ids must be empty",
                "conflicting": "evidence_ids must contain at least two distinct allowed IDs",
            },
        }
        system_prompt = LIVE_SYSTEM_PROMPT
    if prompt_version == ANCHORED_PROMPT_VERSION:
        constraints = payload["output_constraints"]
        if not isinstance(constraints, dict):
            raise TypeError("live output constraints must be a mapping")
        constraints["scoring_anchors"] = {
            "0.00": "no relevant CV information for the criterion",
            "0.25": "skill or activity is named but application is not demonstrated",
            "0.50": "one applied example exists but depth, role, or outcome is limited",
            "0.70": "clear applied work and role are described but impact or verification is limited",
            "0.85": "multiple direct details include sound execution and a credible outcome",
            "1.00": "comprehensive direct information demonstrates depth, ownership, impact, and verifiability",
        }
        system_prompt = ANCHORED_SYSTEM_PROMPT
    if prompt_version in {
        CALIBRATED_PROMPT_VERSION,
        SCOPED_PROMPT_VERSION,
        STRICT_SCOPED_PROMPT_VERSION,
        HARD_SCOPED_PROMPT_VERSION,
        GPT_5_4_MINI_PROMPT_VERSION,
        VALIDATED_PROMPT_VERSION,
        ROLE_CALIBRATED_PROMPT_VERSION,
        REQUIREMENT_GUARDED_PROMPT_VERSION,
        CONFLICT_AUDITED_PROMPT_VERSION,
        AUTHORITATIVE_REQUIREMENTS_PROMPT_VERSION,
        CRITERION_STATUS_PROMPT_VERSION,
    }:
        constraints = cast(dict[str, object], payload["output_constraints"])
        constraints["requirement_decision_rules"] = {
            "satisfied": (
                "direct current application of the exact requirement with an action, artifact, "
                "technical detail, or outcome; keywords, coursework, aspirations, and broad "
                "summaries alone are insufficient"
            ),
            "unsatisfied": (
                "an explicit current denial, inability, or demonstrated failure for the exact "
                "requirement; general education does not override an explicit denial"
            ),
            "missing": (
                "neither direct positive application nor explicit negative information is present"
            ),
            "conflicting": (
                "both direct positive application and direct negative information exist for the "
                "same current capability; background education alone is not a conflict"
            ),
        }
        constraints["calibration_protocol"] = {
            "scoring_precision": (
                "use weighted points directly and use 0.5-point precision when useful; do not "
                "round every criterion to multiples of five"
            ),
            "common_anchors": {
                "0.00": "no relevant CV information for this criterion",
                "0.20": "only names, coursework, aspirations, or unsupported claims",
                "0.40": "a limited applied example without enough depth, ownership, or outcome",
                "0.60": "relevant applied work with some detail but important dimensions are weak",
                "0.75": "clear execution and role with a credible outcome but limited breadth or verification",
                "0.90": "multiple direct details show depth, ownership, outcomes, and few material gaps",
                "1.00": "rare comprehensive information covers every dimension with verifiable depth and impact",
            },
            "criterion_specific_caps": {
                "mandatory_requirements": {
                    "any_unsatisfied": "at most 0.35 of criterion weight",
                    "any_conflicting_without_unsatisfied": "at most 0.60 of criterion weight",
                    "any_missing_without_unsatisfied_or_conflicting": (
                        "at most 0.67 of criterion weight"
                    ),
                    "all_missing": "at most 0.50 of criterion weight",
                    "all_satisfied": (
                        "does not automatically earn full points; apply evidence depth anchors"
                    ),
                },
                "technical_specialization": {
                    "listed_or_coursework_only": "at most 0.35 of criterion weight",
                    "one_limited_applied_example": "at most 0.60 of criterion weight",
                    "missing_depth_or_reproducibility": "at most 0.75 of criterion weight",
                    "maximum": "requires broad direct technical execution with checkable artifacts",
                },
                "role_capability": {
                    "tasks_named_without_decisions": "at most 0.40 of criterion weight",
                    "one_limited_workflow": "at most 0.60 of criterion weight",
                    "missing_ownership_or_tradeoffs": "at most 0.75 of criterion weight",
                    "maximum": "requires clear ownership, reasoning, tradeoffs, and role-relevant delivery",
                },
                "projects_and_impact": {
                    "no_applied_project": "at most 0.25 of criterion weight",
                    "project_without_clear_outcome": "at most 0.55 of criterion weight",
                    "outcome_without_ownership_or_verification": "at most 0.75 of criterion weight",
                    "maximum": "requires end-to-end ownership, credible impact, and checkable delivery",
                },
                "communication_and_evidence_quality": {
                    "generic_or_ambiguous_claims": "at most 0.50 of criterion weight",
                    "specific_but_not_checkable": "at most 0.75 of criterion weight",
                    "maximum": "requires precise scope, artifacts, outcomes, and explicit limitations",
                },
            },
            "cross_criterion_rules": (
                "the same evidence may support multiple criteria, but score each dimension "
                "independently and never award full points everywhere merely because evidence is long"
            ),
            "limiting_language_rule": (
                "explicit clauses such as limited scope, unrelated tasks, one-off demo, missing "
                "method, unverified result, or absent ownership reduce the relevant criterion even "
                "when earlier clauses contain matching technologies"
            ),
            "overall_score_bands": {
                "90-100": "rare comprehensive profile with no material evidence gap",
                "75-89": "strong profile with broad direct evidence and only limited gaps",
                "60-74": "partially demonstrated junior capability with several meaningful limits",
                "40-59": "weak or uneven applied information with major gaps",
                "0-39": "mostly unsupported claims, explicit critical failure, or very little applied work",
            },
        }
        system_prompt = CALIBRATED_SYSTEM_PROMPT
    if prompt_version in {
        SCOPED_PROMPT_VERSION,
        STRICT_SCOPED_PROMPT_VERSION,
        HARD_SCOPED_PROMPT_VERSION,
        GPT_5_4_MINI_PROMPT_VERSION,
        VALIDATED_PROMPT_VERSION,
        REQUIREMENT_GUARDED_PROMPT_VERSION,
        CONFLICT_AUDITED_PROMPT_VERSION,
        AUTHORITATIVE_REQUIREMENTS_PROMPT_VERSION,
        CRITERION_STATUS_PROMPT_VERSION,
        ROLE_CALIBRATED_PROMPT_VERSION,
    }:
        constraints = cast(dict[str, object], payload["output_constraints"])
        constraints["requirement_scoping_rules"] = {
            "independent_assessment": (
                "evaluate each requirement_id independently from every other requirement_id"
            ),
            "exact_negative_scope": (
                "negative or conflicting information changes only the exact capability it "
                "explicitly names or directly denies"
            ),
            "preserve_other_positive_evidence": (
                "direct positive application for another requirement remains satisfied unless "
                "that same capability also has direct negative information"
            ),
            "general_limit_scope": (
                "general limitations may reduce relevant criterion scores but do not by "
                "themselves create unsatisfied or conflicting requirement statuses"
            ),
        }
        system_prompt = SCOPED_SYSTEM_PROMPT
    if prompt_version in {
        STRICT_SCOPED_PROMPT_VERSION,
        HARD_SCOPED_PROMPT_VERSION,
        GPT_5_4_MINI_PROMPT_VERSION,
        VALIDATED_PROMPT_VERSION,
        ROLE_CALIBRATED_PROMPT_VERSION,
        REQUIREMENT_GUARDED_PROMPT_VERSION,
        CONFLICT_AUDITED_PROMPT_VERSION,
        AUTHORITATIVE_REQUIREMENTS_PROMPT_VERSION,
        CRITERION_STATUS_PROMPT_VERSION,
    }:
        constraints = cast(dict[str, object], payload["output_constraints"])
        constraints["requirement_status_algorithm"] = {
            "direct_positive": (
                "the exact capability is applied in a concrete action, artifact, technical "
                "detail, or outcome"
            ),
            "exact_negative": (
                "the evidence explicitly denies, lacks, or fails the exact named capability"
            ),
            "context_only": (
                "coursework, education title, keyword lists, aspirations, and general limiting "
                "phrases that do not name the exact capability"
            ),
            "satisfied": "direct_positive exists and exact_negative does not exist",
            "unsatisfied": "exact_negative exists and direct_positive does not exist",
            "conflicting": "both direct_positive and exact_negative exist for the exact capability",
            "missing": "neither direct_positive nor exact_negative exists",
            "criterion_only_limits": (
                "context_only limitations may lower relevant criterion scores but never change "
                "a requirement status by themselves"
            ),
        }
        system_prompt = STRICT_SCOPED_SYSTEM_PROMPT
    if prompt_version in {
        HARD_SCOPED_PROMPT_VERSION,
        GPT_5_4_MINI_PROMPT_VERSION,
        VALIDATED_PROMPT_VERSION,
        REQUIREMENT_GUARDED_PROMPT_VERSION,
        CONFLICT_AUDITED_PROMPT_VERSION,
        AUTHORITATIVE_REQUIREMENTS_PROMPT_VERSION,
        CRITERION_STATUS_PROMPT_VERSION,
    }:
        constraints = cast(dict[str, object], payload["output_constraints"])
        constraints["context_only_evidence_ids"] = [
            item.evidence_id for item in evidence if item.section is EvidenceSection.EDUCATION
        ]
        constraints["hard_requirement_invariants"] = {
            "education": (
                "never use an education-section evidence ID as direct_positive or as the "
                "positive side of conflicting"
            ),
            "unnamed_negative": (
                "a negative sentence that does not name the exact requirement capability is "
                "context_only and cannot create unsatisfied or conflicting"
            ),
            "generic_example": (
                "a phrase such as technology not used without naming which technology is "
                "context_only for every requirement"
            ),
            "evidence_ids": (
                "requirement evidence_ids may cite only direct_positive and exact_negative "
                "evidence, never context_only evidence"
            ),
        }
        system_prompt = HARD_SCOPED_SYSTEM_PROMPT
    if prompt_version == GPT_5_4_MINI_PROMPT_VERSION:
        system_prompt = GPT_5_4_MINI_SYSTEM_PROMPT
    if prompt_version == VALIDATED_PROMPT_VERSION:
        system_prompt = VALIDATED_SYSTEM_PROMPT
    if prompt_version in {
        ROLE_CALIBRATED_PROMPT_VERSION,
        REQUIREMENT_GUARDED_PROMPT_VERSION,
        CONFLICT_AUDITED_PROMPT_VERSION,
        AUTHORITATIVE_REQUIREMENTS_PROMPT_VERSION,
        CRITERION_STATUS_PROMPT_VERSION,
    }:
        constraints = cast(dict[str, object], payload["output_constraints"])
        constraints.pop("calibration_protocol", None)
        constraints["qualitative_calibration"] = {
            "mapping_version": "l3-deterministic-level-mapping-v1",
            "levels": {
                "unsupported": "no direct applied information for the criterion",
                "minimal": "only names, coursework, aspirations, or unsupported claims",
                "limited": "a narrow applied example with major depth, ownership, or outcome gaps",
                "developing": "relevant applied work with concrete detail but meaningful gaps",
                "competent": "clear end-to-end execution and a credible outcome with limited breadth",
                "strong": "multiple direct details show depth, ownership, outcomes, and few gaps",
                "exceptional": "rare comprehensive, verifiable depth and impact across the criterion",
            },
            "selection_rule": (
                "select the lower level when evidence lies between levels; the level describes "
                "evidence strength and is not a numeric score"
            ),
            "mandatory_policy": (
                "assess evidence depth, while deterministic code applies the exact critical-status "
                "policy for all-missing, unsatisfied, conflicting, missing, or all-satisfied states"
            ),
            "role_calibration_profile": _role_calibration_profile(job_profile.job_profile_id),
        }
        system_prompt = ROLE_CALIBRATED_SYSTEM_PROMPT
    if prompt_version == REQUIREMENT_GUARDED_PROMPT_VERSION:
        constraints = cast(dict[str, object], payload["output_constraints"])
        constraints["requirement_capability_guards"] = _requirement_capability_guards(
            job_profile.job_profile_id
        )
        system_prompt = REQUIREMENT_GUARDED_SYSTEM_PROMPT
    if prompt_version == CONFLICT_AUDITED_PROMPT_VERSION:
        constraints = cast(dict[str, object], payload["output_constraints"])
        constraints["requirement_capability_guards"] = _requirement_capability_guards(
            job_profile.job_profile_id
        )
        constraints["requirement_conflict_audit"] = {
            "scan_scope": "scan every evidence item across every section for each requirement",
            "positive_does_not_override_negative": (
                "direct_positive never cancels exact_negative for the same capability"
            ),
            "conflicting_rule": (
                "when both signals exist, return conflicting and cite IDs from both sides"
            ),
            "other_section_rule": (
                "an explicit capability denial in the other section remains exact_negative"
            ),
        }
        system_prompt = CONFLICT_AUDITED_SYSTEM_PROMPT
    if prompt_version in {
        AUTHORITATIVE_REQUIREMENTS_PROMPT_VERSION,
        CRITERION_STATUS_PROMPT_VERSION,
    }:
        expected_ids = set(rubric.critical_requirement_ids)
        supplied_ids = {item.requirement_id for item in authoritative_requirement_assessments}
        if supplied_ids != expected_ids or len(supplied_ids) != len(
            authoritative_requirement_assessments
        ):
            raise ValueError("authoritative requirement assessments must match the rubric")
        allowed_evidence_ids = {item.evidence_id for item in evidence}
        if any(
            not set(item.evidence_ids).issubset(allowed_evidence_ids)
            for item in authoritative_requirement_assessments
        ):
            raise ValueError("authoritative requirements reference unknown evidence")
        constraints = cast(dict[str, object], payload["output_constraints"])
        constraints["authoritative_requirement_assessments"] = [
            {
                "requirement_id": item.requirement_id,
                "evidence_status": item.evidence_status.value,
                "evidence_ids": list(item.evidence_ids),
            }
            for item in authoritative_requirement_assessments
        ]
        constraints["authoritative_requirement_rule"] = (
            "copy every authoritative requirement status and evidence_ids exactly"
        )
        system_prompt = AUTHORITATIVE_REQUIREMENTS_SYSTEM_PROMPT
    if prompt_version == CRITERION_STATUS_PROMPT_VERSION:
        constraints = cast(dict[str, object], payload["output_constraints"])
        constraints["criterion_evidence_status_rule"] = {
            "missing": "no supplied evidence is related to the criterion",
            "unsatisfied": (
                "related evidence states a limitation, failure, non-ownership, or absent output"
            ),
            "requirement_context_rule": (
                "context_only for a requirement may still support criterion-level evaluation"
            ),
        }
        system_prompt = CRITERION_STATUS_SYSTEM_PROMPT
    return (
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        },
    )


def _role_calibration_profile(job_profile_id: str) -> dict[str, str]:
    for prefix, profile in ROLE_CALIBRATION_PROFILES.items():
        if job_profile_id.startswith(prefix):
            return profile
    raise ValueError("role-calibrated prompt does not support this job profile")


def _requirement_capability_guards(job_profile_id: str) -> dict[str, str]:
    guards = {
        "junior-data-analyst-": {
            "language_boundary": (
                "SQL, BI tools, data analysis, and statistics do not prove Python or R unless "
                "Python, R, or an accepted named alternative is explicitly applied"
            ),
            "scope_boundary": (
                "a negative about one analysis language changes only the requirement atom that "
                "names that language or the explicit Python-or-R alternative"
            ),
        },
        "junior-python-backend-": {
            "language_boundary": (
                "API, SQL, framework, or deployment work does not prove Python unless Python is "
                "explicitly applied"
            ),
            "scope_boundary": (
                "a negative about Python does not negate SQL, Git, API concepts, or another "
                "independently evidenced requirement"
            ),
        },
        "junior-frontend-": {
            "language_boundary": (
                "HTML, CSS, React, API integration, and testing do not prove JavaScript or "
                "TypeScript unless the required language capability is explicitly applied"
            ),
            "scope_boundary": (
                "a JavaScript or TypeScript negative changes the language requirement only; it "
                "does not negate separately evidenced HTML, CSS, responsive, or accessibility work"
            ),
        },
        "junior-qa-engineer-": {
            "language_boundary": (
                "test artifacts, API tools, automation tools, and CI do not prove a named testing "
                "foundation unless its required practices are explicitly applied"
            ),
            "scope_boundary": (
                "a negative about automation does not negate separately evidenced manual test "
                "design, defect reporting, API testing, or SQL checks"
            ),
        },
        "junior-data-engineer-": {
            "language_boundary": (
                "ETL tools, pipelines, SQL, orchestration, or data modeling do not prove Python; "
                "Python must be explicitly named and applied"
            ),
            "scope_boundary": (
                "a negative about Python changes de-python only and does not negate separately "
                "evidenced SQL, pipeline, modeling, quality, or delivery requirements"
            ),
        },
    }
    for prefix, profile in guards.items():
        if job_profile_id.startswith(prefix):
            return profile
    raise ValueError("requirement-guarded prompt does not support this job profile")
