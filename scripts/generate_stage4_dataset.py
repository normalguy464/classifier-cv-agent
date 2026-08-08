from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from backend.app.contracts import CVProfile

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIRECTORY = REPOSITORY_ROOT / "data" / "to_review"
CV_OUTPUT_FILE = OUTPUT_DIRECTORY / "stage4_cv_profiles_v1.jsonl"
ANNOTATION_OUTPUT_FILE = OUTPUT_DIRECTORY / "stage4_annotations_v1.json"


@dataclass(frozen=True)
class Scenario:
    number: int
    status_override_indexes: tuple[int, int] | None
    status_override: str | None
    criterion_points: tuple[int, int, int, int, int]
    draft_label: str
    review_reasons: tuple[str, ...]
    technical_detail: str
    reasoning_detail: str
    delivery_detail: str
    communication_detail: str
    preferred_skill_count: int


@dataclass(frozen=True)
class RoleDefinition:
    code: str
    scenario_role_index: int
    job_profile_id: str
    rubric_id: str
    profile_summary: str
    requirement_ids: tuple[str, ...]
    requirement_skill_names: tuple[str, ...]
    positive_evidence_texts: tuple[str, ...]
    negative_evidence_texts: tuple[str, ...]
    preferred_skills: tuple[tuple[str, str], ...]
    criterion_ids: tuple[str, ...]
    criterion_rationale_bases: tuple[str, ...]
    reasoning_prefix: str
    delivery_prefix: str
    project_title: str
    project_summary: str
    project_requirement_index: int


