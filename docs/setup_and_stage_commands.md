# Hướng dẫn setup và chạy theo stage

## Stage 7: Runtime v2 đã khóa và test set mới

Kiểm tra runtime đã khóa mà không gọi API:

```powershell
uv run pytest -q tests/contract/test_five_role_runtime_v2.py
```

Tạo lại test set Bronze 50 case cho Runtime v2 và chạy QC/tính tái tạo:

```powershell
uv run python -m scripts.generate_stage7_runtime_v2_test_set
uv run pytest -q tests/evaluation/test_stage7_runtime_v2_test_set.py
```

Kết quả nằm tại `data/to_review/stage7_runtime_v2_test_v1/`. Đọc `docs/stage_7_runtime_v2_test_set_review.md` và duyệt toàn bộ 50 case trước khi tạo Gold. Hai lệnh trên không chạy classifier và không gọi API LLM.

Không dùng lại `data/frozen_test/stage7_v1` để đánh giá Runtime v2. Không xóa case khỏi test mới sau khi đã xem prediction; mismatch hiếm chỉ được ghi trong error analysis nếu quality gate và điều kiện an toàn vẫn đạt.

Sau khi hai người duyệt, khóa Gold và chạy preflight mà không gọi API:

```powershell
uv run python -m scripts.approve_stage7_runtime_v2_test_set --reviewed-at <ISO-8601-with-timezone>
uv run python -m scripts.preflight_stage7_runtime_v2 --generated-at <ISO-8601-with-timezone>
uv run pytest -q tests/evaluation/test_stage7_runtime_v2_lock.py
```

Bản Gold nằm tại `data/frozen_test/stage7_runtime_v2_v1/`; report preflight nằm tại `evaluation/reports/stage7_runtime_v2_preflight_v1.json`. Script khóa từ chối ghi đè thư mục Gold đã có. Preflight không đọc `.env`, không nạp API key và không gọi provider. Provider execution vẫn cần người dùng cho phép riêng.

Sau khi có authorization riêng, chạy final evaluation Runtime v2:

```powershell
$env:HF_HUB_OFFLINE="1"
$env:TRANSFORMERS_OFFLINE="1"
uv run python -m evaluation.experiments.run_stage7_runtime_v2_frozen_evaluation --generated-at <ISO-8601-with-timezone>
```

Runner kiểm tra authorization và ba hash trước khi gọi provider, dùng cache/resume và hard cap 60. Lần final hiện tại đã hoàn tất với 55 output hợp lệ, 56 HTTP request tính cả một lỗi mạng sandbox, và report tại `evaluation/reports/stage7_runtime_v2_frozen_evaluation_v1.json`. Quality gate không đạt; không chạy lại để tuning hoặc thay đổi kết quả.

## Stage 7: chu kỳ cải tiến Runtime v2

Tạo lại tập development Bronze 75 case và chạy QC:

```powershell
uv run python -m scripts.generate_runtime_v2_development
uv run pytest -q tests/evaluation/test_runtime_v2_development.py
```

Kết quả nằm tại `data/runtime_v2/to_review/development_v1/`. Đọc `docs/runtime_v2_development_review.md` và duyệt toàn bộ 75 case. Không chạy L1/L2 tuning hoặc gọi LLM khi manifest còn `ground_truth_status: pending_human_review` và `tuning_allowed: false`.

Runtime v1 và report Stage 7 v1 phải được giữ nguyên. Chu kỳ v2 sẽ tạo runtime version mới và một frozen test mới; không dùng lại 50 case Stage 7 v1 để chọn rule, prompt, model, weight hoặc threshold.

## Stage 7: khóa test set và chạy frozen evaluation

Tạo lại bộ nháp 50 case theo cách xác định:

```powershell
uv run python -m scripts.generate_stage7_test_set
```

Chạy test contract, tính tái tạo, QC và chống leakage của bộ Stage 7:

```powershell
uv run pytest -q tests/evaluation/test_stage7_test_set.py
```

Nguồn Bronze vẫn nằm tại `data/to_review/stage7_test_v1/`. Sau khi hai người thống nhất toàn bộ 50 case, lệnh sau tạo bản Gold riêng và không ghi đè nguồn:

```powershell
uv run python -m scripts.approve_stage7_test_set --reviewed-at <ISO-8601-with-timezone>
```

Kiểm tra bản Gold và runner Stage 7:

```powershell
uv run pytest -q tests/evaluation/test_stage7_test_set.py tests/evaluation/test_stage7_frozen_evaluation.py
```

Chạy final evaluation chỉ sau khi đã có quyền gọi API. Runner dùng cache/resume, dừng khi provider unavailable, không lưu raw response và không vượt hard cap 60:

```powershell
$env:HF_HUB_OFFLINE="1"
$env:TRANSFORMERS_OFFLINE="1"
uv run python -m evaluation.experiments.run_stage7_frozen_evaluation --generated-at <ISO-8601-with-timezone>
```

Report nằm tại `evaluation/reports/stage7_frozen_evaluation_v1.json`. Kết quả hiện tại không đạt quality gate và không được dùng để tuning runtime v1; xem `docs/stage_7_evaluation_review.md`.

## Mục đích

Tài liệu này ghi các công cụ cần cài trên máy, trạng thái scaffold thật của repository và lệnh có thể chạy ở từng stage. Mọi lệnh được thực hiện từ:

```powershell
Set-Location D:\graduation_project\Classifier_agent_code
```

Không thay đổi dependency major, lockfile, rubric, threshold hoặc quality gate chỉ để làm một lệnh pass.

## Công cụ cài trên máy

