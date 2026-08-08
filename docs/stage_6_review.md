# Stage 6 — Validation Tuning and Configuration Freeze

## Trạng thái hiện tại

Live L3 validation bằng Google AI Studio đã hoàn tất trên đúng 20 hồ sơ validation. Mười hồ sơ frozen test chưa được đưa qua classifier và chưa có prediction hoặc metric nào được tạo.

Một cấu hình mới đã đủ điều kiện kỹ thuật để trình người dùng duyệt, nhưng vẫn là `provisional_pending_human_approval`. Cấu hình chính thức chưa được cập nhật, `configuration_frozen` vẫn là `false` và Gate 6 chưa hoàn tất.

## Phạm vi dữ liệu

Ba mươi hồ sơ đã được duyệt được chia một lần bằng role-label stratification và SHA-256 ranking:

| Partition | Số case | Data Analyst | Python Backend | Pass | Waitlist | Reject | Needs Review |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Validation | 20 | 10 | 10 | 4 | 4 | 1 | 11 |
| Frozen test | 10 | 5 | 5 | 2 | 2 | 1 | 5 |

Split manifest lưu source hash, các ID không giao nhau và quy tắc cấm tuning trên frozen test. Nếu reviewed source bị thay đổi, validation loader từ chối chạy.

## Chiến lược model đã validation

| Tầng | Strategy được dùng |
| --- | --- |
| L1 | Versioned deterministic rules hiện tại |
| L2 | `intfloat/multilingual-e5-base` chạy cục bộ |
| E5 resolved revision | `d128750597153bb5987e10b1c3493a34e5a4502a` |
| L3 provider | Google AI Studio qua OpenAI-compatible API |
| L3 model | `gemini-3.5-flash-lite` |
| Prompt được chọn | `l3-evidence-rubric-v3` |

`gemini-2.5-flash` không còn khả dụng cho API key mới tại thời điểm kiểm tra. `gemini-3.5-flash` hoạt động nhưng free tier bị giới hạn tốc độ quá thấp cho batch validation. `gemini-3.5-flash-lite` trả structured output hợp lệ và phù hợp hơn với lần chạy nhỏ này.

Prompt v3 buộc model:

- trả đúng toàn bộ requirement ID và criterion ID;
- không tham chiếu evidence ID ngoài input;
- tuân thủ quan hệ giữa evidence status và số evidence ID;
- không cho điểm criterion vượt mức tối đa;
- bảo đảm `overall_score` bằng tổng năm criterion score.

Prompt v4 có thêm scoring anchors đã được smoke test trên một case mạnh và một case sát ngưỡng. Nó vẫn cho điểm case sát ngưỡng cao hơn human score đáng kể, nên không được chọn và không chạy trên toàn bộ validation.

## Chất lượng provider và output

| Kiểm tra | Kết quả |
| --- | ---: |
| Primary output hợp lệ | 20/20 |
| Structured output không hợp lệ | 0 |
| Requirement status khớp human review | 1,000 |
| Sai số tuyệt đối trung bình mỗi criterion | 2,255 điểm |
| Sai số tuyệt đối trung bình total score L3 | 8,775 điểm |
| Request primary có token usage | 20/20 |
| Thời gian trung bình primary request | 3.980 ms |
| Stability case | 4 |
| Số lần quan sát mỗi stability case | 2 |
| Score range lớn nhất | 2,5 điểm |
| Requirement status agreement giữa các lần | 1,000 |

Provider quality gate đạt. Cache chỉ lưu structured result đã validate, usage và latency; không lưu raw provider response hoặc API key. Báo cáo ghi chi phí ước tính là `0` theo giả định free tier do người dùng cung cấp, nhưng không thể xác minh billing thực tế từ phía provider.

## Vì sao candidate cũ chưa đạt

Với trọng số và threshold đã phê duyệt trước đây, candidate `approved-current-v1` đạt:

| Metric | Kết quả |
| --- | ---: |
| Accuracy | 0,650 |
| Macro-F1 | 0,362 |
| Needs Review recall | 0,818 |
| Review rate | 0,600 |
| False Reject | 0 |
| Unsafe Pass | 2 |

Hai `Unsafe Pass` là `cv-s4-be-014` và `cv-s4-da-014`. Cả hai có human score 74 và human label `Needs Review` vì nằm sát ngưỡng trên, nhưng L1, L2 và L3 đều cho tín hiệu cao nên final score không còn nằm trong boundary zone.

Các candidate hiệu chỉnh L2 loại bỏ `Unsafe Pass` nhưng chuyển 100% validation case thành `Needs Review`, vượt giới hạn review rate `0,80`. Vì vậy chúng không đủ điều kiện được đề xuất.