SCENARIOS: tuple[Scenario, ...] = (
    Scenario(
        number=1,
        status_override_indexes=None,
        status_override=None,
        criterion_points=(30, 23, 18, 13, 9),
        draft_label="pass",
        review_reasons=(),
        technical_detail=(
            "Phần kỹ thuật kết hợp nhiều nguồn đầu vào, kiểm tra kiểu dữ liệu, "
            "bản ghi trùng và trường hợp lỗi trước khi tạo đầu ra."
        ),
        reasoning_detail=(
            "Ứng viên so sánh hai cách xử lý, ghi giả định và kiểm tra kết quả "
            "trên các trường hợp biên."
        ),
        delivery_detail=(
            "Đầu ra được chạy định kỳ trong tám tuần và rút ngắn thao tác tổng hợp "
            "từ ba giờ xuống còn bốn mươi lăm phút."
        ),
        communication_detail=(
            "Tài liệu mô tả nguồn đầu vào, cách tái tạo kết quả, quyết định kỹ thuật, "
            "ví dụ và giới hạn còn lại."
        ),
        preferred_skill_count=4,
    ),
    Scenario(
        number=2,
        status_override_indexes=None,
        status_override=None,
        criterion_points=(30, 21, 16, 12, 8),
        draft_label="pass",
        review_reasons=(),
        technical_detail=(
            "Phần kỹ thuật ghép hai nguồn đầu vào, tách bước biến đổi và đối chiếu "
            "kết quả bằng một bộ mẫu đã chuẩn bị."
        ),
        reasoning_detail=(
            "Ứng viên xác định mục tiêu, chọn cách xử lý theo dữ liệu quan sát được "
            "và ghi lại các ngoại lệ chính."
        ),
        delivery_detail=(
            "Quy trình được thử với một nghìn hai trăm bản ghi và có lệnh tái chạy "
            "cho người tiếp nhận."
        ),
        communication_detail=(
            "README nêu cách cài đặt, cấu trúc đầu ra, giả định và một ví dụ sử dụng."
        ),
        preferred_skill_count=3,
    ),
    Scenario(
        number=3,
        status_override_indexes=None,
        status_override=None,
        criterion_points=(30, 19, 14, 10, 7),
        draft_label="pass",
        review_reasons=(),
        technical_detail=(
            "Phần kỹ thuật xử lý một nguồn có cấu trúc, chuẩn hóa trường dữ liệu "
            "và kiểm tra định dạng đầu vào."
        ),
        reasoning_detail=(
            "Ứng viên nêu mục tiêu, đối chiếu kết quả trước và sau xử lý, đồng thời "
            "ghi nhận một giới hạn của dữ liệu mẫu."
        ),
        delivery_detail=(
            "Đầu ra được tái chạy trên ba bộ dữ liệu mẫu và kèm tệp kết quả để đối chiếu."
        ),
        communication_detail=(
            "Hướng dẫn mô tả cách chạy, cấu trúc đầu ra và một số lỗi thường gặp."
        ),
        preferred_skill_count=2,
    ),
    Scenario(
        number=4,
        status_override_indexes=None,
        status_override=None,
        criterion_points=(30, 16, 11, 8, 5),
        draft_label="waitlist",
        review_reasons=(),
        technical_detail=(
            "Phần kỹ thuật xử lý một nguồn dữ liệu, thực hiện phép biến đổi chính "
            "và kiểm tra thủ công một số giá trị đầu ra."
        ),
        reasoning_detail=(
            "Ứng viên nêu mục tiêu và chọn một cách xử lý nhưng chỉ ghi ngắn gọn các giả định."
        ),
        delivery_detail=(
            "Sản phẩm có thể chạy cục bộ với dữ liệu mẫu nhưng chưa ghi nhận quá trình "
            "sử dụng sau khi bàn giao."
        ),
        communication_detail=(
            "README có bước cài đặt và ví dụ đầu ra nhưng chưa giải thích các quyết định chính."
        ),
        preferred_skill_count=1,
    ),
    Scenario(
        number=5,
        status_override_indexes=None,
        status_override=None,
        criterion_points=(30, 14, 10, 7, 6),
        draft_label="waitlist",
        review_reasons=(),
        technical_detail=(
            "Phần kỹ thuật thực hiện các thao tác cơ bản trên đầu vào dự kiến và "
            "chưa tự động kiểm tra trường hợp bất thường."
        ),
        reasoning_detail=(
            "Ứng viên mô tả kết quả mong muốn nhưng chưa so sánh phương án hoặc "
            "phân tích nguyên nhân sai lệch."
        ),
        delivery_detail=("Sản phẩm được chạy một lần trên tập mẫu nhỏ và lưu lại ảnh chụp đầu ra."),
        communication_detail=(
            "Tài liệu liệt kê lệnh cài đặt và các chức năng chính bằng mô tả ngắn."
        ),
        preferred_skill_count=1,
    ),
    Scenario(
        number=6,
        status_override_indexes=None,
        status_override=None,
        criterion_points=(30, 13, 9, 7, 5),
        draft_label="waitlist",
        review_reasons=(),
        technical_detail=(
            "Phần kỹ thuật thực hiện thao tác chính trên một tệp mẫu và chưa mô tả "
            "kiểm tra chất lượng hoặc xử lý lỗi."
        ),
        reasoning_detail=(
            "Ứng viên nêu nhiệm vụ cần làm nhưng không giải thích lý do chọn phương pháp."
        ),
        delivery_detail=(
            "Đầu ra chỉ được xác nhận trên máy cá nhân và chưa có quy trình tái tạo độc lập."
        ),
        communication_detail=("Ghi chú chỉ gồm một số lệnh chạy, không nêu bối cảnh và giới hạn."),
        preferred_skill_count=0,
    ),
    Scenario(
        number=7,
        status_override_indexes=(0, 0),
        status_override="missing",
        criterion_points=(20, 17, 13, 10, 6),
        draft_label="needs_review",
        review_reasons=("missing-critical-evidence",),
        technical_detail=(
            "Phần kỹ thuật còn lại mô tả hai bước biến đổi, kiểm tra định dạng "
            "và đối chiếu kết quả bằng mẫu nhỏ."
        ),
        reasoning_detail=(
            "Ứng viên nêu câu hỏi cần giải quyết và kiểm tra một trường hợp ngoại lệ."
        ),
        delivery_detail=(
            "Đầu ra có bản chạy thử, tệp mẫu và ghi chú về phạm vi chưa được kiểm chứng."
        ),
        communication_detail=(
            "Tài liệu nêu cách chạy và phần việc cá nhân nhưng thiếu chi tiết về một thành phần."
        ),
        preferred_skill_count=2,
    ),
    Scenario(
        number=8,
        status_override_indexes=(1, 1),
        status_override="missing",
        criterion_points=(20, 15, 12, 9, 6),
        draft_label="needs_review",
        review_reasons=("missing-critical-evidence",),
        technical_detail=(
            "Phần kỹ thuật còn lại có kiểm tra đầu vào và lưu đầu ra nhưng chưa "
            "mô tả cách kiểm thử tự động."
        ),
        reasoning_detail=(
            "Ứng viên trình bày mục tiêu và một giả định, chưa nêu cách kiểm tra độ ổn định."
        ),
        delivery_detail=(
            "Sản phẩm có dữ liệu minh họa và hướng dẫn chạy cục bộ cho một luồng chính."
        ),
        communication_detail=(
            "Ghi chú mô tả đầu vào và đầu ra nhưng không bao quát toàn bộ thành phần."
        ),
        preferred_skill_count=1,
    ),
    Scenario(
        number=9,
        status_override_indexes=(0, 0),
        status_override="conflicting",
        criterion_points=(22, 17, 13, 9, 6),
        draft_label="needs_review",
        review_reasons=("conflicting-critical-evidence",),
        technical_detail=(
            "Phần kỹ thuật mô tả phép biến đổi, bước xác thực đầu vào và một lần "
            "đối chiếu đầu ra với dữ liệu gốc."
        ),
        reasoning_detail=("Ứng viên nêu mục tiêu, giả định và một cách kiểm tra sai lệch."),
        delivery_detail=("Đầu ra có thể chạy lại trên tập mẫu, kèm danh sách vấn đề còn mở."),
        communication_detail=(
            "Tài liệu có hướng dẫn sử dụng và phạm vi đóng góp nhưng một mô tả kỹ năng "
            "không nhất quán."
        ),
        preferred_skill_count=2,
    ),
    Scenario(
        number=10,
        status_override_indexes=(1, 1),
        status_override="conflicting",
        criterion_points=(22, 16, 12, 9, 6),
        draft_label="needs_review",
        review_reasons=("conflicting-critical-evidence",),
        technical_detail=(
            "Phần kỹ thuật tách bước nhập dữ liệu, xử lý và xuất kết quả, với kiểm tra "
            "thủ công cho luồng chính."
        ),
        reasoning_detail=(
            "Ứng viên mô tả mục tiêu và giới hạn của tập mẫu nhưng chưa kiểm tra nhiều ngoại lệ."
        ),
        delivery_detail=(
            "Bản chạy thử có tệp cấu hình mẫu và danh sách bước tái tạo trên máy mới."
        ),
        communication_detail=(
            "README nêu cấu trúc dự án và phần việc cá nhân nhưng có hai phát biểu "
            "kỹ thuật chưa thống nhất."
        ),
        preferred_skill_count=1,
    ),
    Scenario(
        number=11,
        status_override_indexes=(1, 1),
        status_override="unsatisfied",
        criterion_points=(10, 11, 9, 3, 7),
        draft_label="reject",
        review_reasons=(),
        technical_detail=(
            "Phần kỹ thuật chỉ mô tả thao tác nhập và xuất dữ liệu trên ví dụ nhỏ, "
            "không có kiểm tra lỗi."
        ),
        reasoning_detail=(
            "Ứng viên nhắc đến kết quả mong muốn nhưng không nêu giả định hoặc cách đối chiếu."
        ),
        delivery_detail=(
            "Bài tập dừng ở bản minh họa một lần và không cung cấp đầu ra có thể tái tạo."
        ),
        communication_detail=(
            "Tài liệu nêu rõ phạm vi đã làm và phần công nghệ chưa từng sử dụng."
        ),
        preferred_skill_count=0,
    ),
    Scenario(
        number=12,
        status_override_indexes=None,
        status_override=None,
        criterion_points=(24, 10, 8, 7, 6),
        draft_label="needs_review",
        review_reasons=("low-score-without-explicit-critical-unsatisfied",),
        technical_detail=(
            "Phần kỹ thuật chỉ có ví dụ cú pháp cho từng công cụ, chưa kết nối thành "
            "một quy trình và chưa kiểm tra đầu ra."
        ),
        reasoning_detail=(
            "Ứng viên mô tả nhiệm vụ ở mức khái quát, không nêu cách chọn phương pháp "
            "hoặc đánh giá sai lệch."
        ),
        delivery_detail=("Các đoạn thực hành được lưu riêng lẻ và chưa có bản chạy xuyên suốt."),
        communication_detail=(
            "Ghi chú xác định nguồn của từng đoạn thực hành nhưng thiếu hướng dẫn tích hợp."
        ),
        preferred_skill_count=0,
    ),
    Scenario(
        number=13,
        status_override_indexes=None,
        status_override=None,
        criterion_points=(27, 13, 10, 6, 5),
        draft_label="needs_review",
        review_reasons=("lower-threshold-boundary",),
        technical_detail=(
            "Phần kỹ thuật có một luồng xử lý hoàn chỉnh cho dữ liệu mẫu, với kiểm tra "
            "định dạng nhưng chưa xử lý trường hợp biên."
        ),
        reasoning_detail=(
            "Ứng viên nêu mục tiêu và kết quả quan sát được, còn thiếu phép đối chiếu độc lập."
        ),
        delivery_detail=(
            "Bản chạy cục bộ có đầu ra mẫu nhưng chưa ghi nhận khả năng lặp lại trên nguồn khác."
        ),
        communication_detail=(
            "README có các lệnh chính và mô tả đầu ra, chưa nêu quyết định và giới hạn."
        ),
        preferred_skill_count=0,
    ),
    Scenario(
        number=14,
        status_override_indexes=None,
        status_override=None,
        criterion_points=(30, 18, 13, 8, 5),
        draft_label="needs_review",
        review_reasons=("upper-threshold-boundary",),
        technical_detail=(
            "Phần kỹ thuật có luồng xử lý hoàn chỉnh, kiểm tra đầu vào và xử lý hai "
            "trường hợp lỗi thường gặp."
        ),
        reasoning_detail=(
            "Ứng viên giải thích mục tiêu, lựa chọn phương pháp và một giới hạn cần kiểm tra thêm."
        ),
        delivery_detail=("Bản chạy cục bộ có dữ liệu mẫu, đầu ra đối chiếu và hướng dẫn tái tạo."),
        communication_detail=(
            "Tài liệu mô tả cách chạy và cấu trúc đầu ra nhưng phần quyết định kỹ thuật còn ngắn."
        ),
        preferred_skill_count=2,
    ),
    Scenario(
        number=15,
        status_override_indexes=(1, 2),
        status_override="unsatisfied",
        criterion_points=(18, 17, 13, 10, 6),
        draft_label="needs_review",
        review_reasons=("critical-unsatisfied-at-or-above-waitlist-threshold",),
        technical_detail=(
            "Các phần kỹ thuật còn lại có kiểm tra đầu vào, xử lý lỗi cơ bản và "
            "đối chiếu kết quả trên hai bộ mẫu."
        ),
        reasoning_detail=(
            "Ứng viên nêu mục tiêu, giải thích lựa chọn chính và ghi nhận hai giới hạn."
        ),
        delivery_detail=(
            "Sản phẩm có hướng dẫn chạy, đầu ra mẫu và lịch sử thay đổi cho phần đã hoàn thành."
        ),
        communication_detail=(
            "Tài liệu phân biệt rõ phần đã triển khai, phần chưa có kinh nghiệm và việc cần bổ sung."
        ),
        preferred_skill_count=2,
    ),
)

