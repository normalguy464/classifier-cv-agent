from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Sequence, cast

from pydantic import BaseModel

from backend.app.contracts import (
    CVProfile,
    ClassificationDecision,
    EvidenceStatus,
    JobProfile,
    ScoringRubric,
)
from backend.app.infrastructure.config import RepositoryConfigurationLoader
from evaluation.datasets.stage7 import (
    Stage7FileDigest,
    Stage7PriorDatasetReference,
    Stage7TestManifest,
    validate_stage7_test_set,
)
from evaluation.datasets.synthetic_expansion import (
    DatasetRole,
    DatasetTier,
    PendingDatasetReview,
    SyntheticPairAnnotation,
    SyntheticScenario,
    file_sha256,
)
from scripts.generate_stage7_test_set import build_stage7_test_set

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIRECTORY = REPOSITORY_ROOT / "data" / "to_review" / "stage7_runtime_v2_test_v1"
RUNTIME_DIRECTORY = REPOSITORY_ROOT / "configs" / "runtime" / "five_role_v2"
REFERENCE_MANIFEST = (
    REPOSITORY_ROOT / "data" / "runtime_v2" / "reviewed" / "development_v1" / "manifest.json"
)
GENERATED_AT = "2026-08-08T15:00:00+07:00"

PRIOR_DATASET_PATHS: tuple[tuple[str, str], ...] = (
    ("stage4-reviewed-v1", "data/reviewed/stage4_cv_profiles_v1.jsonl"),
    ("synthetic-expansion-v1", "data/synthetic_expansion/v1/cv_profiles.jsonl"),
    ("synthetic-expansion-v2-draft", "data/synthetic_expansion/v2/cv_profiles.jsonl"),
    (
        "synthetic-expansion-v2-3-1-reviewed",
        "data/synthetic_expansion/reviewed/v2_3_1/cv_profiles.jsonl",
    ),
    ("stage7-runtime-v1-draft", "data/to_review/stage7_test_v1/cv_profiles.jsonl"),
    ("stage7-runtime-v1-gold", "data/frozen_test/stage7_v1/cv_profiles.jsonl"),
    (
        "runtime-v2-development-reviewed",
        "data/runtime_v2/reviewed/development_v1/cv_profiles.jsonl",
    ),
)