| Công cụ | Khi cần | Cách kiểm tra | Project có tự cài được không |
| --- | --- | --- | --- |
| Git | Khuyến nghị cho mọi stage | `git --version` | Không nên tự cài vì thay đổi môi trường hệ thống. |
| Python 3.12 | Stage 2 trở đi | `python --version` hoặc để `uv` quản lý interpreter | `uv` có thể tải interpreter sau khi `uv` đã được cài. |
| `uv` | Stage 2 trở đi | `uv --version` | Không nên tự cài vào máy người dùng khi chưa được cho phép. |
| Docker Desktop và WSL 2 | Stage 4 trở đi khi dùng PostgreSQL | `docker version` và `docker compose version` | Không; việc cài đặt cần quyền hệ điều hành. |
| Node.js LTS và pnpm | Stage 8 khi frontend được scaffold | `node --version` và `pnpm --version` | Chưa cần ở Stage 4. |
| API key của LLM provider | Chỉ khi chủ động dùng L3 provider thật | Kiểm tra trong secret store hoặc `.env` cục bộ | Không; chủ tài khoản phải tự cung cấp. |

Không cần cài PostgreSQL hay pgvector trực tiếp nếu dùng Docker Desktop. Image trong `docker-compose.yml` đã bao gồm PostgreSQL 16 và pgvector. Không cần GPU cho bản hiện tại; L2 có thể chạy CPU. Lần đầu tải embedding model có thể cần mạng và dung lượng đĩa.

## Trạng thái scaffold hiện tại

| Thành phần | Trạng thái tại Stage 6 | Có thể chạy |
| --- | --- | --- |
| Python project, Pydantic contracts và lockfile | Đã scaffold | Có |
| L1, L2, L3, aggregation, routing và LangGraph | Đã scaffold | Có |
| FastAPI health, classification và decision routes | Đã scaffold | Có |
| Memory repository | Đã scaffold | Có, không cần database |
| PostgreSQL, pgvector, SQLAlchemy và Alembic | Đã scaffold | Có, cần Docker và cấu hình môi trường |
| Baseline, metrics và pilot experiment ban đầu | Đã scaffold | Có |
| Bộ 30 hồ sơ và annotation đã human review | Đã scaffold | Có; là ground truth cho split Stage 6/7 |
| Ablation, stability và performance experiment cuối | Chưa scaffold | Chưa |
| Next.js frontend và Playwright | Chưa scaffold | Chưa |

## Chuẩn bị Python một lần

```powershell
uv sync --all-groups
```

Lệnh này cài dependency đúng theo `uv.lock` vào môi trường do `uv` quản lý.

## Kiểm tra nhanh API không cần PostgreSQL

Thiết lập biến chỉ cho PowerShell hiện tại:

```powershell
$env:CLASSIFIER_STORAGE_BACKEND="memory"
$env:CLASSIFIER_API_KEY="local-development-only"
$env:CLASSIFIER_LLM_ADAPTER="deterministic_fake"
$env:CLASSIFIER_CONFIG_DIRECTORY="configs/runtime/five_role_v1"
uv run uvicorn backend.app.main:app --reload
```

Giữ server chạy và mở PowerShell thứ hai:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Kết quả mong đợi:

```text
status
------
ok
```

Mở `http://127.0.0.1:8000/docs` để xem OpenAPI. `GET /health` không cần API key; các route dưới `/v1/classifications` cần header:

```text
X-Classifier-API-Key: local-development-only
```

Memory repository mất toàn bộ dữ liệu khi server dừng. Route phân loại còn cần request đúng contract và có đủ Job Profile, rubric, configuration trùng với artifact trong repository. Lần chạy L2 đầu tiên có thể tải `intfloat/multilingual-e5-base`.

## Chạy Stage 4 với PostgreSQL

### 1. Tạo cấu hình cục bộ

```powershell
Copy-Item .env.example .env
```

Mở `.env` và thay toàn bộ giá trị `replace-with-...`. Ít nhất cần:

- `CLASSIFIER_POSTGRES_DB`, `CLASSIFIER_POSTGRES_USER`, `CLASSIFIER_POSTGRES_PASSWORD`;
- `CLASSIFIER_POSTGRES_TEST_DB`, có tên khác database development;
- `CLASSIFIER_DATABASE_URL` trỏ vào database development;
- `CLASSIFIER_TEST_DATABASE_URL` trỏ vào một database test riêng có thể xóa;
- `CLASSIFIER_API_KEY`;
- `CLASSIFIER_STORAGE_BACKEND=postgres`.

Không commit `.env`. Docker Compose và Alembic runtime tự đọc `.env`. PostgreSQL integration tests lấy `CLASSIFIER_TEST_DATABASE_URL` từ environment của PowerShell để tránh việc Alembic runtime vô tình chọn database test.

### 2. Khởi động database development

```powershell
docker compose up -d postgres
docker compose ps
```

Chờ service có trạng thái healthy. Port host mặc định là `55432`.

Nếu Docker báo port đã được sử dụng, đổi `CLASSIFIER_POSTGRES_PORT` trong `.env` sang một port trống, ví dụ `55439`, rồi cập nhật cả `CLASSIFIER_DATABASE_URL` và `CLASSIFIER_TEST_DATABASE_URL` theo cùng port. Không cần sửa `docker-compose.yml`.

Khi volume được khởi tạo lần đầu, `scripts/init_test_database.sh` tạo thêm database có tên `CLASSIFIER_POSTGRES_TEST_DB` và từ chối nếu tên này trùng `CLASSIFIER_POSTGRES_DB`.