DATA_ANALYST = RoleDefinition(
    code="da",
    scenario_role_index=0,
    job_profile_id="junior-data-analyst-v1",
    rubric_id="junior-data-analyst-rubric-v1",
    profile_summary=(
        "Ứng viên trình bày các bài tập và dự án xử lý dữ liệu có cấu trúc "
        "ở cấp độ học tập hoặc cá nhân."
    ),
    requirement_ids=("da-sql", "da-analysis-language", "da-analytical-project"),
    requirement_skill_names=("SQL", "Python or R", "Data analysis project"),
    positive_evidence_texts=(
        "Sử dụng SQL với join, aggregate và kiểm tra chất lượng dữ liệu trong bài tập thực hành.",
        "Dùng Python hoặc R để làm sạch, biến đổi và phân tích dữ liệu có cấu trúc.",
        "Thực hiện dự án phân tích có câu hỏi nghiệp vụ, chỉ số, đầu ra và giới hạn dữ liệu.",
    ),
    negative_evidence_texts=(
        "Ứng viên xác nhận chưa từng sử dụng SQL.",
        "Ứng viên xác nhận chưa từng sử dụng Python hoặc R cho phân tích dữ liệu.",
        "Ứng viên xác nhận chưa từng thực hiện dự án hoặc thực tập phân tích dữ liệu.",
    ),
    preferred_skills=(
        (
            "Power BI",
            "Tạo dashboard Power BI có bộ lọc, định nghĩa chỉ số và kiểm tra số liệu nguồn.",
        ),
        (
            "Applied statistics",
            "Áp dụng thống kê mô tả, khoảng tin cậy và kiểm tra phân phối trên dữ liệu mẫu.",
        ),
        (
            "Data warehouse",
            "Thiết kế bảng fact, dimension và một luồng nạp dữ liệu theo lịch.",
        ),
        (
            "A/B testing",
            "Xác định giả thuyết, chỉ số chính và cách đọc kết quả cho một thử nghiệm A/B.",
        ),
    ),
    criterion_ids=(
        "mandatory-requirements",
        "technical-analysis",
        "analytical-reasoning",
        "projects-and-impact",
        "communication-and-evidence-quality",
    ),
    criterion_rationale_bases=(
        "Ba nhóm năng lực cốt lõi được đối chiếu riêng với thông tin thực hành và xác nhận phủ định.",
        "Các mô tả kỹ thuật thể hiện phạm vi truy vấn, xử lý và kiểm tra chất lượng dữ liệu.",
        "Cách đặt mục tiêu, lựa chọn phương pháp và ghi nhận giới hạn được xem xét từ phần dự án.",
        "Phạm vi đóng góp, khả năng tái tạo đầu ra và tác động được đối chiếu với phần bàn giao.",
        "Mức rõ ràng của hướng dẫn, giả định và giới hạn được xem xét từ tài liệu đi kèm.",
    ),
    reasoning_prefix="Cách thực hiện phân tích: ",
    delivery_prefix="Phần bàn giao của dự án: ",
    project_title="Phân tích hoạt động tổng hợp",
    project_summary="Làm sạch dữ liệu, tính chỉ số, tạo báo cáo và nêu giới hạn của kết quả.",
    project_requirement_index=2,
)

