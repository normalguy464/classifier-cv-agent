from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

from backend.app.contracts import (
    EvidenceSection,
    JobProfile,
    RequirementPriority,
    RubricCriterion,
    ScoringRubric,
)
from backend.app.domain import L2CriterionPolicy, L2Policy, L2ScoringMode, ScoringInputError


@dataclass(frozen=True, slots=True)
class L2CoverageConfiguration:
    similarity_floor: Decimal
    similarity_ceiling: Decimal
    top_k: int
    minimum_query_score: Decimal
    section_weights: tuple[tuple[EvidenceSection, Decimal], ...]
    query_profile: Literal["coverage-v1", "rubric-signals-v2", "rubric-quality-v3"] = "coverage-v1"

    def __post_init__(self) -> None:
        L2CriterionPolicy(
            criterion_id="configuration-validation",
            query_text="configuration validation",
            evidence_sections=tuple(item[0] for item in self.section_weights),
            similarity_floor=self.similarity_floor,
            similarity_ceiling=self.similarity_ceiling,
            top_k=self.top_k,
            scoring_mode=L2ScoringMode.QUERY_COVERAGE,
            minimum_query_score=self.minimum_query_score,
            section_weights=self.section_weights,
        )


def _requirement_query(job: JobProfile, requirement_index: int) -> str:
    requirement = job.requirements[requirement_index]
    accepted = " ".join(requirement.accepted_evidence)
    return (
        f"{job.title}. Yêu cầu {requirement.title}. {requirement.description}. "
        f"Thông tin thực hành được chấp nhận: {accepted}"
    )


def _criterion_queries(
    job: JobProfile,
    rubric: ScoringRubric,
    criterion: RubricCriterion,
    criterion_index: int,
    query_profile: Literal["coverage-v1", "rubric-signals-v2", "rubric-quality-v3"],
) -> tuple[str, ...]:
    if query_profile in {"rubric-signals-v2", "rubric-quality-v3"}:
        if criterion_index == 0:
            queries = tuple(
                _requirement_query(job, index)
                for index, requirement in enumerate(job.requirements)
                if requirement.requirement_id in set(rubric.critical_requirement_ids)
            )
            if len(queries) != len(rubric.critical_requirement_ids):
                raise ScoringInputError("L2 critical requirement queries must cover the rubric")
            return queries
        quality_queries = {
            1: (
                "Năng lực chuyên môn có thao tác trực tiếp, độ sâu, xử lý lỗi và đầu ra chạy lại.",
                "Ứng viên tự thực hiện phần cốt lõi thay vì chỉ làm quen, quan sát hoặc làm theo mẫu.",
            ),
            2: (
                "Ứng viên giải thích lựa chọn, giả định, trade-off, tiêu chí thành công và giới hạn.",
                "Có quyết định kỹ thuật thuộc trách nhiệm ứng viên và cách kiểm tra kết quả.",
            ),
            3: (
                "Dự án nêu vai trò cá nhân, source, kiểm thử, hướng dẫn chạy, đầu ra và tác động.",
                "Phần bàn giao có thể tái tạo và phạm vi đóng góp được mô tả rõ.",
            ),
            4: (
                "CV nêu rõ phạm vi, kết quả định lượng, giới hạn và đóng góp cá nhân.",
                "Thông tin nhất quán, có cấu trúc và có chi tiết kiểm tra được.",
            ),
        }
        if query_profile == "rubric-quality-v3" and criterion_index >= 2:
            return quality_queries[criterion_index]
        return (f"{criterion.title}. {criterion.description}", *quality_queries[criterion_index])
    critical_ids = set(rubric.critical_requirement_ids)
    if criterion_index == 0:
        queries = tuple(
            _requirement_query(job, index)
            for index, requirement in enumerate(job.requirements)
            if requirement.requirement_id in critical_ids
        )
        if len(queries) != len(critical_ids):
            raise ScoringInputError("L2 critical requirement queries must cover the rubric")
        return queries
    if criterion_index == 1:
        return tuple(
            _requirement_query(job, index)
            for index, requirement in enumerate(job.requirements)
            if requirement.priority in {RequirementPriority.REQUIRED, RequirementPriority.PREFERRED}
        )
    if criterion_index == 2:
        return tuple(
            f"{job.title}. Năng lực thực hiện trách nhiệm: {responsibility}"
            for responsibility in job.responsibilities
        )
    if criterion_index == 3:
        return (
            f"{job.title}. {criterion.title}. {criterion.description}. "
            "Dự án hoặc thực tập cần nêu vai trò, cách thực hiện, đầu ra, tác động và giới hạn.",
        )
    return (
        f"{job.title}. {criterion.title}. {criterion.description}. "
        "Thông tin cần rõ ràng, nhất quán, có chi tiết kiểm tra được và nêu giới hạn.",
    )


def _criterion_sections(criterion_index: int) -> tuple[EvidenceSection, ...]:
    if criterion_index in {0, 1}:
        return (
            EvidenceSection.SKILLS,
            EvidenceSection.WORK_EXPERIENCE,
            EvidenceSection.PROJECTS,
            EvidenceSection.EDUCATION,
            EvidenceSection.CERTIFICATIONS,
            EvidenceSection.OTHER,
        )
    if criterion_index in {2, 3}:
        return (
            EvidenceSection.WORK_EXPERIENCE,
            EvidenceSection.PROJECTS,
            EvidenceSection.EDUCATION,
            EvidenceSection.OTHER,
        )
    return (
        EvidenceSection.WORK_EXPERIENCE,
        EvidenceSection.PROJECTS,
        EvidenceSection.OTHER,
    )


def build_query_coverage_l2_policy(
    job: JobProfile,
    rubric: ScoringRubric,
    configuration: L2CoverageConfiguration,
) -> L2Policy:
    if job.job_profile_id != rubric.job_profile_id:
        raise ScoringInputError("L2 Job Profile and rubric must reference each other")
    if len(rubric.criteria) != 5 or rubric.criteria[0].criterion_id != "mandatory-requirements":
        raise ScoringInputError("query coverage requires the canonical five-criterion rubric")
    configured_weights = dict(configuration.section_weights)
    policies: list[L2CriterionPolicy] = []
    for criterion_index, criterion in enumerate(rubric.criteria):
        query_texts = _criterion_queries(
            job,
            rubric,
            criterion,
            criterion_index,
            configuration.query_profile,
        )
        evidence_sections = _criterion_sections(criterion_index)
        section_weights = tuple(
            (section, configured_weights[section])
            for section in evidence_sections
            if section in configured_weights
        )
        policies.append(
            L2CriterionPolicy(
                criterion_id=criterion.criterion_id,
                query_text=query_texts[0],
                additional_query_texts=query_texts[1:],
                evidence_sections=evidence_sections,
                similarity_floor=configuration.similarity_floor,
                similarity_ceiling=configuration.similarity_ceiling,
                top_k=configuration.top_k,
                scoring_mode=L2ScoringMode.QUERY_COVERAGE,
                minimum_query_score=configuration.minimum_query_score,
                section_weights=section_weights,
            )
        )
    return L2Policy(job_profile_id=job.job_profile_id, criteria=tuple(policies))
