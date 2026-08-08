# Phiếu duyệt kết quả Frozen Test Stage 7 Runtime v2

## Kết luận chính

Runtime `five-role-runtime-v2` đã được chạy final evaluation đúng một lần trên 50 case Gold đã khóa. Kết quả **không đạt quality gate Stage 7**.

Kết quả này được giữ nguyên. Không thay đổi Runtime v2, protocol, human label, điểm, Gold dataset hoặc loại bỏ case sau khi xem output.

## Kết quả full hybrid

| Chỉ số | Kết quả | Ngưỡng | Trạng thái |
| --- | ---: | ---: | --- |
| Accuracy | `0,48` | ít nhất `0,70` | Không đạt |
| Macro-F1 | `0,1622` | ít nhất `0,60` | Không đạt |
| Needs Review recall | `0,96` | ít nhất `0,80` | Đạt |
| Review rate | `0,98` | không quá `0,80` | Không đạt |
| False Reject | `0` | `0` | Đạt |
| Unsafe Pass | `0` | `0` | Đạt |

Classifier dự đoán 49 `Needs Review` và 1 `Waitlist`. Human ground truth gồm 10 Pass, 10 Waitlist, 25 Needs Review và 5 Reject. Có 26/50 label mismatch.

Kết quả theo vai trò:

| Vai trò | Accuracy | Macro-F1 |
| --- | ---: | ---: |
| Data Analyst | `0,40` | `0,1429` |
| Python Backend | `0,50` | `0,1667` |
| Frontend | `0,50` | `0,1667` |
| QA Engineer | `0,50` | `0,1667` |
| Data Engineer | `0,50` | `0,1667` |

Mức mục tiêu lớn hơn 70% mà người dùng chấp nhận không đạt. Đây không phải vài mismatch riêng lẻ có thể bỏ qua vì sai lệch xuất hiện ở hơn một nửa số case và review rate gần 100%.

## Kết quả L3 provider

| Chỉ số | Kết quả | Ngưỡng | Trạng thái |
| --- | ---: | ---: | --- |
| Valid structured output | `1,00` | `1,00` | Đạt |
| Requirement-status accuracy | `0,7958` | ít nhất `0,95` | Không đạt |
| Unsafe requirement mismatch | `21` | `0` | Không đạt |
| Criterion MAE | `3,038` | không quá `3` | Không đạt nhẹ |
| Total-score MAE | `11,35` | không quá `12` | Đạt |
| Stability requirement agreement | `1,00` | ít nhất `0,80` | Đạt |
| Stability route agreement | `1,00` | `1,00` | Đạt |
| Stability score range | `14,5` | không quá `10` | Không đạt |

Prompt v15 buộc L3 giữ authoritative requirement status từ L1. Vì vậy requirement accuracy `0,7958` của L3 không phải do model tự ý đổi status; nó phản ánh trực tiếp 49 mismatch của L1 trên Gold test. Điều này bảo đảm LLM không phá rule đã kiểm tra, nhưng cũng khiến sai lệch L1 truyền sang L3.

LLM provider hoạt động ổn về kỹ thuật: 55/55 output cần thiết đều hợp lệ, không có structured-output failure. Total-score MAE đạt ngưỡng. Vấn đề chính không phải API bị lỗi, mà là khả năng khái quát của L1/L2 và routing trên cách diễn đạt mới.

## Nguyên nhân chính

### L1 chưa khái quát sang cách diễn đạt mới

L1 đạt `0,7958` requirement accuracy, có 49/240 mismatch:

- 23 trường hợp human là `satisfied` nhưng L1 trả `missing`;
- 16 trường hợp human là `missing` nhưng L1 suy thành `satisfied`;
- 5 trường hợp `conflicting` bị rút gọn thành `satisfied`;
- 5 trường hợp `unsatisfied` bị hiểu thành `missing`.

Vai trò có nhiều mismatch nhất là Frontend và Data Engineer, mỗi vai trò 13; QA có 11, Backend có 7 và Data Analyst có 5. Các requirement bị ảnh hưởng nhiều nhất là `fe-testing-workflow`, `qa-automation-foundation` và `de-pipeline`.

### L2 vẫn bị nén điểm trên dữ liệu mới

Điểm L2 chỉ nằm trong khoảng `38,46–56,37`, mean `48,53`. Calibrator đã cải thiện development/validation cũ nhưng không giữ được độ phân tách trên cách viết của Gold mới.

