# Theo dõi thay đổi và việc cần khắc phục từ Stage 1 đến Stage 6

Ngày cập nhật: 2026-08-07

## Mục đích

Tài liệu này tập hợp các phần đã phải sửa, đang cần sửa hoặc có thể cải tiến từ Stage 1 đến Stage 6. Nó giúp tránh quên hạn chế khi chuyển Stage, viết báo cáo hoặc mở rộng dự án.

`progress.md` vẫn là nguồn trạng thái chính thức của dự án. File này là danh sách theo dõi theo Stage và phải được cập nhật khi một hạn chế được xử lý, được người dùng chấp nhận hoặc phát sinh việc mới.

## Cách đọc trạng thái

| Trạng thái | Ý nghĩa |
| --- | --- |
| Hoàn tất | Đã sửa hoặc đã được người dùng duyệt; không làm lại nếu không có bằng chứng mới. |
| Hoàn tất kỹ thuật, đang chờ freeze | Source, artifact và test đã xong nhưng chưa trở thành cấu hình khóa cho đến khi người dùng duyệt manifest. |
| Đã chấp nhận hạn chế | Hạn chế đã được ghi nhận và không chặn Gate tương ứng, nhưng vẫn phải nêu trong báo cáo. |
| Đang chờ duyệt | Đã có phương án hoặc kết quả, cần quyết định của người dùng trước khi trở thành cấu hình chính thức. |
| Bắt buộc trước Gate 6 | Phải hoàn thành hoặc được người dùng chấp nhận rõ ràng trước khi đóng Gate 6. |
| Bắt buộc nếu tuyên bố hỗ trợ năm vai trò | Không chặn pilot hai vai trò, nhưng bắt buộc nếu báo cáo kết quả chính thức cho ba vai trò mới. |
| Cải tiến khuyến nghị | Không phải lỗi chức năng tức thời, nhưng nên làm để tăng độ tin cậy hoặc khả năng áp dụng thực tế. |
| Ngoài phạm vi Classifier hiện tại | Thuộc Parser, Stage 7, Stage 8 hoặc vận hành production; không được coi là lỗi chưa sửa của Classifier Agent. |

## Tóm tắt việc còn mở

| Mức ưu tiên | Việc còn mở | Phạm vi | Điều kiện hoàn thành |
| --- | --- | --- | --- |
| Hoàn tất | Duyệt L2 `coverage-70-95-v1` | Nhánh mở rộng năm vai trò | Người dùng đã duyệt làm development candidate; chưa phải hybrid freeze và không mở held-out/frozen test. |
| Hoàn tất | Chọn hybrid v8 cho năm vai trò | Toàn Stage 6 | Người dùng đã duyệt v8; prompt, mapping, weights, thresholds và safety gate đã được chuyển vào runtime đã khóa. |
| Hoàn tất | Khóa bộ runtime `five-role-runtime-v1` | Năm vai trò | Người dùng đã duyệt manifest và chính sách xử lý held-out ngày 2026-08-07; manifest đã chuyển sang `frozen_for_stage7`. |
| Hoàn tất việc loại model | Loại OpenRouter Gemma 4 khỏi runtime đang dùng | Nhánh mở rộng năm vai trò | Gemma 4 chỉ còn trong lịch sử v1; `.env` đã chuyển sang snapshot Qwen được đề xuất. |
| Đã sàng lọc nhưng chưa đạt | Kiểm tra các L3 miễn phí thay thế | Nhánh mở rộng năm vai trò | Các experiment có version riêng ghi nhận malformed JSON, schema mismatch, HTTP 404/429/502 và provider error; không model nào được phép freeze từ các kết quả này. |
| Hoàn tất | Duyệt OpenAI role-calibrated hybrid v8 | Nhánh mở rộng năm vai trò | Người dùng đã duyệt v8 sau khi panel, primary, stability-safety và hybrid gate đều đạt trên development. |
| Hoàn tất | Hoàn thiện runtime configuration cho Frontend, QA và Data Engineer | Ba vai trò mới | Job Profile, rubric, L1 policy, L2 policy, model strategy, version link và contract test đã có trong runtime đã khóa. |
| Bắt buộc nếu tuyên bố kết quả chuẩn năm vai trò | Thay expansion held-out đã bị ảnh hưởng | Stage 7 năm vai trò | Tạo test set mới theo candidate, khóa trước evaluation và không điều chỉnh cấu hình theo output; bộ held-out hiện tại chỉ còn dùng cho diagnostics. |
| Bắt buộc nếu tuyên bố kết quả chuẩn năm vai trò | Nâng dữ liệu Silver lên Gold | Bộ 250 cặp | Có reviewer độc lập bổ sung, xử lý bất đồng, audit trail và QC đạt. |
| Cải tiến khuyến nghị | So sánh E5 query coverage với reranker hoặc cross-encoder | L2 | Chạy trên development, ghi quality/safety/latency và không xem held-out. |
| Cải tiến khuyến nghị | Thu thập pilot CV thực đã đồng ý sử dụng hoặc ẩn danh không thể đảo ngược | Khả năng khái quát | Có JD cố định, annotation theo rubric, group split và báo cáo synthetic/real tách riêng. |
| Cải tiến khuyến nghị | Đánh giá parser-derived `CVProfile` so với bản do con người chuẩn hóa | End-to-end | Parser tồn tại; cùng CV được so sánh ở classifier-only và parser-to-classifier. |
| Trước khi tuyên bố acceptance có database | Chạy lại bảy test PostgreSQL đang bị skip | Persistence | Docker PostgreSQL test hoạt động; migration và repository tests qua, runtime DB và test DB tách biệt. |

