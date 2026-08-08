from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Sequence

from pydantic import BaseModel

from backend.app.contracts import (
    CVProfile,
    ClassificationDecision,
    EducationRecord,
    Evidence,
    EvidenceLocation,
    EvidenceSection,
    EvidenceSourceType,
    EvidenceStatus,
    JobProfile,
    Project,
    QualityWarning,
    ScoringRubric,
    Skill,
    WarningSeverity,
)
from backend.app.infrastructure.config import RepositoryConfigurationLoader
from evaluation.datasets.stage7 import (
    Stage7FileDigest,
    Stage7PriorDatasetReference,
    Stage7TestManifest,
    validate_stage7_test_set,
)
from evaluation.datasets.synthetic_expansion import (
    CriterionDraftAssessment,
    DatasetRole,
    DatasetTier,
    JobVariant,
    PendingDatasetReview,
    RequirementDraftAssessment,
    SyntheticPairAnnotation,
    SyntheticScenario,
    file_sha256,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIRECTORY = REPOSITORY_ROOT / "data" / "to_review" / "stage7_test_v1"
RUNTIME_DIRECTORY = REPOSITORY_ROOT / "configs" / "runtime" / "five_role_v1"
GENERATED_AT = "2026-08-07T16:00:00+07:00"
SOURCE_MANIFEST_SHA256 = "1f420a79f94f0499198b69a3f70bec413f6483ce0552d44013e7c219949c0b24"


@dataclass(frozen=True)
class Stage7ScenarioDefinition:
    scenario: SyntheticScenario
    status_mode: str
    criterion_points: tuple[int, int, int, int, int]
    preferred_count: int
    summary: str
    technical_detail: str
    reasoning_detail: str
    delivery_detail: str
    communication_detail: str


@dataclass(frozen=True)
class Stage7RoleContent:
    role: DatasetRole
    code: str
    field_of_study: str
    requirement_skills: tuple[str, ...]
    positive_evidence: tuple[str, ...]
    negative_evidence: tuple[str, ...]
    project_contexts: tuple[str, ...]


SCENARIOS: tuple[Stage7ScenarioDefinition, ...] = (
    Stage7ScenarioDefinition(
        SyntheticScenario.STRONG,
        "satisfied",
        (30, 24, 18, 14, 9),
        2,
        "Hồ sơ trình bày một sản phẩm hoàn chỉnh, có số liệu đối chiếu và tài liệu tái tạo.",
        "Luồng chính và các trường hợp lỗi được kiểm tra trên nhiều bộ dữ liệu hoặc tình huống đầu vào.",
        "Hai phương án được so sánh bằng tiêu chí đo được trước khi chọn cách triển khai.",
        "Kết quả có chỉ số trước và sau, bộ kiểm tra hồi quy và hướng dẫn chạy độc lập.",
        "Tài liệu nêu rõ phạm vi cá nhân, giả định, giới hạn và quyết định kỹ thuật.",
    ),
    Stage7ScenarioDefinition(
        SyntheticScenario.SOLID,
        "satisfied",
        (30, 22, 17, 12, 8),
        2,
        "Hồ sơ có dự án junior hoàn chỉnh, thông tin nhất quán và đầu ra có thể kiểm tra.",
        "Luồng nghiệp vụ chính và hai trường hợp lỗi phổ biến được triển khai và kiểm thử.",
        "Mục tiêu, giả định và cách đối chiếu kết quả được trình bày rõ.",
        "Sản phẩm có dữ liệu mẫu, lệnh chạy và kết quả kiểm tra nhất quán.",
        "README mô tả phần việc cá nhân và các hạn chế chính.",
    ),
    Stage7ScenarioDefinition(
        SyntheticScenario.MODERATE,
        "satisfied",
        (30, 17, 14, 9, 8),
        1,
        "Hồ sơ đáp ứng phần cốt lõi nhưng dự án mới giới hạn ở một luồng nghiệp vụ.",
        "Một luồng chính được hoàn thành trên tập dữ liệu hoặc chức năng có phạm vi vừa phải.",
        "Phương pháp được giải thích nhưng phần so sánh phương án còn ngắn.",
        "Đầu ra chạy lại được cục bộ và có một số kiểm tra cơ bản.",
        "Tài liệu đủ để chạy thử nhưng chưa mô tả đầy đủ rủi ro vận hành.",
    ),
    Stage7ScenarioDefinition(
        SyntheticScenario.MISSING_CRITICAL,
        "missing",
        (20, 17, 13, 8, 6),
        1,
        "Hồ sơ mô tả một số phần việc liên quan nhưng không đề cập đầy đủ toàn bộ năng lực cốt lõi.",
        "Các phần được nêu có thao tác kỹ thuật và kiểm tra đầu vào cơ bản.",
        "Ứng viên giải thích mục tiêu và một giới hạn của giải pháp.",
        "Có bản chạy thử cùng dữ liệu hoặc tình huống minh họa.",
        "Phạm vi đã làm được ghi rõ, không suy diễn cho phần chưa được mô tả.",
    ),
    Stage7ScenarioDefinition(
        SyntheticScenario.CONFLICTING_CRITICAL,
        "conflicting",
        (22, 17, 13, 9, 7),
        2,
        "Hồ sơ kết hợp mô tả dự án và bản tự đánh giá có một điểm chưa nhất quán.",
        "Một luồng kỹ thuật hoàn chỉnh được mô tả cùng cách kiểm tra sai lệch.",
        "Mục tiêu và kết quả được nêu nhưng một phát biểu năng lực cần xác minh lại.",
        "Có đầu ra mẫu và danh sách vấn đề còn mở.",
        "Tài liệu giữ nguyên cả hai phát biểu để người đánh giá xử lý mâu thuẫn.",
    ),
    Stage7ScenarioDefinition(
        SyntheticScenario.EXPLICIT_FAILURE,
        "unsatisfied",
        (10, 12, 9, 5, 5),
        0,
        "Ứng viên chuyển hướng từ lĩnh vực gần và xác nhận chưa thực hành một năng lực bắt buộc.",
        "Phần việc hiện có chỉ hỗ trợ gián tiếp cho vai trò mục tiêu.",
        "Kết quả mong muốn được nêu nhưng chưa có phương pháp đáp ứng yêu cầu chính.",
        "Bài tập dừng ở bản minh họa một lần và chưa có kiểm tra đầy đủ.",
        "Hồ sơ diễn đạt rõ năng lực chưa từng sử dụng để tránh suy diễn sai.",
    ),
    Stage7ScenarioDefinition(
        SyntheticScenario.LOWER_BOUNDARY,
        "satisfied",
        (28, 14, 11, 8, 9),
        1,
        "Hồ sơ vừa đủ yêu cầu cốt lõi nhưng mức độ sâu và phạm vi dự án còn hạn chế.",
        "Luồng cơ bản hoạt động nhưng mới kiểm tra một số trường hợp phổ biến.",
        "Mục tiêu và kết quả được nêu, phần đối chiếu độc lập còn thiếu.",
        "Đầu ra chạy lại được trên một bộ mẫu cố định.",
        "README rõ lệnh chính nhưng phần quyết định kỹ thuật còn ngắn.",
    ),
    Stage7ScenarioDefinition(
        SyntheticScenario.UPPER_BOUNDARY,
        "satisfied",
        (30, 20, 16, 12, 7),
        2,
        "Hồ sơ khá tốt và nằm gần ngưỡng Pass nên cần kiểm tra tính ổn định của quyết định.",
        "Luồng chính và các lỗi thường gặp được xử lý bằng kiểm tra có thể chạy lại.",
        "Lựa chọn kỹ thuật có lý do và ghi nhận một giới hạn đáng chú ý.",
        "Có dữ liệu mẫu, kết quả đối chiếu và hướng dẫn tái tạo.",
        "Tài liệu rõ cách chạy nhưng phần giải thích một số quyết định còn cô đọng.",
    ),
    Stage7ScenarioDefinition(
        SyntheticScenario.TRANSFERABLE,
        "satisfied",
        (30, 16, 14, 10, 9),
        1,
        "Ứng viên chuyển từ lĩnh vực gần và chứng minh được năng lực tương đương qua dự án mới.",
        "Kiến thức nền từ lĩnh vực gần được áp dụng vào một sản phẩm đúng vai trò mục tiêu.",
        "Hồ sơ phân biệt rõ phần kinh nghiệm chuyển đổi và phần mới học.",
        "Prototype chạy được, có kiểm tra và đầu ra đo được nhưng chưa qua môi trường thực tập.",
        "Tài liệu nêu rõ phạm vi kinh nghiệm trực tiếp và kinh nghiệm tương đương.",
    ),
    Stage7ScenarioDefinition(
        SyntheticScenario.HARD_NEGATIVE,
        "hard_negative",
        (14, 9, 6, 3, 4),
        2,
        "Hồ sơ chủ yếu liệt kê khóa học và công cụ nhưng không mô tả nhiệm vụ hay sản phẩm đã làm.",
        "Danh sách kỹ năng không kèm ngữ cảnh sử dụng hoặc đầu ra kiểm tra được.",
        "Không có phương pháp, giả định hoặc cách xác minh kết quả.",
        "Không có sản phẩm có thể chạy lại hay số liệu tác động.",
        "Các mục chỉ ghi tên công cụ và chứng nhận hoàn thành khóa học.",
    ),
)


ROLE_CONTENT: tuple[Stage7RoleContent, ...] = (
    Stage7RoleContent(
        DatasetRole.DATA_ANALYST,
        "da",
        "Phân tích dữ liệu và hệ thống thông tin",
        ("SQL", "Python hoặc R", "Power BI hoặc Tableau", "Phân tích nghiệp vụ end-to-end"),
        (
            "Trong {context}, ứng viên tự viết truy vấn nhiều bảng, dùng CTE và hàm cửa sổ để đối soát số liệu theo từng kỳ.",
            "Trong {context}, ứng viên dùng pandas để chuẩn hóa kiểu dữ liệu, xử lý giá trị thiếu và đóng gói notebook có thể chạy lại.",
            "Trong {context}, ứng viên dựng dashboard có data model, bộ lọc chi tiết và tài liệu định nghĩa từng KPI.",
            "Trong {context}, ứng viên chuyển câu hỏi kinh doanh thành chỉ số, phân tích nguyên nhân và nêu khuyến nghị kèm giới hạn.",
        ),
        (
            "Ứng viên xác nhận chưa từng viết truy vấn SQL có JOIN hoặc phép tổng hợp.",
            "Ứng viên xác nhận chưa từng dùng Python hay R để xử lý dữ liệu.",
            "Ứng viên xác nhận chưa từng tạo dashboard hoặc báo cáo BI.",
            "Ứng viên xác nhận chưa từng thực hiện một bài phân tích dữ liệu có đầu ra hoàn chỉnh.",
        ),
        (
            "phân tích tỷ lệ khách hàng quay lại của nền tảng bán lẻ",
            "theo dõi tồn kho và thời gian giao hàng tại ba kho mô phỏng",
            "đánh giá phễu đăng ký của ứng dụng học trực tuyến",
            "tìm nguyên nhân gia tăng đơn hoàn trả theo nhóm sản phẩm",
            "đối chiếu chất lượng phục vụ của trung tâm hỗ trợ",
            "kiểm tra chênh lệch doanh thu giữa hệ thống bán hàng và kế toán",
            "xây báo cáo hiệu suất nhà bán hàng trên sàn thử nghiệm",
            "đo mức kích hoạt tính năng mới theo cohort người dùng",
            "chuyển kinh nghiệm nghiên cứu định lượng sang phân tích sản phẩm",
            "tổng hợp danh sách công cụ từ các khóa học phân tích dữ liệu",
        ),
    ),
    Stage7RoleContent(
        DatasetRole.PYTHON_BACKEND,
        "be",
        "Kỹ thuật phần mềm và hệ thống thông tin",
        ("Python", "REST API", "PostgreSQL và SQL", "pytest", "Git và Docker"),
        (
            "Trong {context}, ứng viên tổ chức Python theo lớp dịch vụ, dùng type hint và xử lý ngoại lệ theo hợp đồng lỗi.",
            "Trong {context}, ứng viên xây REST API bằng FastAPI với validation, phân trang và mã trạng thái nhất quán.",
            "Trong {context}, ứng viên thiết kế bảng PostgreSQL, migration và truy vấn transaction cho luồng cập nhật dữ liệu.",
            "Trong {context}, ứng viên viết pytest cho service và API, gồm luồng đúng, dữ liệu sai và dependency giả lập.",
            "Trong {context}, ứng viên quản lý nhánh Git, đóng gói Docker và ghi lệnh khởi động môi trường phát triển.",
        ),
        (
            "Ứng viên xác nhận chưa từng viết chương trình bằng Python.",
            "Ứng viên xác nhận chưa từng xây hoặc tích hợp REST API.",
            "Ứng viên xác nhận chưa từng làm việc với cơ sở dữ liệu quan hệ hay SQL.",
            "Ứng viên xác nhận chưa từng viết automated test cho mã backend.",
            "Ứng viên xác nhận chưa từng dùng Git hoặc đóng gói ứng dụng bằng Docker.",
        ),
        (
            "xây dịch vụ xử lý đơn hàng có idempotency key",
            "phát triển API tồn kho với kiểm soát transaction",
            "tạo backend đặt lịch có phân quyền người dùng",
            "xử lý webhook thanh toán và chống gửi trùng",
            "xây API thư viện số với tìm kiếm và phân trang",
            "chuyển từ lập trình nhúng sang dịch vụ web Python",
            "triển khai service quản lý công việc cho nhóm sinh viên",
            "xây API theo dõi chi tiêu với refresh token",
            "chuyển kinh nghiệm Java sang một microservice FastAPI",
            "liệt kê framework và công cụ backend từ khóa học trực tuyến",
        ),
    ),
    Stage7RoleContent(
        DatasetRole.FRONTEND,
        "fe",
        "Phát triển web và kỹ thuật phần mềm",
        (
            "HTML CSS JavaScript",
            "JavaScript hoặc TypeScript",
            "React",
            "Tích hợp API",
            "Git và kiểm thử giao diện",
        ),
        (
            "Trong {context}, ứng viên xây giao diện semantic HTML, CSS responsive và xử lý tương tác bằng JavaScript.",
            "Trong {context}, ứng viên dùng TypeScript strict, mô hình hóa dữ liệu và thu hẹp kiểu cho dữ liệu bên ngoài.",
            "Trong {context}, ứng viên tách React component, quản lý state và xử lý loading, empty cùng error state.",
            "Trong {context}, ứng viên tích hợp API có xác thực, hủy request cũ và hiển thị lỗi theo từng tình huống.",
            "Trong {context}, ứng viên dùng Git theo pull request và viết Testing Library cho hành vi người dùng chính.",
        ),
        (
            "Ứng viên xác nhận chưa nắm HTML, CSS và JavaScript nền tảng.",
            "Ứng viên xác nhận chưa từng viết JavaScript hoặc TypeScript trong dự án.",
            "Ứng viên xác nhận chưa từng xây giao diện bằng React.",
            "Ứng viên xác nhận chưa từng kết nối giao diện với API.",
            "Ứng viên xác nhận chưa từng dùng Git hoặc viết kiểm thử giao diện.",
        ),
        (
            "xây trang quản lý khóa học hỗ trợ bàn phím",
            "phát triển giỏ hàng responsive có lưu trạng thái",
            "tạo dashboard vận hành với biểu đồ và bộ lọc",
            "xây cổng đăng ký sự kiện có validation nhiều bước",
            "phát triển giao diện quản trị phân quyền theo vai trò",
            "chuyển từ thiết kế UI sang lập trình frontend",
            "xây trang tra cứu thư viện trên thiết bị di động",
            "tạo ứng dụng theo dõi thói quen có đồng bộ API",
            "chuyển kinh nghiệm Vue sang dự án React TypeScript",
            "liệt kê thư viện frontend từ các bài thực hành ngắn",
        ),
    ),
    Stage7RoleContent(
        DatasetRole.QA_ENGINEER,
        "qa",
        "Đảm bảo chất lượng phần mềm",
        (
            "Nền tảng kiểm thử",
            "Thiết kế test case",
            "Kiểm thử API",
            "SQL kiểm tra dữ liệu",
            "Tự động hóa kiểm thử",
        ),
        (
            "Trong {context}, ứng viên phân biệt test level, test type và áp dụng quy trình lỗi từ phát hiện đến xác nhận sửa.",
            "Trong {context}, ứng viên thiết kế test case bằng phân vùng tương đương, giá trị biên và bảng quyết định.",
            "Trong {context}, ứng viên dùng Postman kiểm tra status, schema, authentication và chuỗi request có biến môi trường.",
            "Trong {context}, ứng viên viết SQL đối chiếu dữ liệu trước và sau thao tác, gồm bản ghi thiếu hoặc trùng.",
            "Trong {context}, ứng viên tự động hóa luồng regression chính, có assertion ổn định và báo cáo kết quả.",
        ),
        (
            "Ứng viên xác nhận chưa hiểu STLC, test level hoặc các kỹ thuật thiết kế kiểm thử cơ bản.",
            "Ứng viên xác nhận chưa từng viết test case từ yêu cầu nghiệp vụ.",
            "Ứng viên xác nhận chưa từng kiểm tra API bằng công cụ hoặc mã tự động.",
            "Ứng viên xác nhận chưa từng dùng SQL để kiểm tra dữ liệu.",
            "Ứng viên xác nhận chưa từng viết bất kỳ kiểm thử tự động nào.",
        ),
        (
            "kiểm thử hệ thống đặt lịch có giới hạn khung giờ",
            "kiểm thử quy trình checkout với nhiều phương thức thanh toán",
            "đánh giá API quản lý tài khoản và phân quyền",
            "kiểm thử dữ liệu đồng bộ giữa đơn hàng và kho",
            "xây regression cho cổng đăng ký khóa học",
            "chuyển từ hỗ trợ khách hàng sang kiểm thử phần mềm",
            "kiểm thử ứng dụng quản lý công việc của nhóm sinh viên",
            "đánh giá tính ổn định của luồng đặt vé thử nghiệm",
            "chuyển kinh nghiệm phân tích nghiệp vụ sang QA",
            "liệt kê công cụ kiểm thử từ các khóa học nhập môn",
        ),
    ),
    Stage7RoleContent(
        DatasetRole.DATA_ENGINEER,
        "de",
        "Kỹ thuật dữ liệu và hệ thống thông tin",
        ("Python", "SQL", "ETL hoặc ELT", "Mô hình dữ liệu và chất lượng", "Git Linux Docker"),
        (
            "Trong {context}, ứng viên viết Python theo module để đọc nhiều nguồn, chuẩn hóa bản ghi và ghi log lỗi theo batch.",
            "Trong {context}, ứng viên dùng SQL với CTE, hàm cửa sổ và execution plan để biến đổi dữ liệu dung lượng vừa.",
            "Trong {context}, ứng viên xây pipeline incremental có checkpoint, retry và cơ chế chạy lại không tạo dữ liệu trùng.",
            "Trong {context}, ứng viên thiết kế grain, khóa fact-dimension và kiểm tra null, unique cùng referential integrity.",
            "Trong {context}, ứng viên quản lý mã bằng Git, chạy tác vụ trên Linux và đóng gói môi trường bằng Docker.",
        ),
        (
            "Ứng viên xác nhận chưa từng dùng Python cho tác vụ xử lý dữ liệu.",
            "Ứng viên xác nhận chưa từng viết truy vấn SQL có JOIN hoặc tổng hợp.",
            "Ứng viên xác nhận chưa từng xây pipeline ETL hay ELT.",
            "Ứng viên xác nhận chưa từng thiết kế mô hình dữ liệu hoặc kiểm tra chất lượng dữ liệu.",
            "Ứng viên xác nhận chưa từng dùng Git, Linux hoặc Docker trong dự án dữ liệu.",
        ),
        (
            "xây pipeline giao dịch theo lô với checkpoint",
            "đồng bộ dữ liệu sản phẩm từ API vào kho phân tích",
            "tạo mart doanh thu theo mô hình sao",
            "xử lý file sự kiện đến muộn và bản ghi trùng",
            "xây luồng dữ liệu chất lượng không khí theo ngày",
            "chuyển từ backend sang kỹ thuật dữ liệu",
            "tạo pipeline log ứng dụng cho dashboard vận hành",
            "xây luồng incremental cho dữ liệu học tập",
            "chuyển kinh nghiệm SQL phân tích sang data engineering",
            "liệt kê nền tảng dữ liệu từ các khóa học trực tuyến",
        ),
    ),
)


PRIOR_DATASET_PATHS: tuple[tuple[str, str], ...] = (
    ("stage4-reviewed-v1", "data/reviewed/stage4_cv_profiles_v1.jsonl"),
    ("synthetic-expansion-v1", "data/synthetic_expansion/v1/cv_profiles.jsonl"),
    ("synthetic-expansion-v2-draft", "data/synthetic_expansion/v2/cv_profiles.jsonl"),
    ("synthetic-expansion-v2-reviewed", "data/synthetic_expansion/reviewed/v2/cv_profiles.jsonl"),
    (
        "synthetic-expansion-v2-2-reviewed",
        "data/synthetic_expansion/reviewed/v2_2/cv_profiles.jsonl",
    ),
    (
        "synthetic-expansion-v2-3-reviewed",
        "data/synthetic_expansion/reviewed/v2_3/cv_profiles.jsonl",
    ),
    (
        "synthetic-expansion-v2-3-1-reviewed",
        "data/synthetic_expansion/reviewed/v2_3_1/cv_profiles.jsonl",
    ),
)

MISSING_CRITICAL_INDEX: dict[DatasetRole, int] = {
    DatasetRole.DATA_ANALYST: 0,
    DatasetRole.PYTHON_BACKEND: 4,
    DatasetRole.FRONTEND: 0,
    DatasetRole.QA_ENGINEER: 4,
    DatasetRole.DATA_ENGINEER: 0,
}

EXPLICIT_FAILURE_INDEX: dict[DatasetRole, int] = {
    DatasetRole.DATA_ANALYST: 0,
    DatasetRole.PYTHON_BACKEND: 4,
    DatasetRole.FRONTEND: 4,
    DatasetRole.QA_ENGINEER: 4,
    DatasetRole.DATA_ENGINEER: 0,
}


def _status_for_scenario(
    role: DatasetRole,
    scenario: Stage7ScenarioDefinition,
    index: int,
) -> EvidenceStatus:
    if scenario.status_mode == "missing" and index == MISSING_CRITICAL_INDEX[role]:
        return EvidenceStatus.MISSING
    if scenario.status_mode == "conflicting" and index == 1:
        return EvidenceStatus.CONFLICTING
    if scenario.status_mode == "unsatisfied" and index == EXPLICIT_FAILURE_INDEX[role]:
        return EvidenceStatus.UNSATISFIED
    if scenario.status_mode == "hard_negative":
        return EvidenceStatus.MISSING
    return EvidenceStatus.SATISFIED


def _review_reasons(
    statuses: tuple[EvidenceStatus, ...],
    total_score: int,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if EvidenceStatus.MISSING in statuses:
        reasons.append("missing-critical-evidence")
    if EvidenceStatus.CONFLICTING in statuses:
        reasons.append("conflicting-critical-evidence")
    if 68 <= total_score <= 72:
        reasons.append("lower-threshold-boundary")
    if 83 <= total_score <= 87:
        reasons.append("upper-threshold-boundary")
    if EvidenceStatus.UNSATISFIED in statuses and total_score >= 70:
        reasons.append("critical-unsatisfied-at-or-above-waitlist-threshold")
    if total_score < 70 and EvidenceStatus.UNSATISFIED not in statuses:
        reasons.append("low-score-without-explicit-critical-unsatisfied")
    return tuple(dict.fromkeys(reasons))


def _draft_decision(
    statuses: tuple[EvidenceStatus, ...],
    total_score: int,
    reasons: tuple[str, ...],
) -> ClassificationDecision:
    if reasons:
        return ClassificationDecision.NEEDS_REVIEW
    if EvidenceStatus.UNSATISFIED in statuses:
        if total_score < 70:
            return ClassificationDecision.REJECT
        return ClassificationDecision.NEEDS_REVIEW
    if total_score >= 85:
        return ClassificationDecision.PASS
    if total_score >= 70:
        return ClassificationDecision.WAITLIST
    return ClassificationDecision.NEEDS_REVIEW


def _evidence(
    evidence_id: str,
    source_record_id: str,
    section: EvidenceSection,
    text: str,
) -> Evidence:
    return Evidence(
        evidence_id=evidence_id,
        source_type=EvidenceSourceType.CANDIDATE,
        section=section,
        text=text,
        location=EvidenceLocation(source_record_id=source_record_id),
        extraction_confidence=None,
        is_verified=False,
    )


def _build_profile_and_assessments(
    role_content: Stage7RoleContent,
    scenario: Stage7ScenarioDefinition,
    sequence: int,
    job: JobProfile,
) -> tuple[CVProfile, tuple[RequirementDraftAssessment, ...]]:
    role_requirements = tuple(
        requirement for requirement in job.requirements if requirement.is_critical
    )
    preferred_requirements = tuple(
        requirement for requirement in job.requirements if not requirement.is_critical
    )
    if len(role_requirements) != len(role_content.positive_evidence):
        raise ValueError(f"Stage 7 role content is incomplete for {role_content.role.value}")
    code = f"s7-{role_content.code}-{sequence:02d}"
    cv_profile_id = f"cv-{code}"
    candidate_reference = f"candidate-{code}"
    source_record_id = f"source-{code}"
    context = role_content.project_contexts[sequence - 1]
    evidence: list[Evidence] = []
    skills: list[Skill] = []
    project_evidence_ids: list[str] = []
    assessment_values: list[RequirementDraftAssessment] = []
    evidence_sequence = 1

    def add_evidence(section: EvidenceSection, text: str) -> str:
        nonlocal evidence_sequence
        evidence_id = f"ev-{code}-{evidence_sequence:02d}"
        evidence_sequence += 1
        evidence.append(_evidence(evidence_id, source_record_id, section, text))
        return evidence_id

    education_id = add_evidence(
        EvidenceSection.EDUCATION,
        f"Hoàn thành chương trình định hướng {role_content.field_of_study} với đồ án tổng hợp {context}.",
    )
    for index, requirement in enumerate(role_requirements):
        status = _status_for_scenario(role_content.role, scenario, index)
        linked_ids: list[str] = []
        if scenario.status_mode == "hard_negative":
            evidence_id = add_evidence(
                EvidenceSection.SKILLS,
                f"Đã hoàn thành bài học giới thiệu về {role_content.requirement_skills[index]} và tự ghi tên công cụ trong danh sách kỹ năng.",
            )
            skills.append(
                Skill(
                    name=role_content.requirement_skills[index],
                    evidence_ids=(evidence_id,),
                )
            )
            linked_ids.append(evidence_id)
        else:
            if status in {EvidenceStatus.SATISFIED, EvidenceStatus.CONFLICTING}:
                positive_id = add_evidence(
                    EvidenceSection.PROJECTS,
                    role_content.positive_evidence[index].format(context=context),
                )
                skills.append(
                    Skill(
                        name=role_content.requirement_skills[index],
                        evidence_ids=(positive_id,),
                    )
                )
                project_evidence_ids.append(positive_id)
                linked_ids.append(positive_id)
            if status in {EvidenceStatus.UNSATISFIED, EvidenceStatus.CONFLICTING}:
                negative_id = add_evidence(
                    EvidenceSection.OTHER,
                    role_content.negative_evidence[index],
                )
                linked_ids.append(negative_id)
        rationale_by_status = {
            EvidenceStatus.SATISFIED: "Có mô tả thao tác trực tiếp và đầu ra trong dự án.",
            EvidenceStatus.MISSING: "Hồ sơ không đề cập đủ thông tin để xác nhận yêu cầu này.",
            EvidenceStatus.UNSATISFIED: "Hồ sơ có phát biểu phủ định rõ ràng về yêu cầu này.",
            EvidenceStatus.CONFLICTING: "Hồ sơ đồng thời có mô tả thực hành và phát biểu phủ định mâu thuẫn.",
        }
        assessment_values.append(
            RequirementDraftAssessment(
                requirement_id=requirement.requirement_id,
                evidence_status=status,
                evidence_ids=tuple(linked_ids),
                rationale=rationale_by_status[status],
            )
        )

    selected_preferred = preferred_requirements[: scenario.preferred_count]
    if (
        role_content.role is DatasetRole.QA_ENGINEER
        and scenario.scenario is SyntheticScenario.MISSING_CRITICAL
    ):
        selected_preferred = preferred_requirements[1:2]
    for requirement in selected_preferred:
        evidence_id = add_evidence(
            EvidenceSection.PROJECTS,
            f"Ở phần mở rộng của {context}, ứng viên áp dụng {requirement.title} và ghi lại kết quả thử nghiệm riêng.",
        )
        skills.append(Skill(name=requirement.title, evidence_ids=(evidence_id,)))
        project_evidence_ids.append(evidence_id)

    projects: tuple[Project, ...] = ()
    if scenario.status_mode != "hard_negative":
        detail_ids = (
            add_evidence(
                EvidenceSection.PROJECTS,
                f"Phạm vi kỹ thuật của {context}: {scenario.technical_detail}",
            ),
            add_evidence(
                EvidenceSection.PROJECTS,
                f"Cách ra quyết định trong {context}: {scenario.reasoning_detail}",
            ),
            add_evidence(
                EvidenceSection.PROJECTS,
                f"Bàn giao cho {context}: {scenario.delivery_detail}",
            ),
            add_evidence(
                EvidenceSection.OTHER,
                f"Tài liệu của {context}: {scenario.communication_detail}",
            ),
        )
        project_evidence_ids.extend(detail_ids)
        projects = (
            Project(
                project_id=f"project-{code}",
                title=context.capitalize(),
                summary=(
                    f"{scenario.technical_detail} {scenario.reasoning_detail} "
                    f"{scenario.delivery_detail}"
                ),
                technologies=tuple(skill.name for skill in skills),
                evidence_ids=tuple(dict.fromkeys(project_evidence_ids)),
            ),
        )

    warnings: list[QualityWarning] = []
    warning_values = {
        "missing": (
            "incomplete-critical-information",
            "Một năng lực bắt buộc chưa có thông tin đủ để xác nhận.",
        ),
        "conflicting": (
            "conflicting-critical-information",
            "Một năng lực bắt buộc có hai phát biểu không nhất quán.",
        ),
        "hard_negative": (
            "keyword-only-information",
            "Danh sách kỹ năng chưa có nhiệm vụ hoặc đầu ra chứng minh.",
        ),
    }
    if scenario.status_mode in warning_values:
        warning_code, warning_message = warning_values[scenario.status_mode]
        warnings.append(
            QualityWarning(
                code=warning_code,
                severity=WarningSeverity.WARNING,
                message=warning_message,
            )
        )

    profile = CVProfile(
        cv_profile_id=cv_profile_id,
        candidate_reference=candidate_reference,
        summary=f"{scenario.summary} Mục tiêu ứng tuyển là {job.title}.",
        skills=tuple(skills),
        work_experiences=(),
        education=(
            EducationRecord(
                education_id=f"education-{code}",
                degree="Chương trình đào tạo kỹ thuật",
                field_of_study=role_content.field_of_study,
                institution_reference=f"institution-stage7-{role_content.code}",
                evidence_ids=(education_id,),
            ),
        ),
        projects=projects,
        certifications=(),
        evidence=tuple(evidence),
        quality_warnings=tuple(warnings),
    )
    return profile, tuple(assessment_values)


def _criterion_evidence_ids(
    profile: CVProfile,
    assessments: tuple[RequirementDraftAssessment, ...],
) -> tuple[tuple[str, ...], ...]:
    mandatory = tuple(
        dict.fromkeys(
            evidence_id for assessment in assessments for evidence_id in assessment.evidence_ids
        )
    )
    technical = tuple(
        evidence.evidence_id
        for evidence in profile.evidence
        if evidence.section in {EvidenceSection.SKILLS, EvidenceSection.PROJECTS}
    )
    project_ids = tuple(
        dict.fromkeys(
            evidence_id for project in profile.projects for evidence_id in project.evidence_ids
        )
    )
    role_capability = project_ids[-4:-1] if len(project_ids) >= 4 else project_ids
    communication = tuple(
        evidence.evidence_id
        for evidence in profile.evidence
        if evidence.section is EvidenceSection.OTHER
    )
    fallback = tuple(evidence.evidence_id for evidence in profile.evidence[:1])
    return tuple(
        value or fallback
        for value in (mandatory, technical, role_capability, project_ids, communication)
    )


def _build_pair(
    role_content: Stage7RoleContent,
    scenario: Stage7ScenarioDefinition,
    sequence: int,
    profile: CVProfile,
    assessments: tuple[RequirementDraftAssessment, ...],
    job: JobProfile,
    rubric: ScoringRubric,
) -> SyntheticPairAnnotation:
    total_score = sum(scenario.criterion_points)
    statuses = tuple(assessment.evidence_status for assessment in assessments)
    reasons = _review_reasons(statuses, total_score)
    criterion_evidence = _criterion_evidence_ids(profile, assessments)
    criterion_assessments = tuple(
        CriterionDraftAssessment(
            criterion_id=criterion.criterion_id,
            awarded_points=Decimal(points),
            maximum_points=criterion.weight,
            evidence_ids=evidence_ids,
            rationale=(
                f"Thông tin liên kết hỗ trợ mức {points}/{int(criterion.weight)} cho "
                f"{criterion.title}; đây là điểm nháp cần người đánh giá xác nhận."
            ),
        )
        for criterion, points, evidence_ids in zip(
            rubric.criteria,
            scenario.criterion_points,
            criterion_evidence,
            strict=True,
        )
    )
    decision = _draft_decision(statuses, total_score, reasons)
    payload = {
        "pair_id": f"s7-pair-{role_content.code}-{sequence:02d}",
        "cv_profile_id": profile.cv_profile_id,
        "candidate_reference": profile.candidate_reference,
        "job_profile_id": job.job_profile_id,
        "rubric_id": rubric.rubric_id,
        "role": role_content.role,
        "job_variant": JobVariant.STANDARD,
        "scenario": scenario.scenario,
        "dataset_tier": DatasetTier.BRONZE,
        "critical_requirement_assessments": assessments,
        "criterion_assessments": criterion_assessments,
        "total_score": Decimal(total_score),
        "draft_label": decision,
        "review_reasons": reasons,
        "overall_rationale": (
            "Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. "
            "Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier."
        ),
        "review": PendingDatasetReview(),
    }
    return SyntheticPairAnnotation.model_validate(payload)


def build_stage7_test_set() -> tuple[
    tuple[CVProfile, ...],
    tuple[JobProfile, ...],
    tuple[ScoringRubric, ...],
    tuple[SyntheticPairAnnotation, ...],
]:
    loader = RepositoryConfigurationLoader(REPOSITORY_ROOT, RUNTIME_DIRECTORY)
    jobs_by_role = {
        DatasetRole(
            artifact.job_profile_id.removeprefix("junior-")
            .removesuffix("-std-v2")
            .replace("-", "_")
        ): artifact.to_contract()
        for artifact in loader.load_job_artifacts()
    }
    profiles: list[CVProfile] = []
    jobs: list[JobProfile] = []
    rubrics: list[ScoringRubric] = []
    annotations: list[SyntheticPairAnnotation] = []
    for role_content in ROLE_CONTENT:
        job = jobs_by_role[role_content.role]
        rubric = loader.load_for_job(job.job_profile_id).rubric
        jobs.append(job)
        rubrics.append(rubric)
        for sequence, scenario in enumerate(SCENARIOS, start=1):
            profile, assessments = _build_profile_and_assessments(
                role_content,
                scenario,
                sequence,
                job,
            )
            profiles.append(profile)
            annotations.append(
                _build_pair(
                    role_content,
                    scenario,
                    sequence,
                    profile,
                    assessments,
                    job,
                    rubric,
                )
            )
    return tuple(profiles), tuple(jobs), tuple(rubrics), tuple(annotations)


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
    profile_by_id = {profile.cv_profile_id: profile for profile in profiles}
    job_by_id = {job.job_profile_id: job for job in jobs}
    lines = [
        "# Phiếu duyệt test set Stage 7 v1",
        "",
        "Bộ này có 50 cặp mới, mỗi vai trò 10 cặp và chỉ dùng JD standard đã khóa. Tất cả nhãn hiện là draft; classifier chưa được chạy và chưa có API LLM nào được gọi.",
        "",
        "Với mỗi case, hãy kiểm tra trạng thái từng yêu cầu bắt buộc, năm nhóm điểm, tổng điểm, nhãn dự kiến và lý do. Nếu đồng ý toàn bộ, có thể duyệt bằng một câu xác nhận chung; nếu không, ghi rõ ID case và giá trị cần sửa.",
        "",
        "| Case | Vai trò | Tổng | Nhãn nháp | Lý do review |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for annotation in annotations:
        reasons = ", ".join(annotation.review_reasons) or "không có"
        lines.append(
            f"| `{annotation.pair_id}` | {annotation.role.value} | {annotation.total_score} | {annotation.draft_label.value} | {reasons} |"
        )
    for annotation in annotations:
        profile = profile_by_id[annotation.cv_profile_id]
        job = job_by_id[annotation.job_profile_id]
        evidence_by_id = {item.evidence_id: item.text for item in profile.evidence}
        lines.extend(
            (
                "",
                f"## {annotation.pair_id}",
                "",
                f"- Vị trí: {job.title}",
                f"- Hồ sơ: `{profile.cv_profile_id}`",
                f"- Tóm tắt: {profile.summary}",
                f"- Tổng điểm nháp: {annotation.total_score}",
                f"- Nhãn nháp: `{annotation.draft_label.value}`",
                f"- Lý do review: {', '.join(annotation.review_reasons) or 'không có'}",
                "",
                "| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |",
                "| --- | --- | --- |",
            )
        )
        for assessment in annotation.critical_requirement_assessments:
            evidence_text = " / ".join(
                evidence_by_id[evidence_id] for evidence_id in assessment.evidence_ids
            )
            lines.append(
                f"| `{assessment.requirement_id}` | `{assessment.evidence_status.value}` | {evidence_text or 'Không có thông tin'} |"
            )
        lines.extend(
            (
                "",
                "| Nhóm tiêu chí | Điểm |",
                "| --- | ---: |",
            )
        )
        for assessment in annotation.criterion_assessments:
            lines.append(
                f"| `{assessment.criterion_id}` | {assessment.awarded_points}/{assessment.maximum_points} |"
            )
        lines.extend(("", f"Lý do tổng hợp: {annotation.overall_rationale}"))
    return "\n".join(lines) + "\n"


def write_stage7_test_set(output_directory: Path = OUTPUT_DIRECTORY) -> tuple[Path, ...]:
    profiles, jobs, rubrics, annotations = build_stage7_test_set()
    output_directory.mkdir(parents=True, exist_ok=True)
    paths = (
        output_directory / "cv_profiles.jsonl",
        output_directory / "job_profiles.jsonl",
        output_directory / "rubrics.jsonl",
        output_directory / "pairs.jsonl",
    )
    records = (profiles, jobs, rubrics, annotations)
    for path, values in zip(paths, records, strict=True):
        _write_json_lines(path, values)
    review_sheet_path = output_directory / "review_sheet.md"
    review_sheet_path.write_text(
        _review_sheet(profiles, jobs, annotations),
        encoding="utf-8",
    )
    prior_datasets = tuple(
        Stage7PriorDatasetReference(
            dataset_id=dataset_id,
            cv_profiles_path=relative_path,
            cv_profiles_sha256=file_sha256(REPOSITORY_ROOT / relative_path),
        )
        for dataset_id, relative_path in PRIOR_DATASET_PATHS
    )
    role_counts = Counter(annotation.role for annotation in annotations)
    scenario_counts = Counter(annotation.scenario for annotation in annotations)
    label_counts = Counter(annotation.draft_label for annotation in annotations)
    runtime_manifest_path = RUNTIME_DIRECTORY / "runtime_manifest.yaml"
    manifest = Stage7TestManifest(
        schema_version="1.1.0",
        dataset_id="stage7-five-role-test-v1",
        dataset_version="1.0.1",
        status="draft_for_human_review",
        generated_at=datetime.fromisoformat(GENERATED_AT),
        source_type="synthetic_new_profiles",
        runtime_configuration_set_id="five-role-runtime-v1",
        runtime_manifest_path=runtime_manifest_path.relative_to(REPOSITORY_ROOT).as_posix(),
        runtime_manifest_sha256=file_sha256(runtime_manifest_path),
        cv_schema_version="1.0.0",
        job_profile_schema_version="1.0.0",
        rubric_schema_version="1.0.0",
        candidate_count=50,
        job_profile_count=5,
        rubric_count=5,
        pair_count=50,
        role_pair_counts=dict(role_counts),
        scenario_pair_counts=dict(scenario_counts),
        draft_label_counts=dict(label_counts),
        dataset_tier=DatasetTier.BRONZE,
        ground_truth_status="pending_human_review",
        minimum_human_reviewers_for_gold=2,
        locked_for_evaluation=False,
        classifier_results_generated=False,
        llm_requests_made=False,
        source_dataset_version="1.0.0",
        source_manifest_sha256=SOURCE_MANIFEST_SHA256,
        prior_datasets=prior_datasets,
        provenance=(
            "All CV profiles were newly authored for Stage 7 and contain no real candidate data.",
            "Frozen five-role standard Job Profiles and rubrics were copied without modification.",
            "Opaque identifiers exclude scenario names and draft labels to prevent label leakage.",
            "Draft annotations are not ground truth until required human review is complete.",
            "No classifier layer or LLM provider was executed while constructing this test set.",
            "Version 1.0.1 resolves five cross-requirement evidence contradictions found during two-person human review.",
            "Backend missing and explicit-failure scenarios now target delivery workflow instead of Python.",
            "Frontend and QA explicit-failure scenarios now target testing automation or workflow requirements.",
            "QA missing-critical now targets automation foundation instead of testing foundations.",
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
    quality_report = validate_stage7_test_set(REPOSITORY_ROOT, output_directory)
    quality_report_path = output_directory / "quality_report.json"
    quality_report_path.write_text(
        json.dumps(
            quality_report.model_dump(mode="json"),
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    if not quality_report.passed:
        raise ValueError(f"Stage 7 test set failed quality control: {quality_report.errors}")
    return paths + (review_sheet_path, manifest_path, quality_report_path)


def main() -> None:
    for path in write_stage7_test_set():
        print(path)


if __name__ == "__main__":
    main()
