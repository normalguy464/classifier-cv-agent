# Hướng dẫn review synthetic-cv-jd-expansion-v2

## Mục tiêu của phiên bản v2

Phiên bản v2 thay thế v1 cho vòng review mở rộng bằng mức Junior cạnh tranh hơn. V1 được giữ nguyên để truy vết nhưng không nên tiếp tục được duyệt hoặc đưa vào split mới.

Nội dung v2 được viết lại sau khi đối chiếu các tin tuyển dụng Việt Nam đang hiển thị ngày 31/07/2026. Nguồn, cách tổng hợp và giới hạn nằm trong `docs/junior_market_requirements_v1.md`.

## Phạm vi

| Thành phần | Số lượng |
| --- | ---: |
| Vị trí | 5 |
| CVProfile synthetic | 50 |
| Job Profile/JD | 25 |
| Rubric | 25 |
| Cặp CV-JD | 250 |
| Cặp mỗi vị trí | 50 |

Mỗi vị trí có 10 CV persona và 5 biến thể JD. Mỗi CV được ghép với toàn bộ 5 JD cùng vị trí để tạo 50 cặp mỗi vai trò.

## Khác biệt chính so với v1

| Vị trí | V1 | V2 |
| --- | --- | --- |
| Data Analyst | SQL, Python/R và dự án phân tích là cốt lõi | Thêm BI/KPI vào cốt lõi; yêu cầu SQL trung cấp, data quality và phân tích end-to-end |
| Python Backend | Python, REST, SQL và Git là cốt lõi | Thêm automated testing và container delivery; tăng chiều sâu schema, transaction, OpenAPI và error handling |
| Frontend | HTML/CSS/JS, framework, API và Git là cốt lõi | TypeScript, accessibility, authentication, testing và trạng thái lỗi trở thành cốt lõi |
| QA Engineer | Manual testing và SQL là cốt lõi; API/automation là ưu tiên | Chuyển thành QA đa năng: API, SQL và automation foundation đều là cốt lõi |
| Data Engineer | Python, SQL, pipeline và Git/Linux là cốt lõi | Thêm data modeling, data quality, incremental load và container delivery vào cốt lõi |

Trọng số rubric vẫn là `30/25/20/15/10`. Ngưỡng và chính sách bảo vệ ứng viên không thay đổi. Dự án học tập, cá nhân hoặc thực tập có thông tin cụ thể vẫn được chấp nhận cho cấp Junior 0–2 năm.

## Những gì cần duyệt

### 1. Mức yêu cầu theo vị trí

Duyệt bảng bắt buộc và ưu tiên trong `docs/junior_market_requirements_v1.md`.

Đạt khi:

- yêu cầu bắt buộc là năng lực thực sự cần cho công việc Junior, không chỉ là công cụ riêng của một doanh nghiệp;
- một ứng viên 0–2 năm có thể chứng minh bằng dự án, thực tập hoặc việc làm;
- yêu cầu ưu tiên tạo khác biệt nhưng không trực tiếp gây Reject;
- không dùng bằng cấp, GPA, số năm cứng hoặc thuộc tính nhạy cảm để thay cho năng lực.

### 2. Năm JD `standard`

Trong `data/synthetic_expansion/v2/job_profiles.jsonl`, tìm các ID chứa `-std-v2`.

Đạt khi:

- trách nhiệm và yêu cầu phản ánh đúng phạm vi công việc;
- loại thông tin được chấp nhận đủ cụ thể để đánh giá;
- `missing` khác `unsatisfied`;
- không có yêu cầu Senior bị đặt thành bắt buộc cho mọi Junior.

### 3. Năm mươi CV persona

Trong `data/synthetic_expansion/v2/cv_profiles.jsonl`, ưu tiên đọc 5 CV `strong`, 5 `solid`, 5 `moderate`, 5 `explicit_failure` và 5 `hard_negative` trước.

Đạt khi:

- CV mạnh thể hiện kỹ thuật, cách giải quyết, đầu ra và giới hạn chứ không chỉ liệt kê từ khóa;
- CV trung bình có thiếu chiều sâu thực tế, không bị làm yếu bằng lỗi vô lý;
- CV không phù hợp có thông tin phủ định hoặc thiếu thật sự, không bị hạ điểm bởi thuộc tính cá nhân;
- văn phong có thể là synthetic nhưng công việc, dự án và công nghệ phải hợp lý.

### 4. Draft annotation

Trong `data/synthetic_expansion/v2/pairs.jsonl`, kiểm tra `critical_requirement_assessments`, năm `criterion_assessments`, `total_score`, `draft_label`, `review_reasons` và `overall_rationale`.

Đạt khi:

- mọi yêu cầu bắt buộc đều có trạng thái và liên kết thông tin tương ứng;
- điểm không vượt `30/25/20/15/10` và tổng điểm bằng tổng năm nhóm;
- thiếu hoặc mâu thuẫn thông tin bắt buộc đi `Needs Review`;
- dưới 60 chỉ `Reject` khi có `unsatisfied` rõ ràng;
- draft label được hiểu là đề xuất chờ người duyệt, không phải ground truth.

## Trạng thái và giới hạn

- Người dùng đã duyệt toàn bộ 250 cặp. Bản Bronze tại `data/synthetic_expansion/v2/` vẫn giữ nguyên đề xuất trước review để truy vết.
- Bản đã duyệt nằm tại `data/synthetic_expansion/reviewed/v2/`: toàn bộ 250 cặp là Silver, có một vòng human review và không có score override.
- Tên hiển thị của tiêu chí thứ năm được làm rõ thành `Độ rõ ràng và khả năng kiểm tra của thông tin trong CV`; ID, trọng số 10 điểm và ý nghĩa chấm không đổi.
- Group split mới đặt 150 cặp của 30 ứng viên vào development và 100 cặp của 20 ứng viên vào held-out diagnostic. Không ứng viên nào xuất hiện ở cả hai tập.
- Không cặp nào thuộc validation hoặc frozen test hiện tại.
- Dataset v2 không thay đổi kết quả Stage 6 đã có.
- Silver được phép dùng cho tuning có kiểm soát và phân tích lỗi, nhưng chưa phải Gold ground truth để tuyên bố hiệu năng cuối.
- Held-out Silver chưa được chạy. Chỉ được tạo kết quả cuối sau khi đạt Gold và khóa kế hoạch đánh giá.

## Lệnh kiểm tra

Sinh lại v2:

```powershell
uv run python -m scripts.generate_synthetic_expansion
```

Chạy test và QC:

```powershell
uv run python -m scripts.approve_synthetic_expansion --reviewed-at <ISO-8601-with-timezone>
uv run python -m scripts.create_synthetic_expansion_split --created-at <ISO-8601-with-timezone>
uv run pytest -q tests/evaluation/test_synthetic_expansion.py tests/evaluation/test_synthetic_expansion_review.py
Get-Content -Raw -Encoding utf8 data/synthetic_expansion/v2/quality_report.json
Get-Content -Raw -Encoding utf8 data/synthetic_expansion/reviewed/v2/quality_report.json
```

Không chạy lại hai script review và split chỉ để nhận nhãn hoặc phân bố thuận lợi hơn. Nếu nguồn review thay đổi hợp lệ, phải tăng version và lưu migration note.