PYTHON_BACKEND = RoleDefinition(
    code="be",
    scenario_role_index=1,
    job_profile_id="junior-python-backend-developer-v1",
    rubric_id="junior-python-backend-developer-rubric-v1",
    profile_summary=(
        "Ứng viên trình bày các bài tập và dự án dịch vụ phần mềm ở cấp độ học tập hoặc cá nhân."
    ),
    requirement_ids=("be-python", "be-rest-api", "be-relational-data", "be-git"),
    requirement_skill_names=("Python", "REST API", "Relational SQL", "Git"),
    positive_evidence_texts=(
        "Dùng Python với type hints và validation để triển khai logic backend.",
        "Xây REST API có endpoint, request, response và xử lý lỗi bằng framework backend.",
        "Thiết kế dữ liệu quan hệ, viết SQL và quản lý thay đổi schema.",
        "Dùng Git với branch, commit và quy trình review thay đổi.",
    ),
    negative_evidence_texts=(
        "Ứng viên xác nhận chưa từng sử dụng Python cho backend.",
        "Ứng viên xác nhận chưa từng xây REST API.",
        "Ứng viên xác nhận không có kiến thức SQL.",
        "Ứng viên xác nhận chưa từng sử dụng Git.",
    ),
    preferred_skills=(
        (
            "Pytest",
            "Viết unit test và integration test cho luồng thành công, dữ liệu sai và lỗi repository.",
        ),
        (
            "Docker",
            "Đóng gói dịch vụ và cơ sở dữ liệu bằng Docker với cấu hình chạy cục bộ.",
        ),
        (
            "CI/CD",
            "Thiết lập pipeline chạy lint, test và build trước khi hợp nhất thay đổi.",
        ),
        (
            "API authentication",
            "Triển khai xác thực token, phân quyền theo vai trò và quản lý cấu hình nhạy cảm.",
        ),
    ),
    criterion_ids=(
        "mandatory-requirements",
        "backend-implementation",
        "api-and-data-design",
        "projects-and-delivery",
        "communication-and-evidence-quality",
    ),
    criterion_rationale_bases=(
        "Bốn nhóm năng lực cốt lõi được đối chiếu riêng với thông tin thực hành và xác nhận phủ định.",
        "Các mô tả kỹ thuật thể hiện phạm vi triển khai Python, validation, xử lý lỗi và kiểm thử.",
        "Thiết kế request, response, dữ liệu quan hệ và tính nhất quán được xem xét từ phần dự án.",
        "Phạm vi đóng góp, khả năng chạy lại và tài liệu bàn giao được đối chiếu với đầu ra.",
        "Mức rõ ràng của README, quyết định kỹ thuật và phần việc cá nhân được xem xét từ tài liệu.",
    ),
    reasoning_prefix="Cách lựa chọn thiết kế: ",
    delivery_prefix="Phần bàn giao của dịch vụ: ",
    project_title="Dịch vụ quản lý công việc",
    project_summary="Xây dịch vụ có validation, lưu dữ liệu và hướng dẫn chạy cục bộ.",
    project_requirement_index=1,
)


