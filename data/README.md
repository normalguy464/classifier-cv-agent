# Dữ liệu của Classifier Agent

`data/samples/external_trials/` chứa các bản chuyển đổi thủ công đã ẩn danh để kiểm tra luồng Stage 8. Chúng không thuộc pilot, Silver, Gold hoặc frozen test; không được dùng để tuning hay báo cáo accuracy.

## Stage 7 Runtime v2 test v1

`data/to_review/stage7_runtime_v2_test_v1/` chứa nguồn Bronze 50 cặp CV–JD synthetic mới cho Runtime v2. Nguồn này đã được hai người duyệt và được giữ nguyên để audit. `manifest.json` liên kết Runtime v2 và các nguồn dữ liệu cũ dùng để chống leakage; `quality_report.json` xác nhận 0 lỗi, 0 cảnh báo và token Jaccard tối đa `0.7479` dưới ngưỡng `0.82`.

`data/frozen_test/stage7_runtime_v2_v1/` là bản Gold riêng đã khóa sau hội đồng đồng thuận hai người. Bản này có review record, manifest và QC riêng; preflight đã đạt nhưng classifier và API LLM chưa chạy. Không sửa, ghi đè hoặc loại case khỏi bản Gold sau khi xem prediction.

## Runtime v2 development v1

`data/runtime_v2/to_review/development_v1/` chứa nguồn 75 cặp Bronze, 15 cặp cho mỗi vai trò. Tập này tập trung vào cách diễn đạt thay thế, thông tin liên quan gián tiếp, phủ định, mâu thuẫn và case sát ngưỡng. Bản nguồn được giữ nguyên để audit.

`data/runtime_v2/reviewed/development_v1/` là bản Silver sau khi người dùng duyệt toàn bộ requirement status, năm nhóm điểm, nhãn và rationale. `data/runtime_v2/splits/development_v1_split.json` chia theo ứng viên thành 50 development và 25 validation. Hai partition này chỉ dùng cho tuning/checkpoint Runtime v2, không phải frozen test độc lập.

Checkpoint L1/L2 không gọi API và không mở Stage 7 v1 frozen test. Report được lưu tại `evaluation/reports/runtime_v2_offline_l1_l2_checkpoint_v1.json`.

## Stage 7 five-role test set v1

`data/to_review/stage7_test_v1/` chứa nguồn Bronze phiên bản `1.0.1` với 50 CV synthetic mới, năm Job Profile `standard`, năm rubric runtime và 50 annotation nháp. Version `1.0.1` sửa năm mâu thuẫn xuyên requirement được phát hiện trong lúc review bản `1.0.0`.

`review_sheet.md` là tài liệu người dùng đọc để duyệt trạng thái yêu cầu, năm nhóm điểm, nhãn và rationale. `manifest.json` khóa nguồn runtime, nguồn dữ liệu cũ dùng cho leakage audit và hash của mọi artifact. `quality_report.json` ghi kết quả QC nhưng không phải classifier report.

`data/frozen_test/stage7_v1/` là bản Gold riêng đã được khóa sau review đồng thuận của hai người. `review_record.json` ghi cách review, `manifest.json` khóa nguồn và hash, còn `quality_report.json` xác nhận QC không có lỗi hoặc cảnh báo. Bản Gold đã được dùng đúng một lần cho final evaluation; không sửa hoặc dùng kết quả này để tuning runtime v1.

## Phạm vi hiện tại

Thư mục này chỉ chứa dữ liệu tổng hợp phục vụ pilot Stage 3, review dataset Stage 4 và bộ mở rộng Bronze/Silver tại Stage 6. Không có CV thật, tên người, email, số điện thoại, địa chỉ, credential hoặc thuộc tính được bảo vệ. Mọi candidate, organization, institution và repository reference đều là định danh giả lập.

CV input và annotation được lưu riêng để nhãn, score, rationale hoặc review status không lọt vào đầu vào của classifier.

## Cấu trúc và trạng thái