Init script của PostgreSQL chỉ chạy khi data volume còn trống. Nếu bạn đã có volume từ cấu hình cũ, kiểm tra database test và chỉ tạo thủ công khi nó chưa tồn tại; thay các giá trị ví dụ dưới đây cho khớp `.env`:

```powershell
docker compose exec postgres createdb -U classifier_user classifier_agent_test
```

Nếu database test đã tồn tại, lệnh `createdb` sẽ báo lỗi trùng tên; không cần tạo lại.

### 3. Chạy migration development

Alembic runtime đọc `CLASSIFIER_DATABASE_URL` từ process environment hoặc `.env`. Nó không tự lấy `CLASSIFIER_TEST_DATABASE_URL`. Vì vậy lệnh development thông thường dùng đúng runtime database:

```powershell
uv run alembic -c backend/alembic.ini upgrade head
uv run alembic -c backend/alembic.ini check
```

Nếu không dùng `.env`, đặt `CLASSIFIER_DATABASE_URL` trong PowerShell trước hai lệnh trên. Không lưu URL thật vào tài liệu hoặc source.

### 4. Chạy API với PostgreSQL

Nếu `.env` đã đúng, `RuntimeSettings` sẽ đọc file này:

```powershell
uv run uvicorn backend.app.main:app --reload
```

Kiểm tra health trong PowerShell khác:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

### 5. Chạy integration tests với database test

Migration tests có thao tác `downgrade base` rồi `upgrade head`. Chúng xóa schema Stage 4 trong database được chỉ định. Tuyệt đối không đặt `CLASSIFIER_TEST_DATABASE_URL` trỏ vào database development, staging, production hoặc database có dữ liệu cần giữ.

```powershell
$env:CLASSIFIER_TEST_DATABASE_URL="postgresql+psycopg://classifier_user:local_password@localhost:55432/classifier_agent_test"
uv run pytest -q tests/integration/test_migrations.py tests/integration/test_persistence.py
```

Tests truyền URL test trực tiếp vào Alembic config; URL này ghi đè runtime URL trong `.env` chỉ cho migration test. Nếu không có `CLASSIFIER_TEST_DATABASE_URL` trong PowerShell, các PostgreSQL test sẽ bị skip thay vì xác minh persistence thật.

### 6. Dừng service

```powershell
docker compose down
```

Lệnh này dừng container nhưng giữ volume. Chỉ xóa volume khi bạn chủ động muốn xóa toàn bộ dữ liệu local và đã kiểm tra đúng phạm vi.

## Lệnh kiểm tra theo stage

### Stage 1: Requirements và Rubric

Stage 1 chủ yếu là YAML và tài liệu. Sau khi Python project đã tồn tại, các contract tests cũng kiểm tra liên kết artifact:

```powershell
uv run pytest -q tests/contract/test_config_loaders.py
```

### Stage 2: Data Contracts

```powershell
uv run pytest -q tests/contract/test_contracts.py
uv run pyright backend
```

Kết quả cần đạt: contract version, field validation, score bounds, protected-field policy và approval invariants đều pass.

### Stage 3: Pilot Dataset

```powershell
uv run pytest -q tests/contract/test_pilot_dataset.py
```

Mười annotation pilot đã được duyệt và được phép làm ground truth pilot.

### Stage 4: Classifier Core, Persistence và Dataset Review

Các quality command đầy đủ:

```powershell
uv run ruff check backend evaluation scripts tests
uv run ruff format --check backend evaluation scripts tests
uv run pyright backend evaluation scripts
uv run pytest -q
uv run pytest -q tests/unit
uv run pytest -q tests/contract
uv run pytest -q tests/integration
```

Kiểm tra riêng bộ 30 hồ sơ:

```powershell
uv run pytest -q tests/contract/test_stage4_dataset.py
```

Chạy baseline hiện có:

```powershell
uv run python -m evaluation.experiments.run_baselines
```

Report phải ghi `report_scope` là `reviewed-pilot-diagnostic-only` và `is_final_performance` là `false`. Đây chỉ là kiểm tra pipeline trên mười pilot case, không phải số liệu hiệu năng cuối.

Sinh lại dataset nháp chỉ khi chưa có human review hoặc khi chủ động reset bản nháp:

```powershell
uv run python -m scripts.generate_stage4_dataset
```

Script này ghi đè hai file trong `data/to_review/`; không chạy sau khi review fields đã được cập nhật nếu chưa sao lưu và chưa có chủ đích reset.

### Stage 5: Classifier Review

FastAPI route classify và retrieve đã tồn tại. Batch runner Stage 5 chạy classifier trên đủ 30 hồ sơ đã duyệt và ghi report có score breakdown, disagreement, mismatch và review queue:

```powershell
uv run python -m evaluation.experiments.run_stage5_review
uv run pytest -q tests/contract/test_stage4_reviewed_dataset.py
uv run pytest -q tests/evaluation/test_stage5_review.py
uv run pytest -q
uv run pytest -q tests/integration
```

Report được ghi tại `evaluation/reports/stage5_classifier_review_v1.json`. Runner hiện dùng hashing embedding và L3 fake xác định cho controlled diagnostic. Không dùng các metrics này làm final performance và không dùng model output để tự thay đổi ground-truth label đã được người dùng xác nhận.

### Stage 6: Validation Tuning và Configuration Freeze

Tải model embedding đã khai báo vào cache local nếu máy chưa có:

```powershell
uv run hf download intfloat/multilingual-e5-base
```

Split đã được tạo bằng lệnh sau. Không chạy lại chỉ để thay đổi kết quả validation:

```powershell
uv run python -m scripts.create_stage6_split --frozen-at <ISO-8601-with-timezone>
```