def requirement_statuses(role: RoleDefinition, scenario: Scenario) -> tuple[str, ...]:
    statuses = ["satisfied"] * len(role.requirement_ids)
    if scenario.status_override_indexes is not None and scenario.status_override is not None:
        override_index = scenario.status_override_indexes[role.scenario_role_index]
        statuses[override_index] = scenario.status_override
    return tuple(statuses)


def profile_prefix(role: RoleDefinition, scenario: Scenario) -> str:
    return f"s4-{role.code}-{scenario.number:03d}"


def evidence_record(
    evidence_id: str,
    section: str,
    text: str,
    source_type: str = "manual",
) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "evidence_id": evidence_id,
        "source_type": source_type,
        "section": section,
        "text": text,
        "location": {"source_record_id": f"record-{evidence_id}"},
        "is_verified": False,
    }


def build_cv_profile(role: RoleDefinition, scenario: Scenario) -> CVProfile:
    prefix = profile_prefix(role, scenario)
    statuses = requirement_statuses(role, scenario)
    evidence: list[dict[str, Any]] = []
    skills: list[dict[str, Any]] = []
    positive_ids: list[str] = []

    for index, (skill_name, status) in enumerate(
        zip(role.requirement_skill_names, statuses, strict=True)
    ):
        if status in {"satisfied", "conflicting"}:
            evidence_id = f"ev-{prefix}-req-{index + 1}"
            section = "projects" if index == role.project_requirement_index else "skills"
            evidence.append(
                evidence_record(evidence_id, section, role.positive_evidence_texts[index])
            )
            positive_ids.append(evidence_id)
            if index != role.project_requirement_index:
                skills.append({"name": skill_name, "evidence_ids": [evidence_id]})
        if status in {"unsatisfied", "conflicting"}:
            evidence_id = f"ev-{prefix}-gap-{index + 1}"
            evidence.append(
                evidence_record(
                    evidence_id,
                    "other",
                    role.negative_evidence_texts[index],
                    "candidate",
                )
            )

    preferred_ids: list[str] = []
    for index, (skill_name, evidence_text) in enumerate(
        role.preferred_skills[: scenario.preferred_skill_count]
    ):
        evidence_id = f"ev-{prefix}-preferred-{index + 1}"
        evidence.append(evidence_record(evidence_id, "skills", evidence_text))
        preferred_ids.append(evidence_id)
        skills.append({"name": skill_name, "evidence_ids": [evidence_id]})

    technical_id = f"ev-{prefix}-technical"
    reasoning_id = f"ev-{prefix}-reasoning"
    delivery_id = f"ev-{prefix}-delivery"
    communication_id = f"ev-{prefix}-communication"
    education_id = f"ev-{prefix}-education"
    evidence.extend(
        (
            evidence_record(
                technical_id,
                "projects",
                scenario.technical_detail,
            ),
            evidence_record(
                reasoning_id,
                "projects",
                f"{role.reasoning_prefix}{scenario.reasoning_detail}",
            ),
            evidence_record(
                delivery_id,
                "projects",
                f"{role.delivery_prefix}{scenario.delivery_detail}",
            ),
            evidence_record(
                communication_id,
                "other",
                scenario.communication_detail,
            ),
            evidence_record(
                education_id,
                "education",
                "Chương trình học có nội dung kỹ thuật liên quan ở mức nền tảng.",
            ),
        )
    )

    project_requirement_status = statuses[role.project_requirement_index]
    project_evidence_ids = [
        *positive_ids,
        *preferred_ids,
        technical_id,
        reasoning_id,
        delivery_id,
    ]
    if project_requirement_status == "conflicting":
        project_evidence_ids.append(f"ev-{prefix}-gap-{role.project_requirement_index + 1}")
    projects: list[dict[str, Any]] = []
    if project_requirement_status in {"satisfied", "conflicting"}:
        projects.append(
            {
                "project_id": f"project-{prefix}",
                "title": role.project_title,
                "summary": f"{role.project_summary} {scenario.delivery_detail}",
                "technologies": [item["name"] for item in skills],
                "evidence_ids": list(dict.fromkeys(project_evidence_ids)),
            }
        )

    payload: dict[str, Any] = {
        "schema_version": "1.0.0",
        "cv_profile_id": f"cv-{prefix}",
        "candidate_reference": f"candidate-synthetic-{prefix}",
        "summary": role.profile_summary,
        "skills": skills,
        "work_experiences": [],
        "education": [
            {
                "education_id": f"education-{prefix}",
                "degree": "Technical program",
                "field_of_study": "Applied Computing",
                "institution_reference": f"institution-synthetic-{prefix}",
                "evidence_ids": [education_id],
            }
        ],
        "projects": projects,
        "certifications": [],
        "evidence": evidence,
        "quality_warnings": [],
    }
    return CVProfile.model_validate(payload)


