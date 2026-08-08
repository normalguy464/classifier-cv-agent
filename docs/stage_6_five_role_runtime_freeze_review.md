# Review Stage 6 — Bộ runtime năm vai trò

Ngày tạo: 2026-08-01

Ngày phê duyệt và khóa: 2026-08-07

## Kết luận ngắn

Phê duyệt v8 của người dùng đã được chuyển thành bộ runtime artifact riêng `five-role-runtime-v1`. Backend có thể nạp và chạy năm Job Profile tiêu chuẩn:

1. Junior Data Analyst;
2. Junior Python Backend Developer;
3. Junior Frontend Developer;
4. Junior QA Engineer;
5. Junior Data Engineer.

Bộ artifact dùng scoring `2.0.0`, models `2.0.0`, L1 rules `2.0.0`, Job Profile `2.0.0` và rubric `2.0.1`. Job Profile và rubric runtime được kiểm tra tự động là khớp chính xác với năm input `standard` đã dùng trong experiment v8.

Manifest hiện có trạng thái `frozen_for_stage7`. Người dùng đã phê duyệt bộ runtime và chính sách thay expansion held-out cũ; Gate 6 đã hoàn tất. Stage 7 được phép chuẩn bị test set mới và protocol đã khóa, nhưng chưa có final evaluation nào được chạy tại thời điểm cập nhật tài liệu này.

## Cấu hình được đưa vào runtime

| Thành phần | Giá trị |
| --- | --- |
| L1/L2/L3 | `40% / 20% / 40%` |
| Waitlist | từ 70 |
| Pass | từ 85 |
| Large disagreement | từ 35 điểm |
| Boundary offset | 2 điểm |
| L2 | `coverage-70-95-v1`, `top_k=1`, minimum query score 20 |
| Embedding | `intfloat/multilingual-e5-base` |
| Embedding revision | `d128750597153bb5987e10b1c3493a34e5a4502a` |
| L3 provider | `openai` |
| L3 model | `gpt-5.4-mini-2026-03-17` |
| Prompt | `l3-evidence-rubric-v12` |
| Ánh xạ điểm L3 | `l3-deterministic-level-mapping-v1` |

Runtime từ chối provider hoặc model khác với artifact đã duyệt. Việc đổi model sau này vẫn thực hiện được, nhưng phải tạo phiên bản models configuration và manifest mới thay vì âm thầm thay đổi `.env`.

## Ý nghĩa các file

### Cấu hình runtime

- `configs/runtime/five_role_v1/runtime_manifest.yaml`: manifest truy vết nguồn v8, danh sách năm vai trò, chiến lược scoring và SHA-256 của từng artifact. Đây là configuration và chưa chứa secret.
- `configs/runtime/five_role_v1/scoring.yaml`: trọng số, ngưỡng, disagreement và vùng biên của hybrid v8.
- `configs/runtime/five_role_v1/models.yaml`: L2 query coverage, embedding revision, prompt, score mapping và provider/model L3 được duyệt.
- `configs/runtime/five_role_v1/l1_rules.yaml`: quy tắc từ khóa xác định cho toàn bộ 24 requirement bắt buộc của năm vai trò.
- `configs/runtime/five_role_v1/job_profiles/*.yaml`: năm Job Profile tiêu chuẩn, gồm trách nhiệm, requirement bắt buộc, requirement ưu tiên và loại thông tin được chấp nhận.
- `configs/runtime/five_role_v1/rubrics/*.yaml`: năm rubric cùng cấu trúc `30/25/20/15/10`, nhưng nội dung chuyên môn riêng theo vai trò.

### Source code

- `backend/app/infrastructure/config/artifacts.py`: schema kiểm tra artifact runtime, query coverage, model revision, prompt và score mapping.
- `backend/app/infrastructure/config/runtime_manifest.py`: kiểm tra manifest, đường dẫn, SHA-256 và source report v8.
- `backend/app/infrastructure/config/loaders.py`: nạp một config directory độc lập, dựng L2 query coverage và từ chối provider/model không được duyệt.
- `backend/app/infrastructure/embeddings/adapters.py`: truyền đúng embedding revision vào Sentence Transformers.
- `backend/app/infrastructure/bootstrap.py`: cho phép backend dùng config directory lồng trong repository.
- `backend/app/infrastructure/llm/adapters.py`: deterministic fake chấp nhận prompt version của config để demo offline v12 vẫn chạy được.

### Test