Kiểm tra split và chạy validation tuning:

```powershell
uv run pytest -q tests/evaluation/test_stage6_split.py
uv run pytest -q tests/evaluation/test_stage6_validation.py
uv run python -m evaluation.experiments.run_stage6_validation
```

Output offline ban đầu nằm tại `evaluation/reports/stage6_validation_tuning_v1.json`. Báo cáo này không đề xuất candidate vì khi đó live L3 chưa được validation và các candidate an toàn đều review 100%. Mọi lần Stage 6 chỉ tuning trên 20 validation case, không dùng 10 frozen-test case.

Live L3 đã được validation bằng Google AI Studio. Tệp `.env` phải nằm ngay tại thư mục gốc `D:\graduation_project\Classifier_agent_code\.env` và có các giá trị sau; thay `<secret>` bằng key cục bộ, không gửi key vào chat hoặc commit:

```text
CLASSIFIER_LLM_ADAPTER=environment_configured
CLASSIFIER_LLM_PROVIDER=google_ai_studio
CLASSIFIER_LLM_MODEL=gemini-3.5-flash-lite
CLASSIFIER_LLM_API_KEY=<secret>
CLASSIFIER_LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
```

Kiểm tra tối đa một request mới và lưu tiến độ vào cache:

```powershell
uv run python -m evaluation.experiments.run_stage6_live_validation --collect-only --maximum-new-requests 1 --request-interval-seconds 4
```

Chạy hoặc tiếp tục toàn bộ live validation:

```powershell
uv run python -m evaluation.experiments.run_stage6_live_validation --request-interval-seconds 4
```

Runner chỉ gọi những attempt chưa có trong cache. Cache nằm trong `evaluation/reports/generated/`, được `.gitignore` loại trừ và không lưu raw provider response. Lần chạy mới có thể chịu rate limit hoặc phát sinh chi phí tùy tài khoản; không cần gọi provider lại để đọc report đã sinh.

Sinh lại đề xuất routing từ live report đã khóa hash, không gọi provider:

```powershell
uv run python -m evaluation.experiments.run_stage6_freeze_proposal --generated-at 2026-07-26T23:55:00+07:00
```

Kiểm tra riêng live adapter, validation và freeze proposal:

```powershell
uv run pytest -q tests/contract/test_llm_adapters.py tests/evaluation/test_stage6_live_validation.py tests/evaluation/test_stage6_freeze_proposal.py
```

Kết quả nằm tại:

- `evaluation/reports/stage6_live_llm_validation_v1.json`;
- `evaluation/reports/stage6_freeze_proposal_v1.json`.

Hai report đều là validation-only và ghi `is_final_performance: false`. Freeze proposal vẫn chờ human approval; chưa được xem như cấu hình chính thức.

Tạo và kiểm tra bộ mở rộng synthetic 250 cặp:

```powershell
uv run python -m scripts.generate_synthetic_expansion
uv run pytest -q tests/evaluation/test_synthetic_expansion.py
Get-Content -Raw -Encoding utf8 data/synthetic_expansion/v2/quality_report.json
```

Bản Bronze giữ nguyên draft. Ghi nhận vòng human review đã được người dùng xác nhận và tạo group split Silver bằng timestamp có timezone:

```powershell
uv run python -m scripts.approve_synthetic_expansion --reviewed-at <ISO-8601-with-timezone>
uv run python -m scripts.create_synthetic_expansion_split --created-at <ISO-8601-with-timezone>
uv run pytest -q tests/evaluation/test_synthetic_expansion_review.py
```

Chạy chẩn đoán L1/L2/L3 fake trên đúng 150 cặp development. Hai biến offline ngăn Sentence Transformers thử kết nối lại khi model E5 đã có trong cache:

```powershell
$env:HF_HUB_OFFLINE="1"
$env:TRANSFORMERS_OFFLINE="1"
uv run python -m evaluation.experiments.run_synthetic_expansion_v2_diagnostic
uv run pytest -q tests/evaluation/test_synthetic_expansion_diagnostic.py
```

Report nằm tại `evaluation/reports/synthetic_expansion_v2_development_diagnostic.json`. Đây là diagnostic trên Silver, không phải hiệu năng cuối. Runner không đánh giá 100 cặp held-out, không dùng frozen test Stage 6 cũ và không gọi Google AI Studio.

Chạy tuning L2 theo độ bao phủ trên cùng 150 cặp development, dùng snapshot E5 cục bộ và không gọi LLM provider thật:

```powershell
$env:HF_HUB_OFFLINE="1"
$env:TRANSFORMERS_OFFLINE="1"
uv run python -m evaluation.experiments.run_synthetic_expansion_v2_l2_tuning --generated-at <ISO-8601-with-timezone>
uv run pytest -q tests/unit/test_l2.py tests/unit/test_l2_coverage.py tests/evaluation/test_synthetic_expansion_l2_tuning.py
```

Report nằm tại `evaluation/reports/synthetic_expansion_v2_l2_tuning_v1.json`. Runner mã hóa các truy vấn và nội dung CV theo hai batch dùng chung để tránh suy luận trùng lặp. Lần tuning này không đánh giá 100 cặp held-out, không dùng 10 frozen-test case cũ và không đóng băng cấu hình hybrid. Sau v8, expansion held-out bị mất tính độc lập bởi một test L1 ngoài dự kiến; xem phần bộ runtime bên dưới trước khi chuẩn bị Stage 7.

Các module ablation, stability và performance vẫn là target cho Stage 7 sau khi Gate 6 đóng:

```powershell
uv run python -m evaluation.experiments.run_ablation
uv run python -m evaluation.experiments.run_stability
uv run python -m evaluation.experiments.run_performance
```

### Stage 7: Frozen Test Evaluation

Stage 7 hiện đã có runner thật tại `evaluation.experiments.run_stage7_frozen_evaluation`. Các module target tổng quát bên dưới vẫn là định hướng tách runner trong tương lai; không dùng chúng thay cho report đã khóa của Stage 7 v1.

Sau Gate 6, chạy baseline, ablation, stability và performance trên test set còn độc lập để tạo report cuối. Không thay đổi weights, thresholds, prompt hoặc model dựa trên test outcomes.

Original frozen test mười case vẫn chưa mở nhưng chỉ đại diện Data Analyst và Python Backend. Expansion held-out 100 cặp hiện chỉ dùng cho diagnostics vì tám pair đã bị một test L1 truy cập và một rule đã được sửa sau output. Muốn báo cáo kết quả chính thức cho đủ năm vai trò phải tạo, kiểm tra leakage và khóa một test set mới trước khi chạy classifier trên nó.

### Stage 8: Demonstration

Frontend chưa được scaffold ở Stage 4. Chỉ chạy các lệnh sau khi `.nvmrc`, `frontend/package.json` và `pnpm-lock.yaml` tồn tại:

```powershell
pnpm --dir frontend install --frozen-lockfile
pnpm --dir frontend dev
pnpm --dir frontend lint
pnpm --dir frontend test --run
pnpm --dir frontend build
pnpm --dir frontend exec playwright test
```

## Dùng L3 provider thật

Mặc định Stage 4 dùng `deterministic_fake`, không cần API key provider. Khi chủ động thử một provider tương thích OpenAI, đặt các biến sau trong `.env` hoặc secret store cục bộ:

```text
CLASSIFIER_LLM_ADAPTER=environment_configured
CLASSIFIER_LLM_PROVIDER=<provider-identifier>
CLASSIFIER_LLM_MODEL=<model-identifier>
CLASSIFIER_LLM_API_KEY=<secret>
CLASSIFIER_LLM_BASE_URL=<provider-base-url>
```

Không đưa giá trị thật vào `.env.example`, source, test fixture, tài liệu hoặc `progress.md`. Provider output không hợp lệ hoặc không khả dụng phải đi theo fallback `Needs Review`.

### Chuẩn bị OpenRouter cho validation năm vai trò

Không gửi OpenRouter API key qua chat hoặc ảnh. Đặt key trong file cục bộ `D:\graduation_project\Classifier_agent_code\.env`, file này đã bị loại khỏi source control. Khối dưới đây chỉ là cấu hình lịch sử của experiment Gemma 4 v1 và không còn được dùng làm runtime:

```text
CLASSIFIER_LLM_ADAPTER=environment_configured
CLASSIFIER_LLM_PROVIDER=openrouter
CLASSIFIER_LLM_MODEL=google/gemma-4-26b-a4b-it:free
CLASSIFIER_LLM_API_KEY=<secret>
CLASSIFIER_LLM_BASE_URL=https://openrouter.ai/api/v1
CLASSIFIER_REQUEST_TIMEOUT_SECONDS=120
```

Không đặt key thật trong `Classifier_agent_code.env`, `.env.example` hoặc một file có tên tùy ý rồi giả định runtime sẽ tự đọc. `RuntimeSettings` hiện tự động đọc đúng file `.env` tại repository root. Trước live run, chỉ kiểm tra biến bắt buộc có mặt và không in giá trị secret ra terminal hoặc report.

Experiment OpenRouter v1 đã được version hóa với 25 primary case, năm stability repeat, hard cap 40 HTTP request, khoảng cách tối thiểu bốn giây và tối đa một retry cho mỗi output lỗi. Hai lệnh mặc định dưới đây chỉ tái hiện v1; không dùng chúng để chạy model mục tiêu mới:

```powershell
uv run python -m evaluation.experiments.run_synthetic_expansion_v2_l3_validation --collect-only --maximum-new-requests 1
```

Tạo hoặc cập nhật report từ cache:

```powershell
uv run python -m evaluation.experiments.run_synthetic_expansion_v2_l3_validation
```

Lần chạy Gemma 4 free đã dừng sớm sau 11 request do quality gate trở nên không thể đạt và model đã bị loại khỏi runtime. Report lịch sử nằm tại `evaluation/reports/synthetic_expansion_v2_openrouter_l3_validation_v1.json`.

Ứng viên mục tiêu hiện tại là Qwen3 Next snapshot `2509`. `.env` cục bộ dùng:

```dotenv
CLASSIFIER_LLM_ADAPTER=environment_configured
CLASSIFIER_LLM_PROVIDER=openrouter
CLASSIFIER_LLM_MODEL=qwen/qwen3-next-80b-a3b-instruct-2509:free
CLASSIFIER_LLM_API_KEY=<secret>
CLASSIFIER_LLM_BASE_URL=https://openrouter.ai/api/v1
CLASSIFIER_REQUEST_TIMEOUT_SECONDS=120
```

Chạy đúng experiment v15 với một request mới tối đa:

```powershell
uv run python -m evaluation.experiments.run_synthetic_expansion_v2_l3_validation --collect-only --maximum-new-requests 1 --configuration evaluation/configs/synthetic_expansion_l3_openrouter_v15.yaml --cache evaluation/reports/generated/synthetic_expansion_v2_openrouter_l3_cache_v15.json
```

Tạo report terminal từ cache mà không gọi lại các case đã hết retry:

```powershell
uv run python -m evaluation.experiments.run_synthetic_expansion_v2_l3_validation --configuration evaluation/configs/synthetic_expansion_l3_openrouter_v15.yaml --cache evaluation/reports/generated/synthetic_expansion_v2_openrouter_l3_cache_v15.json --output evaluation/reports/synthetic_expansion_v2_openrouter_l3_validation_v15.json --generated-at 2026-08-01T12:30:00+07:00
```

V15 hiện đã dừng vì hai HTTP 404 và không được gọi tiếp từ cache terminal. Khi đổi model, prompt hoặc provider policy, phải tạo version mới; không sửa cache hay report cũ. Chỉ chạy dữ liệu synthetic development qua free endpoint, không gửi CV thật hoặc PII.

### Chạy Gemini cho development năm vị trí

Tệp `.env` tại thư mục gốc dùng cấu hình sau và chỉ thay `<secret>` ở máy cục bộ:

```dotenv
CLASSIFIER_LLM_ADAPTER=environment_configured
CLASSIFIER_LLM_PROVIDER=google_ai_studio
CLASSIFIER_LLM_MODEL=gemini-3.5-flash-lite
CLASSIFIER_LLM_API_KEY=<secret>
CLASSIFIER_LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
```

Experiment v16 dùng 25 cặp development cân bằng năm vai trò và năm lần lặp stability. Policy giới hạn tối đa 35 request, cách nhau ít nhất 6 giây, timeout 60 giây và tối đa một retry cho mỗi attempt. Request Gemini không gửi `temperature` vì model hiện tại đã ngừng khuyến nghị sampling parameter này.

Chạy thăm dò đúng một request:

```powershell
uv run python -m evaluation.experiments.run_synthetic_expansion_v2_l3_validation --collect-only --maximum-new-requests 1 --request-interval-seconds 6 --configuration evaluation/configs/synthetic_expansion_l3_google_ai_studio_v1.yaml --cache evaluation/reports/generated/synthetic_expansion_v2_google_ai_studio_l3_cache_v1.json
```

Tiếp tục batch từ cache mà không gọi lại output hợp lệ:

```powershell
uv run python -m evaluation.experiments.run_synthetic_expansion_v2_l3_validation --collect-only --maximum-new-requests 29 --request-interval-seconds 6 --configuration evaluation/configs/synthetic_expansion_l3_google_ai_studio_v1.yaml --cache evaluation/reports/generated/synthetic_expansion_v2_google_ai_studio_l3_cache_v1.json
```

Tạo report từ cache với embedding snapshot cục bộ:

```powershell
$env:HF_HUB_OFFLINE="1"
$env:TRANSFORMERS_OFFLINE="1"
uv run python -m evaluation.experiments.run_synthetic_expansion_v2_l3_validation --request-interval-seconds 6 --configuration evaluation/configs/synthetic_expansion_l3_google_ai_studio_v1.yaml --cache evaluation/reports/generated/synthetic_expansion_v2_google_ai_studio_l3_cache_v1.json --output evaluation/reports/synthetic_expansion_v2_google_ai_studio_l3_validation_v1.json --generated-at 2026-08-01T12:18:36+07:00
```

Lần chạy ngày 2026-08-01 hoàn tất 30 output hợp lệ sau 31 HTTP request. Report không đạt calibration và stability gate nên chưa được freeze; không được hạ ngưỡng để biến kết quả này thành đạt. Một trăm cặp held-out và mười frozen-test case cũ vẫn chưa được chạy.

Experiment v17 giữ nguyên model nhưng dùng prompt calibration v5:

```powershell
uv run python -m evaluation.experiments.run_synthetic_expansion_v2_l3_validation --collect-only --maximum-new-requests 1 --request-interval-seconds 6 --configuration evaluation/configs/synthetic_expansion_l3_google_ai_studio_v2.yaml --cache evaluation/reports/generated/synthetic_expansion_v2_google_ai_studio_l3_cache_v2.json
```

Tiếp tục và tạo report v17:

```powershell
uv run python -m evaluation.experiments.run_synthetic_expansion_v2_l3_validation --collect-only --maximum-new-requests 29 --request-interval-seconds 6 --configuration evaluation/configs/synthetic_expansion_l3_google_ai_studio_v2.yaml --cache evaluation/reports/generated/synthetic_expansion_v2_google_ai_studio_l3_cache_v2.json
$env:HF_HUB_OFFLINE="1"
$env:TRANSFORMERS_OFFLINE="1"
uv run python -m evaluation.experiments.run_synthetic_expansion_v2_l3_validation --request-interval-seconds 6 --configuration evaluation/configs/synthetic_expansion_l3_google_ai_studio_v2.yaml --cache evaluation/reports/generated/synthetic_expansion_v2_google_ai_studio_l3_cache_v2.json --output evaluation/reports/synthetic_expansion_v2_google_ai_studio_l3_validation_v2.json --generated-at 2026-08-01T12:53:15+07:00
```

V17 hoàn tất 30 output hợp lệ sau 34 HTTP request. Criterion MAE, total-score MAE, endpoint-score và stability đều đạt; requirement match còn 0,9417 và review rate còn 1,0 nên configuration vẫn không được freeze. Đọc `docs/stage_6_gemini_v17_review.md` trước khi sửa dataset hoặc chạy prompt version tiếp theo.

Sau khi hiệu chỉnh QA, cấu hình mới nhất là v22 trên dataset 2.3.1 và prompt v8. Tạo report lại từ cache terminal không gọi thêm API bằng lệnh:

