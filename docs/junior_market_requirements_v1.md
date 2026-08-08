# Đối chiếu yêu cầu Junior trên thị trường Việt Nam

## Thông tin phiên bản

- Mã tham chiếu: `vn-junior-market-2026-07-31-v1`.
- Ngày đối chiếu: 31/07/2026.
- Phạm vi: năm vị trí Junior hoặc Fresher–Junior, định hướng 0–2 năm kinh nghiệm tại Việt Nam.
- Mục đích: hiệu chỉnh độ khó cho Job Profile và CV synthetic trong `synthetic-cv-jd-expansion-v2`.
- Không phải mục đích: sao chép nguyên văn tin tuyển dụng, tạo ground truth, hoặc chứng minh mọi doanh nghiệp đều có cùng yêu cầu.

## Phương pháp

Các yêu cầu được tổng hợp từ tin tuyển dụng trực tiếp hoặc trang nghề nghiệp đang hiển thị tại thời điểm đối chiếu. Một năng lực chỉ được đưa vào nhóm bắt buộc khi nó xuất hiện lặp lại, gắn trực tiếp với công việc hằng ngày và có thể được ứng viên 0–2 năm thể hiện qua dự án, thực tập hoặc kinh nghiệm chính thức.

Những công nghệ phụ thuộc mạnh vào doanh nghiệp, hạ tầng hoặc vị trí có phạm vi cao hơn Junior được giữ ở nhóm ưu tiên. Yêu cầu bằng cấp, GPA, tuổi, giới tính, tình trạng hôn nhân, quê quán và thuộc tính nhạy cảm không được dùng để chấm điểm. Số năm kinh nghiệm không được thay thế cho thông tin thực hành cụ thể.

Nội dung dataset là câu chữ mới do dự án tự viết. Không có CV, JD hoặc nhãn bên ngoài nào được nhập vào dataset.

## Nguồn đã đối chiếu