PROFILE_CONTEXTS: dict[DatasetRole, tuple[str, ...]] = {
    DatasetRole.DATA_ANALYST: (
        "Nhóm vận hành cần đối soát thất thoát đơn hàng giữa ba nguồn dữ liệu khác múi giờ.",
        "Bộ phận tăng trưởng cần phân tách tác động của chiến dịch theo cohort và kênh thu hút.",
        "Đội sản phẩm cần kiểm tra nguyên nhân tỷ lệ kích hoạt giảm sau một lần thay đổi giao diện.",
        "Nhóm tài chính cần tái lập báo cáo doanh thu với quy tắc hoàn tiền thay đổi theo kỳ.",
        "Trung tâm hỗ trợ cần phân tích thời gian xử lý và tỷ lệ mở lại theo loại yêu cầu.",
        "Đơn vị bán lẻ cần theo dõi tồn kho chậm luân chuyển và cảnh báo sai lệch nhập xuất.",
        "Nhóm giáo dục cần đo tiến trình học tập khi dữ liệu sự kiện có bản ghi đến muộn.",
        "Đội marketplace cần xây định nghĩa thống nhất cho GMV, đơn hợp lệ và nhà bán hoạt động.",
        "Ứng viên chuyển từ nghiên cứu định lượng sang bài toán phân tích hành vi người dùng.",
        "Hồ sơ mô tả kiến thức khóa học nhưng chưa gắn với một quyết định kinh doanh cụ thể.",
    ),
    DatasetRole.PYTHON_BACKEND: (
        "Dịch vụ cần chống tạo trùng yêu cầu khi client gửi lại sau lỗi mạng.",
        "API quản lý kho phải giữ nhất quán dữ liệu khi hai tiến trình cập nhật đồng thời.",
        "Hệ thống đặt lịch cần phân quyền, audit log và chuẩn hóa phản hồi lỗi.",
        "Webhook thanh toán cần xác minh chữ ký và xử lý sự kiện không đúng thứ tự.",
        "Dịch vụ thư viện số cần phân trang ổn định và giới hạn truy vấn tốn tài nguyên.",
        "Ứng viên chuyển từ lập trình nhúng sang backend và công khai phạm vi chưa thành thạo.",
        "Ứng dụng quản lý công việc cần migration có thể rollback và health check riêng.",
        "API chi tiêu cần refresh token, thu hồi phiên và kiểm tra quyền sở hữu tài nguyên.",
        "Ứng viên chuyển từ Java sang FastAPI với bài tập đo tải và theo dõi lỗi.",
        "Hồ sơ liệt kê framework backend nhưng không nêu endpoint hay dữ liệu từng xử lý.",
    ),
    DatasetRole.FRONTEND: (
        "Cổng học tập phải dùng được bằng bàn phím và giữ trạng thái khi quay lại trang.",
        "Giỏ hàng cần đồng bộ nhiều tab và giải quyết phản hồi API đến không đúng thứ tự.",
        "Dashboard vận hành cần tải dần biểu đồ lớn và hiển thị trạng thái dữ liệu cũ.",
        "Biểu mẫu sự kiện nhiều bước phải khôi phục bản nháp sau khi phiên đăng nhập hết hạn.",
        "Trang quản trị cần ẩn thao tác theo quyền và vẫn xử lý phản hồi 403 từ máy chủ.",
        "Ứng viên chuyển từ thiết kế giao diện sang lập trình và mô tả rõ phần tự triển khai.",
        "Trang tra cứu thư viện cần responsive, hỗ trợ screen reader và điều hướng lịch sử.",
        "Ứng dụng thói quen cần optimistic update cùng cơ chế hoàn tác khi đồng bộ thất bại.",
        "Ứng viên chuyển từ Vue sang React và so sánh cách quản lý state trong hai hệ sinh thái.",
        "Hồ sơ chỉ nêu tên thư viện giao diện mà chưa có luồng người dùng hoàn chỉnh.",
    ),
    DatasetRole.QA_ENGINEER: (
        "Luồng thanh toán cần ma trận kiểm thử cho retry, timeout và sự kiện gửi trùng.",
        "Ứng dụng đặt lịch cần kiểm tra xung đột thời gian trên trình duyệt và múi giờ khác nhau.",
        "API kho cần đối chiếu contract, dữ liệu biên và transaction chạy đồng thời.",
        "Ứng dụng học tập cần truy vết lỗi tiến trình bài học qua nhiều phiên đăng nhập.",
        "Cổng quản trị cần kiểm tra quyền truy cập và lưu audit trail cho thao tác nhạy cảm.",
        "Ứng viên chuyển từ hỗ trợ khách hàng sang QA với taxonomy lỗi có thể tái sử dụng.",
        "Ứng dụng di động cần kiểm tra gián đoạn mạng và đồng bộ lại sau khi offline.",
        "Pipeline phát hành cần smoke test, tiêu chí dừng và bằng chứng hồi quy tối thiểu.",
        "Ứng viên chuyển từ phân tích nghiệp vụ sang QA và liên kết acceptance criteria với test.",
        "Hồ sơ liệt kê công cụ kiểm thử nhưng không mô tả test case hoặc defect đã theo dõi.",
    ),
    DatasetRole.DATA_ENGINEER: (
        "Pipeline giao dịch cần checkpoint và khôi phục mà không nhân đôi bản ghi.",
        "Luồng đồng bộ sản phẩm phải xử lý schema thay đổi và giới hạn tốc độ API nguồn.",
        "Data mart doanh thu cần kiểm soát late-arriving dimension và lịch sử thay đổi.",
        "Luồng sự kiện cần watermark, dead-letter queue và phép đo độ trễ theo partition.",
        "Pipeline chất lượng không khí cần kiểm tra sensor drift và dữ liệu thiếu theo trạm.",
        "Ứng viên chuyển từ backend sang data engineering và mô tả rõ phần batch mới học.",
        "Luồng log ứng dụng cần chuẩn hóa schema trước khi phục vụ dashboard vận hành.",
        "Pipeline học tập cần incremental load và backfill không làm thay đổi kết quả cũ.",
        "Ứng viên chuyển từ SQL phân tích sang xây pipeline có orchestration và quan sát lỗi.",
        "Hồ sơ chỉ liệt kê nền tảng dữ liệu mà chưa nêu nguồn, đích hoặc lịch chạy cụ thể.",
    ),
}