def assessment_evidence_ids(
    role: RoleDefinition,
    scenario: Scenario,
    status: str,
    requirement_index: int,
) -> list[str]:
    prefix = profile_prefix(role, scenario)
    if status == "missing":
        return []
    if status == "satisfied":
        return [f"ev-{prefix}-req-{requirement_index + 1}"]
    if status == "unsatisfied":
        return [f"ev-{prefix}-gap-{requirement_index + 1}"]
    return [
        f"ev-{prefix}-req-{requirement_index + 1}",
        f"ev-{prefix}-gap-{requirement_index + 1}",
    ]


def status_rationale(requirement_id: str, status: str) -> str:
    rationales = {
        "satisfied": f"{requirement_id} có thông tin thực hành trực tiếp trong CV.",
        "unsatisfied": f"{requirement_id} có xác nhận rõ rằng ứng viên chưa đáp ứng.",
        "missing": f"{requirement_id} không được đề cập và không có thông tin phủ định.",
        "conflicting": f"{requirement_id} có thông tin thực hành và thông tin phủ định mâu thuẫn.",
    }
    return rationales[status]


def criterion_evidence_ids(
    role: RoleDefinition,
    scenario: Scenario,
    profile: CVProfile,
    requirement_assessments: list[dict[str, Any]],
) -> tuple[tuple[str, ...], ...]:
    prefix = profile_prefix(role, scenario)
    mandatory_ids = tuple(
        evidence_id
        for assessment in requirement_assessments
        for evidence_id in assessment["evidence_ids"]
    )
    technical_ids = tuple(
        item.evidence_id
        for item in profile.evidence
        if any(token in item.evidence_id for token in ("-req-", "-preferred-", "-technical"))
    )
    reasoning_ids = tuple(
        evidence_id
        for evidence_id in (
            f"ev-{prefix}-reasoning",
            f"ev-{prefix}-req-{role.project_requirement_index + 1}",
        )
        if any(item.evidence_id == evidence_id for item in profile.evidence)
    )
    project_ids = tuple(
        dict.fromkeys(
            evidence_id for project in profile.projects for evidence_id in project.evidence_ids
        )
    )
    if not project_ids:
        project_ids = (f"ev-{prefix}-delivery",)
    communication_ids = (f"ev-{prefix}-communication",)
    return (
        mandatory_ids,
        technical_ids,
        reasoning_ids,
        project_ids,
        communication_ids,
    )


