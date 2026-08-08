# AI Classifier Agent

## Trạng thái dự án

Đây là prototype nghiên cứu của Classifier Agent trong hệ thống tuyển dụng có AI hỗ trợ. Phạm vi triển khai tám Stage đã hoàn thành ở mức phục vụ đồ án: FastAPI backend, Runtime v2 cho năm vai trò, giao diện Next.js, chế độ offline và LLM thật, human review cùng lịch sử quyết định.

Runtime v2 `3.0.0` đã được khóa sau Stage 7. Trên 50 case Gold tổng hợp, kết quả cuối là accuracy `48%`, Macro-F1 `16,22%`, review rate `98%`, false Reject `0` và unsafe Pass `0`. Quality gate mục tiêu `70%` không đạt. Vì vậy, hệ thống chỉ được trình bày là công cụ hỗ trợ người duyệt, không phải hệ thống tuyển dụng tự động hoặc production-ready.

Nguồn trạng thái và ngữ cảnh quan trọng:

- [HANDOFF.md](HANDOFF.md): điểm bắt đầu ngắn gọn cho lần tiếp tục sau.
- [progress.md](progress.md): lịch sử tiến độ và quyết định đầy đủ.
- [AGENTS.md](AGENTS.md): quy tắc kiến trúc, dữ liệu, kiểm thử và workflow.
- [Kết quả Stage 7](docs/stage_7_runtime_v2_evaluation_review.md): metric, lỗi và giới hạn đã được khóa.
- [Chế độ demo Stage 8](docs/stage_8_demo_modes.md): cách phân biệt offline và LLM thật.

## Hệ thống làm gì

Classifier nhận `CVProfile` đã được Parser hoặc con người chuẩn hóa, sau đó đối chiếu với `JobProfile`, rubric và cấu hình có phiên bản qua ba tầng:

- L1 kiểm tra các yêu cầu bắt buộc bằng quy tắc xác định.
- L2 so khớp ngữ nghĩa từng phần CV bằng embedding đa ngôn ngữ.
- L3 đánh giá thông tin trong CV bằng adapter offline hoặc LLM thật.
- Aggregation và routing tổng hợp điểm, áp dụng quality gate và chuyển trường hợp không chắc chắn sang `Needs Review`.

`ClassificationResult` chỉ là đề xuất. Chỉ `ApprovedDecision` do người có thẩm quyền xác nhận mới được chuyển cho agent phía sau.

Classifier không đọc trực tiếp PDF, DOCX, ảnh hoặc OCR; không gửi email, đặt lịch; không dùng tuổi, giới tính, quê quán hoặc thuộc tính nhạy cảm để chấm điểm; không tự đưa ra quyết định tuyển dụng không thể đảo ngược.

## Công nghệ và yêu cầu cài đặt

| Thành phần | Phiên bản hoặc yêu cầu |
| --- | --- |
| Python | `3.12.x`, không dùng `3.13` |
| uv | Trình quản lý môi trường và dependency Python |
| Node.js | `22.14.0`, được ghi trong `.nvmrc` |
| pnpm | `11.16.0`, được ghi trong `frontend/package.json` |
| Docker Desktop và WSL 2 | Chỉ bắt buộc khi chạy PostgreSQL |
| Internet | Cần khi cài dependency, tải embedding model lần đầu hoặc gọi LLM thật |

Kiểm tra môi trường trong PowerShell:

```powershell
python --version
uv --version
node --version
pnpm --version
docker version
docker compose version
```

Nếu PowerShell chưa nhận `pnpm` nhưng đã có Node.js:

```powershell
corepack enable
corepack prepare pnpm@11.16.0 --activate
pnpm --version
```

Nếu `corepack` cũng không tồn tại, hãy cài Node.js 22 LTS rồi mở PowerShell mới.

## Cài đặt lần đầu

Từ thư mục gốc repository:

```powershell
Set-Location D:\graduation_project\Classifier_agent_code
uv sync --all-groups
pnpm --dir frontend install --frozen-lockfile
```

Chỉ tạo `.env` từ mẫu nếu máy chưa có file này:

```powershell
Copy-Item .env.example .env
```

Không chạy lệnh trên nếu `.env` hiện tại đã chứa cấu hình riêng, vì nó có thể bị ghi đè. `.env` đã nằm trong `.gitignore` và không được commit.

## Cấu hình `.env`

Cấu hình tối thiểu để chạy demo bằng memory repository:

```dotenv
CLASSIFIER_API_KEY=replace-with-a-local-backend-key
CLASSIFIER_STORAGE_BACKEND=memory
CLASSIFIER_CONFIG_DIRECTORY=configs/runtime/five_role_v2
CLASSIFIER_EMBEDDING_ADAPTER=sentence_transformers
CLASSIFIER_LLM_ADAPTER=deterministic_fake
CLASSIFIER_REQUEST_TIMEOUT_SECONDS=30
```

`CLASSIFIER_API_KEY` là khóa nội bộ giữa frontend và backend, không phải API key trả phí của provider.