## Cấu hình được đề xuất

Candidate `live-l3-automatic-pass-gate-v1` giữ nguyên:

- L2 similarity floor/ceiling: `0,20–0,80`;
- aggregate weights L1/L2/L3: `45%/25%/30%`;
- ngưỡng `Pass`: `75`;
- ngưỡng `Waitlist`: `60`;
- disagreement gate: `25` điểm;
- boundary offset: `2` điểm.

Candidate bổ sung một quy tắc bảo vệ:

> Nếu routing hiện tại định tự động `Pass`, L3 phải đạt ít nhất 95 điểm. Nếu L3 thiếu hoặc dưới 95, kết quả chuyển thành `Needs Review`, không chuyển thành `Reject`.

Giá trị đúng `95` vẫn được phép `Pass`. Quy tắc không thay đổi một kết quả vốn là `Waitlist`, `Reject` hoặc `Needs Review`.

Quy tắc làm thay đổi bốn validation case:

| Case | Human label | Trước quy tắc | Sau quy tắc |
| --- | --- | --- | --- |
| `cv-s4-be-005` | Waitlist | Pass | Needs Review |
| `cv-s4-be-014` | Needs Review | Pass | Needs Review |
| `cv-s4-da-004` | Waitlist | Pass | Needs Review |
| `cv-s4-da-014` | Needs Review | Pass | Needs Review |

## Kết quả của cấu hình đề xuất

| Metric | Kết quả |
| --- | ---: |
| Accuracy | 0,750 |
| Macro-F1 | 0,454 |
| Needs Review recall | 1,000 |
| Review rate | 0,800 |
| False Reject | 0 |
| Unsafe Pass | 0 |
| Prediction Pass | 4 |
| Prediction Waitlist | 0 |
| Prediction Reject | 0 |
| Prediction Needs Review | 16 |

Candidate đạt đúng toàn bộ selection policy và được đánh dấu `eligible_for_human_approval`. Đây vẫn chỉ là validation result trên 20 case tổng hợp, không phải final performance.

## Hạn chế phải chấp nhận nếu freeze

- L2 ở khoảng `0,20–0,80` vẫn saturation ở 100 trên validation, nên đóng góp phân biệt hồ sơ của L2 hiện thấp.
- Ngưỡng L3 `95` được chọn trên tập validation nhỏ và review rate chạm đúng giới hạn `0,80`; có rủi ro validation overfitting.
- Cấu hình ưu tiên bảo vệ ứng viên, nhưng không tự động tạo `Waitlist` hoặc `Reject` trên 20 validation case.
- L3 có xu hướng cho điểm cao ở một số case đầy đủ từ khóa nhưng chất lượng hoặc tác động còn yếu.
- Kết quả free tier có thể thay đổi khi provider cập nhật model, quota hoặc chính sách.
- Chỉ sau khi freeze mới được chạy Stage 7 trên frozen test. Không được quay lại tuning theo kết quả Stage 7.

## Nội dung người dùng cần duyệt

Bạn cần xác nhận sáu quyết định:

1. Giữ split 20 validation và 10 frozen test; xác nhận frozen test chưa được xem trước Stage 7.
2. Freeze L2 là `intfloat/multilingual-e5-base` revision `d128750597153bb5987e10b1c3493a34e5a4502a`, đồng thời chấp nhận hạn chế saturation đã ghi.
3. Freeze L3 provider/model là Google AI Studio và `gemini-3.5-flash-lite`.
4. Freeze prompt `l3-evidence-rubric-v3`; giữ prompt v4 là thử nghiệm không được chọn.
5. Giữ weights `45/25/30`, threshold `75/60`, disagreement `25` và boundary offset `2`.
6. Thêm automatic Pass gate yêu cầu L3 từ `95`; chấp nhận review rate validation là `0,80` và không có automatic Waitlist/Reject trong validation.

Nếu đồng ý toàn bộ, có thể duyệt bằng câu:

> Tôi duyệt đề xuất Stage 6: giữ split và frozen-test policy; freeze E5 revision đã ghi, Gemini 3.5 Flash-Lite, prompt v3, weights 45/25/30, threshold 75/60, disagreement 25, boundary offset 2 và automatic Pass gate L3 từ 95. Tôi chấp nhận các hạn chế về L2 saturation, validation nhỏ và review rate 0,80. Hãy hoàn tất Gate 6.

Sau xác nhận này, coding agent mới tăng version các artifact chính thức, liên kết cấu hình, chạy kiểm tra freeze và đóng Gate 6. Stage 7 sau đó chỉ đánh giá cấu hình đã khóa.

## Artifact tạo hoặc thay đổi trong lần validation live

