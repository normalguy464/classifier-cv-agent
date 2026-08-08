# Phiếu duyệt kết quả Frozen Test Stage 7

## Kết luận ngắn

Bộ runtime `five-role-runtime-v1` đã được chạy đúng một lần trên 50 case Gold đã khóa. Kết quả có tính an toàn cao nhưng **không đạt quality gate Stage 7** vì toàn bộ 50 case đều bị chuyển sang `Needs Review`.

Không có weight, threshold, prompt, model, rubric, L1 rule, L2 policy hoặc ground truth nào được thay đổi sau khi xem kết quả test.

## Artifact cần đối chiếu

| File | Loại | Mục đích |
| --- | --- | --- |
| `data/frozen_test/stage7_v1/` | Dữ liệu | Bản Gold bất biến của 50 case, kèm review record, manifest, SHA-256 và QC report. |
| `evaluation/configs/stage7_frozen_evaluation_v1.yaml` | Cấu hình | Protocol `1.0.1`, ngưỡng metric, năm case stability, request cap và chính sách chi phí đã khóa trước khi gọi API. |
| `evaluation/experiments/run_stage7_frozen_evaluation.py` | Source code | Runner có cache/resume, retry giới hạn, fail-fast, baseline, ablation, hybrid, bootstrap và error analysis. |
| `evaluation/reports/stage7_frozen_evaluation_v1.json` | Báo cáo | Kết quả chi tiết từng case và toàn bộ metric cuối. SHA-256: `72a7ae2700114fc32d2c6290393a5f5ff94338b4537e85e58304743901909c9a`. |
| `tests/evaluation/test_stage7_frozen_evaluation.py` | Test | Kiểm tra kế hoạch 55 output, cache/resume, không lưu raw response và fail-fast khi provider unavailable. |

## Kết quả chính

| Chỉ số | Kết quả | Điều kiện | Trạng thái |
| --- | ---: | ---: | --- |
| Accuracy full hybrid | `0.50` | ít nhất `0.70` | Không đạt |
| Macro-F1 full hybrid | `0.1667` | ít nhất `0.60` | Không đạt |
| Needs Review recall | `1.00` | bằng `1.00` | Đạt |
| Review rate | `1.00` | không quá `0.80` | Không đạt |
| False Reject | `0` | bằng `0` | Đạt |
| Unsafe Pass | `0` | bằng `0` | Đạt |
| L3 requirement-status accuracy | `0.9875` | ít nhất `0.95` | Đạt |
| L3 unsafe requirement mismatch | `3` | bằng `0` | Không đạt |
| L3 criterion MAE | `2.162` | không quá `3` | Đạt |
| L3 total-score MAE | `8.55` | không quá `12` | Đạt |
| L3 valid output rate | `1.00` | ít nhất `0.95` | Đạt |
| Stability requirement agreement | `1.00` | ít nhất `0.80` | Đạt |
| Stability route agreement | `1.00` | bằng `1.00` | Đạt |
| Stability maximum score range | `0` | không quá `10` | Đạt |

Provider tạo đủ `55/55` output hợp lệ. Bộ đếm bảo thủ là `56/60` vì một lần kết nối bị sandbox chặn trước khi chạy lại với quyền mạng. Chi phí ước tính từ usage hợp lệ là khoảng `0.3601 USD`; hóa đơn provider mới là nguồn xác nhận cuối cùng.

## Vì sao toàn bộ case thành Needs Review

L1 chỉ khớp `64.17%` trạng thái requirement với human review, tương ứng `86/240` assessment lệch. Nhiều cách diễn đạt hợp lệ trong bộ test mới không khớp danh sách term xác định đã học từ dữ liệu development:

- `missing-critical-evidence`: 41 case;
- `low-score-without-explicit-critical-unsatisfied`: 31 case;
- `large-level-disagreement`: 18 case;
- boundary quanh ngưỡng: 6 case.

L2 không còn bão hòa ở 100 nhưng bị nén trong khoảng `48.27–62.33`, nên chưa tạo được độ phân tách tốt trên bộ test mới. L3 có khoảng điểm rộng hơn `23–84`, calibration MAE đạt yêu cầu và stability tốt.

Ba mismatch L3 không an toàn đều nằm ở case `conflicting_critical`:

- `s7-pair-be-05`: `be-rest-api`, human là `conflicting`, L3 là `satisfied`;
- `s7-pair-qa-05`: `qa-test-cases`, human là `conflicting`, L3 là `unsatisfied`;
- `s7-pair-de-05`: `de-sql`, human là `conflicting`, L3 là `unsatisfied`.

Đây là kết quả khái quát hóa chưa đạt của runtime đã khóa, không phải lý do để thay đổi nhãn Gold hoặc nới quality gate.

## Baseline và ablation

Không phương án nào đạt gate. Accuracy tốt nhất là tổ hợp `L2+L3` ở `0.52`; full `L1+L2+L3` đạt `0.50`. Keyword baseline đạt `0.46`, còn TF-IDF và embedding-only đều đạt `0.50` vì chuyển toàn bộ case sang review.

Kết quả này cho thấy policy bảo vệ ứng viên đang hoạt động đúng theo nghĩa không tự động loại nhầm, nhưng mức tự động hóa không đủ để tuyên bố runtime hỗ trợ tốt năm vai trò.

## Các case nên dùng trong báo cáo hoặc bảo vệ

- `s7-pair-da-01`: ground truth `Pass`, nhưng bị review do chênh lệch L1–L2–L3; minh họa disagreement gate.
- `s7-pair-be-01`: ground truth `Pass`, nhưng L1 thiếu requirement; minh họa giới hạn term-based L1.
- `s7-pair-qa-06`: ground truth `Reject`, nhưng hệ thống chọn review; minh họa chính sách không Reject khi L1 chưa thấy explicit failure.
- `s7-pair-de-04`: ground truth và dự đoán đều `Needs Review`; minh họa tuyến an toàn đúng.
- `s7-pair-be-05`, `s7-pair-qa-05`, `s7-pair-de-05`: minh họa ba lỗi xử lý thông tin mâu thuẫn của L3.

## Bạn cần duyệt gì

Bạn không cần chấm lại 50 ground-truth case. Hãy xác nhận ba nội dung:

1. Kết luận trung thực là runtime v1 không đạt quality gate cuối cho năm vai trò, dù các đường an toàn ứng viên hoạt động.
2. Sáu nhóm case đại diện ở trên phản ánh đúng nguyên nhân và phù hợp để đưa vào báo cáo/error analysis.
3. Chọn một trong hai hướng:
   - đóng Gate 7 với kết quả không đạt, giữ nguyên runtime và chuyển Stage 8 để demo prototype kèm hạn chế;
   - mở một chu kỳ cải tiến runtime v2 bằng development data mới, sau đó phải tạo một frozen test set mới hoàn toàn nếu muốn có tuyên bố hiệu năng mới. Không được tuning bằng 50 case Stage 7 hiện tại rồi dùng lại chúng làm final test.

Gate 7 chưa hoàn tất cho đến khi bạn xác nhận kết luận và hướng xử lý. Không cần gọi thêm API để duyệt báo cáo này.
