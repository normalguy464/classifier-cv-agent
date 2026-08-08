# Review dataset 2.3.1 và Gemini L3 v22 tại Stage 6

## Kết luận

Yêu cầu hiệu chỉnh QA đã được thực hiện đúng phạm vi development. Dataset 2.3.0 loại bỏ ba nhóm thông tin testing-foundation bị mâu thuẫn. Bản vá 2.3.1 làm câu phủ định còn lại nêu đúng năng lực `qa-testing-foundations`, vì bản 2.3.0 chỉ nói chung chung nên LLM có thể hiểu là `missing` thay vì `unsatisfied`. Năm cặp CV-JD liên quan giữ nguyên requirement status, năm nhóm điểm, nhãn và rationale đã duyệt.

QC và L2 đều đạt. L3 xác nhận case QA mục tiêu đúng về mặt nghiệp vụ, nhưng experiment v22 dừng sớm vì tỷ lệ structured output hợp lệ của Gemini free tier không đủ để hoàn thành 30 attempt trong hard request cap 35. Cấu hình năm vai trò vì vậy chưa đủ điều kiện freeze và Gate 6 vẫn mở.

## Dataset đã hiệu chỉnh

| Nội dung | Kết quả |
| --- | --- |
| Dataset nguồn | Silver 2.2.0 |
| Dataset loại bỏ thông tin mâu thuẫn | 2.3.0 |
| Dataset làm rõ exact negative | 2.3.1 |
| CV được thay đổi | `cv-syn-qa-failed-v2` |
| Cặp được review lại | 5 cặp development của CV trên |
| Requirement mục tiêu | `qa-testing-foundations=unsatisfied` |
| Điểm, nhãn, rationale | Giữ nguyên |
| Membership development/held-out | Giữ nguyên |
| QC | 50 CV, 25 JD, 25 rubric, 250 cặp; 0 lỗi, 0 cảnh báo |

Dataset 2.3.0 bỏ các tuyên bố về acceptance criteria, risk-based testing, boundary value, decision table và test plan khỏi ba composite evidence. Probe tiếp theo cho thấy câu phủ định cũ vẫn chưa nêu tên năng lực đủ rõ. Dataset 2.3.1 chỉ thay một evidence bằng câu xác nhận ứng viên chưa biết STLC và chưa từng áp dụng equivalence partitioning, boundary value hoặc decision table để thiết kế test từ requirement. Đây là cách diễn đạt cụ thể của đúng trạng thái `unsatisfied` đã được người dùng duyệt, không phải thay nhãn để chạy theo output model.

## Kết quả L2 trên dataset 2.3.1

| Chỉ số | Kết quả |
| --- | ---: |
| Candidate được đề xuất | `coverage-70-95-v1` |
| Total-score MAE | 9,9196 |
| Tỷ lệ đúng 100 điểm | 0 |
| Vai trò có strong cao hơn hard negative | 5/5 |
| False Reject | 0 |
| Unsafe Pass | 0 |

L2 tiếp tục ổn định sau thay đổi dữ liệu nhỏ. Đây vẫn là kết quả trên 150 cặp development Silver, không phải kết quả held-out hoặc frozen test.

## Các lần probe L3

| Experiment | Dataset | Prompt | Kết quả case QA mục tiêu |
| --- | --- | --- | --- |
| v19 | 2.3.0 | v6 | `qa-testing-foundations=conflicting`; còn dùng thông tin giáo dục và câu phủ định chung |
| v20 | 2.3.0 | v7 | Output hợp lệ sau retry nhưng lan `conflicting` sang cả năm requirement |
| v21 | 2.3.0 | v8 | Bốn requirement đúng; requirement mục tiêu thành `missing` vì chưa có exact negative |
| v22 | 2.3.1 | v8 | Requirement mục tiêu `unsatisfied`, bốn requirement còn lại `satisfied`, tổng điểm 38 |

