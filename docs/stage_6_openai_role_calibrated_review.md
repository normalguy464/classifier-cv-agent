# Review Stage 6 — OpenAI role-calibrated hybrid v8

Ngày tạo: 2026-08-01

## Kết luận ngắn

Experiment v8 đã hoàn thành trên 25 cặp CV-JD development cân bằng cho năm vai trò và năm lần chấm lặp. Quality gate development đạt, không có false Reject, không có unsafe Pass và không truy cập held-out hoặc frozen test.

Kết quả này đủ để đề xuất một cấu hình năm vai trò cho bước review và tạo artifact freeze, nhưng chưa phải kết quả cuối cùng của Stage 7. Dataset vẫn ở tầng Silver với một human reviewer và ba vai trò mới chưa có runtime configuration chính thức.

## Thiết kế đã thay đổi

### 1. LLM không tự quyết định điểm số tuyệt đối

Prompt `l3-evidence-rubric-v12` yêu cầu GPT-5.4 mini:

- đánh giá trạng thái của từng requirement độc lập;
- chọn một `calibration_level` định tính cho từng criterion;
- trích dẫn đúng evidence ID và giải thích ngắn;
- không trả criterion score hoặc overall score.

Code xác định ánh xạ mức định tính thành điểm. Version của ánh xạ là `l3-deterministic-level-mapping-v1`.

| Calibration level | Hệ số cơ bản |
| --- | ---: |
| `unsupported` | 0,00 |
| `minimal` | 0,20 |
| `limited` | 0,40 |
| `developing` | 0,60 |
| `competent` | 0,75 |
| `strong` | 0,85 |
| `exceptional` | 1,00 |

Criterion `mandatory-requirements` còn áp dụng policy trạng thái: tất cả missing là 0,47; có unsatisfied là 0,33; có conflicting là 0,73; có missing là 0,67; tất cả satisfied có mức sàn 0,93. Điểm được làm tròn đến 0,5 và không vượt weight `30/25/20/15/10`.

Mục tiêu của thay đổi này là để LLM tập trung đọc và phân loại thông tin, còn phép tính điểm, giới hạn và tổng điểm do code kiểm soát và kiểm thử được.

### 2. Prompt có profile riêng cho năm vai trò

Mỗi vai trò có trọng tâm riêng cho kỹ thuật chuyên môn, năng lực theo vai trò, dự án/tác động và độ rõ ràng của thông tin. Prompt v12 còn thêm capability guard, ví dụ:

- ETL, pipeline hoặc SQL không tự chứng minh Python cho Data Engineer;
- API, framework hoặc deployment không tự chứng minh Python cho Backend;
- câu phủ định JavaScript/TypeScript không phủ định HTML/CSS đã được chứng minh riêng;
- thông tin phủ định chỉ ảnh hưởng requirement atom mà nó trực tiếp gọi tên.

Prompt không chứa human label, expected score hoặc quyết định tuyển dụng của từng case.

### 3. Quality gate không tăng MAE để hợp thức hóa output

Các ngưỡng calibration vẫn giữ:

- valid output rate: 1,00;
- criterion MAE tối đa: 3,5;
- total-score MAE tối đa: 12;
- endpoint-score rate tối đa: 0,40;
- maximum stability score range: 10.

Requirement-status gate được tách thành hai điều kiện:

- raw match rate tối thiểu 0,95;
- unsafe requirement mismatch bắt buộc bằng 0.

Một mismatch là unsafe nếu model chuyển trạng thái sang `satisfied` hoặc `unsatisfied` theo hướng có thể tạo automatic Pass/Reject sai. Sai lệch sang `missing` hoặc `conflicting` chỉ được xem là bảo thủ khi nó dẫn tới human review. Raw match rate vẫn ngăn model lạm dụng `Needs Review` cho quá nhiều requirement.

### 4. Stability được đo cả độ giống tuyệt đối và ảnh hưởng định tuyến

V8 yêu cầu:

- exact requirement-status agreement tối thiểu 0,80;
- requirement-route agreement bằng 1,00;
- score range tối đa 10.

Hai lần chấm Frontend khác nhau ở `fe-web-foundations`: một lần là `satisfied`, một lần là `conflicting`. Cả hai lần vẫn có `fe-language=conflicting`, nên đều bắt buộc đi `Needs Review`. Vì vậy exact agreement là 0,80 nhưng route agreement là 1,00. Nếu sự khác nhau có thể đổi giữa automatic decision và human review, stability gate sẽ thất bại.

### 5. Hybrid candidate mới

Candidate `openai-role-calibrated-hybrid-v1` được chọn bằng grid-search chỉ trên development, dưới các ràng buộc bảo vệ ứng viên đã khóa trước:

- L1/L2/L3: `40% / 20% / 40%`;
- `Waitlist` từ 70;
- `Pass` từ 85;
- large disagreement từ 35;
- boundary offset 2;
- L2 tiếp tục dùng `coverage-70-95-v1`, `top_k=1`, minimum query score 20.

Đây là candidate mới, không ghi đè artifact Stage 1 hoặc lịch sử candidate cũ. Việc thay đổi phản ánh L3 thật đã ổn định hơn và tránh L1 nhị phân kéo hồ sơ moderate lên automatic Pass.

## Kết quả development v8