EVIDENCE_ANGLES: tuple[str, ...] = (
    "Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.",
    "Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.",
    "Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.",
    "Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.",
    "Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.",
    "Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.",
    "Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.",
    "Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.",
    "Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.",
    "Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.",
    "Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.",
    "Kết luận chỉ giới hạn trong phạm vi mẫu đã quan sát và không suy diễn quá mức.",
    "Cách đặt tên đầu ra giúp truy vết từ yêu cầu tới kết quả kiểm tra.",
    "Thời gian xử lý được đo trên cùng cấu hình trước khi nêu mức cải thiện.",
    "Bản bàn giao nêu rõ việc còn thiếu để người đánh giá không hiểu thành đã hoàn tất.",
)

BOUNDARY_POINTS: dict[SyntheticScenario, tuple[int, int, int, int, int]] = {
    SyntheticScenario.LOWER_BOUNDARY: (27, 13, 10, 8, 9),
    SyntheticScenario.UPPER_BOUNDARY: (30, 18, 15, 12, 7),
}


def _replace_identifiers(value: object) -> object:
    if isinstance(value, str):
        return value.replace("s7-", "s7v2-").replace("stage7-", "stage7v2-")
    if isinstance(value, list):
        values = cast(list[object], value)
        return [_replace_identifiers(item) for item in values]
    if isinstance(value, tuple):
        values = cast(tuple[object, ...], value)
        return tuple(_replace_identifiers(item) for item in values)
    if isinstance(value, dict):
        values = cast(dict[str, object], value)
        return {key: _replace_identifiers(item) for key, item in values.items()}
    return value


def _transform_profile(
    profile: CVProfile,
    role: DatasetRole,
    sequence: int,
) -> CVProfile:
    payload = cast(dict[str, object], _replace_identifiers(profile.model_dump(mode="json")))
    context = PROFILE_CONTEXTS[role][sequence - 1]
    payload["summary"] = f"{context} {cast(str, payload['summary'])}"
    evidence_values = cast(list[dict[str, object]], payload["evidence"])
    for index, evidence in enumerate(evidence_values):
        evidence["text"] = (
            f"{cast(str, evidence['text'])} {context} "
            f"{EVIDENCE_ANGLES[index % len(EVIDENCE_ANGLES)]}"
        )
    project_values = cast(list[dict[str, object]], payload["projects"])
    for project in project_values:
        project["summary"] = (
            f"{cast(str, project['summary'])} {context} "
            f"{EVIDENCE_ANGLES[(sequence + 3) % len(EVIDENCE_ANGLES)]}"
        )
    return CVProfile.model_validate(payload)