def evidence_strength_phrase(awarded_points: int, maximum_points: int) -> str:
    if awarded_points * 5 >= maximum_points * 4:
        return "Thông tin có phạm vi rộng, nêu được bước kiểm tra và đầu ra có thể đối chiếu."
    if awarded_points * 5 >= maximum_points * 3:
        return "Thông tin mô tả được thao tác liên quan nhưng phạm vi kiểm chứng còn giới hạn."
    return "Thông tin hiện có chủ yếu ở mức tác vụ cơ bản hoặc chưa đủ chi tiết để kiểm chứng."


def criterion_rationale(
    role: RoleDefinition,
    criterion_index: int,
    awarded_points: int,
    maximum_points: int,
    statuses: tuple[str, ...],
) -> str:
    base = role.criterion_rationale_bases[criterion_index]
    if criterion_index == 0:
        counts = {
            status: statuses.count(status)
            for status in ("satisfied", "unsatisfied", "missing", "conflicting")
        }
        return (
            f"{base} Kết quả đối chiếu gồm {counts['satisfied']} mục có thông tin thực hành, "
            f"{counts['unsatisfied']} mục có xác nhận phủ định, {counts['missing']} mục chưa "
            f"có thông tin và {counts['conflicting']} mục có mô tả mâu thuẫn."
        )
    return f"{base} {evidence_strength_phrase(awarded_points, maximum_points)}"


def review_note(reason: str) -> str:
    notes = {
        "missing-critical-evidence": (
            "Một năng lực cốt lõi chưa có thông tin trực tiếp; người review cần xác nhận "
            "trước khi dùng kết quả."
        ),
        "conflicting-critical-evidence": (
            "Một năng lực cốt lõi có cả mô tả thực hành và xác nhận phủ định; "
            "người review cần làm rõ nguồn nào chính xác."
        ),
        "low-score-without-explicit-critical-unsatisfied": (
            "Kết quả tổng hợp thấp nhưng không có xác nhận phủ định cho năng lực cốt lõi."
        ),
        "lower-threshold-boundary": (
            "Kết quả tổng hợp nằm gần mốc chuyển ở vùng thấp và cần người review kiểm tra."
        ),
        "upper-threshold-boundary": (
            "Kết quả tổng hợp nằm gần mốc chuyển ở vùng cao và cần người review kiểm tra."
        ),
        "critical-unsatisfied-at-or-above-waitlist-threshold": (
            "Có xác nhận phủ định cho một năng lực cốt lõi trong khi các phần còn lại "
            "có thông tin thực hành."
        ),
    }
    return notes[reason]


