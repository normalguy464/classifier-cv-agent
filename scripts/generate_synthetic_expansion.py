from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Literal, Sequence

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
    ExperienceRange,
    JobProfile,
    JobRequirement,
    Project,
    QualityWarning,
    RequirementPriority,
    RubricCriterion,
    ScoringRubric,
    SeniorityLevel,
    Skill,
    WarningSeverity,
)
from evaluation.datasets.synthetic_expansion import (
    CriterionDraftAssessment,
    DatasetRole,
    DatasetTier,
    FileDigest,
    JobVariant,
    PendingDatasetReview,
    RequirementDraftAssessment,
    SyntheticExpansionManifest,
    SyntheticPairAnnotation,
    SyntheticScenario,
    file_sha256,
    validate_synthetic_expansion,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIRECTORY = REPOSITORY_ROOT / "data" / "synthetic_expansion" / "v2"
GENERATED_AT = "2026-07-31T21:00:00+07:00"
DATASET_ID = "synthetic-cv-jd-expansion-v2"
DATASET_VERSION = "2.0.1"
MARKET_REFERENCE_VERSION = "vn-junior-market-2026-07-31-v1"
CRITERION_MAXIMUMS = (30, 25, 20, 15, 10)


@dataclass(frozen=True)
class RequirementDefinition:
    requirement_id: str
    title: str
    skill_name: str
    positive_evidence: str
    explicit_negative_evidence: str


@dataclass(frozen=True)
class PreferredDefinition:
    requirement_id: str
    title: str
    skill_name: str
    evidence: str


@dataclass(frozen=True)
class CriterionDefinition:
    criterion_id: str
    title: str
    description: str


@dataclass(frozen=True)
class RoleDefinition:
    role: DatasetRole
    code: str
    title: str
    field_of_study: str
    responsibilities: tuple[str, ...]
    requirements: tuple[RequirementDefinition, ...]
    preferred: tuple[PreferredDefinition, ...]
    criteria: tuple[CriterionDefinition, ...]
    project_title: str
    project_context: str
    reasoning_context: str
    delivery_context: str
    communication_context: str


@dataclass(frozen=True)
class VariantDefinition:
    variant: JobVariant
    code: str
    title: str
    responsibility_suffix: str
    preferred_count: int
    criterion_adjustments: tuple[int, int, int, int, int]
    ambiguous: bool


@dataclass(frozen=True)
class ScenarioDefinition:
    scenario: SyntheticScenario
    code: str
    summary: str
    status_mode: Literal["satisfied", "missing", "conflicting", "unsatisfied", "hard_negative"]
    criterion_points: tuple[int, int, int, int, int]
    preferred_count: int
    technical_detail: str
    reasoning_detail: str
    delivery_detail: str
    communication_detail: str


COMMON_CRITERION_TITLES = (
    "Yêu cầu bắt buộc",
    "Năng lực kỹ thuật chuyên môn",
    "Năng lực theo vai trò",
    "Dự án, thực tập và tác động",
    "Độ rõ ràng và khả năng kiểm tra của thông tin trong CV",
)


def criteria_for_role(
    code: str, specialization: str, capability: str
) -> tuple[CriterionDefinition, ...]:
    identifiers = (
        "mandatory-requirements",
        f"{code}-technical-specialization",
        f"{code}-role-capability",
        "projects-and-impact",
        "communication-and-evidence-quality",
    )
    descriptions = (
        "Đối chiếu riêng từng yêu cầu bắt buộc và phân biệt đạt, không đạt, thiếu và mâu thuẫn.",
        specialization,
        capability,
        "Đánh giá phạm vi đóng góp, khả năng tái tạo đầu ra và tác động phù hợp cấp junior.",
        "Đánh giá mức rõ ràng, nhất quán, khả năng kiểm tra và giới hạn được ứng viên trình bày.",
    )
    return tuple(
        CriterionDefinition(identifier, title, description)
        for identifier, title, description in zip(
            identifiers, COMMON_CRITERION_TITLES, descriptions, strict=True
        )
    )


ROLES: tuple[RoleDefinition, ...] = (
    RoleDefinition(
        role=DatasetRole.DATA_ANALYST,
        code="da",
        title="Junior Data Analyst",
        field_of_study="Phân tích dữ liệu ứng dụng",
        responsibilities=(
            "Thu thập, làm sạch, đối soát và kết hợp dữ liệu từ cơ sở dữ liệu, tệp hoặc API.",
            "Dùng SQL và Python hoặc R để phân tích chỉ số, xu hướng và nguyên nhân sai lệch.",
            "Xây dashboard có định nghĩa chỉ số nhất quán và kiểm tra chất lượng dữ liệu đầu vào.",
            "Chuyển câu hỏi nghiệp vụ thành phân tích có khuyến nghị, giả định và giới hạn rõ ràng.",
        ),
        requirements=(
            RequirementDefinition(
                "da-sql",
                "Dùng SQL ở mức trung cấp để truy vấn, tổng hợp và kiểm tra chất lượng dữ liệu.",
                "SQL",
                "Dùng nhiều JOIN, CTE, window function, CASE và truy vấn đối soát bản ghi trùng hoặc thiếu trong một dự án.",
                "Ứng viên xác nhận chưa thể viết truy vấn SQL có JOIN và tổng hợp dữ liệu.",
            ),
            RequirementDefinition(
                "da-analysis-language",
                "Dùng Python hoặc R để làm sạch, phân tích và tự động hóa tác vụ lặp lại.",
                "Python",
                "Dùng Python với pandas hoặc R để chuẩn hóa kiểu dữ liệu, xử lý missing value, phát hiện outlier và tạo phân tích có thể chạy lại.",
                "Ứng viên xác nhận chưa từng dùng Python hoặc R để xử lý dữ liệu.",
            ),
            RequirementDefinition(
                "da-bi-reporting",
                "Có thể xây dashboard hoặc báo cáo BI và định nghĩa chỉ số nhất quán.",
                "Power BI",
                "Xây dashboard Power BI, Tableau hoặc công cụ tương đương có data model, bộ lọc, drill-down và tài liệu định nghĩa KPI.",
                "Ứng viên xác nhận chưa từng xây dashboard hoặc báo cáo dữ liệu bằng bất kỳ công cụ nào.",
            ),
            RequirementDefinition(
                "da-business-analysis",
                "Có dự án hoặc thực tập phân tích end-to-end gắn với câu hỏi nghiệp vụ.",
                "End-to-end data analysis",
                "Chuyển câu hỏi nghiệp vụ thành chỉ số, kiểm tra dữ liệu, phân tích nguyên nhân, trình bày khuyến nghị và nêu giới hạn.",
                "Ứng viên xác nhận chưa từng thực hiện dự án hoặc thực tập phân tích dữ liệu có đầu ra.",
            ),
        ),
        preferred=(
            PreferredDefinition(
                "da-statistics",
                "Có thống kê ứng dụng hoặc A/B testing.",
                "Applied statistics",
                "Áp dụng phân phối, khoảng tin cậy, kiểm định giả thuyết và diễn giải effect size trên dữ liệu mẫu.",
            ),
            PreferredDefinition(
                "da-warehouse",
                "Có data warehouse, data modeling hoặc ETL/ELT.",
                "Data warehouse",
                "Mô hình hóa fact, dimension, grain và luồng incremental load cho báo cáo.",
            ),
            PreferredDefinition(
                "da-reproducibility",
                "Có Git và quy trình phân tích có thể tái tạo.",
                "Git",
                "Quản lý SQL, notebook, data dictionary và kiểm tra dữ liệu bằng Git trong dự án nhóm.",
            ),
            PreferredDefinition(
                "da-data-access",
                "Có kinh nghiệm lấy dữ liệu từ API, cloud warehouse hoặc hệ thống nghiệp vụ.",
                "Data access",
                "Kết nối API hoặc cloud warehouse, theo dõi refresh và xử lý thay đổi schema đầu vào.",
            ),
        ),
        criteria=criteria_for_role(
            "da",
            "Đánh giá SQL trung cấp, Python hoặc R, BI, làm sạch, đối soát và khả năng tái tạo phân tích.",
            "Đánh giá cách chuyển câu hỏi nghiệp vụ thành KPI, phân tích nguyên nhân, khuyến nghị và giới hạn.",
        ),
        project_title="Phân tích hoạt động bán hàng đa kênh",
        project_context="kết hợp dữ liệu đơn hàng và vận hành, viết CTE và window function, làm sạch bằng pandas rồi xây dashboard KPI",
        reasoning_context="đối soát tổng doanh thu, kiểm tra missing value và giải thích lựa chọn grain cùng định nghĩa chỉ số",
        delivery_context="bàn giao SQL, notebook, data dictionary và dashboard có hướng dẫn refresh",
        communication_context="mô tả nguồn dữ liệu, logic KPI, khuyến nghị nghiệp vụ và giới hạn suy luận",
    ),
    RoleDefinition(
        role=DatasetRole.PYTHON_BACKEND,
        code="be",
        title="Junior Python Backend Developer",
        field_of_study="Phát triển phần mềm",
        responsibilities=(
            "Phát triển REST API bằng Python với validation, xác thực và hợp đồng lỗi nhất quán.",
            "Thiết kế schema quan hệ, migration và truy vấn có xem xét index, transaction và tính toàn vẹn.",
            "Viết unit test và integration test, thực hiện code review và duy trì OpenAPI.",
            "Đóng gói dịch vụ để chạy lặp lại, theo dõi log và xử lý lỗi tích hợp cơ bản.",
        ),
        requirements=(
            RequirementDefinition(
                "be-python",
                "Có nền tảng Python dùng cho phần mềm backend có cấu trúc.",
                "Python",
                "Dùng Python với module, OOP, type hints, dependency management, validation và exception handling trong dịch vụ backend.",
                "Ứng viên xác nhận chưa từng dùng Python để xây phần mềm backend.",
            ),
            RequirementDefinition(
                "be-rest-api",
                "Có dự án REST API bằng FastAPI, Django hoặc Flask.",
                "REST API",
                "Xây REST API có phân lớp, request validation, status code, pagination, OpenAPI và xử lý lỗi bằng FastAPI, Django hoặc Flask.",
                "Ứng viên xác nhận chưa từng xây HTTP hoặc REST API.",
            ),
            RequirementDefinition(
                "be-relational-data",
                "Có SQL và thiết kế cơ sở dữ liệu quan hệ.",
                "PostgreSQL",
                "Thiết kế schema PostgreSQL, quan hệ và constraint; dùng migration, transaction, index và truy vấn có JOIN.",
                "Ứng viên xác nhận chưa thể thiết kế schema hoặc truy vấn cơ sở dữ liệu quan hệ.",
            ),
            RequirementDefinition(
                "be-testing",
                "Có kiểm thử tự động cho backend.",
                "pytest",
                "Viết unit test và integration test bằng pytest cho luồng thành công, validation, xác thực và lỗi cơ sở dữ liệu.",
                "Ứng viên xác nhận chưa từng viết hoặc chạy kiểm thử tự động cho backend.",
            ),
            RequirementDefinition(
                "be-delivery-workflow",
                "Có Git và khả năng chạy dịch vụ nhất quán bằng container.",
                "Git Docker",
                "Dùng branch, pull request và code review; đóng gói API cùng database bằng Docker Compose và cấu hình ngoài source.",
                "Ứng viên xác nhận chưa từng dùng Git và chưa thể đóng gói hoặc bàn giao cách chạy dịch vụ.",
            ),
        ),
        preferred=(
            PreferredDefinition(
                "be-async-integration",
                "Có async, cache, message queue hoặc webhook.",
                "Async integration",
                "Xử lý async I/O, webhook idempotent, Redis cache hoặc background task trong dịch vụ.",
            ),
            PreferredDefinition(
                "be-operations",
                "Có CI/CD, logging và monitoring.",
                "CI/CD",
                "Chạy lint, test và migration check trong CI; thêm structured logging, health check và metrics cơ bản.",
            ),
            PreferredDefinition(
                "be-security",
                "Có xác thực và bảo mật API cơ bản.",
                "API authentication",
                "Triển khai JWT hoặc session, phân quyền, rate limiting, secret management và kiểm tra input.",
            ),
            PreferredDefinition(
                "be-cloud-architecture",
                "Có cloud hoặc kiến thức kiến trúc dịch vụ.",
                "Cloud architecture",
                "Triển khai dịch vụ thử nghiệm lên cloud và giải thích ranh giới module, retry hoặc trade-off đồng bộ bất đồng bộ.",
            ),
        ),
        criteria=criteria_for_role(
            "be",
            "Đánh giá Python, framework, cấu trúc dịch vụ, dependency management, kiểm thử và khả năng chạy lặp lại.",
            "Đánh giá thiết kế API, schema quan hệ, transaction, validation, xác thực và quan sát lỗi.",
        ),
        project_title="Dịch vụ quản lý đơn hàng",
        project_context="xây FastAPI phân lớp, JWT, PostgreSQL migration, pagination và hợp đồng lỗi nhất quán",
        reasoning_context="giải thích schema, constraint, transaction, index, status code và chiến lược test",
        delivery_context="bàn giao Docker Compose, OpenAPI, pytest suite và pipeline lint-test",
        communication_context="mô tả endpoint, mô hình dữ liệu, quyết định bảo mật và giới hạn vận hành",
    ),
    RoleDefinition(
        role=DatasetRole.FRONTEND,
        code="fe",
        title="Junior Frontend Developer",
        field_of_study="Phát triển ứng dụng web",
        responsibilities=(
            "Xây giao diện responsive và accessible bằng React cùng TypeScript.",
            "Tích hợp API, xác thực và quản lý trạng thái loading, error, empty và cache phía client.",
            "Viết unit hoặc component test, thực hiện code review và theo dõi lỗi giao diện.",
            "Tối ưu bundle, rendering và trải nghiệm trên nhiều kích thước màn hình.",
        ),
        requirements=(
            RequirementDefinition(
                "fe-web-foundations",
                "Có nền tảng HTML, CSS, responsive design và accessibility.",
                "HTML CSS JavaScript",
                "Xây giao diện bằng semantic HTML, CSS Grid hoặc Flexbox, responsive breakpoint, form accessible và keyboard navigation.",
                "Ứng viên xác nhận chưa thể xây giao diện responsive bằng HTML và CSS.",
            ),
            RequirementDefinition(
                "fe-language",
                "Có JavaScript hiện đại và TypeScript.",
                "JavaScript TypeScript",
                "Dùng ES modules, async flow, array/object transformation và khai báo kiểu cho props, state và API response bằng TypeScript.",
                "Ứng viên xác nhận chưa từng dùng JavaScript hoặc TypeScript để phát triển ứng dụng web.",
            ),
            RequirementDefinition(
                "fe-framework",
                "Có React hoặc framework component tương đương.",
                "React",
                "Xây React component bằng Hooks, routing, form validation, composition và quản lý state phù hợp phạm vi.",
                "Ứng viên xác nhận chưa từng xây ứng dụng bằng framework frontend dựa trên component.",
            ),
            RequirementDefinition(
                "fe-api",
                "Có kinh nghiệm tích hợp API phía client.",
                "API integration",
                "Tích hợp REST API có authentication, xử lý loading, empty, retry, lỗi và hủy request khi cần.",
                "Ứng viên xác nhận chưa từng tích hợp API vào giao diện.",
            ),
            RequirementDefinition(
                "fe-testing-workflow",
                "Có Git và kiểm thử component hoặc luồng người dùng.",
                "Git Testing Library",
                "Dùng branch và pull request; viết test bằng Vitest hoặc Testing Library cho render, tương tác, lỗi API và trạng thái biên.",
                "Ứng viên xác nhận chưa từng dùng Git và chưa từng kiểm thử giao diện.",
            ),
        ),
        preferred=(
            PreferredDefinition(
                "fe-framework-advanced",
                "Có Next.js hoặc rendering phía server.",
                "Next.js",
                "Dùng routing, server rendering hoặc data fetching của Next.js và giải thích ranh giới server-client.",
            ),
            PreferredDefinition(
                "fe-performance",
                "Có web performance và accessibility.",
                "Web performance",
                "Đo bundle hoặc Core Web Vitals, áp dụng lazy loading, memoization có chủ đích và tối ưu hình ảnh.",
            ),
            PreferredDefinition(
                "fe-security-observability",
                "Có bảo mật và quan sát lỗi frontend.",
                "Frontend security",
                "Xử lý token an toàn, hiểu XSS và cookie, thêm error boundary hoặc theo dõi lỗi runtime.",
            ),
            PreferredDefinition(
                "fe-delivery",
                "Có CI/CD và triển khai frontend.",
                "Frontend CI/CD",
                "Chạy lint, type-check, test và build trong CI rồi triển khai bản preview.",
            ),
        ),
        criteria=criteria_for_role(
            "fe",
            "Đánh giá HTML, CSS, JavaScript, TypeScript, React, kiểm thử và chất lượng component.",
            "Đánh giá responsive, accessibility, API, authentication, state, performance và xử lý lỗi.",
        ),
        project_title="Giao diện quản lý khóa học",
        project_context="xây React TypeScript responsive, form validation, authentication và các trạng thái API đầy đủ",
        reasoning_context="giải thích ranh giới component, lựa chọn state, accessibility và xử lý race condition",
        delivery_context="bàn giao bản build, component test, type-check và pipeline preview",
        communication_context="mô tả luồng người dùng, quyết định UI, số đo performance và giới hạn accessibility",
    ),
    RoleDefinition(
        role=DatasetRole.QA_ENGINEER,
        code="qa",
        title="Junior QA Engineer",
        field_of_study="Kiểm thử và đảm bảo chất lượng phần mềm",
        responsibilities=(
            "Phân tích requirement và acceptance criteria để lập phạm vi, mức ưu tiên và test coverage.",
            "Thực hiện functional, regression, exploratory, API và database testing.",
            "Ghi, theo dõi và xác nhận defect với thông tin tái hiện và mức ảnh hưởng rõ ràng.",
            "Duy trì một phần automation regression và phối hợp trong quy trình Agile.",
        ),
        requirements=(
            RequirementDefinition(
                "qa-testing-foundations",
                "Hiểu STLC và áp dụng kỹ thuật thiết kế test từ requirement.",
                "Testing foundations",
                "Phân tích acceptance criteria và áp dụng equivalence partitioning, boundary value, decision table cùng risk-based prioritization.",
                "Ứng viên xác nhận chưa biết quy trình hoặc kỹ thuật kiểm thử phần mềm.",
            ),
            RequirementDefinition(
                "qa-test-cases",
                "Có thực hành test case, regression và quản lý defect.",
                "Test case design",
                "Viết test case có precondition, dữ liệu, bước chạy, expected result; lập regression checklist và bug report có severity cùng bằng chứng tái hiện.",
                "Ứng viên xác nhận chưa từng viết test case hoặc báo cáo bug.",
            ),
            RequirementDefinition(
                "qa-api-testing",
                "Có kiểm thử REST API.",
                "Postman",
                "Dùng Postman hoặc công cụ tương đương để kiểm tra method, status, schema, authentication, validation và negative cases.",
                "Ứng viên xác nhận chưa từng kiểm thử API hoặc đọc request và response HTTP.",
            ),
            RequirementDefinition(
                "qa-data-check",
                "Có thể kiểm tra dữ liệu bằng SQL.",
                "SQL",
                "Dùng SELECT, JOIN, GROUP BY và truy vấn đối soát để xác minh dữ liệu sau thao tác kiểm thử.",
                "Ứng viên xác nhận chưa thể dùng SQL để kiểm tra dữ liệu.",
            ),
            RequirementDefinition(
                "qa-automation-foundation",
                "Có nền tảng automation bằng một ngôn ngữ và framework kiểm thử.",
                "Test automation",
                "Viết một test suite nhỏ bằng Playwright, Cypress, Selenium hoặc framework tương đương, có assertion, fixture và chạy lặp lại bằng Git.",
                "Ứng viên xác nhận chưa từng viết script hoặc test tự động bằng bất kỳ ngôn ngữ nào.",
            ),
        ),
        preferred=(
            PreferredDefinition(
                "qa-ci",
                "Có tích hợp test trong CI.",
                "CI testing",
                "Chạy API hoặc UI test trong pipeline, lưu report và phân biệt test failure với environment failure.",
            ),
            PreferredDefinition(
                "qa-performance-security",
                "Có performance hoặc security testing cơ bản.",
                "Non-functional testing",
                "Tạo kịch bản tải nhỏ bằng k6 hoặc JMeter, hoặc kiểm tra rủi ro xác thực và phân quyền.",
            ),
            PreferredDefinition(
                "qa-test-management",
                "Có công cụ quản lý test và Agile workflow.",
                "Jira TestRail",
                "Theo dõi requirement, test execution và defect bằng Jira, TestRail, Zephyr hoặc công cụ tương đương.",
            ),
            PreferredDefinition(
                "qa-istqb",
                "Có kiến thức ISTQB hoặc tương đương.",
                "ISTQB",
                "Vận dụng test levels, test types và kỹ thuật theo syllabus ISTQB Foundation trong một test plan.",
            ),
        ),
        criteria=criteria_for_role(
            "qa",
            "Đánh giá STLC, thiết kế test, API, SQL, automation và khả năng duy trì regression suite.",
            "Đánh giá phân tích requirement, risk-based coverage, defect lifecycle và xác nhận bản sửa.",
        ),
        project_title="Kiểm thử hệ thống đặt lịch",
        project_context="phân tích acceptance criteria, thiết kế risk-based test, kiểm tra API và SQL rồi tự động hóa regression chính",
        reasoning_context="áp dụng boundary, decision table, negative testing và ưu tiên lỗi theo tác động",
        delivery_context="bàn giao test plan, Postman collection, automation suite, bug report và regression report",
        communication_context="mô tả expected, actual, severity, môi trường, coverage và phạm vi chưa kiểm tra",
    ),
    RoleDefinition(
        role=DatasetRole.DATA_ENGINEER,
        code="de",
        title="Junior Data Engineer",
        field_of_study="Kỹ thuật dữ liệu",
        responsibilities=(
            "Xây, lập lịch và theo dõi pipeline ETL hoặc ELT theo batch ở mức junior.",
            "Dùng Python và SQL để tích hợp nhiều nguồn, chuẩn hóa schema và tối ưu truy vấn cơ bản.",
            "Mô hình hóa dữ liệu cho warehouse, triển khai incremental load và data quality checks.",
            "Điều tra job failure, quản lý code bằng Git và bàn giao môi trường chạy có thể tái tạo.",
        ),
        requirements=(
            RequirementDefinition(
                "de-python",
                "Có Python có cấu trúc cho xử lý và tích hợp dữ liệu.",
                "Python",
                "Dùng Python với module, logging, configuration và exception handling để đọc nhiều nguồn, chuẩn hóa schema và xử lý dữ liệu lỗi.",
                "Ứng viên xác nhận chưa từng dùng Python cho xử lý dữ liệu.",
            ),
            RequirementDefinition(
                "de-sql",
                "Có SQL trung cấp và hiểu tối ưu truy vấn cơ bản.",
                "SQL",
                "Dùng CTE, nhiều JOIN, window function, execution plan hoặc index cơ bản và truy vấn kiểm tra chất lượng dữ liệu.",
                "Ứng viên xác nhận chưa có kiến thức SQL hoặc cơ sở dữ liệu quan hệ.",
            ),
            RequirementDefinition(
                "de-pipeline",
                "Có dự án pipeline ETL hoặc ELT có thể chạy lại.",
                "ETL pipeline",
                "Xây pipeline batch có extract, transform, load, incremental strategy, retry, logging và kiểm tra đầu ra.",
                "Ứng viên xác nhận chưa từng xây pipeline ETL hoặc ELT.",
            ),
            RequirementDefinition(
                "de-data-model-quality",
                "Có data modeling và data quality cho warehouse.",
                "Data modeling",
                "Xác định grain, fact, dimension, key và kiểm tra uniqueness, completeness, referential integrity trong data mart.",
                "Ứng viên xác nhận chưa từng mô hình hóa bảng hoặc kiểm tra chất lượng dữ liệu đầu ra.",
            ),
            RequirementDefinition(
                "de-delivery-workflow",
                "Có Git, Linux và container để bàn giao pipeline.",
                "Git Linux Docker",
                "Dùng branch và pull request, chạy pipeline trên Linux, đọc log và đóng gói môi trường bằng Docker Compose.",
                "Ứng viên xác nhận chưa từng dùng Git, Linux và chưa thể bàn giao môi trường chạy pipeline.",
            ),
        ),
        preferred=(
            PreferredDefinition(
                "de-airflow",
                "Có orchestration.",
                "Airflow",
                "Tạo DAG Airflow có dependency, retry, backfill, parameter và cảnh báo job failure.",
            ),
            PreferredDefinition(
                "de-cloud-warehouse",
                "Có cloud storage hoặc cloud warehouse.",
                "Cloud data platform",
                "Dùng S3, GCS, BigQuery, Redshift, Snowflake hoặc dịch vụ tương đương trong pipeline thử nghiệm.",
            ),
            PreferredDefinition(
                "de-spark",
                "Có Spark hoặc PySpark.",
                "PySpark",
                "Dùng PySpark cho transformation, partitioning, shuffle awareness và kiểm tra đầu ra phân tán.",
            ),
            PreferredDefinition(
                "de-dataops-streaming",
                "Có DataOps, streaming hoặc CDC.",
                "DataOps streaming",
                "Chạy data quality trong CI hoặc xây luồng Kafka, CDC hay streaming nhỏ có monitoring.",
            ),
        ),
        criteria=criteria_for_role(
            "de",
            "Đánh giá Python, SQL trung cấp, ETL/ELT, warehouse modeling, orchestration và môi trường chạy.",
            "Đánh giá incremental load, idempotency, data quality, retry, logging và xử lý job failure.",
        ),
        project_title="Pipeline dữ liệu giao dịch theo lô",
        project_context="xây pipeline nhiều nguồn bằng Python và SQL, incremental load vào star schema cùng data quality checks",
        reasoning_context="giải thích grain, key, idempotency, execution plan, retry và cách cách ly dữ liệu lỗi",
        delivery_context="bàn giao Docker Compose, migration, pipeline code, test dữ liệu và runbook vận hành",
        communication_context="mô tả lineage, nguồn, đích, SLA, metadata và giới hạn vận hành",
    ),
)


VARIANTS: tuple[VariantDefinition, ...] = (
    VariantDefinition(
        JobVariant.MINIMUM,
        "min",
        "Yêu cầu tối thiểu",
        "Tập trung vào năng lực cốt lõi và khả năng học hỏi.",
        1,
        (0, 1, 1, 1, 0),
        False,
    ),
    VariantDefinition(
        JobVariant.STANDARD,
        "std",
        "Yêu cầu tiêu chuẩn",
        "Kết hợp năng lực cốt lõi với quy trình làm việc nhóm.",
        2,
        (0, 0, 0, 0, 0),
        False,
    ),
    VariantDefinition(
        JobVariant.PREFERRED_HEAVY,
        "pref",
        "Nhiều yêu cầu ưu tiên",
        "Ưu tiên ứng viên có thêm công cụ nâng cao và khả năng bàn giao.",
        4,
        (0, -2, -2, -1, -1),
        False,
    ),
    VariantDefinition(
        JobVariant.AMBIGUOUS,
        "amb",
        "Mô tả cần làm rõ",
        "Mức độ thành thạo và phạm vi công việc chưa được mô tả đầy đủ.",
        1,
        (0, 0, 0, 0, -1),
        True,
    ),
    VariantDefinition(
        JobVariant.PROJECT_EQUIVALENT,
        "proj",
        "Chấp nhận dự án tương đương",
        "Dự án học tập, cá nhân hoặc thực tập có thông tin cụ thể được tính ở cấp junior.",
        3,
        (0, 1, 1, 2, 1),
        False,
    ),
)


SCENARIOS: tuple[ScenarioDefinition, ...] = (
    ScenarioDefinition(
        SyntheticScenario.STRONG,
        "strong",
        "Hồ sơ mô tả nhiều đầu ra kỹ thuật có thể kiểm tra.",
        "satisfied",
        (30, 24, 18, 14, 8),
        4,
        "Triển khai đầy đủ luồng chính, kiểm tra lỗi và đối chiếu đầu ra trên nhiều bộ mẫu.",
        "So sánh hai phương án và ghi rõ lý do lựa chọn.",
        "Sản phẩm được chạy lại độc lập và có kết quả định lượng phù hợp.",
        "Tài liệu nêu rõ đầu vào, đầu ra, quyết định và giới hạn.",
    ),
    ScenarioDefinition(
        SyntheticScenario.SOLID,
        "solid",
        "Hồ sơ có dự án hoàn chỉnh ở mức junior và thông tin nhất quán.",
        "satisfied",
        (30, 20, 16, 11, 7),
        3,
        "Hoàn thành luồng chính, xử lý hai trường hợp lỗi và kiểm tra đầu ra.",
        "Nêu mục tiêu, giả định và một phép đối chiếu độc lập.",
        "Sản phẩm có hướng dẫn chạy và dữ liệu minh họa.",
        "README mô tả phần việc cá nhân và các giới hạn chính.",
    ),
    ScenarioDefinition(
        SyntheticScenario.MODERATE,
        "moderate",
        "Hồ sơ đáp ứng phần cốt lõi nhưng phạm vi dự án còn hẹp.",
        "satisfied",
        (30, 15, 11, 7, 5),
        1,
        "Thực hiện luồng cơ bản trên một nguồn dữ liệu hoặc một chức năng chính.",
        "Nêu mục tiêu nhưng chỉ giải thích ngắn gọn phương pháp.",
        "Đầu ra chạy được cục bộ trên tập mẫu nhỏ.",
        "Tài liệu có lệnh chạy và mô tả đầu ra ở mức ngắn.",
    ),
    ScenarioDefinition(
        SyntheticScenario.MISSING_CRITICAL,
        "missing",
        "Một phần năng lực cốt lõi không được hồ sơ đề cập.",
        "missing",
        (20, 16, 12, 8, 6),
        1,
        "Các phần còn lại có thao tác kỹ thuật và kiểm tra đầu vào cơ bản.",
        "Nêu câu hỏi cần giải quyết và một giới hạn.",
        "Có bản chạy thử cùng tệp mẫu.",
        "Ghi chú rõ phần đã thực hiện nhưng thiếu một thành phần cốt lõi.",
    ),
    ScenarioDefinition(
        SyntheticScenario.CONFLICTING_CRITICAL,
        "conflict",
        "Hồ sơ có hai mô tả không nhất quán về một năng lực cốt lõi.",
        "conflicting",
        (22, 16, 12, 8, 6),
        2,
        "Có một luồng kỹ thuật hoàn chỉnh nhưng một mô tả kỹ năng mâu thuẫn.",
        "Nêu mục tiêu và cách kiểm tra sai lệch.",
        "Có đầu ra mẫu và danh sách vấn đề còn mở.",
        "Tài liệu mô tả cả phần đã làm và phát biểu chưa thống nhất.",
    ),
    ScenarioDefinition(
        SyntheticScenario.EXPLICIT_FAILURE,
        "failed",
        "Hồ sơ xác nhận chưa có một năng lực cốt lõi.",
        "unsatisfied",
        (10, 11, 8, 5, 4),
        0,
        "Chỉ thực hiện tác vụ không liên quan trực tiếp đến yêu cầu chính.",
        "Mô tả kết quả mong muốn nhưng chưa có phương pháp phù hợp.",
        "Bài tập dừng ở bản minh họa một lần.",
        "Ghi chú nêu rõ công nghệ chưa từng sử dụng.",
    ),
    ScenarioDefinition(
        SyntheticScenario.LOWER_BOUNDARY,
        "lowbd",
        "Hồ sơ có mức thông tin vừa đủ và nhạy cảm với cách chấm chi tiết.",
        "satisfied",
        (28, 12, 9, 7, 4),
        1,
        "Hoàn thành một luồng cơ bản nhưng ít kiểm tra trường hợp bất thường.",
        "Nêu mục tiêu và kết quả nhưng thiếu đối chiếu độc lập.",
        "Đầu ra có thể chạy lại trên một bộ mẫu.",
        "README có lệnh chính nhưng thiếu giải thích quyết định.",
    ),
    ScenarioDefinition(
        SyntheticScenario.UPPER_BOUNDARY,
        "upbd",
        "Hồ sơ khá tốt nhưng nằm gần mốc chuyển kết quả.",
        "satisfied",
        (30, 18, 13, 8, 6),
        2,
        "Hoàn thành luồng chính và xử lý một số lỗi thường gặp.",
        "Giải thích lựa chọn và ghi nhận một giới hạn.",
        "Có dữ liệu mẫu, đầu ra đối chiếu và hướng dẫn tái tạo.",
        "Tài liệu rõ cách chạy nhưng phần quyết định còn ngắn.",
    ),
    ScenarioDefinition(
        SyntheticScenario.TRANSFERABLE,
        "transfer",
        "Hồ sơ chuyển hướng từ lĩnh vực gần và có năng lực có thể chuyển đổi.",
        "satisfied",
        (30, 14, 12, 7, 5),
        1,
        "Áp dụng nền tảng kỹ thuật từ lĩnh vực gần vào một dự án nhỏ đúng vai trò mục tiêu.",
        "Giải thích phần kiến thức có thể chuyển đổi và phần còn phải học.",
        "Có prototype chạy được nhưng chưa qua môi trường thực tập.",
        "Tài liệu phân biệt rõ kinh nghiệm trực tiếp và kinh nghiệm tương đương.",
    ),
    ScenarioDefinition(
        SyntheticScenario.HARD_NEGATIVE,
        "hardneg",
        "Hồ sơ liệt kê nhiều công nghệ nhưng không cung cấp ngữ cảnh sử dụng.",
        "hard_negative",
        (14, 8, 5, 2, 3),
        4,
        "Danh sách kỹ năng dài nhưng không có tác vụ, dự án hoặc kết quả liên quan.",
        "Không nêu phương pháp, giả định hoặc cách kiểm tra.",
        "Không có sản phẩm hoặc đầu ra có thể tái tạo.",
        "Chỉ nêu tên công cụ và khóa học, không nêu phần việc cụ thể.",
    ),
)


def requirement_status(scenario: ScenarioDefinition, index: int) -> EvidenceStatus:
    if scenario.status_mode == "missing" and index == 0:
        return EvidenceStatus.MISSING
    if scenario.status_mode == "conflicting" and index == 1:
        return EvidenceStatus.CONFLICTING
    if scenario.status_mode == "unsatisfied" and index == 0:
        return EvidenceStatus.UNSATISFIED
    if scenario.status_mode == "hard_negative":
        return EvidenceStatus.MISSING
    return EvidenceStatus.SATISFIED


def make_evidence(
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


def build_cv_profile(role: RoleDefinition, scenario: ScenarioDefinition) -> CVProfile:
    prefix = f"{role.code}-{scenario.code}"
    cv_profile_id = f"cv-syn-{prefix}-v2"
    source_record_id = f"source-syn-{prefix}-v2"
    evidence: list[Evidence] = []
    skills: list[Skill] = []
    project_evidence_ids: list[str] = []
    education_id = f"ev-{prefix}-education"
    evidence.append(
        make_evidence(
            education_id,
            source_record_id,
            EvidenceSection.EDUCATION,
            f"Hoàn thành chương trình học định hướng {role.field_of_study} và các học phần thực hành.",
        )
    )
    for index, requirement in enumerate(role.requirements):
        status = requirement_status(scenario, index)
        positive_id = f"ev-{prefix}-req-{index + 1}"
        negative_id = f"ev-{prefix}-gap-{index + 1}"
        weak_id = f"ev-{prefix}-weak-{index + 1}"
        if scenario.status_mode == "hard_negative":
            evidence.append(
                make_evidence(
                    weak_id,
                    source_record_id,
                    EvidenceSection.SKILLS,
                    f"Tự liệt kê {requirement.skill_name} nhưng không nêu dự án, nhiệm vụ hoặc đầu ra đã thực hiện.",
                )
            )
            skills.append(Skill(name=requirement.skill_name, evidence_ids=(weak_id,)))
            continue
        if status in {EvidenceStatus.SATISFIED, EvidenceStatus.CONFLICTING}:
            evidence.append(
                make_evidence(
                    positive_id,
                    source_record_id,
                    EvidenceSection.PROJECTS,
                    requirement.positive_evidence,
                )
            )
            skills.append(Skill(name=requirement.skill_name, evidence_ids=(positive_id,)))
            project_evidence_ids.append(positive_id)
        if status in {EvidenceStatus.UNSATISFIED, EvidenceStatus.CONFLICTING}:
            evidence.append(
                make_evidence(
                    negative_id,
                    source_record_id,
                    EvidenceSection.OTHER,
                    requirement.explicit_negative_evidence,
                )
            )

    for index, preferred in enumerate(role.preferred[: scenario.preferred_count]):
        evidence_id = f"ev-{prefix}-preferred-{index + 1}"
        text = preferred.evidence
        if scenario.status_mode == "hard_negative":
            text = f"Tự liệt kê {preferred.skill_name} sau khóa học nhưng không nêu lần áp dụng."
        evidence.append(
            make_evidence(
                evidence_id,
                source_record_id,
                EvidenceSection.SKILLS
                if scenario.status_mode == "hard_negative"
                else EvidenceSection.PROJECTS,
                text,
            )
        )
        skills.append(Skill(name=preferred.skill_name, evidence_ids=(evidence_id,)))
        if scenario.status_mode != "hard_negative":
            project_evidence_ids.append(evidence_id)

    projects: tuple[Project, ...] = ()
    if scenario.status_mode != "hard_negative":
        detail_ids: list[str] = []
        detail_values = (
            (
                "technical",
                EvidenceSection.PROJECTS,
                f"Trong dự án, {role.project_context}; {scenario.technical_detail}",
            ),
            (
                "reasoning",
                EvidenceSection.PROJECTS,
                f"Cách giải quyết: {role.reasoning_context}; {scenario.reasoning_detail}",
            ),
            (
                "delivery",
                EvidenceSection.PROJECTS,
                f"Kết quả bàn giao: {role.delivery_context}; {scenario.delivery_detail}",
            ),
            (
                "communication",
                EvidenceSection.OTHER,
                f"Tài liệu: {role.communication_context}; {scenario.communication_detail}",
            ),
        )
        for suffix, section, text in detail_values:
            evidence_id = f"ev-{prefix}-{suffix}"
            evidence.append(make_evidence(evidence_id, source_record_id, section, text))
            detail_ids.append(evidence_id)
        project_evidence_ids.extend(detail_ids)
        projects = (
            Project(
                project_id=f"project-{prefix}",
                title=role.project_title,
                summary=(
                    f"{scenario.technical_detail} {scenario.reasoning_detail} "
                    f"{scenario.delivery_detail}"
                ),
                technologies=tuple(skill.name for skill in skills),
                evidence_ids=tuple(dict.fromkeys(project_evidence_ids)),
            ),
        )

    warnings: list[QualityWarning] = []
    if scenario.status_mode == "hard_negative":
        warnings.append(
            QualityWarning(
                code="keyword-only-information",
                severity=WarningSeverity.WARNING,
                message="Nhiều kỹ năng chỉ được tự liệt kê và chưa có ngữ cảnh sử dụng.",
            )
        )
    if scenario.status_mode == "missing":
        warnings.append(
            QualityWarning(
                code="incomplete-critical-information",
                severity=WarningSeverity.WARNING,
                message="Một năng lực cốt lõi không được đề cập trong hồ sơ.",
            )
        )
    if scenario.status_mode == "conflicting":
        warnings.append(
            QualityWarning(
                code="conflicting-critical-information",
                severity=WarningSeverity.WARNING,
                message="Một năng lực cốt lõi có mô tả không nhất quán.",
            )
        )
    return CVProfile(
        cv_profile_id=cv_profile_id,
        candidate_reference=f"candidate-syn-{prefix}-v2",
        summary=f"{scenario.summary} Mục tiêu nghề nghiệp là {role.title} ở cấp độ junior.",
        skills=tuple(skills),
        work_experiences=(),
        education=(
            EducationRecord(
                education_id=f"education-{prefix}",
                degree="Chương trình đào tạo kỹ thuật",
                field_of_study=role.field_of_study,
                institution_reference=f"institution-synthetic-{role.code}",
                evidence_ids=(education_id,),
            ),
        ),
        projects=projects,
        certifications=(),
        evidence=tuple(evidence),
        quality_warnings=tuple(warnings),
    )


def build_job_profile(role: RoleDefinition, variant: VariantDefinition) -> JobProfile:
    job_profile_id = f"junior-{role.role.value.replace('_', '-')}-{variant.code}-v2"
    requirements = tuple(
        JobRequirement(
            requirement_id=requirement.requirement_id,
            title=requirement.title,
            description=(
                f"{requirement.title} Mức độ cụ thể cần được HR làm rõ."
                if variant.ambiguous
                else requirement.title
            ),
            priority=RequirementPriority.REQUIRED,
            is_critical=True,
            accepted_evidence=(
                requirement.positive_evidence,
                "Dự án học tập, dự án cá nhân hoặc thực tập có ngữ cảnh cụ thể được chấp nhận.",
            ),
            missing_evidence_policy="Thiếu thông tin phải được đánh dấu missing và chuyển người phụ trách xem lại.",
            explicit_failure_policy="Chỉ đánh dấu unsatisfied khi hồ sơ có thông tin phủ định rõ ràng.",
        )
        for requirement in role.requirements
    )
    preferred = tuple(
        JobRequirement(
            requirement_id=item.requirement_id,
            title=item.title,
            description=item.title,
            priority=RequirementPriority.PREFERRED,
            is_critical=False,
            accepted_evidence=(item.evidence,),
            missing_evidence_policy="Thiếu yêu cầu ưu tiên không đồng nghĩa không đạt yêu cầu bắt buộc.",
            explicit_failure_policy="Yêu cầu ưu tiên không tạo quyết định Reject trực tiếp.",
        )
        for item in role.preferred[: variant.preferred_count]
    )
    return JobProfile(
        job_profile_id=job_profile_id,
        title=f"{role.title} - {variant.title}",
        language="vi",
        seniority=SeniorityLevel.JUNIOR,
        experience_range=ExperienceRange(
            minimum_years=0,
            maximum_years=2,
            formal_work_experience_required=False,
        ),
        responsibilities=role.responsibilities + (variant.responsibility_suffix,),
        requirements=requirements + preferred,
    )


def build_rubric(
    role: RoleDefinition,
    variant: VariantDefinition,
    job: JobProfile,
) -> ScoringRubric:
    rubric_id = f"{role.code}-{variant.code}-rubric-v2"
    criteria = tuple(
        RubricCriterion(
            criterion_id=definition.criterion_id,
            title=definition.title,
            description=definition.description,
            weight=Decimal(maximum),
        )
        for definition, maximum in zip(role.criteria, CRITERION_MAXIMUMS, strict=True)
    )
    return ScoringRubric(
        rubric_id=rubric_id,
        rubric_version="2.0.1",
        job_profile_id=job.job_profile_id,
        criteria=criteria,
        critical_requirement_ids=tuple(
            requirement.requirement_id for requirement in role.requirements
        ),
    )


def evidence_ids_for_requirement(
    role: RoleDefinition,
    scenario: ScenarioDefinition,
    index: int,
    status: EvidenceStatus,
) -> tuple[str, ...]:
    prefix = f"{role.code}-{scenario.code}"
    if scenario.status_mode == "hard_negative":
        return (f"ev-{prefix}-weak-{index + 1}",)
    if status is EvidenceStatus.MISSING:
        return ()
    if status is EvidenceStatus.SATISFIED:
        return (f"ev-{prefix}-req-{index + 1}",)
    if status is EvidenceStatus.UNSATISFIED:
        return (f"ev-{prefix}-gap-{index + 1}",)
    return (f"ev-{prefix}-req-{index + 1}", f"ev-{prefix}-gap-{index + 1}")


def requirement_rationale(requirement_id: str, status: EvidenceStatus) -> str:
    values = {
        EvidenceStatus.SATISFIED: f"{requirement_id} có thông tin thực hành trực tiếp trong dự án.",
        EvidenceStatus.UNSATISFIED: f"{requirement_id} có xác nhận phủ định rõ ràng trong hồ sơ.",
        EvidenceStatus.MISSING: f"{requirement_id} chưa có thông tin thực hành đủ để xác nhận.",
        EvidenceStatus.CONFLICTING: f"{requirement_id} có thông tin thực hành và thông tin phủ định mâu thuẫn.",
    }
    return values[status]


def adjusted_points(
    scenario: ScenarioDefinition,
    variant: VariantDefinition,
) -> tuple[int, int, int, int, int]:
    values = tuple(
        min(maximum, max(0, point + adjustment))
        for point, adjustment, maximum in zip(
            scenario.criterion_points,
            variant.criterion_adjustments,
            CRITERION_MAXIMUMS,
            strict=True,
        )
    )
    return values[0], values[1], values[2], values[3], values[4]


def review_reasons(
    statuses: tuple[EvidenceStatus, ...],
    scenario: ScenarioDefinition,
    variant: VariantDefinition,
    total_score: int,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if EvidenceStatus.MISSING in statuses:
        reasons.append("missing-critical-evidence")
    if EvidenceStatus.CONFLICTING in statuses:
        reasons.append("conflicting-critical-evidence")
    if variant.ambiguous:
        reasons.append("ambiguous-job-description")
    if scenario.scenario is SyntheticScenario.TRANSFERABLE:
        reasons.append("transferable-skills")
    if 58 <= total_score <= 62:
        reasons.append("lower-threshold-boundary")
    if 73 <= total_score <= 77:
        reasons.append("upper-threshold-boundary")
    if EvidenceStatus.UNSATISFIED in statuses and total_score >= 60:
        reasons.append("critical-unsatisfied-at-or-above-waitlist-threshold")
    if total_score < 60 and EvidenceStatus.UNSATISFIED not in statuses:
        reasons.append("low-score-without-explicit-critical-unsatisfied")
    return tuple(dict.fromkeys(reasons))


def draft_decision(
    statuses: tuple[EvidenceStatus, ...],
    total_score: int,
    reasons: tuple[str, ...],
) -> ClassificationDecision:
    if reasons:
        return ClassificationDecision.NEEDS_REVIEW
    if EvidenceStatus.UNSATISFIED in statuses and total_score < 60:
        return ClassificationDecision.REJECT
    if total_score >= 75:
        return ClassificationDecision.PASS
    if total_score >= 60:
        return ClassificationDecision.WAITLIST
    return ClassificationDecision.NEEDS_REVIEW


def criterion_evidence_ids(
    profile: CVProfile,
    requirement_assessments: tuple[RequirementDraftAssessment, ...],
) -> tuple[tuple[str, ...], ...]:
    mandatory = tuple(
        dict.fromkeys(
            evidence_id
            for assessment in requirement_assessments
            for evidence_id in assessment.evidence_ids
        )
    )
    technical = tuple(
        evidence.evidence_id
        for evidence in profile.evidence
        if evidence.section in {EvidenceSection.SKILLS, EvidenceSection.PROJECTS}
    )
    role_capability = tuple(
        evidence.evidence_id
        for evidence in profile.evidence
        if "reasoning" in evidence.evidence_id or "technical" in evidence.evidence_id
    )
    projects = tuple(
        dict.fromkeys(
            evidence_id for project in profile.projects for evidence_id in project.evidence_ids
        )
    )
    communication = tuple(
        evidence.evidence_id
        for evidence in profile.evidence
        if evidence.section is EvidenceSection.OTHER
    )
    fallback = tuple(evidence.evidence_id for evidence in profile.evidence[:1])
    return tuple(
        value or fallback
        for value in (mandatory, technical, role_capability, projects, communication)
    )


def build_pair_annotation(
    role: RoleDefinition,
    scenario: ScenarioDefinition,
    variant: VariantDefinition,
    profile: CVProfile,
    job: JobProfile,
    rubric: ScoringRubric,
) -> SyntheticPairAnnotation:
    statuses = tuple(requirement_status(scenario, index) for index in range(len(role.requirements)))
    requirement_assessments = tuple(
        RequirementDraftAssessment(
            requirement_id=requirement.requirement_id,
            evidence_status=status,
            evidence_ids=evidence_ids_for_requirement(role, scenario, index, status),
            rationale=requirement_rationale(requirement.requirement_id, status),
        )
        for index, (requirement, status) in enumerate(zip(role.requirements, statuses, strict=True))
    )
    points = adjusted_points(scenario, variant)
    total_score = sum(points)
    reasons = review_reasons(statuses, scenario, variant, total_score)
    decision = draft_decision(statuses, total_score, reasons)
    evidence_by_criterion = criterion_evidence_ids(profile, requirement_assessments)
    criterion_assessments = tuple(
        CriterionDraftAssessment(
            criterion_id=criterion.criterion_id,
            awarded_points=Decimal(point),
            maximum_points=criterion.weight,
            evidence_ids=evidence_ids,
            rationale=(
                f"{criterion.title} được chấm từ thông tin liên kết trong hồ sơ; "
                f"mức điểm {point}/{int(criterion.weight)} phản ánh phạm vi của kịch bản "
                f"{scenario.scenario.value} đối với JD {variant.variant.value}."
            ),
        )
        for criterion, point, evidence_ids in zip(
            rubric.criteria, points, evidence_by_criterion, strict=True
        )
    )
    return SyntheticPairAnnotation(
        pair_id=f"pair-{role.code}-{scenario.code}-{variant.code}",
        cv_profile_id=profile.cv_profile_id,
        candidate_reference=profile.candidate_reference,
        job_profile_id=job.job_profile_id,
        rubric_id=rubric.rubric_id,
        role=role.role,
        job_variant=variant.variant,
        scenario=scenario.scenario,
        critical_requirement_assessments=requirement_assessments,
        criterion_assessments=criterion_assessments,
        total_score=Decimal(total_score),
        draft_label=decision,
        review_reasons=reasons,
        overall_rationale=(
            f"Hồ sơ {profile.cv_profile_id} được đối chiếu với {job.job_profile_id}; "
            f"các trạng thái yêu cầu gồm {', '.join(status.value for status in statuses)}. "
            "Đây là đề xuất synthetic chờ người đánh giá xác nhận, không phải ground truth."
        ),
        review=PendingDatasetReview(),
    )


def build_dataset() -> tuple[
    tuple[CVProfile, ...],
    tuple[JobProfile, ...],
    tuple[ScoringRubric, ...],
    tuple[SyntheticPairAnnotation, ...],
]:
    profiles: list[CVProfile] = []
    jobs: list[JobProfile] = []
    rubrics: list[ScoringRubric] = []
    annotations: list[SyntheticPairAnnotation] = []
    for role in ROLES:
        role_profiles = tuple(build_cv_profile(role, scenario) for scenario in SCENARIOS)
        profiles.extend(role_profiles)
        for variant in VARIANTS:
            job = build_job_profile(role, variant)
            rubric = build_rubric(role, variant, job)
            jobs.append(job)
            rubrics.append(rubric)
            for scenario, profile in zip(SCENARIOS, role_profiles, strict=True):
                annotations.append(
                    build_pair_annotation(role, scenario, variant, profile, job, rubric)
                )
    return tuple(profiles), tuple(jobs), tuple(rubrics), tuple(annotations)


def write_json_lines(path: Path, records: Sequence[BaseModel]) -> None:
    values: list[str] = []
    for record in records:
        payload = record.model_dump(mode="json")
        values.append(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    path.write_text("\n".join(values) + "\n", encoding="utf-8")


def write_dataset(output_directory: Path = OUTPUT_DIRECTORY) -> tuple[Path, ...]:
    profiles, jobs, rubrics, annotations = build_dataset()
    output_directory.mkdir(parents=True, exist_ok=True)
    paths = (
        output_directory / "cv_profiles.jsonl",
        output_directory / "job_profiles.jsonl",
        output_directory / "rubrics.jsonl",
        output_directory / "pairs.jsonl",
    )
    write_json_lines(paths[0], profiles)
    write_json_lines(paths[1], jobs)
    write_json_lines(paths[2], rubrics)
    write_json_lines(paths[3], annotations)
    counts = (len(profiles), len(jobs), len(rubrics), len(annotations))
    manifest = SyntheticExpansionManifest(
        schema_version="1.1.0",
        dataset_id=DATASET_ID,
        dataset_version=DATASET_VERSION,
        status="draft_for_human_review",
        generated_at=GENERATED_AT,
        cv_schema_version="1.0.0",
        job_profile_schema_version="1.0.0",
        rubric_schema_version="1.0.0",
        configuration_version="1.1.0",
        roles=tuple(role.role for role in ROLES),
        job_variants=tuple(variant.variant for variant in VARIANTS),
        scenarios=tuple(scenario.scenario for scenario in SCENARIOS),
        cv_profile_count=len(profiles),
        job_profile_count=len(jobs),
        rubric_count=len(rubrics),
        pair_count=len(annotations),
        tier_counts={DatasetTier.BRONZE: len(annotations)},
        human_reviewed_pair_count=0,
        split_status="unassigned",
        frozen_test_created=False,
        market_reference_version=MARKET_REFERENCE_VERSION,
        provenance=(
            "Synthetic content authored for this repository; no external CV or job posting text was copied verbatim.",
            "Role requirements were synthesized from current Vietnamese employer postings reviewed on 2026-07-31 and documented in docs/junior_market_requirements_v1.md.",
            "O*NET and ESCO were retained as occupation-taxonomy references rather than sources of CV-JD labels.",
            "The Claude reference directory informed workflow design only; its records and labels were not imported.",
        ),
        files=tuple(
            FileDigest(path=path.name, sha256=file_sha256(path), record_count=count)
            for path, count in zip(paths, counts, strict=True)
        ),
    )
    manifest_path = output_directory / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report = validate_synthetic_expansion(output_directory)
    report_path = output_directory / "quality_report.json"
    report_path.write_text(
        json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if not report.passed:
        raise ValueError("Generated dataset failed quality validation")
    return paths + (manifest_path, report_path)


def main() -> None:
    for path in write_dataset():
        print(path)


if __name__ == "__main__":
    main()