### Routing bảo thủ bị kích hoạt quá nhiều

Các lý do chính:

- `missing-critical-evidence`: 34 case;
- `low-score-without-explicit-critical-unsatisfied`: 32 case;
- `large-level-disagreement`: 15 case;
- `lower-threshold-boundary`: 7 case.

Việc routing bảo thủ giữ false Reject và unsafe Pass bằng 0, nhưng đánh đổi bằng review rate 98% và accuracy 48%.

## Một số case đại diện cần xem

- `s7v2-pair-fe-01`: hồ sơ strong nhưng bị Needs Review; đại diện L1 bỏ sót testing workflow và điểm tổng thấp.
- `s7v2-pair-de-01`: hồ sơ strong nhưng bị Needs Review; đại diện lỗi nhận diện pipeline trong cách diễn đạt mới.
- `s7v2-pair-da-05`: human Needs Review do conflicting critical nhưng hệ thống ra Waitlist; đây là case duy nhất không đi Needs Review và cần chú ý vì conflict bị L1 rút thành satisfied.
- `s7v2-pair-be-06`: human Reject nhưng hệ thống ra Needs Review; sai nhãn nhưng theo hướng bảo thủ, không phải false Reject hay unsafe Pass.
- `s7v2-pair-fe-07`: stability score thay đổi `14,5` điểm giữa hai lượt dù requirement route giống nhau.

Chi tiết đầy đủ của 50 case nằm trong `evaluation/reports/stage7_runtime_v2_frozen_evaluation_v1.json`.

## Baseline và ablation

Không phương án nào đạt 70%:

- keyword baseline: accuracy `0,42`;
- TF-IDF baseline: accuracy `0,50`;
- embedding baseline: accuracy `0,50`;
- L1-only: `0,42`;
- L2-only: `0,50`;
- L3-only: `0,44`;
- L1-L3: `0,44`;
- L2-L3: `0,50`;
- full L1-L2-L3: `0,48`.

Điều này cho thấy thất bại không thể sửa hợp lệ bằng cách chọn lại một ablation sau khi xem test. Mọi lựa chọn lại weight, threshold, rule, prompt hoặc calibrator từ kết quả này đều là tuning theo frozen test và bị cấm.

## API usage

- 55 output hợp lệ;
- 1 request thất bại do sandbox network trước khi chạy ngoài sandbox;
- tổng 56/60 HTTP request;
- 368.620 input token, trong đó 32.000 cached input token;
- 64.711 output token;
- chi phí ước tính từ usage: `0,5460645 USD`, chưa đối chiếu hóa đơn;
- không lưu raw provider response, API key hoặc secret.

Acceptance cuối đạt: Ruff không có lỗi, 167 file Python đúng format, Pyright có 0 lỗi/cảnh báo và full pytest có `504 passed, 7 skipped`. Bảy skip là test PostgreSQL khi disposable database đang tắt. Audit cache/report không tìm thấy raw response, tên biến API key hoặc giá trị có hình dạng secret.

## Những lựa chọn hợp lệ tiếp theo

### Lựa chọn 1: đóng Gate 7 với kết quả không đạt

Giữ báo cáo làm kết quả cuối trung thực, sang Stage 8 xây demo và trình bày rõ rằng prototype an toàn nhưng tự động hóa chưa đạt mục tiêu 70%. Không được quảng bá Runtime v2 là mô hình đạt chuẩn năm vai trò.

### Lựa chọn 2: mở chu kỳ Runtime v3

Giữ Runtime v2 và Gold test này làm lịch sử bất biến. Tạo development data mới tập trung vào 49 pattern L1 và độ nén L2, nhưng không dùng lại 50 Gold case này làm benchmark cuối. Sau khi cải thiện trên development mới phải tạo một test set độc lập khác và human review lại trước final evaluation. Phương án này dài và có thể phát sinh thêm API cost; không bảo đảm chắc chắn đạt 70%.

## Nội dung cần người dùng xác nhận

Hãy kiểm tra kết luận, năm case đại diện và lựa chọn một trong hai hướng. Nếu chấp nhận đóng Gate 7 với quality gate không đạt:

> Tôi xác nhận kết quả Frozen Test Stage 7 Runtime v2 là accuracy 48%, quality gate không đạt nhưng không có false Reject hoặc unsafe Pass; tôi chấp nhận giữ nguyên report, không tuning theo test output và đóng Gate 7 với hạn chế đã ghi để chuyển sang Stage 8.