```powershell
$env:HF_HUB_OFFLINE="1"
$env:TRANSFORMERS_OFFLINE="1"
uv run python -m evaluation.experiments.run_synthetic_expansion_v2_l3_validation --configuration evaluation/configs/synthetic_expansion_l3_google_ai_studio_v7.yaml --cache evaluation/reports/generated/synthetic_expansion_v2_google_ai_studio_l3_cache_v7.json --output evaluation/reports/synthetic_expansion_v2_google_ai_studio_l3_validation_v7.json --generated-at 2026-08-01T16:30:00+07:00
```

Cache v22 có 21 output hợp lệ và 8 output sai contract sau 29 request. Sáu request còn lại không thể bù đủ chín output hợp lệ còn thiếu, nên runner dừng terminal và lệnh trên chỉ kết xuất report. Không tiếp tục gọi API từ cache này. Đọc `docs/stage_6_gemini_v22_review.md` để xem kết quả và lựa chọn Gate 6.

### Tái hiện GPT-5.4 mini v3 trên development

Đặt secret trong `.env` cục bộ, không đưa giá trị thật vào source hoặc tài liệu:

```dotenv
CLASSIFIER_LLM_ADAPTER=environment_configured
CLASSIFIER_LLM_PROVIDER=openai
CLASSIFIER_LLM_MODEL=gpt-5.4-mini-2026-03-17
CLASSIFIER_LLM_API_KEY=<secret>
CLASSIFIER_LLM_BASE_URL=https://api.openai.com/v1
CLASSIFIER_REQUEST_TIMEOUT_SECONDS=60
```

Config v3 dùng prompt v10, `max_completion_tokens=4096`, `reasoning_effort=none`, giãn cách tối thiểu một giây, hard cap 35 và chỉ chọn development. Cache hiện đã terminal; lệnh sau chỉ tái hiện trạng thái và không được dùng để ép retry thêm:

```powershell
uv run python -m evaluation.experiments.run_synthetic_expansion_v2_l3_validation --configuration evaluation/configs/synthetic_expansion_l3_openai_gpt_5_4_mini_v3.yaml --cache evaluation/reports/generated/synthetic_expansion_v2_openai_gpt_5_4_mini_l3_cache_v3.json --output evaluation/reports/synthetic_expansion_v2_openai_gpt_5_4_mini_l3_validation_v3.json --generated-at 2026-08-01T18:30:00+07:00
```

V3 có bốn output hợp lệ và hai output sai contract sau sáu request. Không chạy batch tiếp từ cache này. Đọc `docs/stage_6_openai_gpt_5_4_mini_review.md` và lấy phê duyệt rõ ràng trước khi tạo schema v4 hoặc chuyển sang freeze proposal hai vai trò.

### Tái hiện checkpoint GPT-5.4 mini v4 trên development

V4 giữ model và prompt v10, dùng schema động, hard cap 32 request mới, ghi nhận 13 request lịch sử và khóa tổng chuỗi ở 45. Panel năm case đã hoàn tất nhưng không đạt total-score MAE, nên lệnh sau chỉ tạo lại report từ cache terminal và không gọi thêm API:

```powershell
uv run python -m evaluation.experiments.run_synthetic_expansion_v2_l3_validation --configuration evaluation/configs/synthetic_expansion_l3_openai_gpt_5_4_mini_v4.yaml --cache evaluation/reports/generated/synthetic_expansion_v2_openai_gpt_5_4_mini_l3_cache_v4.json --output evaluation/reports/synthetic_expansion_v2_openai_gpt_5_4_mini_l3_validation_v4.json --generated-at 2026-08-01T20:00:00+07:00
```

Report phải có `development_panel.passed=false`, `total_http_request_count=5`, `cumulative_series_request_count=18`, `held_out_evaluated=false` và `original_stage6_frozen_test_evaluated=false`. Không dùng `--collect-only` để tiếp tục cache v4 vì batch không được panel gate cho phép.

### Tái hiện OpenAI role-calibrated hybrid v8 từ cache

V8 dùng prompt v12, deterministic level mapping v1 và hybrid candidate `40/20/40`. Cache đã có đủ 30 output hợp lệ, vì vậy lệnh sau không gọi thêm API:

```powershell
$env:HF_HUB_OFFLINE="1"
$env:TRANSFORMERS_OFFLINE="1"
uv run python -m evaluation.experiments.run_synthetic_expansion_v2_l3_validation --configuration evaluation/configs/synthetic_expansion_l3_openai_gpt_5_4_mini_v8.yaml --cache evaluation/reports/generated/synthetic_expansion_v2_openai_gpt_5_4_mini_l3_cache_v8.json --output evaluation/reports/synthetic_expansion_v2_openai_gpt_5_4_mini_l3_validation_v8.json --generated-at 2026-08-01T16:45:00+07:00
```

Kiểm tra các giá trị review chính:

```powershell
$report = Get-Content evaluation/reports/synthetic_expansion_v2_openai_gpt_5_4_mini_l3_validation_v8.json -Raw | ConvertFrom-Json
$report.quality_gate_passed
$report.provider_quality | Select-Object valid_output_rate, requirement_status_match_rate, unsafe_requirement_status_mismatch_count, criterion_mean_absolute_error, total_score_mean_absolute_error
$report.stability | Select-Object maximum_score_range, requirement_status_agreement_rate, requirement_route_agreement_rate, passes_stability_policy
$report.hybrid_diagnostic | Select-Object hybrid_candidate_id, accuracy, macro_f1, needs_review_recall, false_reject_count, unsafe_pass_count, review_rate
$report.traceability | Select-Object held_out_evaluated, original_stage6_frozen_test_evaluated
```