Nếu dùng OpenAI LLM thật, bổ sung hoặc cập nhật các biến sau trong `.env`:

```dotenv
CLASSIFIER_LLM_PROVIDER=openai
CLASSIFIER_LLM_MODEL=gpt-5.4-mini-2026-03-17
CLASSIFIER_LLM_API_KEY=replace-with-your-own-provider-key
CLASSIFIER_LLM_BASE_URL=https://api.openai.com/v1
```

Không thêm tiền tố `NEXT_PUBLIC_` vào API key. Frontend chỉ tự đọc danh sách biến kết nối backend được cho phép; `CLASSIFIER_LLM_API_KEY` chỉ được FastAPI đọc và không được gửi xuống trình duyệt.

Nếu dùng provider hoặc model khác, phải tạo một runtime/configuration version mới và kiểm thử lại; không sửa Runtime v2 đã khóa rồi tiếp tục gọi đó là cùng một kết quả Stage 7.

## Chạy demo offline

Chế độ này không gọi provider trả phí. L3 dùng `deterministic_fake`; L1, L2, aggregation, quality gate, human review và audit vẫn chạy thật theo source hiện tại.

Mở PowerShell thứ nhất:

```powershell
Set-Location D:\graduation_project\Classifier_agent_code
$env:CLASSIFIER_LLM_ADAPTER="deterministic_fake"
uv run uvicorn backend.app.main:app --reload --port 8000
```

Mở PowerShell thứ hai:

```powershell
Set-Location D:\graduation_project\Classifier_agent_code
pnpm --dir frontend dev
```

Mở giao diện tại `http://localhost:3000`. Kiểm tra backend mà không tạo classification:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod "http://127.0.0.1:3000/api/health?execution_mode=offline"
```

Lần phân loại đầu tiên có thể tải snapshot `intfloat/multilingual-e5-base`. Nếu model chưa có trong cache và máy mất mạng, L2 không thể khởi tạo.

## Chạy đồng thời offline và LLM thật

Đảm bảo `.env` chứa provider, model và `CLASSIFIER_LLM_API_KEY` hợp lệ. Hai backend dùng chung `CLASSIFIER_API_KEY` trong `.env`.

PowerShell thứ nhất, backend offline:

```powershell
Set-Location D:\graduation_project\Classifier_agent_code
$env:CLASSIFIER_LLM_ADAPTER="deterministic_fake"
uv run uvicorn backend.app.main:app --reload --port 8000
```

PowerShell thứ hai, backend LLM thật:

```powershell
Set-Location D:\graduation_project\Classifier_agent_code
$env:CLASSIFIER_LLM_ADAPTER="environment_configured"
uv run uvicorn backend.app.main:app --reload --port 8001
```

PowerShell thứ ba, frontend:

```powershell
Set-Location D:\graduation_project\Classifier_agent_code
pnpm --dir frontend dev
```

Kiểm tra kết nối trước khi phát sinh request provider:

```powershell
Invoke-RestMethod http://127.0.0.1:8001/health
Invoke-RestMethod "http://127.0.0.1:3000/api/health?execution_mode=llm"
```

Trên giao diện, chọn `LLM thật`, xác nhận khả năng phát sinh phí rồi mới chạy. Nếu thấy `fetch failed`, kiểm tra backend cổng `8001` và khởi động lại frontend sau khi thay `.env`. Hệ thống không tự fallback sang offline khi LLM thật lỗi.

## Chạy với PostgreSQL

Điền các biến database trong `.env` bằng giá trị cục bộ của bạn:

```dotenv
CLASSIFIER_POSTGRES_DB=classifier_runtime
CLASSIFIER_POSTGRES_TEST_DB=classifier_test
CLASSIFIER_POSTGRES_USER=classifier_user
CLASSIFIER_POSTGRES_PASSWORD=replace-with-a-local-password
CLASSIFIER_POSTGRES_PORT=55432
CLASSIFIER_DATABASE_URL=postgresql+psycopg://classifier_user:replace-with-a-local-password@127.0.0.1:55432/classifier_runtime
CLASSIFIER_TEST_DATABASE_URL=postgresql+psycopg://classifier_user:replace-with-a-local-password@127.0.0.1:55432/classifier_test
CLASSIFIER_STORAGE_BACKEND=postgres
```

Khởi động database và chạy migration:

```powershell
docker compose up -d postgres
docker compose ps
uv run alembic -c backend/alembic.ini upgrade head
uv run alembic -c backend/alembic.ini check
```

Sau đó chạy backend offline hoặc LLM như các phần trên. Dừng dịch vụ khi hoàn tất:

```powershell
docker compose down
```

`docker compose down` không xóa named volume. Không dùng tùy chọn xóa volume nếu còn cần dữ liệu.

## Chạy bản frontend production cục bộ

Backend cần được khởi động trước. Sau đó:

```powershell
pnpm --dir frontend build
pnpm --dir frontend start
```

## Lệnh kiểm tra dự án

Backend đầy đủ:

```powershell
uv run ruff check backend evaluation scripts tests
uv run ruff format --check backend evaluation scripts tests
uv run pyright backend evaluation scripts
uv run pytest -q
```

Backend theo nhóm:

```powershell
uv run pytest -q tests/unit
uv run pytest -q tests/contract
uv run pytest -q tests/integration
```

Các test PostgreSQL được skip nếu test database chưa chạy. Database test phải dùng `CLASSIFIER_TEST_DATABASE_URL` trỏ tới database riêng, không dùng database chứa dữ liệu cần giữ.

Frontend:

```powershell
pnpm --dir frontend lint
pnpm --dir frontend test
pnpm --dir frontend build
```

E2E tùy chọn, cần backend offline và browser Playwright:

```powershell
pnpm --dir frontend exec playwright install chromium
pnpm --dir frontend test:e2e
```

Không cần gọi LLM thật để chạy test thường hoặc E2E. Adapter fake và mock được dùng để tránh chi phí và giữ kết quả tái lập.

## API chính

| Phương thức và đường dẫn | Chức năng | Xác thực |
| --- | --- | --- |
| `GET /health` | Kiểm tra backend | Không |
| `POST /v1/classifications` | Chạy và lưu `ClassificationResult` | `X-Classifier-API-Key` |
| `GET /v1/classifications/{id}` | Lấy kết quả đã lưu | `X-Classifier-API-Key` |
| `POST /v1/classifications/{id}/decisions` | Ghi approval hoặc override | `X-Classifier-API-Key` |
| `GET /v1/classifications/{id}/decisions` | Lấy lịch sử human review | `X-Classifier-API-Key` |

Swagger UI nằm tại `http://127.0.0.1:8000/docs` hoặc cổng backend đang chạy.

