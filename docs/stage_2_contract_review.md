# Stage 2 Review: Data Contracts v1

## Trạng thái

Các contract v1 đã được định nghĩa, có test validation và được người dùng phê duyệt ngày 2026-07-25 để dùng cho pilot dataset. Schema `1.0.0` được đóng băng trong phạm vi pilot.

> Cập nhật Stage 4 ngày 2026-07-26: nội dung bên dưới ghi lại trạng thái tại Gate 2. `CVProfile`, `JobProfile`, `ScoringRubric` và `ApprovedDecision` vẫn ở `1.0.0`; riêng `ClassificationConfig`, `ClassificationRequest` và `ClassificationResult` đã migration lên `1.1.0` để bắt buộc ghi version của Job Profile artifact, luật L1 và cấu hình model. Xem migration note đầy đủ trong [stage_4_review.md](stage_4_review.md).

## Phân biệt các contract chính

| Contract | Vai trò |
| --- | --- |
| `CVProfile` | Dữ liệu CV đã được cấu trúc; chỉ nhận evidence và dữ liệu nghề nghiệp, không nhận PDF/DOCX trực tiếp. |
| `JobProfile` | Mô tả vị trí đang tuyển, yêu cầu và cách chấp nhận evidence. |
| `ScoringRubric` | Tiêu chí chấm và trọng số tổng 100 cho một Job Profile. |
| `ClassificationConfig` | Trọng số L1/L2/L3, ngưỡng quyết định, quality gate và metadata model/prompt. |
| `Evidence` | Đoạn evidence có nguồn, section, vị trí và confidence extraction tùy chọn. |
| `ClassificationResult` | Điểm L1/L2/L3, điểm cuối, criterion assessments, quality gate, warnings và mọi version của lần chạy. |
| `ApprovedDecision` | Quyết định đã được HR phê duyệt hoặc override; đây là contract duy nhất được phép đi tới agent downstream. |

## Quy tắc dữ liệu quan trọng

- Tất cả contract công khai có `schema_version: "1.0.0"`.
- `ClassificationConfig.schema_version` vẫn là `1.0.0`; scoring `configuration_version` tăng lên `1.1.0` khi hai quy tắc routing được bổ sung vì hành vi thay đổi nhưng cấu trúc contract không đổi.
- Thuộc tính không khai báo bị từ chối. Vì vậy tuổi, giới tính, quê quán và các thuộc tính được bảo vệ không thể đi vào `CVProfile` hoặc output bằng cách vô tình thêm field.
- `EvidenceStatus` luôn là một trong `satisfied`, `unsatisfied`, `missing`, `conflicting`. Missing không đồng nghĩa với unsatisfied.
- Mọi `evidence_id` trong skill, project, kinh nghiệm, học vấn hoặc chứng chỉ phải tham chiếu evidence tồn tại trong cùng `CVProfile`.
- Rubric phải tổng trọng số đúng 100; aggregation L1/L2/L3 phải tổng đúng 1; score và confidence bị giới hạn trong phạm vi hợp lệ.
- `Needs Review` cho phép L2 hoặc L3 không có điểm khi provider lỗi. `Pass`, `Waitlist` và `Reject` phải có final score.
- `ApprovedDecision` có override reason bắt buộc khi HR thay đổi đề xuất; khi chỉ approve, final decision phải giữ nguyên đề xuất.

## Ví dụ tối thiểu

```json
{
  "schema_version": "1.0.0",
  "cv_profile_id": "cv-001",
  "candidate_reference": "candidate-001",
  "skills": [
    {"name": "SQL", "evidence_ids": ["ev-sql"]}
  ],
  "evidence": [
    {
      "schema_version": "1.0.0",
      "evidence_id": "ev-sql",
      "source_type": "parser",
      "section": "skills",
      "text": "SQL: joined and aggregated sales data.",
      "location": {"source_record_id": "record-skills", "page_number": 1}
    }
  ]
}
```

## Điều cần xác nhận cho Gate 2

1. `CVProfile` có đủ section để biểu diễn CV đã parse: skills, work experience, education, projects, certifications, evidence và quality warnings.
2. `JobProfile` có đủ để HR hoặc workflow tạo vị trí tuyển: seniority, experience range, responsibilities và requirements.
3. Requirement evidence state và output `ClassificationResult` đủ rõ để HR phân biệt thiếu evidence, không đáp ứng và evidence mâu thuẫn.
4. `ApprovedDecision` có audit fields và ngăn downstream agent dùng dự đoán chưa được HR chấp thuận.
5. Không cần thêm field công khai nào trước khi schema `1.0.0` được đóng băng cho pilot dataset.

Gate 2 đã hoàn tất. Mọi thay đổi không tương thích với các contract này phải có migration note, version mới và contract test.