## Stage 1 — Requirements và Rubric

### Đã hoàn tất

- Hai Job Profile Junior Data Analyst và Junior Python Backend Developer 0–2 năm, rubric `30/25/20/15/10`, weights `45/25/30`, thresholds và chính sách ưu tiên `Needs Review` đã được người dùng duyệt.
- Phân biệt yêu cầu bắt buộc với ưu tiên, thiếu thông tin với không đáp ứng, đồng thời loại protected attributes khỏi scoring.
- Job Profile là mô tả vị trí tuyển dụng có cấu trúc, không phải định dạng CV mà nhà tuyển dụng hoặc ứng viên phải tự tạo.

### Thay đổi phát sinh sau Stage 1

- Bộ mở rộng ban đầu bị đánh giá gần mức Intern. Yêu cầu Junior đã được đối chiếu thị trường và tạo lại thành synthetic expansion v2 khó hơn cho năm vai trò.
- Thay đổi v2 không ghi đè hai artifact Stage 1 đã duyệt. Nó là nhánh mở rộng riêng để giữ audit trail và tránh làm mất cơ sở của pilot cũ.

### Còn mở

| Việc | Trạng thái | Cách xử lý |
| --- | --- | --- |
| Ba vai trò Frontend, QA và Data Engineer chưa phải vai trò runtime chính thức | Bắt buộc nếu tuyên bố hỗ trợ năm vai trò | Duyệt và version hóa Job Profile, rubric, L1/L2/model configuration cho từng vai trò. |
| Yêu cầu thị trường có thể thay đổi theo thời gian | Cải tiến khuyến nghị | Định kỳ tạo phiên bản market calibration mới; không sửa âm thầm artifact cũ. |

## Stage 2 — Data Contracts

### Đã hoàn tất

- Contract `CVProfile`, `JobProfile`, `ScoringRubric`, `ClassificationConfig`, `Evidence`, `ClassificationResult` và `ApprovedDecision` đã được định nghĩa, kiểm thử và đóng băng schema v1 cho pilot.
- Contract phân biệt `missing`, `unsatisfied` và `conflicting`; chỉ `ApprovedDecision` được phép đi tới agent downstream.
- PDF và DOCX không phải input trực tiếp của Classifier. Parser tương lai phải chuyển chúng thành `CVProfile` có version.

### Còn mở