| Đường dẫn | Nội dung | Trạng thái |
| --- | --- | --- |
| `samples/cvs/` | Mười `CVProfile` JSON schema `1.0.0`: năm Data Analyst và năm Python Backend | Pilot đã duyệt |
| `annotations/pilot_annotations_v1.json` | Mười phiếu pilot có điểm, rationale và audit fields | `annotation_status: reviewed`; 10 `review.status: approved` |
| `to_review/stage4_cv_profiles_v1.jsonl` | 30 hồ sơ tổng hợp, mỗi dòng là một `CVProfile`: 15 cho mỗi vị trí | Bản nháp được giữ làm audit source |
| `to_review/stage4_annotations_v1.json` | 30 phiếu đề xuất liên kết bằng `cv_profile_id` | Bản nháp giữ nguyên đề xuất và `review.status: pending` |
| `reviewed/stage4_cv_profiles_v1.jsonl` | Bản CV Stage 4 dùng cho controlled evaluation | Đã liên kết với 30 human-approved annotation |
| `reviewed/stage4_annotations_v1.json` | 30 phiếu có reviewer, final label và timestamp | `annotation_status: reviewed`; 30 `review.status: approved` |
| `splits/stage6_split_manifest_v1.json` | Manifest chia reviewed data thành validation và frozen test | 20 validation; 10 frozen; source hashes đã khóa |
| `synthetic_expansion/v1/` | Bản mở rộng đầu tiên trước khi đối chiếu thị trường chi tiết | Bronze, draft; đã được v2 thay thế trước human review, chỉ giữ để truy vết |
| `synthetic_expansion/v2/` | 50 CV, 25 Job Profile/JD, 25 rubric và 250 cặp có yêu cầu Junior khó hơn cho năm vị trí | Bronze nguồn; giữ nguyên draft trước human review để truy vết |
| `synthetic_expansion/reviewed/v2/` | Bản sao có audit fields sau khi người dùng duyệt đủ 250 cặp | Silver; một reviewer; 250 final label giữ nguyên draft; QC không có lỗi hoặc cảnh báo |
| `synthetic_expansion/splits/v2_silver_split_manifest.json` | Group split cố định theo ứng viên cho bản Silver | 150 development; 100 held-out diagnostic; không tạo frozen test |
| `synthetic_expansion/reviewed/v2_2/`, `v2_3/`, `v2_3_1/` | Các bản remediation có version cho thông tin SQL, Python và QA explicit-negative | `v2_3_1` là lineage hiện hành; 250 Silver pair; QC không có lỗi hoặc cảnh báo |
| `synthetic_expansion/splits/v2_3_1_silver_split_manifest.json` | Split theo ứng viên của lineage hiện hành | 150 development; 100 held-out đã retired khỏi final benchmark; không tạo frozen test |

Mười pilot annotation và ba mươi annotation Stage 4 đã duyệt được phép dùng làm ground truth cho đúng phạm vi của chúng. Stage 4 reviewed data chưa tự động trở thành validation split hoặc frozen test data; việc chia tập được thực hiện ở stage sau theo chính sách chống leakage.

Bộ `synthetic-cv-jd-expansion-v2-reviewed-silver` không được gộp vào original frozen test hiện tại. Cả năm vị trí đã có cấu hình chính thức trong runtime `five-role-runtime-v1`, nhưng annotation vẫn chỉ ở tầng Silver với một reviewer. Không gộp các version v1, v2, v2.2, v2.3 và v2.3.1 thành dữ liệu độc lập vì chúng dùng cùng candidate/persona và sẽ gây leakage.

## Phân bố Stage 4

- Junior Data Analyst: 15 hồ sơ.
- Junior Python Backend Developer: 15 hồ sơ.
- Draft label toàn bộ: 6 `pass`, 6 `waitlist`, 2 `reject`, 16 `needs_review`.
- Mỗi vai trò có case mạnh, case Waitlist, thiếu thông tin, thông tin mâu thuẫn, Reject rõ ràng, hai candidate-protection fallback và hai vùng điểm biên.

Hướng dẫn duyệt từng scenario nằm trong `docs/stage_4_review.md`.

## Khi nào một annotation trở thành ground truth

Một record chỉ được coi là đã được con người xác nhận khi có đủ:

