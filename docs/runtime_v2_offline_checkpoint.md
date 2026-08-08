# Phiếu checkpoint offline Runtime v2

Ngày ghi nhận: 2026-08-08

## Phạm vi

Checkpoint này xác nhận dữ liệu Silver và hành vi L1/L2 trước khi phát sinh thêm chi phí LLM. Nó chỉ dùng 50 case development và 25 case validation của Runtime v2. Stage 7 v1 frozen test không được mở và Runtime v1 không bị sửa.

## Dữ liệu và phân chia

- Dataset: `five-role-runtime-v2-development-v1-reviewed-silver`.
- Development: 50 cặp, 10 cặp mỗi vai trò.
- Validation: 25 cặp, 5 cặp mỗi vai trò.
- Hai partition không dùng chung ứng viên.
- Human review đã khóa requirement status, năm nhóm điểm, nhãn và rationale của cả 75 cặp.

## Kết quả L1

| Partition | Requirement đúng | Accuracy | Unsafe mismatch |
| --- | ---: | ---: | ---: |
| Development | 240/240 | 1,000 | 0 |
| Validation | 120/120 | 1,000 | 0 |

L1 chỉ lấy tín hiệu tích cực từ phần kỹ năng, kinh nghiệm và dự án được cấu hình. Education hoặc phần bối cảnh vẫn có thể chứa câu phủ định để xác định `unsatisfied`, nhưng không tự chứng minh năng lực bắt buộc.

## Kết quả L2 tích hợp

| Chỉ số | Development | Validation | Gate |
| --- | ---: | ---: | ---: |
| Total-score MAE | 4,03 | 9,68 | tối đa 15 |
| Criterion MAE | 0,89 | 1,96 | tối đa 4 |
| Correlation | 0,954 | 0,864 | tối thiểu 0,65 |
| Score range | 49,95 | 45,12 | tối thiểu 35 |
| Pass trừ Waitlist | 4,28 | 4,60 | tối thiểu 3 |
| Waitlist trừ Reject | 26,53 | 18,35 | tối thiểu 10 |

L2 gồm hai phần: embedding đa ngôn ngữ cục bộ theo query profile `rubric-quality-v3`, sau đó calibrator `extra-trees-leaf3-v1`. Calibrator được train trên development và chỉ dùng năm criterion score semantic cùng role one-hot. Validation không được dùng để fit model.

## Quy tắc an toàn và truy vết

- Model local phải khớp SHA-256 trong `configs/runtime/five_role_v2_candidate/models.yaml` trước khi được nạp.
- Model trả sai số lượng tiêu chí, số không hữu hạn hoặc điểm vượt giới hạn làm L2 `invalid` hoặc `unavailable`; hệ thống không tiếp tục như thể điểm hợp lệ.
- Report chính: `evaluation/reports/runtime_v2_offline_l1_l2_checkpoint_v1.json`.
- Report huấn luyện: `evaluation/reports/runtime_v2_l2_calibration_v1.json`.
- Không gọi LLM provider và không dùng Stage 7 v1 frozen test.

## Giới hạn còn lại

Development và validation đều là dữ liệu synthetic, đồng thời dùng chung các họ scenario ở năm vai trò. Vì vậy checkpoint chứng minh pipeline đã hết lỗi bão hòa và hoạt động nhất quán trên dữ liệu phát triển, nhưng chưa chứng minh độ chính xác trên CV thực tế hoặc cách diễn đạt hoàn toàn mới. Một frozen test Runtime v2 độc lập vẫn bắt buộc trước kết luận cuối.

## Quyết định tiếp theo

Checkpoint offline đã đạt. Bước kế tiếp được phép là L3 provider pilot nhỏ trên các case development đã chọn trước. Chỉ khi pilot đạt structured output, requirement safety và score calibration mới được gửi batch lớn hơn.