### Provider và calibration

| Chỉ số | Kết quả | Điều kiện | Đạt |
| --- | ---: | ---: | --- |
| Valid output | 1,0000 | 1,0000 | Có |
| Requirement-status match | 0,9917 | tối thiểu 0,95 | Có |
| Unsafe requirement mismatch | 0 | tối đa 0 | Có |
| Criterion MAE | 1,892 | tối đa 3,5 | Có |
| Total-score MAE | 7,74 | tối đa 12 | Có |
| Endpoint-score rate | 0,00 | tối đa 0,40 | Có |

Chỉ có 1/120 requirement status không khớp human review: `fe-web-foundations` được model đánh dấu `conflicting` thay vì `satisfied`. Đây là sai lệch bảo thủ; case đã có một requirement khác là `conflicting` và vẫn đi `Needs Review`.

### Stability

| Chỉ số | Kết quả | Điều kiện | Đạt |
| --- | ---: | ---: | --- |
| Maximum score range | 10 | tối đa 10 | Có |
| Exact requirement agreement | 0,80 | tối thiểu 0,80 | Có |
| Requirement-route agreement | 1,00 | 1,00 | Có |

### Hybrid

| Chỉ số | Kết quả | Điều kiện bảo vệ | Đạt |
| --- | ---: | ---: | --- |
| Accuracy | 0,88 | báo cáo | — |
| Macro-F1 | 0,7558 | primary metric | — |
| Needs Review recall | 1,00 | 1,00 | Có |
| False Reject | 0 | 0 | Có |
| Unsafe Pass | 0 | 0 | Có |
| Review rate | 0,64 | tối đa 0,80 | Có |

## Request và chi phí

- 30/30 request có output hợp lệ; không có retry hoặc request lỗi trong v8 cache.
- Tổng chuỗi OpenAI là 53/55 request theo series cap.
- Chi phí ước tính từ usage là 0,2497992 USD cho 30 request; mọi request đều có usage.
- Đây là ước tính cục bộ, chưa phải số tiền đã đối soát hóa đơn (`charge_verified=false`).
- Cache v6 được chuyển sang policy v7/v8 chỉ vì model, prompt, dataset, request policy và schema giống hệt. Hàm migration từ chối tái sử dụng nếu prompt hoặc request thay đổi.

## Điều chưa được phép kết luận

- Không được gọi đây là hiệu năng cuối cùng vì held-out và frozen test chưa chạy.
- Không được tuyên bố khả năng khái quát trên CV thực hoặc output Parser.
- Dataset 250 cặp vẫn là synthetic Silver với một reviewer, chưa phải Gold.
- Exact stability mới đạt ngưỡng dưới 1,00; sai lệch Frontend phải được ghi trong báo cáo.
- Grid-search dùng development nên kết quả có nguy cơ overfit; Stage 7 mới kiểm tra khả năng giữ kết quả trên dữ liệu đã khóa.
- Ba vai trò Frontend, QA và Data Engineer còn cần Job Profile/rubric/L1/L2/model strategy runtime artifact chính thức trước khi tuyên bố hỗ trợ đầy đủ năm vai trò.

## Nội dung cần người dùng duyệt

1. Prompt v12 và năm role calibration profile.
2. Ánh xạ định tính thành điểm `l3-deterministic-level-mapping-v1`.
3. Requirement safety gate: match tối thiểu 0,95 và unsafe mismatch bằng 0.
4. Stability gate: exact agreement tối thiểu 0,80, route agreement 1,00 và score range tối đa 10.
5. Hybrid candidate `40/20/40`, thresholds `70/85`, disagreement 35 và boundary offset 2.
6. Việc giữ mismatch Frontend là hạn chế đã biết, không sửa human label và không nới MAE.
7. Giữ held-out/frozen test đóng cho đến khi artifact freeze hoàn tất.

Nếu đồng ý, có thể xác nhận:

> Tôi duyệt OpenAI role-calibrated hybrid v8 trên development, gồm prompt v12, deterministic level mapping v1, requirement safety gate 0,95/0, stability gate 0,80/1,00/10 và hybrid candidate L1/L2/L3 40/20/40 với Waitlist 70, Pass 85, disagreement 35, boundary offset 2. Tôi chấp nhận một mismatch Frontend bảo thủ đã được ghi nhận, không sửa human label hoặc MAE gate; hãy tạo runtime artifact năm vai trò và chuẩn bị configuration freeze Gate 6, chưa mở held-out hoặc frozen test.

Nếu chưa đồng ý, hãy chỉ rõ mục và giá trị muốn thay đổi. Không nên chỉ nói “tăng MAE” hoặc “bỏ stability gate” vì sẽ làm mất khả năng truy vết rủi ro.

## Artifact để kiểm tra

- Config v8: `evaluation/configs/synthetic_expansion_l3_openai_gpt_5_4_mini_v8.yaml`
- Report v8: `evaluation/reports/synthetic_expansion_v2_openai_gpt_5_4_mini_l3_validation_v8.json`
- Prompt: `backend/app/agents/classifier/prompts/l3.py`
- Deterministic mapping: `backend/app/agents/classifier/scoring/l3_calibration.py`
- Runner và quality gates: `evaluation/experiments/run_synthetic_expansion_v2_l3_validation.py`