- `review.status` là `approved`;
- `review.reviewer_reference` là định danh giả danh của người duyệt;
- `review.final_label` là nhãn người duyệt xác nhận;
- `review.reviewed_at` là thời gian ISO 8601 có timezone;
- mọi thay đổi điểm được ghi trong `review.criterion_score_overrides` kèm lý do;
- contract test và liên kết CV-annotation vẫn pass.

Không sửa `draft_label` để phản ánh quyết định mới. Các trường `review` bảo toàn đề xuất ban đầu và audit trail. Nếu người dùng yêu cầu thay đổi nội dung CV hoặc annotation dự thảo, phải ghi rõ thay đổi và đưa case đó review lại trước khi approval.

## Quy trình review 30 hồ sơ

1. Tìm một `cv_profile_id` trong `stage4_cv_profiles_v1.jsonl`.
2. Tìm cùng ID trong `stage4_annotations_v1.json`.
3. Kiểm tra trạng thái yêu cầu bắt buộc, năm nhóm điểm, tổng điểm, draft label, rationale và review reasons.
4. Người dùng chấp thuận hoặc nêu sửa đổi cụ thể.
5. Coding agent ghi human-review fields, không ghi đè đề xuất ban đầu.
6. Chạy lại data contract tests.
7. Chỉ sau khi đủ 30 approval mới tạo artifact reviewed dùng cho controlled evaluation.

Gate 4 đã hoàn tất sau khi người dùng xác nhận đủ 30 record. Bản đã duyệt được tạo riêng; bản nháp không bị ghi đè.

## Split Stage 6

Split manifest được tạo trước tuning. Validation loader chỉ trả 20 case có `tuning_allowed: true`. Mười frozen-test ID không được đưa qua classifier trước Stage 7.

Không chạy lại lệnh split chỉ để nhận phân bố hoặc metrics thuận lợi hơn. Nếu reviewed source, split policy hoặc dataset version thay đổi hợp lệ, phải tạo manifest version mới và ghi migration note.

## Ngăn label leakage

Classifier chỉ được nhận `CVProfile`. Các trường sau chỉ được tồn tại trong annotation, không được sao chép vào summary, evidence hoặc phần input khác của CV:

- draft hoặc final label;
- total score và criterion scores;
- review reason hoặc quality-gate identifier;
- rationale mô tả trước kết quả cần dự đoán;
- review status và reviewer decision.

Dataset contract test phải phát hiện các marker trực tiếp có thể tiết lộ scenario hoặc nhãn. Việc tách file không đủ nếu nội dung CV tự mô tả nhãn hay ngưỡng của chính nó.

## Quy tắc an toàn

- Chỉ thêm dữ liệu synthetic, consented hoặc irreversibly anonymized.
- Không đưa tuổi, giới tính, dân tộc, tôn giáo, tình trạng hôn nhân, khuyết tật, quê quán hoặc thuộc tính nhạy cảm khác vào scoring input.
- Không thêm CV thật, PII, API key, secret hoặc provider response.
- `missing` là thiếu thông tin; không tự đổi thành `unsatisfied`.
- Không dùng annotation do model hoặc coding agent tạo làm ground truth nếu chưa có human review.
- Không dùng dữ liệu frozen test để tuning model, prompt, weight hoặc threshold.

## Kiểm tra dữ liệu

Từ thư mục gốc:

```powershell
uv run pytest -q tests/contract/test_pilot_dataset.py
uv run pytest -q tests/contract/test_stage4_dataset.py
uv run pytest -q tests/contract/test_stage4_reviewed_dataset.py
uv run pytest -q tests/evaluation/test_synthetic_expansion.py
uv run pytest -q tests/evaluation/test_synthetic_expansion_review.py
uv run pytest -q tests/evaluation/test_synthetic_expansion_diagnostic.py
```

Các test kiểm tra contract `CVProfile`, số lượng và phân bố role, ID, evidence reference, score bounds, tổng điểm, version links, candidate-protection cases, protected fields, label-leakage markers và human-review state.