| Việc | Trạng thái | Cách xử lý |
| --- | --- | --- |
| Chưa đo lỗi khi Parser chuyển PDF/DOCX thành `CVProfile` | Ngoài phạm vi Classifier hiện tại | Khi Parser tồn tại, tạo contract/integration test và đo suy giảm end-to-end trên cùng hồ sơ đã chuẩn hóa. |
| Thay đổi public contract trong tương lai | Chỉ thực hiện khi có yêu cầu mới | Tăng schema version, viết migration note và contract test; không sửa schema v1 tại chỗ. |

## Stage 3 — Pilot Dataset

### Đã hoàn tất

- Mười CV synthetic pilot đã được người dùng duyệt về requirement status, năm nhóm điểm, label và rationale.
- Hai quy tắc bảo vệ ứng viên đã được bổ sung và mười case đã được kiểm tra lại.
- Gate 3 đã đóng; không còn structural ambiguity bắt buộc phải sửa trong rubric pilot.

### Hạn chế phải giữ trong báo cáo

| Hạn chế | Trạng thái | Cách khắc phục nếu cần kết quả mạnh hơn |
| --- | --- | --- |
| Chỉ có 10 hồ sơ synthetic và chủ yếu một reviewer | Đã chấp nhận hạn chế cho pilot | Dùng dữ liệu lớn hơn, reviewer độc lập và adjudication; không sửa label cũ chỉ để tăng metric. |
| CV synthetic sạch và gần vocabulary của rubric | Đã chấp nhận hạn chế cho pilot | Bổ sung CV thực đã ẩn danh, hard negative, thông tin mơ hồ, lỗi chính tả và dữ liệu parser-derived. |

## Stage 4 — Classifier Core, API và Persistence

### Đã hoàn tất

- Đã triển khai L1, L2, L3, aggregation, routing, LangGraph workflow, application use case, FastAPI, authentication, memory/PostgreSQL repository, Alembic migration và pgvector-compatible storage.
- Ba mươi hồ sơ Stage 4 đã được người dùng duyệt; draft và human decision được lưu tách riêng.
- Khi PostgreSQL test service hoạt động, Stage 4 từng đạt migration check và full test không có skip; Gate 4 đã đóng.

### Còn mở hoặc chuyển sang Stage khác

| Việc | Trạng thái | Cách xử lý |
| --- | --- | --- |
| Frontend chưa được scaffold | Ngoài phạm vi Stage 4 đã duyệt; thuộc Stage 8 | Tạo Next.js demo sau khi cấu hình classifier được freeze và API contract ổn định. |
| Bảy PostgreSQL test hiện bị skip vì test service đang dừng | Trước khi tuyên bố acceptance có database | Chạy Docker PostgreSQL, Alembic check và full integration suite; không đổi code chỉ để bỏ skip. |
| Chưa có authorization/retention/privacy ở mức production | Ngoài phạm vi internship release hiện tại | Thiết kế trước khi dùng CV thực hoặc triển khai nhiều người dùng. |

## Stage 5 — Classifier Review

### Đã hoàn tất

- Workflow xác định đã chạy trên 30 hồ sơ human-reviewed.
- L1 requirement status khớp 30/30; 14 label mismatch được người dùng xác nhận là hạn chế của hashing L2 và deterministic L3, không phải lý do sửa human label hoặc rubric.
- Năm `Needs Review` case đại diện và quality gate đã được duyệt; Gate 5 đã đóng.

### Hạn chế phải giữ trong báo cáo

| Hạn chế | Trạng thái | Ý nghĩa |
| --- | --- | --- |
| Hashing embedding và deterministic L3 không đại diện model thật | Đã chấp nhận hạn chế | Stage 5 chỉ chứng minh workflow, traceability và fallback; không dùng metric đó làm hiệu năng cuối. |
| 30 hồ sơ cũ đơn giản hơn synthetic expansion v2 | Đã chấp nhận hạn chế | Giữ nguyên làm regression dataset; không trộn thành record độc lập với v2 nếu có nguy cơ leakage. |

## Stage 6 — Validation, Tuning và Configuration Freeze

### Đã hoàn tất