| Vị trí | Nguồn | Tín hiệu yêu cầu được ghi nhận |
| --- | --- | --- |
| Data Analyst | [Home Credit Vietnam – Home Racer Data Analyst](https://career.homecredit.vn/vn/job/home-racer-data-analyst/) | SQL, Python hoặc ngôn ngữ lập trình, thống kê, dashboard hoặc model bằng SQL/Python/Power BI, phối hợp với bộ phận nghiệp vụ |
| Data Analyst | [Vexere – Junior Data Analyst](https://careers.vexere.com/jobs/junior-data-analyst/) | SQL mạnh, visualization, data lake hoặc GCP, chuyển dữ liệu thành insight có thể hành động |
| Data Analyst | [ITviec – Data Analyst SQL/Python/Power BI/Tableau/API](https://itviec.com/it-jobs/data-analyst-sql-python-powerbi-tableau-api-cong-ty-tnhh-dich-vu-tiep-van-toan-cau-1617) | Làm sạch và validation, ETL đơn giản, KPI vận hành, SQL, Python, BI và API |
| Python Backend | [ITviec – Junior Backend Developer Python APIs](https://itviec.com/viec-lam-it/junior-backend-developer-python-apis-qualityrealty-quality-realty-b-v-2250?lab_feature=similar_job) | FastAPI/Flask/Django, PostgreSQL, API ngoài, webhook, migration, logging, test, OpenAPI; Docker, async, JWT và rate limiting là lợi thế |
| Python Backend | [ITviec – Junior/Senior Python Backend Engineer](https://itviec.com/viec-lam-it/junior-senior-python-backend-engineer-django-mysql-gon-tech-0345) | Python, Django/FastAPI, OOP, database và tối ưu query, REST, Git, Docker, CI/CD và pytest; các kiến trúc nâng cao xuất hiện ở tin ghép nhiều cấp độ |
| Frontend | [VNG – Frontend Engineer VNGGames](https://career.vng.com.vn/tim-kiem-viec-lam/chi-tiet/6726-frontend-engineer-vnggames-vi?isShowForm=1) | React, TypeScript, browser/rendering, unit test, frontend security, reliability và operational health |
| Frontend | [CareerViet – Front End Junior](https://careerviet.vn/en/search-job/chuyen-vien-lap-trinh-front-end-junior.35C66F79.html) | 0,5–2 năm, HTML/CSS/JavaScript, framework hiện đại, Git, API, responsive; TypeScript là lợi thế |
| Frontend | [Icetea Software – Frontend Developer Junior](https://careers.iceteasoftware.com/jobs/frontend-developer-junior) | 0–2 năm, framework frontend và Git; TypeScript cùng testing là lợi thế |
| QA Engineer | [ITviec – Junior QA Engineer AvePoint](https://itviec.com/it-jobs/junior-qa-engineer-tester-sql-avepoint-vietnam-company-limited-2550) | Requirement discovery, test case, black-box, functional và regression testing; chấp nhận Fresher |
| QA Engineer | [ITviec – Senior/Junior QA Engineer Panasonic](https://itviec.com/it-jobs/senior-junior-qa-engineer-manual-panasonic-vietnam-group-panasonic-r-d-center-vietnam-prdcv-5500) | Requirement, UAT, functional/regression, bug lifecycle, SQL, Agile; automation và scripting là lợi thế |
| QA Engineer | [ITviec – Junior/Senior/Leader QA Tester](https://itviec.com/viec-lam-it/junior-senior-leader-qa-tester-erp-api-sql-nosql-ai-di-4555) | Requirement analysis, test plan, API/integration, Postman/Swagger, SQL, Jira, automation và CI trong tin ghép nhiều cấp độ |
| Data Engineer | [ITviec – Junior Data Engineer PVcomBank](https://itviec.com/it-jobs/cv-phat-trien-tich-hop-du-lieu-junior-data-engineer-pvcombank-3317?lab_feature=employer_job) | SQL nâng cao, Python/Shell/Scala, ETL/ELT, warehouse/lake, data modeling, data quality, CI/CD; Spark, Airflow, dbt, cloud và streaming theo môi trường |
| Data Engineer | [Indeed – Fresher/Junior Data Engineer](https://jobs.vn.indeed.com/viewjob?jk=499fb236279680b1) | SQL, Python, ETL/ELT, data warehouse và hỗ trợ Airflow DAG |

O*NET và ESCO vẫn được dùng để kiểm tra tên nghề và quan hệ nghề–kỹ năng ở mức taxonomy:

- [O*NET Database](https://www.onetcenter.org/database.html).
- [ESCO downloadable datasets](https://esco.ec.europa.eu/en/structure-esco-downloadable-datasets).

## Quyết định cho từng vị trí

### Junior Data Analyst

Bắt buộc:

- SQL trung cấp: nhiều `JOIN`, `CTE`, `window function`, `CASE` và truy vấn đối soát chất lượng.
- Python hoặc R để làm sạch, phân tích và tự động hóa tác vụ lặp lại.
- Dashboard hoặc BI có data model, bộ lọc và định nghĩa KPI.
- Một dự án hoặc thực tập phân tích end-to-end: câu hỏi nghiệp vụ, kiểm tra dữ liệu, phân tích, khuyến nghị và giới hạn.

Ưu tiên:

- Thống kê ứng dụng hoặc A/B testing.
- Data warehouse, data modeling hoặc ETL/ELT.
- Git và quy trình phân tích có thể tái tạo.
- API, cloud warehouse hoặc hệ thống nghiệp vụ.

### Junior Python Backend Developer

Bắt buộc:

- Python có cấu trúc, type hints, dependency management, validation và exception handling.
- REST API bằng FastAPI, Django hoặc Flask, có phân lớp, validation, status code và OpenAPI.
- SQL, schema quan hệ, constraint, migration, transaction và index cơ bản.
- Unit test và integration test cho cả luồng thành công và lỗi.
- Git, pull request, code review và môi trường chạy bằng container.

Ưu tiên:

- Async I/O, webhook, cache, message queue hoặc background task.
- CI/CD, structured logging, health check và monitoring.
- Authentication, authorization, rate limiting và secret management.
- Cloud hoặc kiến thức kiến trúc dịch vụ.

### Junior Frontend Developer

Bắt buộc:

- Semantic HTML, CSS responsive và accessibility cơ bản.
- JavaScript hiện đại và TypeScript cho props, state cùng API contract.
- React hoặc framework component tương đương, routing, form và state.
- Tích hợp API có authentication cùng trạng thái loading, empty và error.
- Git và unit hoặc component testing.

Ưu tiên:

- Next.js hoặc server-side rendering.
- Đo và tối ưu web performance.
- Frontend security và theo dõi lỗi runtime.
- CI/CD và preview deployment.

### Junior QA Engineer

Dataset v2 mô tả QA Engineer đa năng, không phải vị trí Manual Tester thuần túy.

Bắt buộc:

- STLC, phân tích requirement và kỹ thuật thiết kế test.
- Test case, regression và defect lifecycle.
- Kiểm thử REST API gồm authentication, validation và negative cases.
- SQL để đối soát dữ liệu.
- Automation foundation bằng một ngôn ngữ và framework kiểm thử.

Ưu tiên:

- Chạy test trong CI.
- Performance hoặc security testing cơ bản.
- Jira, TestRail, Zephyr hoặc công cụ quản lý tương đương.
- Vận dụng kiến thức ISTQB.

### Junior Data Engineer

Bắt buộc:

- Python có module, logging, configuration và xử lý lỗi.
- SQL trung cấp gồm CTE, window function và tối ưu cơ bản.
- Pipeline ETL/ELT có incremental load, retry và kiểm tra đầu ra.
- Data modeling cùng data quality cho warehouse.
- Git, Linux và container để bàn giao môi trường chạy.

Ưu tiên:

- Airflow hoặc orchestration tương đương.
- Cloud storage hoặc cloud warehouse.
- Spark hoặc xử lý dữ liệu phân tán.
- DataOps, streaming hoặc CDC.

## Giới hạn của lần đối chiếu

- Tin tuyển dụng thay đổi theo thời gian và có thể bị gỡ khỏi nguồn.
- Một số tin ghép Junior với Senior nên chỉ các năng lực phù hợp 0–2 năm mới được đưa vào nhóm bắt buộc.
- Tin tuyển dụng thường mô tả ứng viên lý tưởng và có thể nhiều hơn công việc thực tế; việc xuất hiện trong một tin không đủ để trở thành điều kiện loại.
- Dataset vẫn là synthetic và cần người có chuyên môn duyệt rubric, JD, CV persona và draft annotation.
- Đối chiếu thị trường không thay thế validation bằng CV thực đã đồng ý sử dụng hoặc được ẩn danh không thể đảo ngược.