def _review_reasons(
    statuses: tuple[EvidenceStatus, ...],
    total_score: int,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if EvidenceStatus.MISSING in statuses:
        reasons.append("missing-critical-evidence")
    if EvidenceStatus.CONFLICTING in statuses:
        reasons.append("conflicting-critical-evidence")
    if 65 <= total_score <= 69:
        reasons.append("lower-threshold-boundary")
    if 80 <= total_score <= 84:
        reasons.append("upper-threshold-boundary")
    if EvidenceStatus.UNSATISFIED in statuses and total_score >= 67:
        reasons.append("critical-unsatisfied-at-or-above-waitlist-threshold")
    if total_score < 67 and EvidenceStatus.UNSATISFIED not in statuses:
        reasons.append("low-score-without-explicit-critical-unsatisfied")
    return tuple(dict.fromkeys(reasons))


def _draft_decision(
    statuses: tuple[EvidenceStatus, ...],
    total_score: int,
    review_reasons: tuple[str, ...],
) -> ClassificationDecision:
    if review_reasons:
        return ClassificationDecision.NEEDS_REVIEW
    if EvidenceStatus.UNSATISFIED in statuses:
        return ClassificationDecision.REJECT
    if total_score >= 82:
        return ClassificationDecision.PASS
    if total_score >= 67:
        return ClassificationDecision.WAITLIST
    return ClassificationDecision.NEEDS_REVIEW


def _transform_annotation(
    annotation: SyntheticPairAnnotation,
    profile: CVProfile,
    job: JobProfile,
    rubric: ScoringRubric,
) -> SyntheticPairAnnotation:
    payload = cast(dict[str, object], _replace_identifiers(annotation.model_dump(mode="json")))
    payload["cv_profile_id"] = profile.cv_profile_id
    payload["candidate_reference"] = profile.candidate_reference
    payload["job_profile_id"] = job.job_profile_id
    payload["rubric_id"] = rubric.rubric_id
    points = BOUNDARY_POINTS.get(annotation.scenario)
    criterion_values = cast(list[dict[str, object]], payload["criterion_assessments"])
    if points is not None:
        for assessment, awarded_points in zip(criterion_values, points, strict=True):
            assessment["awarded_points"] = awarded_points
    total_score = sum(
        int(cast(int | float | str, assessment["awarded_points"]))
        for assessment in criterion_values
    )
    requirement_values = cast(list[dict[str, object]], payload["critical_requirement_assessments"])
    statuses = tuple(
        EvidenceStatus(cast(str, assessment["evidence_status"]))
        for assessment in requirement_values
    )
    review_reasons = _review_reasons(statuses, total_score)
    payload["total_score"] = total_score
    payload["draft_label"] = _draft_decision(statuses, total_score, review_reasons)
    payload["review_reasons"] = review_reasons
    payload["overall_rationale"] = (
        "Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, "
        "vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới "
        "khi hoàn tất human review và khóa Gold."
    )
    payload["review"] = PendingDatasetReview().model_dump(mode="json")
    return SyntheticPairAnnotation.model_validate(payload)


def build_stage7_runtime_v2_test_set() -> tuple[
    tuple[CVProfile, ...],
    tuple[JobProfile, ...],
    tuple[ScoringRubric, ...],
    tuple[SyntheticPairAnnotation, ...],
]:
    base_profiles, _, _, base_annotations = build_stage7_test_set()
    loader = RepositoryConfigurationLoader(REPOSITORY_ROOT, RUNTIME_DIRECTORY)
    jobs_by_role = {
        DatasetRole(
            artifact.job_profile_id.removeprefix("junior-")
            .removesuffix("-std-v2")
            .replace("-", "_")
        ): artifact.to_contract()
        for artifact in loader.load_job_artifacts()
    }
    rubrics_by_role = {
        role: loader.load_for_job(job.job_profile_id).rubric for role, job in jobs_by_role.items()
    }
    profiles: list[CVProfile] = []
    annotations: list[SyntheticPairAnnotation] = []
    for index, (base_profile, base_annotation) in enumerate(
        zip(base_profiles, base_annotations, strict=True)
    ):
        sequence = index % 10 + 1
        role = base_annotation.role
        profile = _transform_profile(base_profile, role, sequence)
        job = jobs_by_role[role]
        rubric = rubrics_by_role[role]
        profiles.append(profile)
        annotations.append(_transform_annotation(base_annotation, profile, job, rubric))
    ordered_roles = tuple(DatasetRole)
    jobs = tuple(jobs_by_role[role] for role in ordered_roles)
    rubrics = tuple(rubrics_by_role[role] for role in ordered_roles)
    return tuple(profiles), jobs, rubrics, tuple(annotations)


def _write_json_lines(path: Path, records: Sequence[BaseModel]) -> None:
    values = (
        json.dumps(record.model_dump(mode="json"), ensure_ascii=False, sort_keys=True)
        for record in records
    )
    path.write_text("\n".join(values) + "\n", encoding="utf-8")


def _review_sheet(
    profiles: tuple[CVProfile, ...],
    jobs: tuple[JobProfile, ...],
    annotations: tuple[SyntheticPairAnnotation, ...],
) -> str:
    profiles_by_id = {profile.cv_profile_id: profile for profile in profiles}
    jobs_by_id = {job.job_profile_id: job for job in jobs}
    lines = [
        "# Phiếu duyệt test set Stage 7 cho Runtime v2",
        "",
        "Bộ này gồm 50 cặp CV–JD mới, 10 cặp cho mỗi vai trò. Tất cả nhãn đang là bản nháp Bronze; classifier và API LLM chưa được chạy trên bộ dữ liệu này.",
        "",
        "Với mỗi case, hãy duyệt nội dung CV, trạng thái yêu cầu bắt buộc, năm nhóm điểm, tổng điểm, nhãn và lý do. Nếu một lỗi dự đoán sau này chỉ xuất hiện ở số ít case không liên quan an toàn, case vẫn phải được giữ trong báo cáo thay vì xóa khỏi test set.",
    ]
    for annotation in annotations:
        profile = profiles_by_id[annotation.cv_profile_id]
        job = jobs_by_id[annotation.job_profile_id]
        lines.extend(
            (
                "",
                f"## {annotation.pair_id} — {job.title}",
                "",
                f"Kịch bản kiểm thử: `{annotation.scenario.value}`",
                "",
                f"Tóm tắt CV: {profile.summary}",
                "",
                "Thông tin đánh giá chính:",
                "",
            )
        )
        for evidence in profile.evidence:
            lines.append(f"- `{evidence.evidence_id}`: {evidence.text}")
        lines.extend(("", "Trạng thái yêu cầu bắt buộc:", ""))
        for assessment in annotation.critical_requirement_assessments:
            evidence_ids = ", ".join(assessment.evidence_ids) or "không có thông tin liên kết"
            lines.append(
                f"- `{assessment.requirement_id}`: `{assessment.evidence_status.value}`; "
                f"thông tin: {evidence_ids}; {assessment.rationale}"
            )
        lines.extend(("", "Điểm theo tiêu chí:", "", "| Tiêu chí | Điểm |", "| --- | ---: |"))
        for assessment in annotation.criterion_assessments:
            lines.append(
                f"| `{assessment.criterion_id}` | "
                f"{assessment.awarded_points}/{assessment.maximum_points} |"
            )
        reasons = ", ".join(annotation.review_reasons) or "không có"
        lines.extend(
            (
                "",
                f"Tổng điểm: **{annotation.total_score}/100**",
                "",
                f"Nhãn nháp: **{annotation.draft_label.value}**",
                "",
                f"Lý do vào review: {reasons}",
                "",
                f"Lý do tổng hợp: {annotation.overall_rationale}",
            )
        )
    return "\n".join(lines) + "\n"


def write_stage7_runtime_v2_test_set(
    output_directory: Path = OUTPUT_DIRECTORY,
) -> tuple[Path, ...]:
    profiles, jobs, rubrics, annotations = build_stage7_runtime_v2_test_set()
    output_directory.mkdir(parents=True, exist_ok=True)
    paths = tuple(
        output_directory / name
        for name in ("cv_profiles.jsonl", "job_profiles.jsonl", "rubrics.jsonl", "pairs.jsonl")
    )
    for path, records in zip(paths, (profiles, jobs, rubrics, annotations), strict=True):
        _write_json_lines(path, records)
    review_sheet_path = output_directory / "review_sheet.md"
    review_sheet_path.write_text(_review_sheet(profiles, jobs, annotations), encoding="utf-8")
    prior_datasets = tuple(
        Stage7PriorDatasetReference(
            dataset_id=dataset_id,
            cv_profiles_path=relative_path,
            cv_profiles_sha256=file_sha256(REPOSITORY_ROOT / relative_path),
        )
        for dataset_id, relative_path in PRIOR_DATASET_PATHS
    )
    runtime_manifest_path = RUNTIME_DIRECTORY / "runtime_manifest.yaml"
    manifest = Stage7TestManifest(
        schema_version="1.1.0",
        dataset_id="stage7-five-role-runtime-v2-test-v1",
        dataset_version="1.0.0",
        status="draft_for_human_review",
        generated_at=datetime.fromisoformat(GENERATED_AT),
        source_type="synthetic_new_profiles",
        runtime_configuration_set_id="five-role-runtime-v2",
        runtime_manifest_path=runtime_manifest_path.relative_to(REPOSITORY_ROOT).as_posix(),
        runtime_manifest_sha256=file_sha256(runtime_manifest_path),
        cv_schema_version="1.0.0",
        job_profile_schema_version="1.0.0",
        rubric_schema_version="1.0.0",
        candidate_count=50,
        job_profile_count=5,
        rubric_count=5,
        pair_count=50,
        role_pair_counts=dict(Counter(item.role for item in annotations)),
        scenario_pair_counts=dict(Counter(item.scenario for item in annotations)),
        draft_label_counts=dict(Counter(item.draft_label for item in annotations)),
        dataset_tier=DatasetTier.BRONZE,
        ground_truth_status="pending_human_review",
        minimum_human_reviewers_for_gold=2,
        locked_for_evaluation=False,
        classifier_results_generated=False,
        llm_requests_made=False,
        source_dataset_version="2.0.0",
        source_manifest_sha256=file_sha256(REFERENCE_MANIFEST),
        prior_datasets=prior_datasets,
        provenance=(
            "All CV profiles are synthetic and contain no real candidate data.",
            "Runtime v2 Job Profiles and rubrics were copied without modification.",
            "Profiles use new operational contexts and evidence details independent of prior sets.",
            "All prior Stage 3-7 and Runtime v2 development profiles participate in leakage checks.",
            "Opaque identifiers do not expose labels or scenarios.",
            "Draft annotations are not ground truth until two-person human consensus review.",
            "No classifier layer or LLM provider was executed during construction.",
            "Cases must not be removed after predictions are observed to improve metrics.",
        ),
        files=tuple(
            Stage7FileDigest(
                path=path.name,
                sha256=file_sha256(path),
                record_count=count,
            )
            for path, count in (
                (paths[0], len(profiles)),
                (paths[1], len(jobs)),
                (paths[2], len(rubrics)),
                (paths[3], len(annotations)),
                (review_sheet_path, len(annotations)),
            )
        ),
    )
    manifest_path = output_directory / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report = validate_stage7_test_set(REPOSITORY_ROOT, output_directory)
    quality_report_path = output_directory / "quality_report.json"
    quality_report_path.write_text(
        json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if not report.passed or report.warnings:
        raise ValueError(f"Stage 7 Runtime v2 test set failed QC: {report.model_dump()}")
    return paths + (review_sheet_path, manifest_path, quality_report_path)


def main() -> None:
    for path in write_stage7_runtime_v2_test_set():
        print(path)


if __name__ == "__main__":
    main()