- Đã tạo split bất biến 20 validation và 10 frozen test cho pilot hai vai trò. Mười frozen-test case chưa từng được chạy.
- Live L3 hai vai trò đã chạy bằng Google AI Studio `gemini-3.5-flash-lite` và prompt `l3-evidence-rubric-v3` trên validation. Output 20/20 hợp lệ, requirement status khớp human review và không lưu API key hoặc raw provider response.
- Đã đề xuất automatic Pass gate yêu cầu L3 từ 95. Trên 20 validation case, candidate này có zero unsafe Pass, zero false Reject, review rate 0,80, Accuracy 0,750 và Macro-F1 0,454.
- Synthetic expansion v2 có 250 cặp cho năm vai trò, đã được một reviewer xác nhận thành Silver và chia theo ứng viên thành 150 development cùng 100 held-out.
- L2 query coverage `coverage-70-95-v1` đã loại bỏ bão hòa: khoảng điểm 28,12–72,00, không còn điểm 100, MAE 10,010, tương quan theo ứng viên 0,757, zero unsafe Pass và tách strong khỏi hard negative ở 5/5 vai trò.
- Report L2 tuning chỉ dùng 150 development case. Sau v8, một test L1 runtime đã vô tình tính tám pair thuộc held-out và dẫn tới một rule correction; vì vậy toàn bộ expansion held-out hiện tại không còn là final benchmark độc lập. Mười frozen-test case cũ vẫn chưa được mở.
- Live L3 OpenRouter dùng `google/gemma-4-26b-a4b-it:free` đã dừng sớm đúng policy sau 11 HTTP request. Có 4 output hợp lệ trên 8 case đã thử, 7 request lỗi structured output và cả 4 điểm hợp lệ đều ở 0 hoặc 100.
- Report `synthetic_expansion_v2_openrouter_l3_validation_v1.json` ghi quality gate không đạt, không chạy hybrid/stability, không lưu raw response hoặc secret và không mở held-out/frozen test.
- Đã chạy experiment Gemini v16 trên 25 cặp Silver development cân bằng năm vai trò và năm stability repeat. Có 30 output hợp lệ sau 31 HTTP request; một output sai schema đã được retry đúng policy.
- Report `synthetic_expansion_v2_google_ai_studio_l3_validation_v1.json` không lưu raw response hoặc secret và không mở held-out/frozen test. Requirement match đạt 0,975 nhưng criterion MAE 3,656, total-score MAE 15,24 và maximum stability range 15 nên quality gate không đạt.
- OpenAI v4 dùng schema động và đạt 5/5 output hợp lệ cùng requirement match 1,0 trên panel. Total-score MAE 13,3 vượt ngưỡng 12 nên panel gate không mở batch; tổng chuỗi OpenAI dừng ở 18/45 request.
- OpenAI v8 dùng prompt v12 và deterministic level mapping v1. Ba mươi output đều hợp lệ; requirement match 0,9917, unsafe mismatch 0, criterion MAE 1,892, total-score MAE 7,74 và endpoint-score rate 0.
- Stability v8 có exact status agreement 0,80, route agreement 1,00 và maximum score range 10. Hybrid candidate `40/20/40`, thresholds `70/85` và disagreement 35 đạt accuracy 0,88, macro-F1 0,7558, `Needs Review` recall 1,00, false Reject 0, unsafe Pass 0 và review rate 0,64.
- V8 development quality gate đạt và đã được người dùng duyệt. Chi phí ước tính cho 30 request là 0,2497992 USD và chưa đối soát hóa đơn.
- Đã tạo và khóa runtime `five-role-runtime-v1`: năm Job Profile `2.0.0`, năm rubric `2.0.1`, scoring/models/L1 rules `2.0.0`, manifest `1.0.0`, embedding revision cố định và provider/model L3 bị khóa theo v8.
- Contract test xác nhận năm Job Profile/rubric runtime khớp chính xác input `standard` của v8, đủ 24 L1 rule và bốn trạng thái requirement, đúng L2 coverage, model lock và SHA-256 manifest.
- Acceptance runtime candidate đạt 82 test tập trung, Ruff lint/format, Pyright 0 lỗi và toàn suite `405 passed, 7 skipped`; bảy test skip thuộc PostgreSQL khi test database chưa chạy.

### Việc bắt buộc còn mở

