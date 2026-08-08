# Stage 5 — Classifier Review

## Trạng thái bàn giao

Gate 4 đã hoàn tất. Người dùng đã xác nhận đủ 30 hồ sơ Stage 4, gồm requirement status, năm nhóm điểm, draft label và rationale. Bản đã duyệt ghi:

- `annotation_status: reviewed`;
- 30/30 `review.status: approved`;
- reviewer giả danh `reviewer-user-001`;
- `final_label` giữ nguyên nhãn đã được người dùng xác nhận;
- không có criterion score override;
- timestamp có timezone cho toàn bộ quyết định.

Bản nháp trong `data/to_review/` được giữ lại làm audit trail. Stage 5 chỉ đọc bản trong `data/reviewed/`.

Gate 5 đang mở. Người dùng cần xem các case đại diện và xác nhận nguyên nhân sai lệch trước khi chuyển sang Stage 6.

## Phạm vi lần chạy Stage 5 đầu tiên

Classifier đã chạy đủ L1, L2, L3, aggregation và routing trên 30 hồ sơ đã duyệt:

- L1 dùng bộ rule có phiên bản của từng vị trí.
- L2 dùng `deterministic-hashing-embedding` để lần chạy offline có thể tái lập mà không tải model.
- L3 dùng deterministic fake dựa trên mật độ và phạm vi thông tin trong CV.
- Aggregation giữ nguyên trọng số L1 45%, L2 25%, L3 30%.
- Routing giữ nguyên threshold và toàn bộ candidate-protection quality gate.

Đây là controlled diagnostic. Nó kiểm tra workflow, breakdown, disagreement và routing, nhưng không phải kết quả hiệu năng cuối vì chưa chạy multilingual Sentence Transformers và LLM provider thật. Trường `is_final_performance` trong report bắt buộc là `false`.

## Kết quả chính

| Kiểm tra | Kết quả | Ý nghĩa |
| --- | ---: | --- |
| Requirement status của L1 khớp human review | 30/30 | Bộ rule bắt buộc đang đọc đúng các trạng thái đã duyệt trên tập này. |
| Proposed decision khớp final label | 16/30 | 16 case có ground truth `Needs Review` tiếp tục được bảo vệ bằng review. |
| Label mismatch | 14/30 | Sáu Pass, sáu Waitlist và hai Reject đều bị chuyển thành `Needs Review`. |
| Large-level disagreement | 30/30 | Chênh lệch L1/L2/L3 đều vượt ngưỡng 25 điểm. |
| Proposed `Needs Review` | 30/30 | Quality gate hoạt động đúng precedence khi disagreement lớn. |

Điểm trung bình của lần chạy là L1 `88.33`, L2 `19.96`, L3 `95.80` và final score `73.48`. Khoảng disagreement nhỏ nhất vẫn là `61.84`, lớn nhất là `93.41`.

Mẫu sai lệch đồng nhất: hashing embedding tạo điểm L2 thấp, đặc biệt với Python Backend, trong khi L1 và L3 fake cao. Vì vậy kết luận sơ bộ hợp lý là hạn chế của adapter kiểm tra offline, không phải căn cứ tự động sửa human label hoặc rubric.

Accuracy `0.5333`, Macro-F1 `0.1739` và Cohen's kappa `0.0` chỉ mô tả lần chạy controlled này. Không được dùng các số đó làm kết quả nghiên cứu cuối.

## 14 label mismatch cần xác nhận nguyên nhân

| Ground truth | Data Analyst | Python Backend | Classifier output |
| --- | --- | --- | --- |
| Pass | `cv-s4-da-001` đến `cv-s4-da-003` | `cv-s4-be-001` đến `cv-s4-be-003` | `Needs Review` |
| Waitlist | `cv-s4-da-004` đến `cv-s4-da-006` | `cv-s4-be-004` đến `cv-s4-be-006` | `Needs Review` |
| Reject | `cv-s4-da-011` | `cv-s4-be-011` | `Needs Review` |

Hai case Reject có final score của lần chạy trên 60 nên quy tắc `critical-unsatisfied-at-or-above-waitlist-threshold` cũng yêu cầu review. Đây là fallback bảo vệ ứng viên đã được duyệt ở Stage 3.

## Năm `Needs Review` case đại diện cho quality gate

| Case | Ground truth | Lý do cần xem |
| --- | --- | --- |
| `cv-s4-da-007` | `Needs Review` | Thiếu thông tin cho requirement bắt buộc. |
| `cv-s4-da-008` | `Needs Review` | Final score nằm trong lower threshold boundary. |
| `cv-s4-da-009` | `Needs Review` | Thông tin requirement bắt buộc mâu thuẫn. |
| `cv-s4-da-015` | `Needs Review` | Requirement không đáp ứng nhưng aggregate score từ 60 trở lên. |
| `cv-s4-be-012` | `Needs Review` | Final score nằm trong upper threshold boundary. |