def overall_rationale(role: RoleDefinition, statuses: tuple[str, ...]) -> str:
    satisfied_count = statuses.count("satisfied")
    unresolved_count = statuses.count("missing") + statuses.count("conflicting")
    unsatisfied_count = statuses.count("unsatisfied")
    return (
        f"Hồ sơ được đối chiếu theo {len(statuses)} năng lực cốt lõi của vị trí; "
        f"{satisfied_count} mục có thông tin thực hành, {unresolved_count} mục cần làm rõ "
        f"và {unsatisfied_count} mục có xác nhận phủ định. "
        f"{role.criterion_rationale_bases[1]}"
    )


def build_annotation(
    role: RoleDefinition,
    scenario: Scenario,
    profile: CVProfile,
) -> dict[str, Any]:
    statuses = requirement_statuses(role, scenario)
    requirement_assessments = [
        {
            "requirement_id": requirement_id,
            "evidence_status": status,
            "evidence_ids": assessment_evidence_ids(role, scenario, status, index),
            "rationale": status_rationale(requirement_id, status),
        }
        for index, (requirement_id, status) in enumerate(
            zip(role.requirement_ids, statuses, strict=True)
        )
    ]
    maximums = (30, 25, 20, 15, 10)
    evidence_ids_by_criterion = criterion_evidence_ids(
        role,
        scenario,
        profile,
        requirement_assessments,
    )
    criterion_assessments = [
        {
            "criterion_id": criterion_id,
            "awarded_points": awarded_points,
            "maximum_points": maximum_points,
            "evidence_ids": list(evidence_ids),
            "rationale": criterion_rationale(
                role,
                criterion_index,
                awarded_points,
                maximum_points,
                statuses,
            ),
        }
        for criterion_index, (
            criterion_id,
            awarded_points,
            maximum_points,
            evidence_ids,
        ) in enumerate(
            zip(
                role.criterion_ids,
                scenario.criterion_points,
                maximums,
                evidence_ids_by_criterion,
                strict=True,
            )
        )
    ]
    total_score = sum(scenario.criterion_points)
    return {
        "annotation_id": f"annotation-{profile_prefix(role, scenario)}",
        "cv_profile_id": profile.cv_profile_id,
        "source_dataset_file": "data/to_review/stage4_cv_profiles_v1.jsonl",
        "job_profile_id": role.job_profile_id,
        "rubric_id": role.rubric_id,
        "critical_requirement_assessments": requirement_assessments,
        "criterion_assessments": criterion_assessments,
        "total_score": total_score,
        "draft_label": scenario.draft_label,
        "review_reasons": list(scenario.review_reasons),
        "ambiguity_notes": [review_note(reason) for reason in scenario.review_reasons],
        "overall_rationale": overall_rationale(role, statuses),
        "review": {
            "status": "pending",
            "reviewer_reference": None,
            "final_label": None,
            "criterion_score_overrides": [],
            "notes": None,
            "reviewed_at": None,
        },
    }


def build_dataset() -> tuple[tuple[CVProfile, ...], tuple[dict[str, Any], ...]]:
    profiles: list[CVProfile] = []
    annotations: list[dict[str, Any]] = []
    for role in (DATA_ANALYST, PYTHON_BACKEND):
        for scenario in SCENARIOS:
            profile = build_cv_profile(role, scenario)
            profiles.append(profile)
            annotations.append(build_annotation(role, scenario, profile))
    return tuple(profiles), tuple(annotations)


def write_dataset(output_directory: Path = OUTPUT_DIRECTORY) -> tuple[Path, Path]:
    profiles, annotations = build_dataset()
    output_directory.mkdir(parents=True, exist_ok=True)
    cv_output_file = output_directory / CV_OUTPUT_FILE.name
    annotation_output_file = output_directory / ANNOTATION_OUTPUT_FILE.name
    cv_lines = [
        json.dumps(profile.model_dump(mode="json"), ensure_ascii=False, sort_keys=True)
        for profile in profiles
    ]
    cv_output_file.write_text("\n".join(cv_lines) + "\n", encoding="utf-8")
    annotation_artifact = {
        "schema_version": "1.0.0",
        "dataset_id": "stage4-review-dataset-v1",
        "dataset_version": "1.0.0",
        "cv_schema_version": "1.0.0",
        "job_profile_artifact_version": "1.0.0",
        "rubric_version": "1.0.0",
        "configuration_version": "1.1.0",
        "models_configuration_version": "1.1.0",
        "l1_rules_configuration_version": "1.0.0",
        "annotation_status": "draft",
        "records": annotations,
    }
    annotation_output_file.write_text(
        json.dumps(annotation_artifact, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return cv_output_file, annotation_output_file


def main() -> None:
    cv_path, annotation_path = write_dataset()
    print(cv_path)
    print(annotation_path)


if __name__ == "__main__":
    main()