## Cấu trúc chính

```text
backend/app/contracts/                 Pydantic contracts có phiên bản
backend/app/agents/classifier/         L1, L2, L3, aggregation và routing
backend/app/application/               Use case phân loại và human review
backend/app/infrastructure/            Adapter, runtime config và persistence
backend/app/api/                       FastAPI và authentication
backend/migrations/                    Alembic migration
frontend/                              Next.js dashboard và Backend-for-Frontend
configs/runtime/five_role_v2/          Runtime v2 đã khóa
data/                                  Dữ liệu tổng hợp, review và frozen test
evaluation/                            Protocol, runner, metric và report
tests/                                 Unit, contract, integration và E2E
docs/                                  Review, hướng dẫn và tài liệu kỹ thuật
```

## Dữ liệu, bảo mật và GitHub

- Chỉ dùng dữ liệu tổng hợp, có sự đồng ý hoặc đã ẩn danh không thể đảo ngược.
- Không commit `.env`, API key, raw provider response, CV thật hoặc thông tin nhận dạng cá nhân.
- Người clone repository phải tự tạo `.env` và dùng API key của họ nếu muốn chạy LLM thật.
- Khi chỉ chạy offline, không cần provider API key.
- Không dùng dữ liệu frozen test để tuning lại Runtime v2.

Sau khi thư mục đã được `git init` hoặc clone từ GitHub, hãy kiểm tra trước khi push:

```powershell
git check-ignore -v .env
git status --short
```

## Giới hạn đã biết

- Metric `48%` được đo trên 50 case tổng hợp, không dự đoán chắc chắn hiệu năng trên CV thực tế.
- Chưa có Parser Agent nên classifier không nhận PDF, DOCX hoặc ảnh CV trực tiếp.
- Thử nghiệm một CV đã ẩn danh cho thấy L1 có thể nhận nhầm năng lực từ từ khóa lân cận; đánh giá dữ liệu thật cần Parser, JD cố định và human ground truth độc lập.
- L2 có thể bị nén điểm hoặc lệch khi cách viết CV khác dữ liệu phát triển.
- LLM thật tạo rationale tự nhiên hơn nhưng không thay thế ground truth và không đảm bảo sửa được lỗi L1/L2.
- Review rate cao làm hệ thống an toàn hơn trước Reject/Pass sai, nhưng giảm mức tự động hóa.
- Kết quả demo đẹp ở một case không phải bằng chứng về accuracy toàn hệ thống.

Hướng cải thiện tương lai nằm tại [docs/dinh_huong_cai_thien_sau_runtime_v2.md](docs/dinh_huong_cai_thien_sau_runtime_v2.md). Thuật ngữ dự án nằm tại [docs/thuat_ngu.md](docs/thuat_ngu.md).

## Điểm tiếp tục

Phần triển khai hiện được tạm đóng ở Stage 8 theo phạm vi đồ án đã thống nhất. Bước tiếp theo là viết báo cáo: mô tả bài toán, kiến trúc L1-L2-L3, quy trình tám Stage, dữ liệu và human review, thí nghiệm, kết quả không đạt quality gate, error analysis, giới hạn và hướng phát triển. Không thay đổi Runtime v2 hoặc chạy lại frozen test trong lúc viết báo cáo.