Năm case này cùng 14 mismatch tạo thành `representative_case_ids` trong report. Danh sách đầy đủ 30 result vẫn được giữ trong `cases`.

## Cách đọc một case trong report

Mỗi case trong `evaluation/reports/stage5_classifier_review_v1.json` có ba phần:

1. `ground_truth`: final label, requirement status, năm nhóm điểm, total score và rationale đã được người dùng xác nhận.
2. `classifier_result`: L1/L2/L3 score, final score, năm criterion assessment do L3 cung cấp, quality-gate reasons và toàn bộ version metadata.
3. `comparison`: kết quả có khớp nhãn không, requirement status có khớp không, chênh lệch điểm từng criterion, maximum level disagreement và các cờ cần chú ý.

`classifier_l3_weighted_score` là điểm theo criterion do L3 fake trả về. Nó không phải criterion score đã aggregate giữa L1, L2 và L3. Final score mới là kết quả aggregate theo trọng số 45/25/30.

## Người dùng cần duyệt gì

Với 14 mismatch và năm `Needs Review` case đại diện, hãy phân loại nhận định của bạn theo một trong các hướng:

- Model hoặc adapter error: human label và rubric vẫn đúng, output sai do chiến lược model đang dùng.
- Label error: final label hoặc điểm human review cần sửa; phải nêu case ID và giá trị đúng.
- Rubric ambiguity: cùng thông tin có thể dẫn đến nhiều kết quả hợp lý; phải nêu quy tắc nào cần làm rõ.
- Expected review behavior: hệ thống chuyển `Needs Review` đúng và không cần sửa.

Đề xuất hiện tại là ghi nhận 14 mismatch là controlled-adapter limitation, giữ nguyên 30 human label và giữ quality gate. Stage 6 sẽ dùng validation data để thử model, weight, threshold và prompt phù hợp hơn; không tuning trên frozen test.

## Điều kiện hoàn tất Gate 5

Gate 5 đạt khi người dùng xác nhận:

- đã xem 14 label mismatch và năm `Needs Review` case đại diện;
- đồng ý hoặc chỉnh lại phân loại nguyên nhân model error, label error hay rubric ambiguity;
- mọi thay đổi human label hoặc rubric, nếu có, đã được ghi và kiểm tra lại;
- hành vi quality gate bảo vệ ứng viên là chấp nhận được;
- không diễn giải controlled diagnostic như final performance.

Nếu đồng ý với đề xuất hiện tại, có thể duyệt bằng câu:

> Tôi xác nhận 14 label mismatch là hạn chế của adapter offline, không sửa 30 human label hoặc rubric; năm Needs Review case đại diện và quality gate hoạt động đúng. Hãy hoàn tất Gate 5.

## File được tạo hoặc thay đổi

| File | Loại | Mục đích và consumer | Quyết định của người dùng |
| --- | --- | --- | --- |
| `scripts/approve_stage4_dataset.py` | Script | Chuyển đúng 30 draft record thành artifact đã duyệt mà không ghi đè đề xuất ban đầu. | Không cần chạy lại trừ khi chủ động tái lập approval artifact. |
| `data/reviewed/stage4_cv_profiles_v1.jsonl` | Dữ liệu | Bản CV tổng hợp đã được tách riêng cho controlled evaluation. | Đã được duyệt cùng 30 annotation. |
| `data/reviewed/stage4_annotations_v1.json` | Dữ liệu review | Ground truth có reviewer, final label, timestamp và audit link về bản nháp. | Đây là quyết định Gate 4 đã được ghi nhận. |
| `evaluation/datasets/stage4.py` | Source code evaluation | Chỉ nạp đủ 30 record có human approval và kiểm tra score, evidence, ID, timestamp, path. | Không có quyết định nghiệp vụ mới. |
| `evaluation/datasets/__init__.py` | Source code export | Cho experiment import Stage 4 loader qua package chung. | Không có. |
| `evaluation/experiments/run_stage5_review.py` | Source code evaluation | Chạy classifier và tạo metrics, breakdown, disagreement, error list, review queue. | Dùng output để duyệt Gate 5. |
| `evaluation/reports/stage5_classifier_review_v1.json` | Report | Lưu toàn bộ 30 result và so sánh với human ground truth. | Cần xem các case được chỉ ra trong tài liệu này. |
| `tests/contract/test_stage4_reviewed_dataset.py` | Automated test | Bảo vệ quá trình approval, tách draft/reviewed, 30 approval và liên kết dữ liệu. | Không có. |
| `tests/evaluation/test_stage5_review.py` | Automated test | Kiểm tra runner tái lập, score bounds, version metadata, queue và committed report. | Không có. |
| `docs/stage_5_review.md` | Tài liệu review | Hướng dẫn đọc kết quả và điều kiện đóng Gate 5. | Cần phê duyệt hoặc nêu case cần sửa. |