- `tests/contract/test_five_role_runtime_config.py`: kiểm tra năm vai trò, version link, contract khớp input v8, L1 bốn trạng thái, L2, model lock và manifest tamper detection.
- `tests/contract/test_embedding_adapters.py`: kiểm tra embedding revision thực sự được truyền cho model loader.
- `tests/contract/test_llm_adapters.py`: kiểm tra deterministic fake chỉ nhận prompt version đã cấu hình.
- `tests/integration/test_runtime_bootstrap.py`: chạy một classification mới cho Frontend bằng bộ runtime năm vai trò.

## Sự cố expansion held-out đã được ghi nhận

Trong lúc viết test L1, một danh sách scenario theo tên đã vô tình chứa tám cặp `standard` thuộc expansion held-out:

- `pair-be-conflict-std`, `pair-be-missing-std`;
- `pair-da-conflict-std`, `pair-da-failed-std`;
- `pair-de-conflict-std`, `pair-de-failed-std`;
- `pair-fe-failed-std`, `pair-fe-missing-std`.

Test có thể đã tính L1 cho các cặp này trước khi dừng. Rule `be-python` sau đó được sửa khi `pair-be-missing-std` cho thấy từ `pytest` không được phép tự chứng minh Python. Không có L2, L3 hoặc API provider nào được chạy trên các cặp này.

Vì đã có thay đổi sau khi nhìn output held-out, expansion held-out 100 cặp không còn được dùng làm final benchmark độc lập. Nó chỉ được giữ cho diagnostics có ghi chú. Original frozen test mười case chưa bị mở, nhưng chỉ đại diện hai vai trò cũ. Stage 7 năm vai trò cần một test set mới, khóa theo candidate và không dùng trong tuning.

Test artifact hiện không đọc hoặc chấm bất kỳ pair annotation development/held-out nào. Bốn trạng thái L1 được tạo trực tiếp từ từng rule để kiểm tra engine mà không dùng nhãn dataset.

## Kết quả kiểm tra tự động

Các kiểm tra đóng Gate 6 ngày 2026-08-07 đạt:

- `89 passed` cho runtime/config/adapter/bootstrap tập trung;
- Ruff lint không có lỗi;
- Ruff xác nhận 130 file Python đã đúng format;
- Pyright có 0 errors, 0 warnings và 0 informations;
- toàn bộ pytest có `405 passed, 7 skipped in 125.56s` khi dùng thư mục tạm ghi được trong workspace; bảy test bị skip là nhóm PostgreSQL khi database test chưa chạy;
- lượt chạy canonical đầu tiên có 39 setup errors do Windows từ chối quyền ghi thư mục tạm của pytest; chạy lại cùng suite với `--basetemp` hợp lệ đã đạt hoàn toàn, nên đây là lỗi môi trường thực thi chứ không phải lỗi source;
- manifest nạp đủ năm vai trò và 13 artifact, mọi SHA-256 đều khớp;
- bộ 250 cặp Silver v2.3.1 vượt QC với 0 errors và 0 warnings;
- không có dòng comment trong source/test/config và không phát hiện credential-shaped value ngoài `.env` cục bộ cùng placeholder của `.env.example`;
- report v8 vẫn ghi quality gate đạt, không có raw provider response và chưa chạy held-out/frozen test trong chính experiment v8.

Không có request OpenAI mới trong quá trình tạo và kiểm tra runtime artifact.

## Nội dung người dùng đã duyệt để đóng Gate 6

1. Dùng năm Job Profile và rubric `standard` làm runtime scope chính thức v1.
2. Dùng config `40/20/40`, threshold `70/85`, disagreement 35 và boundary offset 2.
3. Khóa L2 `coverage-70-95-v1` cùng embedding revision đã ghi.
4. Khóa L3 vào OpenAI GPT-5.4 mini snapshot, prompt v12 và deterministic mapping v1.
5. Chấp nhận expansion held-out hiện tại chỉ còn là diagnostics; không dùng nó làm final benchmark.
6. Original frozen test chỉ có thể hỗ trợ kết luận cho hai vai trò cũ; Stage 7 phải tạo test set mới nếu muốn kết luận chính thức cho đủ năm vai trò.

Người dùng đã xác nhận ngày 2026-08-07:

> Tôi duyệt bộ runtime five-role-runtime-v1 và đồng ý thay expansion held-out cũ bằng test set mới tại Stage 7. Hãy hoàn tất Gate 6.

Phê duyệt này khóa các giá trị trong bảng cấu hình. Nó không biến kết quả development thành final performance và không cho phép tuning theo output của test set Stage 7.