| Việc | Phạm vi | Điều kiện hoàn thành |
| --- | --- | --- |
| L2 `coverage-70-95-v1` đã được duyệt | Năm vai trò | Hoàn tất cho development; candidate chưa tự động là final hybrid model và có thể được so sánh với reranker nếu người dùng yêu cầu. |
| Duyệt OpenAI role-calibrated hybrid v8 | Năm vai trò | Hoàn tất: người dùng đã duyệt prompt v12, deterministic mapping, safety gate và hybrid candidate. |
| Tăng version và liên kết official artifacts sau khi được duyệt | Năm vai trò | Hoàn tất: runtime config, prompt, model strategy và scoring config đã version hóa, liên kết, kiểm tra và freeze ngày 2026-08-07. |
| Chấp nhận chính sách thay held-out | Năm vai trò | Hoàn tất cho Gate 6: expansion held-out hiện tại chỉ dùng diagnostics; Stage 7 tạo test set mới nếu muốn kết luận năm vai trò. |
| Nâng dữ liệu đánh giá mới lên Gold trước final evaluation năm vai trò | Năm vai trò | Reviewer độc lập, adjudication, QC và manifest test set đều hoàn tất trước khi chạy classifier. |

### Hạn chế chưa được khắc phục hoàn toàn

- L2 embedding đo semantic relevance và query coverage, không xác minh lời khai trong CV là thật, không tự xử lý phủ định hoặc mâu thuẫn thay cho L1/L3.
- Candidate L2 mới chưa được thử trên CV thực, dữ liệu nhiễu hoặc output của Parser; khả năng khái quát chưa được chứng minh.
- Hybrid v8 đã dùng GPT-5.4 mini thật và giảm review rate development xuống 0,64, nhưng mới chạy trên 25 cặp Silver được chọn trước; chưa chứng minh khả năng khái quát.
- Live L3 hai vai trò vẫn có xu hướng cho điểm cao ở một số case; automatic Pass gate giảm rủi ro nhưng làm review rate lên 0,80 và chưa tạo automatic Waitlist/Reject trên validation.
- Validation hai vai trò chỉ có 20 case, frozen test chỉ có 10 case và class distribution nhỏ; metric có độ bất định cao.
- Bộ 250 cặp vẫn là synthetic Silver với một reviewer. Nó cải thiện độ phủ vai trò và case nhưng chưa phải ground truth Gold.
- Free-tier provider có thể đổi model, quota, latency và chính sách. Runtime phải retry có giới hạn, theo dõi usage và fallback về `Needs Review`.
- Gemma 4 free qua OpenRouter không đạt quality gate: tỷ lệ output hợp lệ theo request là 0,3636, ba case hết retry và output hợp lệ bão hòa ở điểm cực trị. Không được dùng các điểm hợp lệ còn lại để bỏ qua lỗi provider.
- Gemini v16 có valid-output coverage đầy đủ nhưng chưa đạt calibration/stability: requirement match 0,975, criterion MAE 3,656, total-score MAE 15,24 và maximum stability range 15. Hybrid an toàn bằng cách đưa 25/25 case vào `Needs Review`, nhưng review rate 1,0 chưa chứng minh khả năng tự động hóa.
- OpenAI v4 đã khắc phục lỗi contract của panel v3 bằng schema động, nhưng score calibration chưa đạt: criterion MAE 2,78 đạt, total-score MAE 13,3 không đạt. Không có stability result vì batch bị khóa đúng policy.
- OpenAI v8 đạt development gate nhưng còn một requirement mismatch Frontend bảo thủ và exact stability agreement 0,80. Hai lần chấm giữ route agreement 1,00; hạn chế này phải được báo cáo và không được mô tả là exact stability hoàn hảo.
- Hybrid candidate v8 được chọn bằng grid-search trên development nên có nguy cơ overfit. Không được thay đổi candidate theo kết quả held-out/frozen test sau khi Gate 6 đã freeze.
- Expansion held-out hiện tại không còn độc lập do tám pair bị chạm trong test L1 và `be-python` được sửa sau output. Không được dùng metric từ partition này để tuyên bố final performance; original frozen test còn độc lập nhưng chỉ có hai vai trò.
- Prompt calibration v5 trong Gemini v17 giảm criterion MAE xuống 2,9144, total-score MAE xuống 9,58, endpoint-score rate xuống 0 và maximum stability range xuống 3. Requirement match giảm còn 0,9417 và hybrid vẫn review 25/25 case nên quality gate tổng thể chưa đạt.
- Bảy requirement mismatch v17 gồm năm lỗi prompt scoping trong một QA explicit-failure case và hai xung đột giữa human `missing` với evidence trực tiếp nêu SQL/Python. Hai xung đột dữ liệu cần người dùng phê duyệt trước khi tạo dataset version mới và chạy lại QC/L2/L3.
- Không được gửi CV thật còn PII hoặc dữ liệu nhạy cảm qua provider free tier khi chưa có chính sách và sự đồng ý phù hợp.

