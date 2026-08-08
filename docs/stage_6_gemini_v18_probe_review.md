# Review probe Gemini v18

## Kết luận

Dataset Silver 2.2.0, L2 và prompt v6 đã được triển khai đúng phạm vi phê duyệt. L2 vẫn ổn định và prompt v6 đã sửa bốn lỗi lan trạng thái giữa các requirement. Batch L3 được dừng sau probe vì phát hiện một mâu thuẫn dữ liệu mới trong hồ sơ QA; tiếp tục gọi API lúc này không thể làm quality gate đạt yêu cầu.

## Phần đã hoàn thành

- Dataset `2.2.0` sửa đúng bốn đoạn thông tin thuộc `cv-syn-da-missing-v2` và `cv-syn-de-missing-v2`.
- Mười cặp CV-JD liên quan giữ nguyên trạng thái yêu cầu, năm nhóm điểm, nhãn và rationale đã duyệt.
- QC xác nhận 50 CV, 25 JD, 25 rubric và 250 cặp Silver hợp lệ.
- L2 E5 chạy offline trên 150 development pair và tiếp tục đề xuất `coverage-70-95-v1`.
- Prompt `l3-evidence-rubric-v6` giới hạn câu phủ định vào đúng requirement được nêu.
- Không có cặp held-out hoặc frozen-test nào được đánh giá.

## Kết quả L2 2.2.0

| Chỉ số | Kết quả |
|---|---:|
| Candidate được đề xuất | `coverage-70-95-v1` |
| Total-score MAE | 10,0071 |
| Tỷ lệ đúng 100 điểm | 0 |
| Vai trò có strong cao hơn hard-negative | 5/5 |
| False Reject | 0 |
| Unsafe Pass | 0 |

## Phát hiện từ probe L3

Probe `pair-qa-failed-std` trả về structured output hợp lệ. Bốn requirement có thông tin tích cực riêng đều được đánh dấu `satisfied`, đúng với annotation:

- `qa-test-cases`
- `qa-api-testing`
- `qa-data-check`
- `qa-automation-foundation`

Riêng `qa-testing-foundations`, annotation đã duyệt là `unsatisfied` nhưng CV chứa cả hai hướng thông tin:

- `ev-qa-failed-gap-1`: ứng viên xác nhận chưa biết quy trình hoặc kỹ thuật kiểm thử phần mềm.
- `ev-qa-failed-technical`: ứng viên phân tích acceptance criteria và thiết kế risk-based test.
- `ev-qa-failed-reasoning`: ứng viên áp dụng boundary và decision table.

Theo rubric, đây là `conflicting`, không phải `unsatisfied`. Vì quality policy yêu cầu requirement-status match bằng 1,0, chạy thêm 29 attempt trước khi xử lý mâu thuẫn này chỉ tốn request mà không thể làm gate đạt.

## Phương án đề xuất

Giữ nguyên ý định `explicit_failure` và nhãn đã duyệt, đồng thời tạo dataset `2.3.0` để:

1. Bỏ các tuyên bố về acceptance criteria, risk-based testing, boundary và decision table khỏi composite evidence của `cv-syn-qa-failed-v2`.
2. Giữ nguyên bằng chứng trực tiếp của bốn requirement còn lại.
3. Review lại năm cặp CV-JD của hồ sơ này, không thay đổi điểm, nhãn hoặc rationale nếu nội dung sau sửa vẫn đúng với rubric.
4. Tạo manifest và split hash mới nhưng giữ nguyên membership development/held-out.
5. Chạy QC, L2 development và một experiment L3 development mới với prompt v6.

## Câu xác nhận

Nếu đồng ý, người dùng có thể xác nhận nguyên văn:

`Tôi duyệt tạo dataset 2.3.0 để bỏ thông tin testing-foundation bị mâu thuẫn trong cv-syn-qa-failed-v2, giữ kịch bản explicit_failure và trạng thái qa-testing-foundations=unsatisfied; hãy review lại năm cặp liên quan, chạy QC, L2 và L3 development, không mở held-out hoặc frozen test.`
