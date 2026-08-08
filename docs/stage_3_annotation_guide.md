# Stage 3 Annotation Guide: Pilot Dataset v1

## Mục đích

Tài liệu này hướng dẫn duyệt mười CV tổng hợp trong `data/samples/cvs/` và phiếu đánh giá tham chiếu trong `data/annotations/pilot_annotations_v1.json`. Mục tiêu là xác nhận rubric có thể dùng nhất quán trước khi phát triển classifier core ở Stage 4.

Phiếu do coding agent đề xuất chưa phải kết quả chuẩn. Chỉ kết quả đã được người dùng kiểm tra và ghi nhận đầy đủ mới được dùng làm đáp án tham chiếu khi evaluation.

## Thứ tự review một record

1. Đọc file `source_cv_file` được liên kết trong phiếu đánh giá.
2. Đối chiếu từng `critical_requirement_assessments` với các đoạn thông tin có mã `evidence_ids`.
3. Xác nhận kết quả đối chiếu là `satisfied`, `unsatisfied`, `missing` hoặc `conflicting`.
4. Xem năm `criterion_assessments`, điểm được cấp và phần giải thích.
5. Kiểm tra `total_score` bằng tổng `awarded_points`.
6. Xác nhận `draft_label` có tuân thủ threshold và điều kiện `Needs Review`.
7. Ghi kết quả người phụ trách xác nhận trong object `review`.

## Kết quả đối chiếu yêu cầu

| Trạng thái mã | Khi sử dụng | Quy tắc về thông tin làm căn cứ |
| --- | --- | --- |
| `satisfied` | CV có thông tin cụ thể để xác nhận yêu cầu được đáp ứng. | Phải có ít nhất một `evidence_id`. |
| `unsatisfied` | CV có thông tin cụ thể để xác nhận yêu cầu chưa được đáp ứng. | Phải có ít nhất một `evidence_id`; không suy ra chỉ vì CV không nhắc tới. |
| `missing` | CV không cung cấp đủ thông tin để xác định. | Không tạo một đoạn thông tin giả cho điều CV không đề cập. |
| `conflicting` | Có ít nhất hai phần thông tin dẫn tới kết luận trái nhau. | Phải trỏ tới ít nhất hai `evidence_id` không nhất quán. |

Ví dụ: CV không nhắc tới Git là `missing`. CV ghi rõ “chưa từng sử dụng Git” mới có thể là `unsatisfied`. CV liệt kê Git nhưng phần mô tả dự án nói ứng viên không trực tiếp dùng Git là `conflicting`.

## Cách chấm điểm

Điểm trong phiếu đánh giá là weighted points, không phải score chuẩn hóa riêng 0–100 cho từng tiêu chí.

| Tiêu chí | Điểm tối đa |
| --- | ---: |
| Yêu cầu bắt buộc | 30 |
| Năng lực kỹ thuật chuyên môn | 25 |
| Năng lực theo vai trò | 20 |
| Dự án/thực tập và tác động | 15 |
| Giao tiếp và chất lượng thông tin làm căn cứ | 10 |
| Tổng | 100 |

Mỗi `awarded_points` phải nằm từ 0 đến `maximum_points`. `total_score` là tổng trực tiếp của năm điểm, không nhân trọng số thêm lần nữa.

Các mốc tham khảo không phải công thức tự động:

- Gần điểm tối đa: thông tin cụ thể, nhất quán, có phạm vi và kết quả rõ.
- Khoảng 60–79 phần trăm điểm tối đa: đủ thông tin ở mức junior nhưng còn thiếu chiều sâu, tác động hoặc khả năng kiểm chứng.
- Khoảng 40–59 phần trăm điểm tối đa: thông tin hạn chế hoặc chỉ hỗ trợ một phần tiêu chí.
- Dưới 40 phần trăm điểm tối đa: có thông tin rõ về việc chưa đáp ứng hoặc gần như không có năng lực liên quan.

Không chấm điểm dựa trên tuổi, giới tính, quê quán, tình trạng hôn nhân, trường danh tiếng hoặc bất kỳ thuộc tính được bảo vệ nào.

## Quy tắc nhãn

- `pass`: tổng điểm từ 75 trở lên và không có điều kiện bắt buộc kiểm tra thủ công.
- `waitlist`: tổng điểm từ 60 đến dưới 75 và không có điều kiện bắt buộc kiểm tra thủ công.
- `reject`: tổng điểm dưới 60 và CV có thông tin rõ xác nhận ít nhất một yêu cầu bắt buộc `unsatisfied`.
- `needs_review`: được ưu tiên nếu yêu cầu bắt buộc là `missing` hoặc `conflicting`, provider output không hợp lệ, mức chênh lệch L1/L2/L3 từ 25 điểm, hoặc tổng điểm nằm trong vùng 58–62 hay 73–77.

Do các vùng điểm sát ngưỡng được xét trước, khoảng tự động thực tế là trên 77 cho `pass`, trên 62 và dưới 73 cho `waitlist`, dưới 58 cho `reject` có điều kiện. Scoring configuration `1.1.0` chuyển sang `needs_review` nếu yêu cầu bắt buộc `unsatisfied` nhưng điểm từ 60 trở lên, hoặc nếu điểm dưới 60 mà không có `unsatisfied` rõ.

Pilot Stage 3 chưa chạy L1/L2/L3 hoặc provider. Các trường hợp ở đây chỉ kiểm tra logic nghiệp vụ dự kiến từ thông tin trong CV và rubric. Điểm trong phiếu đánh giá không phải output đo được của classifier.

## Cách ghi quyết định review

Nếu đồng ý với nhãn và điểm:

```json
{
  "status": "approved",
  "reviewer_reference": "reviewer-user-001",
  "final_label": "pass",
  "criterion_score_overrides": [],
  "notes": "Đồng ý với kết quả đối chiếu yêu cầu, điểm và phần giải thích.",
  "reviewed_at": "2026-07-25T15:00:00+07:00"
}
```

Nếu thay đổi điểm, giữ điểm đề xuất ban đầu và ghi phần thay đổi:

```json
{
  "status": "approved",
  "reviewer_reference": "reviewer-user-001",
  "final_label": "waitlist",
  "criterion_score_overrides": [
    {
      "criterion_id": "technical-analysis",
      "awarded_points": 13,
      "reason": "Thông tin trong CV chỉ mô tả thao tác cơ bản."
    }
  ],
  "notes": "Hạ điểm kỹ thuật và xác nhận nhãn cuối.",
  "reviewed_at": "2026-07-25T15:00:00+07:00"
}
```

Nếu chưa thể kết luận, dùng `status: "changes_requested"`, ghi câu hỏi trong `notes` và để `final_label` là `null`.

## Điều kiện hoàn tất Gate 3

- Cả mười CV và phiếu đánh giá đều đã được người dùng kiểm tra.
- Mỗi record có kết quả phân loại, năm criterion scores, phần giải thích và kết quả đối chiếu yêu cầu được xác nhận.
- Các trường hợp `missing`, `conflicting`, explicit `unsatisfied` và boundary score không còn ambiguity cấu trúc.
- Hai quy tắc bổ sung trong scoring configuration `1.1.0` được áp dụng nhất quán.
- Mọi record được dùng làm kết quả chuẩn có reviewer reference và trạng thái `approved`.
- Nếu rubric không thể xử lý một case mà không suy diễn, sửa rubric và version trước khi sang Stage 4.