## Artifact lịch sử không được sửa lại để làm đẹp kết quả

- Hai Job Profile và rubric Stage 1 đã duyệt cho Data Analyst và Python Backend.
- Contract schema v1 đã freeze cho pilot, trừ khi có migration version mới.
- Mười pilot annotation Stage 3 và ba mươi human label Stage 4.
- Report mismatch Stage 5 và các failed case dùng cho error analysis.
- Bronze v1/v2 và Silver review audit trail; mọi thay đổi phải tạo version mới.
- Split manifest 20/10 của Stage 6 và 150/100 của expansion v2. Manifest 150/100 được giữ làm audit, không được viết lại để che sự cố held-out.
- Mười frozen-test case không được chạy trước khi Gate 6 đóng. Một trăm held-out expansion đã mất tư cách final benchmark và chỉ được dùng cho diagnostics có ghi chú.

## Thứ tự tiếp tục được khuyến nghị

1. L2 `coverage-70-95-v1` đã được người dùng duyệt cho development.
2. Gemma 4 free đã bị loại khỏi runtime; giữ report v1 làm lịch sử lỗi.
3. OpenAI v8 đã đạt development quality gate và được người dùng duyệt.
4. Runtime artifact chính thức cho năm vai trò đã được tạo, liên kết và kiểm tra.
5. Người dùng đã duyệt `docs/stage_6_five_role_runtime_freeze_review.md`; artifact được freeze và Gate 6 đóng ngày 2026-08-07.
6. Stage 7 chỉ dùng test set còn độc lập, không tuning lại theo kết quả test. Kết luận năm vai trò cần test set mới; original frozen test chỉ dùng cho hai vai trò cũ.

## Cập nhật thay thế L3 ngày 2026-08-01

- Adapter và runner đã được mở rộng để kiểm soát `require_parameters`, Response Healing, retry tổng, lỗi provider, score saturation và sai số so với human score. Mọi output vẫn phải qua Pydantic và kiểm tra ID/điểm/evidence trước aggregation.
- Các thử nghiệm thay thế dùng cùng 25 case development đã chọn trước và 5 stability repeat dự kiến; hard cap là 40 request cho mỗi experiment. Held-out và frozen test không được truy cập.
- GPT-OSS 20B có endpoint nhưng không đạt contract: malformed JSON hoặc requirement assessment sai cấu trúc sau retry. Các model cố định miễn phí khác được thử trả HTTP 404, HTTP 502 hoặc provider error envelope trước khi có output hợp lệ.
- Qwen3 Next 80B A3B Instruct snapshot `2509` được chọn làm mục tiêu vì có định danh snapshot, multilingual instruction following và Response Format. Hai request thực tế đều trả HTTP 404, nên report v15 dừng ở `stopped_provider_unavailable` và không đủ điều kiện freeze.
- Tại checkpoint OpenRouter, `.env` từng được cấu hình cho Qwen snapshot. `.env` cục bộ không phải nguồn cấu hình chính thức; runtime đã khóa hiện chỉ chấp nhận OpenAI `gpt-5.4-mini-2026-03-17` theo manifest.
- Cách khắc phục ưu tiên: retry khi OpenRouter có endpoint; hoặc nạp credit nhỏ và chọn fixed provider ổn định; hoặc dùng lại provider riêng đã được phê duyệt cho dữ liệu synthetic. Không dùng random free router làm model frozen và không gửi CV thật/PII qua free tier.