Kỳ vọng: quality gate `true`; valid output 1,0; requirement match khoảng 0,9917; unsafe mismatch 0; criterion MAE 1,892; total-score MAE 7,74; route stability 1,0; hybrid accuracy 0,88; macro-F1 khoảng 0,7558; review rate 0,64; held-out và frozen test đều `false`.

Đọc `docs/stage_6_openai_role_calibrated_review.md` trước khi duyệt. Không sửa config v8 hoặc cache v8; mọi thay đổi sau review phải tạo version mới.

### Kiểm tra bộ runtime năm vai trò sau khi duyệt v8

Backend mặc định nạp candidate tại `configs/runtime/five_role_v1`. Có thể đặt rõ đường dẫn cho phiên PowerShell hiện tại:

```powershell
$env:CLASSIFIER_CONFIG_DIRECTORY="configs/runtime/five_role_v1"
```

Kiểm tra manifest, năm Job Profile/rubric, đủ 24 L1 rule, L2 query coverage, embedding revision, prompt/model lock và một classification Frontend offline:

```powershell
uv run pytest -q tests/contract/test_five_role_runtime_config.py tests/contract/test_embedding_adapters.py tests/contract/test_llm_adapters.py tests/unit/test_settings.py tests/integration/test_runtime_bootstrap.py
```

Chạy toàn bộ acceptance trước khi đề nghị freeze:

```powershell
uv run ruff check backend evaluation scripts tests
uv run ruff format --check backend evaluation scripts tests
uv run pyright backend evaluation scripts
uv run pytest -q
```

Không cần gọi OpenAI để thực hiện các kiểm tra này. Integration test dùng deterministic fake, model E5 snapshot cục bộ và prompt version của artifact. Nếu máy chưa có E5 đúng revision, việc tải model lần đầu cần mạng; không đổi revision để né lỗi tải.

Người dùng đã duyệt đầy đủ ngày 2026-08-07. `runtime_manifest.yaml` hiện ở trạng thái `frozen_for_stage7` và Gate 6 đã đóng. Mọi thay đổi tiếp theo đối với weights, thresholds, prompt, model, rubric hoặc L1/L2 policy phải tạo version runtime mới; không được điều chỉnh runtime này theo output Stage 7.

### Tái hiện checkpoint offline L1/L2 của Runtime v2

Các lệnh sau dùng dữ liệu Silver, model embedding snapshot cục bộ và không gọi LLM API:

```powershell
$env:HF_HUB_OFFLINE="1"
$env:TRANSFORMERS_OFFLINE="1"
uv run python -m evaluation.experiments.train_runtime_v2_l2_calibrator --generated-at 2026-08-08T07:30:00+07:00
uv run python -m evaluation.experiments.run_runtime_v2_offline_l1_l2 --generated-at 2026-08-08T09:00:00+07:00 --runtime-kind candidate --report-path evaluation/reports/runtime_v2_offline_l1_l2_checkpoint_v1.json
```

Kiểm tra nhanh report:

```powershell
$report = Get-Content evaluation/reports/runtime_v2_offline_l1_l2_checkpoint_v1.json -Raw | ConvertFrom-Json
$report.quality_gate
$report.development | Select-Object l1,l2
$report.validation | Select-Object l1,l2
$report | Select-Object llm_provider_calls_made,stage7_v1_test_accessed
```

Kỳ vọng `quality_gate.passed=true`, hai cờ API/frozen đều `false`, L1 không có mismatch và toàn bộ kiểm tra L2 đạt. Đọc `docs/runtime_v2_offline_checkpoint.md` để hiểu ý nghĩa và giới hạn trước khi chạy L3 pilot.

### Tái hiện Runtime v2 candidate 3.0.0 mà không gọi API

Các lệnh sau chấm lại mapping v3 từ cache structured và chạy selection 40 case development. Chúng không gửi request mới:

```powershell
uv run python -m evaluation.experiments.run_runtime_v2_l3_rescore --generated-at 2026-08-08T23:30:00+07:00 --output evaluation/reports/runtime_v2_l3_fresh_confirmation_v2_rescore_v3.json
uv run python -m evaluation.experiments.run_runtime_v2_hybrid_selection --configuration-path evaluation/configs/runtime_v2_hybrid_waitlist_tuning_v6.yaml --generated-at 2026-08-08T23:50:00+07:00 --output evaluation/reports/runtime_v2_hybrid_waitlist_tuning_v6.json
uv run pytest -q tests/contract/test_five_role_runtime_v2_candidate.py tests/evaluation/test_runtime_v2_l3_rescore.py tests/evaluation/test_runtime_v2_hybrid_selection.py
```

Không chạy lại các lệnh provider pilot nếu mục tiêu chỉ là kiểm tra report hiện tại. Cấu hình `configs/runtime/five_role_v2_candidate` vẫn ở trạng thái chờ duyệt và không được dùng như frozen runtime trước khi người dùng xác nhận.

## Khi một lệnh không chạy

1. Kiểm tra đang đứng ở thư mục gốc repository.
2. Chạy `uv sync --all-groups` nếu dependency Python thiếu.
3. Với database, kiểm tra Docker Desktop, `docker version`, `docker compose ps` và health của container.
4. Kiểm tra database URL đang trỏ đúng development hay disposable test database.
5. Nếu PostgreSQL tests bị skip, kiểm tra `CLASSIFIER_TEST_DATABASE_URL` có thật sự tồn tại trong PowerShell hiện tại.
6. Không hạ test, bỏ quality gate hoặc sửa ngưỡng chỉ để làm lệnh pass.
7. Giữ nguyên output lỗi và gửi lại để chẩn đoán.