QC của bộ mở rộng còn kiểm tra đủ tích Descartes 10 CV × 5 JD cho mỗi vị trí, liên kết rubric, draft decision policy, manifest count, SHA-256 và khả năng phát hiện file bị sửa.

## Sinh lại bộ mở rộng synthetic

```powershell
uv run python -m scripts.generate_synthetic_expansion
```

Lệnh ghi lại toàn bộ file trong `data/synthetic_expansion/v2/`. Chỉ dùng khi chủ động tái tạo bản Bronze từ generator; không dùng để ghi đè một artifact đã có human review.

## Ghi nhận review và chia bản Silver

```powershell
uv run python -m scripts.approve_synthetic_expansion --reviewed-at <ISO-8601-with-timezone>
uv run python -m scripts.create_synthetic_expansion_split --created-at <ISO-8601-with-timezone>
```

Lệnh thứ nhất tạo bản Silver riêng, không sửa Bronze. Lệnh thứ hai chia theo `candidate_reference`, giữ cả năm cặp của cùng ứng viên trong một partition. Không chạy lại split để lựa chọn phân bố có lợi hơn.

Chẩn đoán hiện tại chỉ chạy trên development Silver:

```powershell
$env:HF_HUB_OFFLINE="1"
$env:TRANSFORMERS_OFFLINE="1"
uv run python -m evaluation.experiments.run_synthetic_expansion_v2_diagnostic
```

Report tại `evaluation/reports/synthetic_expansion_v2_development_diagnostic.json` không phải hiệu năng cuối. Nó không dùng 100 cặp held-out, không dùng 10 frozen-test case cũ và không gọi LLM provider thật.

Hiệu chỉnh L2 theo độ bao phủ dùng riêng development Silver:

```powershell
$env:HF_HUB_OFFLINE="1"
$env:TRANSFORMERS_OFFLINE="1"
uv run python -m evaluation.experiments.run_synthetic_expansion_v2_l2_tuning --generated-at <ISO-8601-with-timezone>
```

Các report L2 version hóa so sánh sáu candidate và ghi trace từng truy vấn. `coverage-70-95-v1` hiện đã được khóa trong runtime `five-role-runtime-v1`. Expansion held-out cũ chỉ còn dùng cho diagnostics; original frozen test vẫn chưa được chạy.

## Sinh lại bản nháp

```powershell
uv run python -m scripts.generate_stage4_dataset
```

Script ghi đè cả hai file Stage 4 trong `data/to_review/`. Chỉ chạy trước human review hoặc khi chủ động reset bản nháp. Không chạy sau khi review fields đã được cập nhật nếu chưa sao lưu và chưa xác nhận rằng việc ghi đè là mong muốn.

## Controlled evaluation Stage 5

```powershell
uv run python -m evaluation.experiments.run_stage5_review
uv run pytest -q tests/evaluation/test_stage5_review.py
```

Runner chỉ đọc `data/reviewed/` và ghi `evaluation/reports/stage5_classifier_review_v1.json`. Lần chạy mặc định hiện dùng deterministic hashing embedding và deterministic L3 fake, vì vậy report là diagnostic, không phải final performance.

Stage 6 dùng:

```powershell
uv run pytest -q tests/evaluation/test_stage6_split.py
uv run pytest -q tests/evaluation/test_stage6_validation.py
uv run python -m evaluation.experiments.run_stage6_validation
```

Stage 6 report chỉ được chứa validation result. Test kiểm tra không frozen CV ID nào xuất hiện trong report.

Live L3 Stage 6 dùng cùng validation partition và ghi hai report:

- `evaluation/reports/stage6_live_llm_validation_v1.json` chứa structured output đã validate, metrics, usage, latency và stability;
- `evaluation/reports/stage6_freeze_proposal_v1.json` áp dụng candidate-protection gate được đề xuất và vẫn ghi `configuration_frozen: false`.

Cache tiếp tục chạy nằm trong `evaluation/reports/generated/` và bị loại khỏi Git. Cache không được chứa raw provider response, API key, frozen-test prediction hoặc frozen-test metric. Không sửa annotation chuẩn theo output của provider và không chuyển hồ sơ frozen test sang validation để cải thiện kết quả.