| File | Loại | Mục đích và consumer | Quyết định cần từ người dùng |
| --- | --- | --- | --- |
| `evaluation/configs/stage6_live_llm_v1.yaml` | Cấu hình evaluation | Khóa phạm vi live run, model, prompt, retry, stability và quality policy. | Duyệt model và prompt. |
| `evaluation/experiments/stage6_live_config.py` | Source code evaluation | Validate cấu hình live và cấm bật frozen test. | Không có quyết định riêng. |
| `evaluation/experiments/run_stage6_live_validation.py` | Source code evaluation | Gọi provider có cache/resume, retry output lỗi, đo usage, latency, stability và sinh report validation. | Dùng report để duyệt strategy. |
| `evaluation/reports/stage6_live_llm_validation_v1.json` | Báo cáo validation | Lưu structured result, metrics, safety, stability và traceability; không chứa raw response hoặc secret. | Xem chất lượng provider và candidate cũ. |
| `evaluation/configs/stage6_freeze_proposal_v1.yaml` | Cấu hình đề xuất | Mô tả candidate mới và automatic Pass gate; chưa phải config chính thức. | Duyệt hoặc yêu cầu sửa. |
| `evaluation/experiments/run_stage6_freeze_proposal.py` | Source code evaluation | Áp dụng quy tắc mới lên kết quả validation đã khóa hash và tính lại metrics. | Không có quyết định riêng. |
| `evaluation/reports/stage6_freeze_proposal_v1.json` | Báo cáo đề xuất | Chứng minh candidate đạt selection policy nhưng vẫn chờ human approval. | Duyệt trade-off. |
| `backend/app/agents/classifier/prompts/l3.py` | Source code prompt | Thêm prompt v3 được chọn và prompt v4 thử nghiệm, cùng constraint động theo rubric/evidence. | Duyệt prompt v3. |
| `backend/app/agents/classifier/prompts/__init__.py` | Source code export | Công khai các prompt version cho adapter và test. | Không có. |
| `backend/app/infrastructure/llm/adapters.py` | Source code hạ tầng | Đọc token usage từ OpenAI-compatible provider mà không để provider object lọt qua contract. | Không có. |
| `backend/app/infrastructure/llm/__init__.py` | Source code export | Công khai contract usage mới. | Không có. |
| `evaluation/experiments/run_stage6_validation.py` | Source code evaluation | Cho candidate runner nhận live L3 provider và ghi strategy thực tế. | Không có. |
| `tests/contract/test_llm_adapters.py` | Automated test | Kiểm tra usage parsing, malformed usage fallback và constraint của prompt. | Không có. |
| `tests/evaluation/test_stage6_live_validation.py` | Automated test | Kiểm tra cache, retry, metrics, stability, version links và frozen-test isolation. | Không có. |
| `tests/evaluation/test_stage6_freeze_proposal.py` | Automated test | Kiểm tra ngưỡng 95, fallback, metrics, source hash và không dùng frozen ID. | Không có. |

## Cập nhật lựa chọn OpenRouter L3 ngày 2026-08-01

Phần đề xuất Gemini ở trên vẫn là kết quả hợp lệ của nhánh pilot hai vai trò, nhưng không tự động chứng minh khả năng hỗ trợ năm vai trò. Với nhánh mở rộng, người dùng đã yêu cầu loại Gemma 4 và thử model OpenRouter khác.

Kết quả mới:

- Gemma 4 đã bị loại khỏi model runtime và chỉ giữ trong lịch sử experiment v1.
- Qwen3 Next 80B A3B Instruct snapshot `qwen/qwen3-next-80b-a3b-instruct-2509:free` được chọn làm mục tiêu ưu tiên nhờ định danh cố định, khả năng multilingual và Response Format.
- Hai request v15 đều trả HTTP 404 trước khi có output. Vì vậy `quality_gate_passed` và `configuration_freeze_eligible` đều là `false`.
- Các model miễn phí trung gian cũng không đạt: hoặc endpoint/provider unavailable, hoặc JSON/schema sai, hoặc điểm bão hòa. Không kết quả thất bại nào được đưa vào aggregate và không hồ sơ nào bị Reject vì lỗi provider.
- Held-out expansion và frozen test gốc vẫn chưa được chạy.

Do đó chưa có nội dung mới để người dùng duyệt nhằm đóng Gate 6. Qwen là lựa chọn mục tiêu, không phải model đã validation. Bước tiếp theo cần một endpoint cố định hoạt động: retry Qwen sau, dùng OpenRouter có credit với model ổn định, hoặc dùng lại provider riêng đã được phê duyệt trên dữ liệu synthetic. Sau đó phải chạy đủ development experiment và đạt toàn bộ quality gate trước khi yêu cầu duyệt freeze.