## Cập nhật QA remediation và Gemini v22 ngày 2026-08-01

- Dataset Silver 2.3.0 đã bỏ ba nhóm thông tin testing-foundation mâu thuẫn trong `cv-syn-qa-failed-v2`. Bản vá 2.3.1 làm câu phủ định nêu rõ STLC và các kỹ thuật thiết kế test để thể hiện đúng trạng thái `qa-testing-foundations=unsatisfied` đã được duyệt.
- Năm cặp CV-JD liên quan giữ nguyên requirement status, năm nhóm điểm, nhãn và rationale. QC đạt 50 CV, 25 JD, 25 rubric và 250 cặp, không có lỗi hoặc cảnh báo; membership development/held-out không đổi.
- L2 `coverage-70-95-v1` tiếp tục được đề xuất trên 150 development pair, total-score MAE 9,9196, không có điểm 100, zero false Reject và zero unsafe Pass.
- Prompt v8 phân biệt direct positive, exact negative và context-only evidence. Probe v22 trả đúng `qa-testing-foundations=unsatisfied`, bốn requirement QA còn lại `satisfied` và tổng điểm 38.
- Batch v22 dừng sau 29/35 request với 21 output hợp lệ và 8 output sai contract. Chỉ 18/25 primary case và 3/5 stability case đủ output; sáu request còn lại không thể tạo đủ chín output hợp lệ còn thiếu.
- Trên 18 primary output hợp lệ, requirement-status match là 1,0, criterion MAE 2,1756, total-score MAE 7,1111 và endpoint-score rate 0. Đây là tín hiệu calibration tốt có điều kiện, không thay thế yêu cầu coverage đầy đủ.
- V22 là report thất bại chất lượng và không đủ điều kiện freeze. Không tăng cap, không bỏ output lỗi, không chạy hybrid trên batch thiếu và không mở held-out hoặc frozen test.

## Cập nhật GPT-5.4 mini ngày 2026-08-01

- Đã thêm provider `openai`, snapshot `gpt-5.4-mini-2026-03-17`, prompt v9-v10, giới hạn 4096 completion token, reasoning `none`, hard cap 35 và cost policy tối đa 1 USD cho mỗi experiment.
- Adapter chuẩn hóa Pydantic schema sang Strict JSON Schema của OpenAI, chỉ lưu chẩn đoán HTTP đã allowlist và tính lower-bound cost từ usage hợp lệ. Không lưu secret hoặc raw provider response.
- V1-v2 được giữ làm failed history. V3 dùng lần chỉnh prompt duy nhất và chạy panel năm vai trò; bốn output hợp lệ đạt requirement match 1,0, criterion MAE 2,2 và total-score MAE 7,5.
- Case Data Analyst sai quan hệ criterion status/evidence ở request đầu và thiếu requirement ID ở retry. V3 dừng ở `stopped_quality_failure`; không chạy batch, hybrid, held-out hoặc frozen test.
- Việc bắt buộc còn mở: người dùng chọn một schema-v4 development experiment có tổng cap toàn chuỗi 45 request, hoặc dừng mở rộng năm vai trò và chốt controlled pilot hai vai trò. Không được hạ output-coverage gate hoặc lựa chọn riêng output hợp lệ để tuyên bố đạt.
- Người dùng đã chọn schema v4. Năm panel request đều hợp lệ và khớp requirement status, nhưng total-score MAE 13,3 vượt ngưỡng 12; panel gate dừng batch ở tổng 18/45 request toàn chuỗi.
- Schema v4 khóa số assessment, allowed ID enum và evidence cardinality theo từng request. Hạn chế còn lại là calibration điểm, không còn là lỗi structured-output coverage trên panel.
- Bước cần duyệt tiếp là dừng nhánh năm vai trò để chốt controlled pilot hai vai trò, hoặc phê duyệt trước một thiết kế calibration mới; không được tiếp tục v4 batch.
