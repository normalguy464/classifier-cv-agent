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
    WorkExperience,
)
from backend.app.infrastructure.config import RepositoryConfigurationLoader
from evaluation.datasets.runtime_v2 import (
    RuntimeV2DevelopmentManifest,
    RuntimeV2FileDigest,
    RuntimeV2PriorReference,
    file_sha256,
    validate_runtime_v2_development,
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
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIRECTORY = Path("configs/runtime/five_role_v1")
OUTPUT_DIRECTORY = REPOSITORY_ROOT / "data/runtime_v2/to_review/development_v1"


@dataclass(frozen=True, slots=True)
class CapabilityLanguage:
    requirement_id: str
    skill_name: str
    positive: tuple[str, str, str]
    negative: tuple[str, str]
    context_only: tuple[str, str]


@dataclass(frozen=True, slots=True)
class RoleLanguage:
    role: DatasetRole
    code: str
    field_of_study: str
    project_topics: tuple[str, str, str, str, str]
    capabilities: tuple[CapabilityLanguage, ...]


@dataclass(frozen=True, slots=True)
class CaseDesign:
    scenario: SyntheticScenario
    status_mode: str
    criterion_points: tuple[int, int, int, int, int]
    summary: str
    technical_depth: str
    reasoning: str
    delivery: str
    communication: str


ROLE_LANGUAGES: tuple[RoleLanguage, ...] = (
    RoleLanguage(
        role=DatasetRole.DATA_ANALYST,
        code="da",
        field_of_study="Phân tích dữ liệu và hệ thống thông tin",
        project_topics=(
            "phân tích hành vi mua lại của khách hàng",
            "theo dõi hiệu quả chiến dịch đa kênh",
            "đối soát chất lượng đơn hàng",
            "phân tích thời gian xử lý yêu cầu hỗ trợ",
            "xây báo cáo vận hành cho chuỗi bán lẻ",
        ),
        capabilities=(
            CapabilityLanguage(
                requirement_id="da-sql",
                skill_name="Truy vấn dữ liệu quan hệ",
                positive=(
                    "Tự viết chuỗi truy vấn kết hợp nhiều bảng, dùng CTE và hàm cửa sổ để tạo tập dữ liệu phân tích cho {context}.",
                    "Từ kho dữ liệu quan hệ, xây câu lệnh tổng hợp theo nhóm, kiểm tra bản ghi trùng và đối chiếu kết quả trước khi phân tích {context}.",
                    "Tối ưu câu truy vấn nhiều bước sau khi đọc execution plan, giảm thời gian lấy dữ liệu phục vụ {context}.",
                ),
                negative=(
                    "Mới học cú pháp truy vấn cơ bản và chưa tự xử lý bài toán nối nhiều bảng trong sản phẩm nào.",
                    "Không thể tự viết câu lệnh lấy dữ liệu quan hệ; phần truy xuất cho {context} do người khác chuẩn bị.",
                ),
                context_only=(
                    "Đã dự buổi giới thiệu về cơ sở dữ liệu quan hệ nhưng hồ sơ không nêu thao tác truy vấn nào cho {context}.",
                    "Có đọc tài liệu về kho dữ liệu; không có ví dụ sử dụng câu lệnh truy xuất hay biến đổi bảng.",
                ),
            ),
            CapabilityLanguage(
                requirement_id="da-analysis-language",
                skill_name="Lập trình phân tích",
                positive=(
                    "Dùng pandas để làm sạch kiểu dữ liệu, xử lý giá trị thiếu và tái tạo notebook phân tích {context}.",
                    "Viết script R với dplyr và ggplot2 để biến đổi dữ liệu, kiểm tra phân phối và trực quan hóa kết quả {context}.",
                    "Đóng gói các bước tiền xử lý bằng Python thành hàm có kiểm tra đầu vào để nhóm chạy lại phân tích {context}.",
                ),
                negative=(
                    "Chưa từng dùng Python hoặc R để xử lý dữ liệu; chỉ thao tác thủ công trên bảng tính.",
                    "Không thể chỉnh sửa notebook phân tích và chưa viết mã biến đổi dữ liệu cho {context}.",
                ),
                context_only=(
                    "Hoàn thành bài nhập môn lập trình nhưng không trình bày mã nguồn hoặc đầu ra phân tích dữ liệu.",
                    "Có xem notebook mẫu của lớp; hồ sơ không cho biết phần nào do ứng viên tự thực hiện.",
                ),
            ),
            CapabilityLanguage(
                requirement_id="da-bi-reporting",
                skill_name="Báo cáo BI",
                positive=(
                    "Thiết kế dashboard Power BI có bộ lọc, mô hình quan hệ và trang theo dõi KPI cho {context}.",
                    "Xây báo cáo Tableau, định nghĩa chỉ số và kiểm tra số tổng với nguồn trước khi bàn giao {context}.",
                    "Tạo dashboard tương tác trên Looker Studio, tách metric vận hành và metric kết quả cho {context}.",
                ),
                negative=(
                    "Chưa từng tự xây dashboard hoặc báo cáo BI; chỉ xem báo cáo đã được người khác xuất.",
                    "Không sử dụng được công cụ trực quan hóa dữ liệu để bàn giao kết quả {context}.",
                ),
                context_only=(
                    "Biết tên một số công cụ trực quan hóa nhưng không có màn hình, mô hình hoặc chỉ số đã xây.",
                    "Theo dõi buổi demo dashboard của nhóm; không nêu phần việc trực tiếp của ứng viên.",
                ),
            ),
            CapabilityLanguage(
                requirement_id="da-business-analysis",
                skill_name="Phân tích nghiệp vụ",
                positive=(
                    "Chuyển câu hỏi giữ chân khách hàng thành KPI, phân tích nguyên nhân và đề xuất hai hành động có thể kiểm chứng cho {context}.",
                    "Làm rõ định nghĩa chỉ số với người dùng báo cáo, nêu giả định và đưa ra khuyến nghị nghiệp vụ từ {context}.",
                    "Thực hiện luồng phân tích từ câu hỏi, dữ liệu, kiểm tra sai lệch đến kết luận và giới hạn cho {context}.",
                ),
                negative=(
                    "Chưa hoàn thành dự án phân tích có câu hỏi nghiệp vụ, kết luận và đầu ra bàn giao.",
                    "Không thể giải thích chỉ số hoặc đưa ra khuyến nghị từ kết quả {context}.",
                ),
                context_only=(
                    "Có tham dự cuộc họp nghiệp vụ nhưng không nêu câu hỏi, phân tích hoặc quyết định do mình thực hiện.",
                    "Liệt kê khái niệm KPI mà không gắn với dữ liệu, giả định hay kết luận cụ thể.",
                ),
            ),
        ),
    ),
    RoleLanguage(
        role=DatasetRole.PYTHON_BACKEND,
        code="be",
        field_of_study="Kỹ thuật phần mềm và hệ thống backend",
        project_topics=(
            "dịch vụ quản lý đơn đặt hàng",
            "hệ thống đăng ký lịch học",
            "API quản lý kho thiết bị",
            "dịch vụ theo dõi yêu cầu hỗ trợ",
            "backend cho ứng dụng quản lý chi tiêu",
        ),
        capabilities=(
            CapabilityLanguage(
                requirement_id="be-python",
                skill_name="Python backend",
                positive=(
                    "Tự triển khai tầng nghiệp vụ bằng Python, tách module và xử lý ngoại lệ cho {context}.",
                    "Viết service Python có type hints, logging và kiểm tra dữ liệu đầu vào cho {context}.",
                    "Dùng Python xây luồng xử lý bất đồng bộ và theo dõi lỗi trong {context}.",
                ),
                negative=(
                    "Chưa từng dùng Python để xây phần mềm backend; chỉ chạy lại đoạn mã mẫu của lớp.",
                    "Không thể tự viết module Python cho {context}; phần mã nguồn do thành viên khác phụ trách.",
                ),
                context_only=(
                    "Đã học cú pháp Python cơ bản nhưng không có module, chức năng hay sản phẩm backend được mô tả.",
                    "Có đọc source Python của nhóm; hồ sơ không xác định phần mã do ứng viên thực hiện.",
                ),
            ),
            CapabilityLanguage(
                requirement_id="be-rest-api",
                skill_name="Thiết kế HTTP API",
                positive=(
                    "Thiết kế endpoint theo tài nguyên, mã trạng thái và schema request/response cho {context} bằng FastAPI.",
                    "Xây API Django REST có phân trang, xác thực dữ liệu và tài liệu OpenAPI cho {context}.",
                    "Triển khai dịch vụ Flask, xử lý lỗi nhất quán và kiểm thử hợp đồng HTTP cho {context}.",
                ),
                negative=(
                    "Chưa từng xây HTTP API; mới gọi thử endpoint có sẵn bằng công cụ kiểm tra.",
                    "Không thể thiết kế route hoặc schema request/response cho {context}.",
                ),
                context_only=(
                    "Biết khái niệm REST và đã xem Swagger nhưng chưa triển khai endpoint nào.",
                    "Từng gửi request tới API mẫu; không có bằng chứng xây hoặc bảo trì API phía server.",
                ),
            ),
            CapabilityLanguage(
                requirement_id="be-relational-data",
                skill_name="Dữ liệu quan hệ",
                positive=(
                    "Thiết kế schema PostgreSQL, tạo migration và dùng transaction cho luồng cập nhật {context}.",
                    "Xây quan hệ bảng, index và câu truy vấn MySQL cho {context}, sau đó kiểm tra tính toàn vẹn dữ liệu.",
                    "Dùng SQLAlchemy quản lý phiên giao dịch và migration khi thay đổi mô hình dữ liệu của {context}.",
                ),
                negative=(
                    "Chưa thể thiết kế bảng hoặc viết truy vấn cho cơ sở dữ liệu quan hệ.",
                    "Không có kiến thức SQL; dữ liệu của {context} được thành viên khác chuẩn bị sẵn.",
                ),
                context_only=(
                    "Đã xem sơ đồ cơ sở dữ liệu của dự án nhưng không nêu truy vấn, schema hay migration tự thực hiện.",
                    "Biết tên PostgreSQL nhưng chưa kết nối hoặc lưu dữ liệu từ ứng dụng backend.",
                ),
            ),
            CapabilityLanguage(
                requirement_id="be-testing",
                skill_name="Kiểm thử backend",
                positive=(
                    "Viết unit test và integration test bằng pytest cho luồng lỗi và luồng thành công của {context}.",
                    "Tạo fixture cơ sở dữ liệu, mock dịch vụ ngoài và chạy bộ kiểm thử tự động cho {context}.",
                    "Bổ sung test hồi quy cho lỗi production và đo coverage của module trọng yếu trong {context}.",
                ),
                negative=(
                    "Chưa từng viết hoặc chạy kiểm thử tự động cho backend; chỉ kiểm tra thủ công.",
                    "Không có unit test hay integration test cho phần việc trong {context}.",
                ),
                context_only=(
                    "Đã đọc tài liệu pytest nhưng không có test case tự động hoặc kết quả chạy test.",
                    "Có thao tác thử API thủ công; không trình bày bộ kiểm thử có thể chạy lại.",
                ),
            ),
            CapabilityLanguage(
                requirement_id="be-delivery-workflow",
                skill_name="Quy trình bàn giao backend",
                positive=(
                    "Quản lý thay đổi bằng Git, mở pull request có review và đóng gói {context} bằng Docker.",
                    "Dùng nhánh tính năng, xử lý góp ý code review và viết Dockerfile chạy dịch vụ {context}.",
                    "Thiết lập pipeline kiểm tra mã, build container và ghi hướng dẫn triển khai cho {context}.",
                ),
                negative=(
                    "Chưa dùng quản lý phiên bản và chưa thể đóng gói dịch vụ để người khác chạy lại.",
                    "Không có Git hoặc Docker trong quy trình bàn giao {context}.",
                ),
                context_only=(
                    "Biết khái niệm repository và container nhưng không có lịch sử commit hay cấu hình chạy được.",
                    "Đã tải source dạng tệp nén; hồ sơ không nêu pull request, review hoặc cách đóng gói.",
                ),
            ),
        ),
    ),
    RoleLanguage(
        role=DatasetRole.FRONTEND,
        code="fe",
        field_of_study="Phát triển ứng dụng web phía người dùng",
        project_topics=(
            "cổng tra cứu khóa học",
            "giao diện quản lý đơn hàng",
            "ứng dụng theo dõi thói quen",
            "trang điều hành câu lạc bộ",
            "website đặt lịch dịch vụ",
        ),
        capabilities=(
            CapabilityLanguage(
                requirement_id="fe-web-foundations",
                skill_name="Nền tảng giao diện web",
                positive=(
                    "Dựng giao diện semantic HTML và CSS responsive, kiểm tra ở nhiều kích thước màn hình cho {context}.",
                    "Triển khai layout bằng Grid và Flexbox, xử lý keyboard focus và breakpoint cho {context}.",
                    "Chuyển thiết kế thành trang web thích ứng, giữ cấu trúc heading và biểu mẫu có nhãn trong {context}.",
                ),
                negative=(
                    "Chưa thể tự xây giao diện responsive bằng HTML và CSS.",
                    "Không nắm nền tảng bố cục web; phần giao diện {context} dùng nguyên mẫu có sẵn.",
                ),
                context_only=(
                    "Đã xem bài học HTML/CSS nhưng không có trang hoặc component tự triển khai.",
                    "Có chỉnh màu trong template; không trình bày cấu trúc semantic hay xử lý responsive.",
                ),
            ),
            CapabilityLanguage(
                requirement_id="fe-language",
                skill_name="JavaScript và TypeScript",
                positive=(
                    "Viết TypeScript quản lý state, kiểu dữ liệu API và xử lý lỗi phía client cho {context}.",
                    "Dùng JavaScript module hóa logic tương tác và kiểm tra dữ liệu biểu mẫu trong {context}.",
                    "Bật kiểm tra kiểu nghiêm ngặt, loại bỏ kiểu không xác định và xử lý promise cho {context}.",
                ),
                negative=(
                    "Chưa từng dùng JavaScript hoặc TypeScript để phát triển ứng dụng web.",
                    "Không thể tự viết logic phía client cho {context}; chỉ sửa nội dung tĩnh.",
                ),
                context_only=(
                    "Hoàn thành bài cú pháp JavaScript nhưng không có chức năng web được mô tả.",
                    "Biết tên TypeScript; hồ sơ không có kiểu dữ liệu, module hay xử lý bất đồng bộ.",
                ),
            ),
            CapabilityLanguage(
                requirement_id="fe-framework",
                skill_name="Framework component",
                positive=(
                    "Xây component React tái sử dụng, tách state và tối ưu render cho {context}.",
                    "Dùng Vue Composition API tổ chức màn hình và luồng dữ liệu cho {context}.",
                    "Thiết kế cây component, route và trạng thái tải/lỗi cho ứng dụng {context}.",
                ),
                negative=(
                    "Chưa từng xây ứng dụng bằng framework frontend dựa trên component.",
                    "Không sử dụng React, Vue hoặc framework tương đương trong {context}.",
                ),
                context_only=(
                    "Đã chạy project React mẫu nhưng không nêu component hoặc tính năng tự xây.",
                    "Theo dõi khóa học framework; không có source hay đầu ra ứng dụng.",
                ),
            ),
            CapabilityLanguage(
                requirement_id="fe-api",
                skill_name="Tích hợp API phía client",
                positive=(
                    "Tích hợp REST API, xử lý loading, empty, error và hủy request cho {context}.",
                    "Dùng fetch với token xác thực, ánh xạ lỗi HTTP và đồng bộ dữ liệu màn hình {context}.",
                    "Tạo lớp gọi API có validation response và retry có giới hạn cho {context}.",
                ),
                negative=(
                    "Chưa từng tích hợp API vào giao diện; dữ liệu đều được viết cố định.",
                    "Không thể gọi hoặc xử lý response API từ màn hình {context}.",
                ),
                context_only=(
                    "Biết API cung cấp dữ liệu nhưng không có request hoặc trạng thái giao diện được triển khai.",
                    "Đã xem JSON mẫu; hồ sơ không nêu việc kết nối frontend với server.",
                ),
            ),
            CapabilityLanguage(
                requirement_id="fe-testing-workflow",
                skill_name="Kiểm thử và bàn giao frontend",
                positive=(
                    "Dùng Git theo pull request và viết component test cho tương tác chính của {context}.",
                    "Bổ sung test bằng Testing Library, xử lý góp ý review và cấu hình build cho {context}.",
                    "Thiết lập lint, unit test và quy trình merge có kiểm tra tự động cho {context}.",
                ),
                negative=(
                    "Chưa từng dùng Git và chưa từng kiểm thử giao diện.",
                    "Không có component test hoặc quy trình review thay đổi cho {context}.",
                ),
                context_only=(
                    "Biết tên công cụ test frontend nhưng không có test hoặc kết quả chạy tự động.",
                    "Đã gửi source cho nhóm qua tệp nén; không có pull request hay kiểm tra trước merge.",
                ),
            ),
        ),
    ),
    RoleLanguage(
        role=DatasetRole.QA_ENGINEER,
        code="qa",
        field_of_study="Kiểm thử phần mềm và đảm bảo chất lượng",
        project_topics=(
            "kiểm thử cổng đăng ký môn học",
            "đánh giá chất lượng ứng dụng thương mại",
            "kiểm thử hệ thống quản lý kho",
            "xác minh luồng thanh toán thử nghiệm",
            "kiểm thử ứng dụng đặt lịch",
        ),
        capabilities=(
            CapabilityLanguage(
                requirement_id="qa-testing-foundations",
                skill_name="Nền tảng kiểm thử",
                positive=(
                    "Áp dụng phân vùng tương đương, giá trị biên và decision table để thiết kế phạm vi test cho {context}.",
                    "Mô tả các bước STLC, xác định rủi ro và ưu tiên kiểm thử cho {context}.",
                    "Phân tích yêu cầu, lập test condition và giải thích kỹ thuật thiết kế test được chọn trong {context}.",
                ),
                negative=(
                    "Chưa biết quy trình hoặc kỹ thuật thiết kế kiểm thử phần mềm.",
                    "Không thể giải thích cách chọn dữ liệu test cho {context}.",
                ),
                context_only=(
                    "Đã nghe giới thiệu về QA nhưng không nêu kỹ thuật hoặc quy trình đã áp dụng.",
                    "Biết thuật ngữ STLC; hồ sơ không có test condition hay cách phân tích yêu cầu.",
                ),
            ),
            CapabilityLanguage(
                requirement_id="qa-test-cases",
                skill_name="Thiết kế test case và defect",
                positive=(
                    "Viết test case có precondition, dữ liệu, expected result và liên kết defect cho {context}.",
                    "Thực hiện regression, ghi bug report có bước tái hiện và mức độ ảnh hưởng trong {context}.",
                    "Duy trì bộ test theo yêu cầu thay đổi và theo dõi vòng đời lỗi của {context}.",
                ),
                negative=(
                    "Chưa từng viết test case hoặc báo cáo bug có thể tái hiện.",
                    "Không có kinh nghiệm quản lý defect cho {context}.",
                ),
                context_only=(
                    "Đã xem mẫu test case nhưng không có trường hợp tự thiết kế.",
                    "Có báo miệng một lỗi; hồ sơ không nêu bước tái hiện hoặc expected result.",
                ),
            ),
            CapabilityLanguage(
                requirement_id="qa-api-testing",
                skill_name="Kiểm thử API",
                positive=(
                    "Dùng Postman kiểm tra method, status, schema và trường hợp xác thực lỗi cho API của {context}.",
                    "Tạo collection kiểm thử request/response HTTP và biến môi trường cho {context}.",
                    "Đối chiếu hợp đồng API, kiểm tra dữ liệu biên và lưu kết quả chạy lại cho {context}.",
                ),
                negative=(
                    "Chưa từng kiểm thử API hoặc đọc request và response HTTP.",
                    "Không thể dùng Postman để xác minh endpoint của {context}.",
                ),
                context_only=(
                    "Đã mở Postman một lần nhưng không có collection, assertion hoặc kết quả kiểm thử.",
                    "Biết API dùng HTTP; hồ sơ không nêu request hay response đã kiểm tra.",
                ),
            ),
            CapabilityLanguage(
                requirement_id="qa-data-check",
                skill_name="Kiểm tra dữ liệu bằng truy vấn",
                positive=(
                    "Viết truy vấn SELECT, JOIN và GROUP BY để đối chiếu dữ liệu sau thao tác trong {context}.",
                    "Kiểm tra ràng buộc và bản ghi bất thường bằng SQL khi xác minh {context}.",
                    "So sánh dữ liệu API với bảng quan hệ và lưu câu truy vấn tái kiểm tra cho {context}.",
                ),
                negative=(
                    "Chưa thể dùng SQL để kiểm tra dữ liệu.",
                    "Không có kỹ năng truy vấn; phần đối chiếu dữ liệu của {context} do người khác thực hiện.",
                ),
                context_only=(
                    "Đã xem bảng dữ liệu nhưng không có câu truy vấn hoặc phép đối chiếu tự thực hiện.",
                    "Biết dữ liệu nằm trong cơ sở quan hệ; hồ sơ không cho thấy khả năng kiểm tra bằng SQL.",
                ),
            ),
            CapabilityLanguage(
                requirement_id="qa-automation-foundation",
                skill_name="Tự động hóa kiểm thử",
                positive=(
                    "Viết kịch bản Playwright cho luồng chính, dùng locator ổn định và chạy lại trên CI cho {context}.",
                    "Dùng Selenium tổ chức page object và tự động hóa regression của {context}.",
                    "Tạo test Cypress có setup dữ liệu, assertion và báo cáo kết quả cho {context}.",
                ),
                negative=(
                    "Chưa từng viết script hoặc test tự động.",
                    "Không sử dụng framework automation trong {context}; toàn bộ test chạy thủ công.",
                ),
                context_only=(
                    "Đã xem demo Selenium nhưng không có kịch bản tự viết hoặc kết quả chạy.",
                    "Biết khái niệm automation testing; hồ sơ không nêu framework hay test có thể tái chạy.",
                ),
            ),
        ),
    ),
    RoleLanguage(
        role=DatasetRole.DATA_ENGINEER,
        code="de",
        field_of_study="Kỹ thuật dữ liệu và hệ thống phân tích",
        project_topics=(
            "pipeline tổng hợp giao dịch hằng ngày",
            "luồng dữ liệu sự kiện ứng dụng",
            "data mart theo dõi vận hành",
            "pipeline đồng bộ dữ liệu bán hàng",
            "hệ thống kiểm tra dữ liệu nguồn",
        ),
        capabilities=(
            CapabilityLanguage(
                requirement_id="de-python",
                skill_name="Python xử lý dữ liệu",
                positive=(
                    "Viết Python đọc dữ liệu theo lô, chuẩn hóa schema và ghi log lỗi cho {context}.",
                    "Dùng pandas xây bước biến đổi có kiểm tra kiểu và test đầu vào cho {context}.",
                    "Tổ chức package Python xử lý dữ liệu, cấu hình tham số và retry có giới hạn trong {context}.",
                ),
                negative=(
                    "Chưa từng dùng Python cho xử lý dữ liệu.",
                    "Không thể tự viết bước biến đổi Python trong {context}.",
                ),
                context_only=(
                    "Đã học cú pháp Python nhưng không có pipeline hay bước xử lý dữ liệu tự thực hiện.",
                    "Có chạy notebook mẫu; hồ sơ không xác định mã nguồn do ứng viên viết.",
                ),
            ),
            CapabilityLanguage(
                requirement_id="de-sql",
                skill_name="SQL cho kỹ thuật dữ liệu",
                positive=(
                    "Viết CTE và window function để chuẩn hóa, khử trùng và kiểm tra dữ liệu cho {context}.",
                    "Tối ưu truy vấn sau khi đọc execution plan và bổ sung index cho bảng trung gian của {context}.",
                    "Xây câu lệnh incremental merge và đối chiếu số lượng bản ghi trong {context}.",
                ),
                negative=(
                    "Chưa có kiến thức SQL hoặc cơ sở dữ liệu quan hệ.",
                    "Không thể tự viết truy vấn phục vụ {context}.",
                ),
                context_only=(
                    "Đã xem bảng dữ liệu nhưng không có truy vấn hay phép biến đổi SQL được mô tả.",
                    "Biết tên một hệ quản trị quan hệ; hồ sơ không nêu câu lệnh hoặc kết quả thực hành.",
                ),
            ),
            CapabilityLanguage(
                requirement_id="de-pipeline",
                skill_name="Pipeline ETL và ELT",
                positive=(
                    "Xây pipeline ETL có incremental load, checkpoint và xử lý chạy lại cho {context}.",
                    "Thiết kế luồng ELT theo lịch, theo dõi trạng thái và cảnh báo bước thất bại trong {context}.",
                    "Tách extract, transform và load thành các task có dependency rõ ràng cho {context}.",
                ),
                negative=(
                    "Chưa từng xây pipeline ETL hoặc ELT.",
                    "Không có kinh nghiệm incremental load trong {context}.",
                ),
                context_only=(
                    "Đã xem sơ đồ pipeline nhưng không nêu task, lịch chạy hoặc cách xử lý lỗi tự thực hiện.",
                    "Biết thuật ngữ ETL; hồ sơ không có luồng dữ liệu có thể chạy lại.",
                ),
            ),
            CapabilityLanguage(
                requirement_id="de-data-model-quality",
                skill_name="Mô hình và chất lượng dữ liệu",
                positive=(
                    "Thiết kế fact, dimension và kiểm tra uniqueness, null, referential integrity cho {context}.",
                    "Xây data mart dạng star schema, định nghĩa grain và rule chất lượng dữ liệu cho {context}.",
                    "Theo dõi data quality, phân loại lỗi nguồn và lập quy trình đối soát trong {context}.",
                ),
                negative=(
                    "Chưa từng mô hình hóa bảng hoặc kiểm tra chất lượng dữ liệu.",
                    "Không thể giải thích grain, fact hay dimension của {context}.",
                ),
                context_only=(
                    "Đã đọc tài liệu data warehouse nhưng không có mô hình hoặc rule chất lượng tự xây.",
                    "Có xem sơ đồ star schema; hồ sơ không nêu quyết định mô hình hóa nào.",
                ),
            ),
            CapabilityLanguage(
                requirement_id="de-delivery-workflow",
                skill_name="Bàn giao pipeline dữ liệu",
                positive=(
                    "Quản lý source bằng Git, chạy pipeline trên Linux, đọc log và đóng gói môi trường bằng Docker cho {context}.",
                    "Mở pull request, xử lý review và viết hướng dẫn vận hành cùng lệnh kiểm tra cho {context}.",
                    "Thiết lập CI chạy test, build container và tài liệu khôi phục khi pipeline {context} lỗi.",
                ),
                negative=(
                    "Chưa dùng Git, Linux và chưa thể bàn giao môi trường pipeline.",
                    "Không có quy trình đóng gói hoặc đọc log cho {context}.",
                ),
                context_only=(
                    "Biết tên Git, Linux và Docker nhưng không có repository, lệnh chạy hoặc cấu hình bàn giao.",
                    "Đã nhận source có sẵn; hồ sơ không nêu commit, log hay cách tái tạo môi trường.",
                ),
            ),
        ),
    ),
)


CASE_DESIGNS: tuple[CaseDesign, ...] = (
    CaseDesign(
        SyntheticScenario.STRONG,
        "all_satisfied",
        (29, 23, 18, 14, 9),
        "Hồ sơ có năng lực bắt buộc đầy đủ và đầu ra kiểm chứng được.",
        "Giải pháp bao phủ luồng chính, dữ liệu biên và bước kiểm tra lại.",
        "Nêu rõ lựa chọn kỹ thuật, giả định và một phương án đã loại bỏ.",
        "Bàn giao source, hướng dẫn chạy và kết quả kiểm tra cho người dùng nội bộ.",
        "Mô tả ngắn gọn phạm vi, kết quả định lượng và giới hạn còn lại.",
    ),
    CaseDesign(
        SyntheticScenario.STRONG,
        "all_satisfied",
        (28, 22, 17, 13, 8),
        "Hồ sơ mạnh với kinh nghiệm thực hành ở mức junior.",
        "Thực hiện phần cốt lõi và xử lý ít nhất một lỗi phát sinh.",
        "So sánh hai cách triển khai trước khi chọn giải pháp phù hợp phạm vi.",
        "Có quy trình review và tài liệu để thành viên khác chạy lại.",
        "Thông tin nhất quán, có đầu ra nhưng phần đo lường chưa hoàn toàn độc lập.",
    ),
    CaseDesign(
        SyntheticScenario.SOLID,
        "all_satisfied",
        (26, 20, 16, 12, 8),
        "Hồ sơ đáp ứng yêu cầu chính với độ sâu khá.",
        "Hoàn thành luồng chính và kiểm tra dữ liệu đầu vào phổ biến.",
        "Giải thích quyết định dựa trên yêu cầu và giới hạn thời gian.",
        "Bàn giao qua repository và checklist chạy thử.",
        "Nêu vai trò, kết quả và một giới hạn kỹ thuật.",
    ),
    CaseDesign(
        SyntheticScenario.MODERATE,
        "all_satisfied",
        (24, 18, 15, 11, 7),
        "Hồ sơ đáp ứng tối thiểu nhưng phạm vi và tác động còn vừa phải.",
        "Có sản phẩm chạy được trong phạm vi học tập hoặc cá nhân.",
        "Nêu lý do lựa chọn chính nhưng chưa phân tích sâu trade-off.",
        "Có source và hướng dẫn cơ bản để tái chạy.",
        "Thông tin đủ hiểu nhưng thiếu số đo tác động độc lập.",
    ),
    CaseDesign(
        SyntheticScenario.MISSING_CRITICAL,
        "one_missing",
        (18, 17, 14, 10, 7),
        "Một yêu cầu bắt buộc thiếu thông tin trực tiếp.",
        "Các phần được mô tả có thao tác thực hành nhưng độ bao phủ chưa đầy đủ.",
        "Có giải thích cho phần đã làm, không suy diễn phần còn thiếu.",
        "Bàn giao được phạm vi hiện có và ghi rõ giới hạn.",
        "Hồ sơ phân biệt rõ điều đã làm và điều chưa có thông tin.",
    ),
    CaseDesign(
        SyntheticScenario.EXPLICIT_FAILURE,
        "one_conflicting",
        (22, 19, 15, 12, 8),
        "Một năng lực bắt buộc có thông tin tích cực và phủ định mâu thuẫn.",
        "Có đầu ra kỹ thuật nhưng trạng thái một năng lực chưa thể kết luận.",
        "Ghi lại quyết định của dự án nhưng chưa giải thích được mâu thuẫn trong hồ sơ.",
        "Có artifact bàn giao và một cảnh báo cần xác minh.",
        "Thông tin khá rõ ngoài điểm mâu thuẫn cần human review.",
    ),
    CaseDesign(
        SyntheticScenario.EXPLICIT_FAILURE,
        "one_unsatisfied",
        (16, 15, 12, 8, 6),
        "Hồ sơ xác nhận rõ một yêu cầu bắt buộc chưa đạt.",
        "Một phần công việc phụ thuộc vào thành viên khác và không có khả năng thay thế.",
        "Nêu đúng giới hạn hiện tại nhưng chưa có kế hoạch kiểm chứng năng lực thiếu.",
        "Chỉ bàn giao được phần việc hẹp.",
        "Thông tin phủ định rõ và không bị che bởi danh sách từ khóa.",
    ),
    CaseDesign(
        SyntheticScenario.MISSING_CRITICAL,
        "all_unsatisfied",
        (5, 5, 6, 4, 4),
        "Hồ sơ chỉ có mức làm quen và xác nhận chưa thực hiện các năng lực cốt lõi.",
        "Không có artifact hoặc tác vụ chuyên môn do ứng viên tự hoàn thành.",
        "Chưa có quyết định kỹ thuật để đánh giá.",
        "Không có quy trình bàn giao có thể tái tạo.",
        "Giới hạn được phát biểu rõ, không tạo ấn tượng sai về kinh nghiệm.",
    ),
    CaseDesign(
        SyntheticScenario.MISSING_CRITICAL,
        "alternating_missing",
        (14, 13, 12, 8, 6),
        "Nhiều yêu cầu bắt buộc chỉ có thông tin liên quan gián tiếp.",
        "Có một số thao tác đơn lẻ nhưng chưa thành luồng hoàn chỉnh.",
        "Lý do thực hiện chưa gắn với tiêu chí thành công.",
        "Artifact rời rạc và chưa có hướng dẫn tái chạy.",
        "Hồ sơ không khẳng định các năng lực chưa được chứng minh.",
    ),
    CaseDesign(
        SyntheticScenario.LOWER_BOUNDARY,
        "last_missing",
        (20, 17, 13, 10, 8),
        "Hồ sơ gần ngưỡng dưới và thiếu một yêu cầu bắt buộc.",
        "Phần lớn năng lực có ví dụ nhưng chiều sâu chưa đồng đều.",
        "Có giải thích lựa chọn chính và một giả định chưa kiểm tra.",
        "Có bản chạy thử và ghi chú vận hành cơ bản.",
        "Thông tin tương đối rõ nhưng cần xác minh phần còn thiếu.",
    ),
    CaseDesign(
        SyntheticScenario.UPPER_BOUNDARY,
        "first_conflicting",
        (25, 21, 17, 13, 9),
        "Hồ sơ có tổng điểm cao nhưng một năng lực bắt buộc mâu thuẫn.",
        "Artifact kỹ thuật khá hoàn chỉnh ngoài điểm cần xác minh.",
        "Nêu trade-off và cách kiểm tra kết quả.",
        "Bàn giao có review, test và hướng dẫn sử dụng.",
        "Trình bày tốt nhưng chưa giải quyết được phát biểu mâu thuẫn.",
    ),
    CaseDesign(
        SyntheticScenario.CONFLICTING_CRITICAL,
        "last_unsatisfied",
        (23, 20, 16, 12, 8),
        "Hồ sơ có tổng điểm khá nhưng xác nhận một yêu cầu bắt buộc chưa đạt.",
        "Các năng lực còn lại có thực hành và đầu ra cụ thể.",
        "Nêu cách xử lý trong phạm vi đã biết và giới hạn cần hỗ trợ.",
        "Có artifact bàn giao cho phần việc đã hoàn thành.",
        "Hồ sơ minh bạch về năng lực chưa đạt.",
    ),
    CaseDesign(
        SyntheticScenario.HARD_NEGATIVE,
        "all_missing",
        (12, 10, 10, 7, 6),
        "Hồ sơ có kiến thức liên quan nhưng không có thông tin trực tiếp chứng minh yêu cầu bắt buộc.",
        "Chỉ có nội dung học tập và quan sát, chưa có sản phẩm áp dụng.",
        "Không có quyết định kỹ thuật thuộc trách nhiệm ứng viên.",
        "Không có artifact có thể kiểm tra độc lập.",
        "Không suy diễn từ tên khóa học hoặc công cụ được nhắc tới.",
    ),
    CaseDesign(
        SyntheticScenario.TRANSFERABLE,
        "all_satisfied",
        (27, 22, 18, 13, 9),
        "Hồ sơ dùng cách diễn đạt khác chuẩn nhưng có đủ thao tác và đầu ra.",
        "Chứng minh năng lực qua nhiệm vụ tương đương thay vì lặp lại từ khóa JD.",
        "Giải thích mục tiêu, cách đo và một giới hạn của giải pháp.",
        "Có source, kết quả kiểm tra và hướng dẫn tái tạo.",
        "Thông tin có cấu trúc, nhất quán và truy ngược được tới artifact.",
    ),
    CaseDesign(
        SyntheticScenario.TRANSFERABLE,
        "all_satisfied",
        (18, 14, 11, 9, 6),
        "Yêu cầu bắt buộc có tín hiệu trực tiếp nhưng mức sở hữu, chiều sâu và tác động thấp.",
        "Mỗi năng lực chỉ xuất hiện trong một bài tập nhỏ có hướng dẫn.",
        "Quyết định chủ yếu theo mẫu, chưa có so sánh hoặc kiểm chứng độc lập.",
        "Có tệp kết quả nhưng hướng dẫn bàn giao còn tối thiểu.",
        "Nêu đúng phạm vi hạn chế, tổng điểm thấp không đồng nghĩa yêu cầu bị phủ định.",
    ),
)


def _evidence(evidence_id: str, source_id: str, section: EvidenceSection, text: str) -> Evidence:
    return Evidence(
        evidence_id=evidence_id,
        source_type=EvidenceSourceType.CANDIDATE,
        section=section,
        text=text,
        location=EvidenceLocation(source_record_id=source_id),
        extraction_confidence=None,
        is_verified=False,
    )


def _statuses(design: CaseDesign, requirement_count: int) -> tuple[EvidenceStatus, ...]:
    values = [EvidenceStatus.SATISFIED] * requirement_count
    if design.status_mode == "one_missing":
        values[0] = EvidenceStatus.MISSING
    elif design.status_mode == "one_conflicting":
        values[1 % requirement_count] = EvidenceStatus.CONFLICTING
    elif design.status_mode == "one_unsatisfied":
        values[2 % requirement_count] = EvidenceStatus.UNSATISFIED
    elif design.status_mode == "all_unsatisfied":
        values = [EvidenceStatus.UNSATISFIED] * requirement_count
    elif design.status_mode == "alternating_missing":
        values = [
            EvidenceStatus.MISSING if index % 2 == 0 else EvidenceStatus.SATISFIED
            for index in range(requirement_count)
        ]
    elif design.status_mode == "last_missing":
        values[-1] = EvidenceStatus.MISSING
    elif design.status_mode == "first_conflicting":
        values[0] = EvidenceStatus.CONFLICTING
    elif design.status_mode == "last_unsatisfied":
        values[-1] = EvidenceStatus.UNSATISFIED
    elif design.status_mode == "all_missing":
        values = [EvidenceStatus.MISSING] * requirement_count
    return tuple(values)


def _review_reasons(statuses: tuple[EvidenceStatus, ...], total_score: int) -> tuple[str, ...]:
    reasons: list[str] = []
    if EvidenceStatus.MISSING in statuses:
        reasons.append("missing-critical-evidence")
    if EvidenceStatus.CONFLICTING in statuses:
        reasons.append("conflicting-critical-evidence")
    if total_score < 70 and EvidenceStatus.UNSATISFIED not in statuses:
        reasons.append("low-score-without-explicit-critical-unsatisfied")
    if total_score >= 70 and EvidenceStatus.UNSATISFIED in statuses:
        reasons.append("critical-unsatisfied-at-or-above-waitlist-threshold")
    if 68 <= total_score <= 72:
        reasons.append("lower-threshold-boundary")
    if 83 <= total_score <= 87:
        reasons.append("upper-threshold-boundary")
    return tuple(dict.fromkeys(reasons))


def _decision(statuses: tuple[EvidenceStatus, ...], total_score: int) -> ClassificationDecision:
    reasons = _review_reasons(statuses, total_score)
    if reasons:
        return ClassificationDecision.NEEDS_REVIEW
    if total_score >= 85:
        return ClassificationDecision.PASS
    if total_score >= 70:
        return ClassificationDecision.WAITLIST
    if EvidenceStatus.UNSATISFIED in statuses:
        return ClassificationDecision.REJECT
    return ClassificationDecision.NEEDS_REVIEW


def _build_profile(
    role: RoleLanguage,
    design: CaseDesign,
    sequence: int,
    job: JobProfile,
) -> tuple[CVProfile, tuple[RequirementDraftAssessment, ...]]:
    code = f"v2d-{role.code}-{sequence:02d}"
    source_id = f"source-{code}"
    context = role.project_topics[(sequence - 1) % len(role.project_topics)]
    statuses = _statuses(design, len(role.capabilities))
    evidence: list[Evidence] = []
    skills: list[Skill] = []
    project_ids: list[str] = []
    work_ids: list[str] = []
    assessments: list[RequirementDraftAssessment] = []
    evidence_sequence = 1

    def add(section: EvidenceSection, text: str) -> str:
        nonlocal evidence_sequence
        evidence_id = f"ev-{code}-{evidence_sequence:02d}"
        evidence_sequence += 1
        evidence.append(_evidence(evidence_id, source_id, section, text))
        return evidence_id

    education_id = add(
        EvidenceSection.EDUCATION,
        f"Chương trình học có bài tổng hợp về {context}; mức đóng góp phải được xác định từ các mục thực hành bên dưới.",
    )
    for index, (capability, status) in enumerate(zip(role.capabilities, statuses, strict=True)):
        linked: list[str] = []
        variant = (sequence + index) % 3
        if status in {EvidenceStatus.SATISFIED, EvidenceStatus.CONFLICTING}:
            section = (
                EvidenceSection.WORK_EXPERIENCE
                if sequence in {1, 2, 3, 11, 14} and index % 2 == 0
                else EvidenceSection.PROJECTS
            )
            positive_text = capability.positive[variant].format(context=context)
            if sequence == 15:
                positive_text = (
                    "Trong một bài tập nhỏ có hướng dẫn từng bước, "
                    f"{positive_text[0].lower()}{positive_text[1:]} "
                    "Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác."
                )
            positive_id = add(section, positive_text)
            linked.append(positive_id)
            if section is EvidenceSection.WORK_EXPERIENCE:
                work_ids.append(positive_id)
            else:
                project_ids.append(positive_id)
            if sequence % 3 == 0:
                skills.append(Skill(name=capability.skill_name, evidence_ids=(positive_id,)))
        if status in {EvidenceStatus.UNSATISFIED, EvidenceStatus.CONFLICTING}:
            negative_id = add(
                EvidenceSection.OTHER,
                capability.negative[(sequence + index) % 2].format(context=context),
            )
            linked.append(negative_id)
        if status is EvidenceStatus.MISSING:
            add(
                EvidenceSection.EDUCATION if index % 2 == 0 else EvidenceSection.OTHER,
                capability.context_only[(sequence + index) % 2].format(context=context),
            )
        rationales = {
            EvidenceStatus.SATISFIED: "Có mô tả thao tác trực tiếp thuộc đúng năng lực và gắn với đầu ra.",
            EvidenceStatus.UNSATISFIED: "Có phát biểu phủ định rõ ràng về chính năng lực đang xét.",
            EvidenceStatus.MISSING: "Chỉ có thông tin liên quan gián tiếp, không đủ xác nhận hoặc phủ định năng lực.",
            EvidenceStatus.CONFLICTING: "Có cả mô tả thực hành và phát biểu phủ định về cùng năng lực.",
        }
        assessments.append(
            RequirementDraftAssessment(
                requirement_id=capability.requirement_id,
                evidence_status=status,
                evidence_ids=tuple(linked),
                rationale=rationales[status],
            )
        )

    detail_ids = (
        add(
            EvidenceSection.PROJECTS, f"Chiều sâu kỹ thuật của {context}: {design.technical_depth}"
        ),
        add(EvidenceSection.PROJECTS, f"Lập luận trong {context}: {design.reasoning}"),
        add(EvidenceSection.PROJECTS, f"Bàn giao {context}: {design.delivery}"),
        add(EvidenceSection.OTHER, f"Cách trình bày {context}: {design.communication}"),
    )
    project_ids.extend(detail_ids[:3])
    work_experiences: tuple[WorkExperience, ...] = ()
    if work_ids:
        work_experiences = (
            WorkExperience(
                experience_id=f"experience-{code}",
                title="Thành viên kỹ thuật thực tập hoặc dự án có người hướng dẫn",
                organization_reference=f"organization-{role.code}-synthetic",
                duration_months=4 + sequence % 5,
                summary=f"Phụ trách một phần có thể kiểm tra của {context}.",
                technologies=tuple(item.name for item in skills),
                evidence_ids=tuple(work_ids),
            ),
        )
    warnings: list[QualityWarning] = []
    if EvidenceStatus.MISSING in statuses:
        warnings.append(
            QualityWarning(
                code="incomplete-critical-information",
                severity=WarningSeverity.WARNING,
                message="Ít nhất một năng lực bắt buộc chỉ có thông tin liên quan gián tiếp.",
            )
        )
    if EvidenceStatus.CONFLICTING in statuses:
        warnings.append(
            QualityWarning(
                code="conflicting-critical-information",
                severity=WarningSeverity.WARNING,
                message="Ít nhất một năng lực bắt buộc có thông tin không nhất quán.",
            )
        )
    profile = CVProfile(
        cv_profile_id=f"cv-{code}",
        candidate_reference=f"candidate-{code}",
        summary=f"{design.summary} Hồ sơ hướng tới vị trí {job.title}.",
        skills=tuple(skills),
        work_experiences=work_experiences,
        education=(
            EducationRecord(
                education_id=f"education-{code}",
                degree="Chương trình đào tạo kỹ thuật",
                field_of_study=role.field_of_study,
                institution_reference=f"institution-{role.code}-synthetic",
                evidence_ids=(education_id,),
            ),
        ),
        projects=(
            Project(
                project_id=f"project-{code}",
                title=context.capitalize(),
                summary=f"{design.technical_depth} {design.reasoning} {design.delivery}",
                technologies=tuple(item.name for item in skills),
                evidence_ids=tuple(project_ids),
            ),
        ),
        certifications=(),
        evidence=tuple(evidence),
        quality_warnings=tuple(warnings),
    )
    return profile, tuple(assessments)


def _criterion_evidence(
    profile: CVProfile,
    assessments: tuple[RequirementDraftAssessment, ...],
) -> tuple[tuple[str, ...], ...]:
    fallback = (profile.evidence[0].evidence_id,)
    mandatory = tuple(
        dict.fromkeys(evidence_id for item in assessments for evidence_id in item.evidence_ids)
    )
    technical = tuple(
        item.evidence_id
        for item in profile.evidence
        if item.section
        in {EvidenceSection.SKILLS, EvidenceSection.WORK_EXPERIENCE, EvidenceSection.PROJECTS}
    )
    project = tuple(
        item.evidence_id for item in profile.evidence if item.section is EvidenceSection.PROJECTS
    )
    role_capability = project[-3:-1] if len(project) >= 3 else project
    communication = tuple(
        item.evidence_id for item in profile.evidence if item.section is EvidenceSection.OTHER
    )
    return tuple(
        value or fallback
        for value in (mandatory, technical, role_capability, project, communication)
    )


def _build_pair(
    role: RoleLanguage,
    design: CaseDesign,
    sequence: int,
    profile: CVProfile,
    assessments: tuple[RequirementDraftAssessment, ...],
    job: JobProfile,
    rubric: ScoringRubric,
) -> SyntheticPairAnnotation:
    total = sum(design.criterion_points)
    statuses = tuple(item.evidence_status for item in assessments)
    reasons = _review_reasons(statuses, total)
    evidence_groups = _criterion_evidence(profile, assessments)
    criteria = tuple(
        CriterionDraftAssessment(
            criterion_id=criterion.criterion_id,
            awarded_points=Decimal(points),
            maximum_points=criterion.weight,
            evidence_ids=evidence_ids,
            rationale=f"Điểm nháp {points}/{int(criterion.weight)} dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận.",
        )
        for criterion, points, evidence_ids in zip(
            rubric.criteria, design.criterion_points, evidence_groups, strict=True
        )
    )
    return SyntheticPairAnnotation(
        pair_id=f"v2d-pair-{role.code}-{sequence:02d}",
        cv_profile_id=profile.cv_profile_id,
        candidate_reference=profile.candidate_reference,
        job_profile_id=job.job_profile_id,
        rubric_id=rubric.rubric_id,
        role=role.role,
        job_variant=JobVariant.STANDARD,
        scenario=design.scenario,
        dataset_tier=DatasetTier.BRONZE,
        critical_requirement_assessments=assessments,
        criterion_assessments=criteria,
        total_score=Decimal(total),
        draft_label=_decision(statuses, total),
        review_reasons=reasons,
        overall_rationale="Bản nháp được xây từ trạng thái yêu cầu và năm nhóm điểm của rubric. Nội dung này chưa phải ground truth cho đến khi được người dùng duyệt.",
        review=PendingDatasetReview(),
    )


def build_runtime_v2_development() -> tuple[
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
    pairs: list[SyntheticPairAnnotation] = []
    for role in ROLE_LANGUAGES:
        job = jobs_by_role[role.role]
        rubric = loader.load_for_job(job.job_profile_id).rubric
        critical_ids = tuple(item.requirement_id for item in job.requirements if item.is_critical)
        if critical_ids != tuple(item.requirement_id for item in role.capabilities):
            raise ValueError(f"Capability language does not match {job.job_profile_id}")
        jobs.append(job)
        rubrics.append(rubric)
        for sequence, design in enumerate(CASE_DESIGNS, start=1):
            profile, assessments = _build_profile(role, design, sequence, job)
            profiles.append(profile)
            pairs.append(_build_pair(role, design, sequence, profile, assessments, job, rubric))
    return tuple(profiles), tuple(jobs), tuple(rubrics), tuple(pairs)


def _write_json_lines(path: Path, records: Sequence[BaseModel]) -> None:
    path.write_text("\n".join(item.model_dump_json() for item in records) + "\n", encoding="utf-8")


def _review_sheet(
    profiles: tuple[CVProfile, ...],
    jobs: tuple[JobProfile, ...],
    pairs: tuple[SyntheticPairAnnotation, ...],
) -> str:
    profile_by_id = {item.cv_profile_id: item for item in profiles}
    job_by_id = {item.job_profile_id: item for item in jobs}
    lines = [
        "# Phiếu human review Development Runtime v2",
        "",
        "Tập này có 75 case Bronze. Không case nào được dùng để tuning trước khi bạn duyệt.",
        "",
        "## Tổng quan",
        "",
        "| Pair | Vai trò | Tổng | Nhãn nháp | Lý do review |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for pair in pairs:
        reasons = ", ".join(pair.review_reasons) or "Không"
        lines.append(
            f"| `{pair.pair_id}` | `{pair.role.value}` | {pair.total_score} | `{pair.draft_label.value}` | {reasons} |"
        )
    lines.extend(("", "## Chi tiết từng case", ""))
    for pair in pairs:
        profile = profile_by_id[pair.cv_profile_id]
        job = job_by_id[pair.job_profile_id]
        evidence_by_id = {item.evidence_id: item.text for item in profile.evidence}
        lines.extend(
            (
                f"### {pair.pair_id} — {job.title}",
                "",
                f"- Tổng điểm nháp: `{pair.total_score}`",
                f"- Nhãn nháp: `{pair.draft_label.value}`",
                f"- Lý do Needs Review: `{', '.join(pair.review_reasons) or 'không có'}`",
                "",
                "Trạng thái yêu cầu bắt buộc:",
                "",
                "| Requirement | Trạng thái | Thông tin được liên kết |",
                "| --- | --- | --- |",
            )
        )
        for assessment in pair.critical_requirement_assessments:
            linked = (
                "<br>".join(evidence_by_id[item] for item in assessment.evidence_ids)
                or "Không có thông tin trực tiếp"
            )
            lines.append(
                f"| `{assessment.requirement_id}` | `{assessment.evidence_status.value}` | {linked} |"
            )
        lines.extend(
            ("", "Năm nhóm điểm:", "", "| Tiêu chí | Điểm | Lý do nháp |", "| --- | ---: | --- |")
        )
        for criterion in pair.criterion_assessments:
            lines.append(
                f"| `{criterion.criterion_id}` | {criterion.awarded_points}/{criterion.maximum_points} | {criterion.rationale} |"
            )
        lines.extend(("", "Toàn bộ thông tin hồ sơ:", ""))
        for item in profile.evidence:
            lines.append(f"- `{item.evidence_id}` ({item.section.value}): {item.text}")
        lines.extend(("", "Quyết định của người duyệt: `Đồng ý / Cần sửa`", "", "Ghi chú: ", ""))
    return "\n".join(lines)


def write_runtime_v2_development(output_directory: Path = OUTPUT_DIRECTORY) -> tuple[Path, ...]:
    output_directory.mkdir(parents=True, exist_ok=True)
    profiles, jobs, rubrics, pairs = build_runtime_v2_development()
    file_records: tuple[tuple[str, Sequence[BaseModel]], ...] = (
        ("cv_profiles.jsonl", profiles),
        ("job_profiles.jsonl", jobs),
        ("rubrics.jsonl", rubrics),
        ("pairs.jsonl", pairs),
    )
    for name, records in file_records:
        _write_json_lines(output_directory / name, records)
    review_sheet_path = output_directory / "review_sheet.md"
    review_sheet_path.write_text(_review_sheet(profiles, jobs, pairs), encoding="utf-8")
    files = tuple(
        RuntimeV2FileDigest(
            path=name, sha256=file_sha256(output_directory / name), record_count=len(records)
        )
        for name, records in file_records
    ) + (
        RuntimeV2FileDigest(
            path="review_sheet.md", sha256=file_sha256(review_sheet_path), record_count=len(pairs)
        ),
    )
    manifest = RuntimeV2DevelopmentManifest(
        dataset_id="five-role-runtime-v2-development-v1",
        dataset_version="1.0.0",
        status="draft_for_human_review",
        generated_at=datetime.now().astimezone().isoformat(),
        source_runtime_configuration_set_id="five-role-runtime-v1",
        intended_runtime_configuration_set_id="five-role-runtime-v2",
        roles=tuple(DatasetRole),
        cv_profile_count=75,
        job_profile_count=5,
        rubric_count=5,
        pair_count=75,
        pair_count_per_role=15,
        tier=DatasetTier.BRONZE,
        ground_truth_status="pending_human_review",
        tuning_allowed=False,
        classifier_results_generated=False,
        llm_requests_made=False,
        prior_references=(
            RuntimeV2PriorReference(
                dataset_id="synthetic-expansion-v2-3-1",
                directory="data/synthetic_expansion/reviewed/v2_3_1",
            ),
            RuntimeV2PriorReference(
                dataset_id="stage7-five-role-test-v1", directory="data/frozen_test/stage7_v1"
            ),
        ),
        provenance=(
            "Synthetic capability-focused development data created after runtime v1 final evaluation.",
            "Stage 7 v1 case text and labels are excluded from tuning and are used only as a prior leakage source.",
            "Draft annotations require explicit human approval before development or validation use.",
        ),
        files=files,
    )
    manifest_path = output_directory / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    quality = validate_runtime_v2_development(output_directory, REPOSITORY_ROOT)
    quality_path = output_directory / "quality_report.json"
    quality_path.write_text(
        json.dumps(quality.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if not quality.passed:
        raise RuntimeError(f"Runtime v2 development QC failed: {quality.errors}")
    return tuple(output_directory / name for name, _ in file_records) + (
        review_sheet_path,
        manifest_path,
        quality_path,
    )


def main() -> None:
    paths = write_runtime_v2_development()
    label_counts = Counter(pair.draft_label for pair in build_runtime_v2_development()[3])
    print(
        json.dumps(
            {
                "files": [str(path) for path in paths],
                "label_counts": {key.value: value for key, value in label_counts.items()},
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
