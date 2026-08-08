# Stage 1 Review: Requirements and Rubric v1

## Trạng thái

Gate 1 đã được người dùng phê duyệt ngày 2026-07-25. Requirements, rubric, trọng số và ngưỡng v1 được chấp nhận để dùng cho pilot; việc tuning và đóng băng cấu hình cuối vẫn diễn ra ở Stage 6.

## Phạm vi đã đề xuất

Hai Job Profile nhắm tới ứng viên Junior có 0-2 năm kinh nghiệm. Thực tập, dự án học tập và dự án cá nhân có evidence có thể kiểm tra được chấp nhận thay cho kinh nghiệm chính thức. Việc không nêu một kỹ năng trong CV là `missing`, không phải `unsatisfied`.

### Junior Data Analyst

- Bắt buộc: SQL; Python hoặc R cho phân tích dữ liệu; ít nhất một dự án hoặc thực tập phân tích dữ liệu.
- Ưu tiên: Power BI/Tableau/Looker Studio; thống kê ứng dụng hoặc A/B testing; data warehouse/dbt/ETL; diễn giải kết quả cho người không chuyên kỹ thuật.
- Artifact: `configs/job_profiles/junior_data_analyst.yaml`
- Rubric: `configs/rubrics/junior_data_analyst_rubric.yaml`

### Junior Python Backend Developer

- Bắt buộc: Python; dự án hoặc thực tập xây HTTP/REST API; cơ sở dữ liệu quan hệ và SQL; Git.
- Ưu tiên: testing; Docker; async; CI/CD, logging, Redis, caching hoặc queue; xác thực và bảo mật API cơ bản.
- Artifact: `configs/job_profiles/junior_python_backend_developer.yaml`
- Rubric: `configs/rubrics/junior_python_backend_developer_rubric.yaml`

## Rubric chung

| Tiêu chí | Trọng số |
| --- | ---: |
| Requirements bắt buộc | 30 |
| Năng lực kỹ thuật chuyên môn | 25 |
| Năng lực theo vai trò | 20 |
| Dự án/thực tập và tác động | 15 |
| Giao tiếp, tính rõ ràng của evidence | 10 |
| Tổng | 100 |

Mỗi rubric chỉ đánh giá năng lực và evidence. Tuổi, giới tính, dân tộc, tôn giáo, tình trạng hôn nhân, khuyết tật và quê quán bị loại khỏi quyết định chấm điểm.

## Cấu hình scoring

| Thành phần | Trọng số |
| --- | ---: |
| L1 deterministic rules | 45% |
| L2 section-level semantic matching | 25% |
| L3 evidence-grounded reasoning | 30% |
| Tổng | 100% |

- `Pass`: final score từ 75 trở lên, trừ khi một quy tắc `Needs Review` được ưu tiên áp dụng.
- `Waitlist`: final score từ 60 đến dưới 75, trừ khi một quy tắc `Needs Review` được ưu tiên áp dụng.
- `Reject`: final score dưới 60 và có evidence rõ ràng cho ít nhất một yêu cầu bắt buộc không đạt.
- `Needs Review`: evidence bắt buộc missing hoặc conflicting; output L2/L3 không hợp lệ hoặc không có; chênh lệch lớn nhất giữa L1/L2/L3 từ 25 điểm; final score 58–62 hoặc 73–77.
- Scoring configuration `1.1.0` bổ sung `Needs Review` khi final score dưới 60 nhưng chưa có thông tin rõ để `Reject`, hoặc khi một yêu cầu bắt buộc `unsatisfied` nhưng final score từ 60 trở lên.

Không được tự động `Reject` chỉ vì evidence còn thiếu hoặc mâu thuẫn.

## Model strategy

- L2 dùng `intfloat/multilingual-e5-base` chạy cục bộ, đối chiếu theo từng section thay vì embed toàn bộ CV.
- L3 lấy provider, model và API key từ biến môi trường; không có secret trong repository.
- `deterministic-evidence-scorer-v1` chỉ phục vụ test, contract test và demo offline.

## Xác nhận cần có từ người dùng

Xác nhận hoặc yêu cầu sửa từng nội dung sau:

1. Hai vị trí và phạm vi Junior 0–2 năm.
2. Mỗi yêu cầu bắt buộc và yêu cầu ưu tiên của từng vị trí.
3. Năm tiêu chí rubric cùng trọng số 30/25/20/15/10.
4. Trọng số L1/L2/L3 là 45/25/30 và các ngưỡng 75/60.
5. Chính sách ưu tiên `Needs Review` và điều kiện `Reject` dựa trên evidence rõ ràng.
6. Chiến lược embedding cục bộ, LLM cấu hình qua biến môi trường và fake xác định cho test/demo offline.

Người dùng đã chấp thuận các nội dung trên và cho phép bắt đầu Stage 2. Mọi thay đổi nghiệp vụ không tương thích sau mốc này phải được ghi version và đưa ra review lại.