Prompt v8 phân biệt ba loại thông tin: direct positive cho đúng requirement, exact negative cho đúng requirement và context-only evidence không đủ để tự xác nhận năng lực. ID của education evidence được gửi rõ là context-only; một câu phủ định chung không được phép làm nhiều requirement thành `unsatisfied` hoặc `conflicting`.

## Kết quả batch Gemini v22

| Chỉ số | Kết quả | Điều kiện |
| --- | ---: | --- |
| HTTP request | 29/35 | Không vượt hard cap |
| Structured output hợp lệ | 21 | Bao gồm primary và stability repeat |
| Request-level valid-output rate | 0,7241 | Chưa đủ để hoàn tất kế hoạch |
| Primary case có output hợp lệ | 18/25 | Required coverage là 25/25 |
| Requirement-status match trên output hợp lệ | 1,0 | Đạt có điều kiện |
| Criterion MAE trên output hợp lệ | 2,1756 | Đạt ngưỡng tối đa 3,5 |
| Total-score MAE trên output hợp lệ | 7,1111 | Đạt ngưỡng tối đa 12 |
| Endpoint-score rate | 0 | Đạt ngưỡng tối đa 0,4 |
| Stability case đánh giá được | 3/5 | Chưa đủ coverage |
| Maximum stability range đã quan sát | 1,5 | Đạt trên phần đánh giá được |
| Quality gate tổng thể | Không đạt | Coverage không đầy đủ |
| Hybrid diagnostic | Không chạy | Không tổng hợp từ batch L3 thiếu output |

Tám request bị từ chối bởi schema hoặc score-consistency validation. Tất cả 25 primary pair đều đã được thử, nhưng chỉ 18 pair có output hợp lệ; ba trong năm stability case có đủ hai lượt hợp lệ. Sau 29 request còn 6 request, trong khi cần thêm 9 output hợp lệ. Bộ chạy dừng vì ngay cả trường hợp cả sáu request còn lại đều thành công thì vẫn không thể hoàn tất 30 output hợp lệ.

Các metric MAE và requirement match cho thấy prompt/data mới chấm hợp lý khi Gemini trả output đúng contract. Chúng không bù được tỷ lệ output không hợp lệ. Không được bỏ tám lỗi hoặc chỉ báo cáo 18 case thành công như một batch hoàn chỉnh.

## Phạm vi an toàn

- Không có raw provider response, API key hoặc secret được lưu trong dataset, cache hay report.
- Không có cặp nào từ 100-pair held-out được đánh giá.
- Không có case nào từ frozen test Stage 6 cũ được đánh giá.
- Human label, rubric và quality threshold không bị sửa để làm report đạt.
- Lỗi provider không được diễn giải thành ứng viên không đạt; runtime tiếp tục có fallback an toàn về `Needs Review`.

## Trạng thái Gate 6 và lựa chọn tiếp theo

Nhánh năm vai trò chưa thể freeze bằng experiment v22. Chất lượng nghiệp vụ của các output hợp lệ đã cải thiện, nhưng Gemini free tier chưa đạt độ tin cậy structured output theo policy đã công bố.

Hai đường đi hợp lệ vẫn được giữ:

1. Controlled pilot hai vai trò: freeze cấu hình hai vai trò đã hoàn thành validation trước đó, giữ ba vai trò mới ở trạng thái development-only, rồi sang Stage 7 chạy đúng một lần frozen test hai vai trò.
2. Tiếp tục mục tiêu năm vai trò: giữ Gate 6 mở, bổ sung human review độc lập và runtime config cho ba vai trò mới, đồng thời thử provider/model có structured output ổn định hơn hoặc thiết kế lại L3 trong một experiment development mới.

Không khuyến nghị tăng request cap của đúng experiment v22 chỉ để cứu batch sau khi đã thấy kết quả. Nếu thay request policy, model, prompt hoặc chiến lược L3 thì phải tạo experiment version mới và không dùng held-out/frozen test để tuning.
