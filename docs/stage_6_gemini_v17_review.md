# Review Gemini L3 v17 tại Stage 6

## Phạm vi

Experiment `synthetic-expansion-v2-google-ai-studio-l3-validation-v2` chỉ dùng 25 cặp Silver development đã chọn trước và năm lần chấm lặp. Một trăm cặp held-out và mười frozen-test case cũ không được sử dụng. Model giữ nguyên `gemini-3.5-flash-lite`; thay đổi duy nhất về chất lượng là prompt `l3-evidence-rubric-v5`.

## Kết quả so sánh

| Chỉ số | Gemini v16, prompt v3 | Gemini v17, prompt v5 | Ngưỡng | Nhận xét |
| --- | ---: | ---: | ---: | --- |
| Primary valid-output rate | 1,0000 | 1,0000 | 1,0000 | Đạt sau retry có giới hạn |
| Request-level valid-output rate | 0,9677 | 0,8824 | Chỉ theo dõi | v17 có bốn output đầu tiên sai schema hoặc score consistency |
| Requirement-status match | 0,9750 | 0,9417 | 1,0000 | Chưa đạt |
| Criterion MAE | 3,6560 | 2,9144 | Tối đa 3,5 | Đạt và cải thiện |
| Total-score MAE | 15,2400 | 9,5800 | Tối đa 12 | Đạt và cải thiện |
| Endpoint-score rate | 0,2800 | 0,0000 | Tối đa 0,4 | Đạt và không còn bão hòa 0/100 |
| Maximum stability range | 15,0 | 3,0 | Tối đa 10 | Đạt và cải thiện |
| Stability requirement agreement | 1,0000 | 1,0000 | 1,0000 | Đạt |
| Hybrid review rate | 1,0000 | 1,0000 | Mục tiêu tối đa 0,8 | Chưa đạt |
| False Reject / unsafe Pass | 0 / 0 | 0 / 0 | 0 / 0 | Đạt an toàn |

V17 chứng minh các scoring cap và overall band hợp lý hơn v16, nhưng chưa được freeze vì requirement-status policy chưa đạt và hybrid vẫn chuyển toàn bộ case sang `Needs Review`.

## Năm mismatch do prompt áp dụng phủ định quá rộng

Cả năm mismatch nằm ở `pair-qa-failed-std`. Evidence phủ định chỉ nói ứng viên chưa biết quy trình hoặc kỹ thuật kiểm thử phần mềm, nhưng prompt v5 còn lan truyền các câu giới hạn chung sang `qa-test-cases`, `qa-api-testing`, `qa-data-check` và `qa-automation-foundation` dù từng yêu cầu này có thông tin áp dụng trực tiếp.

Hướng sửa không cần đổi dữ liệu hoặc human label: prompt v6 phải quy định câu phủ định chỉ ảnh hưởng requirement mà nó nêu trực tiếp; giới hạn chung vẫn làm giảm điểm tiêu chí nhưng không tự tạo `conflicting` cho các requirement khác.

## Hai mismatch cần người dùng quyết định về dữ liệu

### `pair-da-missing-std`, requirement `da-sql`

- Human status hiện tại: `missing`.
- Gemini v16 và v17: `satisfied`.
- CV đồng thời có thông tin `viết CTE và window function` và bàn giao `SQL`.
- Kịch bản và summary lại nói thiếu một năng lực cốt lõi, nhưng không nêu tên năng lực bị thiếu.

### `pair-de-missing-std`, requirement `de-python`

- Human status hiện tại: `missing`.
- Gemini v16 và v17: `satisfied`.
- CV đồng thời ghi trực tiếp `xây pipeline nhiều nguồn bằng Python và SQL`.
- Kịch bản và summary lại nói thiếu một năng lực cốt lõi, nhưng không nêu tên năng lực bị thiếu.

Hai trường hợp trên là xung đột giữa ý định sinh case `missing_critical` và nội dung evidence tổng hợp. Model trả `satisfied` là có cơ sở từ dữ liệu đầu vào; ép prompt bỏ qua câu trực tiếp chỉ để khớp nhãn sẽ làm giảm tính đúng đắn khi dùng CV thực tế.

## Khuyến nghị cần duyệt

Khuyến nghị tạo dataset version mới và sửa evidence tổng hợp của hai CV để loại nội dung vô tình chứng minh đúng năng lực dự kiến bị thiếu. Giữ human status, điểm và nhãn hiện tại trước khi review lại; sau khi sửa phải:

1. Chạy lại QC và tạo hash/manifest version mới.
2. Review lại năm cặp JD của mỗi CV bị thay đổi, không chỉ cặp standard.
3. Chạy lại L2 development vì nội dung CV đã đổi.
4. Tạo prompt v6 sửa phạm vi câu phủ định.
5. Chạy lại L3 trên development bằng experiment version mới.

Không sửa dataset nếu chưa có phê duyệt rõ ràng. Không đổi hai human status thành `satisfied` chỉ để tăng metric nếu mục tiêu nghiệp vụ vẫn là giữ hai case `missing_critical`.

## Câu xác nhận đề xuất

`Tôi duyệt tạo dataset version mới để sửa evidence bị rò năng lực SQL trong cv-syn-da-missing-v2 và Python trong cv-syn-de-missing-v2, giữ ý định hai case missing_critical; hãy review lại các cặp liên quan, chạy QC, L2 và L3 development, không mở held-out hoặc frozen test.`
