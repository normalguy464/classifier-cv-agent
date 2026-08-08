# Review Stage 4: Classifier Core và Dataset mở rộng

## Mục đích

Stage 4 biến các contract và quy tắc đã duyệt thành một classifier có thể chạy, lưu kết quả, cung cấp API và được kiểm thử. Song song với phần code, Stage 4 tạo thêm 30 hồ sơ tổng hợp để người dùng xác nhận trước khi dùng làm dữ liệu đánh giá có kiểm soát.

Gate 3 được xem là hoàn tất vì mười pilot annotation đã có trạng thái `approved` và người dùng đã yêu cầu chuyển sang triển khai toàn bộ Stage 4. Gate 4 vẫn đang mở vì 30 annotation mới còn `pending`.

Bạn không cần đọc toàn bộ source code để duyệt Gate 4. Quyết định nghiệp vụ bắt buộc của bạn là kiểm tra 30 hồ sơ và phiếu đánh giá; phần code được bảo vệ bằng automated tests và các check kỹ thuật.

## Luồng xử lý đã triển khai

```text
ClassificationRequest
        |
        +-- L1: quy tắc bắt buộc
        +-- L2: so khớp từng phần bằng embedding
        +-- L3: đánh giá dựa trên thông tin trong CV
        |
        v
Aggregation 45% / 25% / 30%
        |
        v
Routing và quality gates
        |
        v
ClassificationResult
        |
        v
Người phụ trách xác nhận hoặc override
        |
        v
ApprovedDecision và audit history
```

## Giải thích artifact và file Stage 4

Các file `__init__.py` chỉ đánh dấu package hoặc công khai tên import; chúng không chứa quyết định nghiệp vụ riêng và không yêu cầu bạn duyệt.

### Runtime, dependency và cấu hình

| Đường dẫn | Loại | Mục đích | Đầu vào hoặc thành phần sử dụng | Quyết định của người dùng |
| --- | --- | --- | --- | --- |
| `.env.example` | Cấu hình mẫu | Liệt kê biến môi trường cho API, runtime database, test database, embedding và LLM mà không chứa secret thật. | Được sao chép thành `.env` cục bộ; `RuntimeSettings`, Alembic và Docker sử dụng. | Đặt runtime DB và disposable test DB khác tên; không commit `.env`. |
| `.gitattributes` | Cấu hình repository | Ép shell script trong `scripts/` dùng LF để container Linux chạy đúng dù repository được thao tác trên Windows. | Git áp dụng khi checkout và commit. | Không có. |
| `.gitignore` | Cấu hình repository | Loại `.env`, virtual environment, cache và report sinh tự động khỏi source control. | Git và người đóng góp sử dụng. | Không có. |
| `docker-compose.yml` | Cấu hình dịch vụ | Chạy PostgreSQL 16 kèm pgvector, chỉ bind `127.0.0.1` trên port mặc định `55432`, và mount init script cho test DB. | Docker Desktop đọc biến `CLASSIFIER_POSTGRES_*`. | Chọn hai tên database khác nhau, user và password cục bộ. |
| `pyproject.toml` | Manifest Python | Khai báo Python 3.12, dependency runtime, dependency test và cấu hình Ruff, Pyright, pytest. | `uv` và các quality tool sử dụng. | Không đổi major version hoặc lockfile nếu không có nhiệm vụ riêng. |
| `uv.lock` | Lockfile | Cố định chính xác dependency đã giải quyết để môi trường có thể lặp lại. | `uv sync --all-groups`. | Không có. |
| `configs/l1_rules.yaml` | Cấu hình chấm L1 | Ánh xạ yêu cầu bắt buộc với phần CV, từ thể hiện đáp ứng và câu phủ định rõ ràng. | L1 loader và L1 scorer. | Chưa cần đóng băng ở Gate 4; thay đổi nghiệp vụ phải được review và test. |
| `configs/models.yaml` | Cấu hình model | Chọn multilingual E5 cho L2, prompt L3, provider qua môi trường và deterministic fake. | Config loader, embedding adapter và LLM adapter. | Provider thật chưa bắt buộc; model cuối được chốt ở Stage 6. |
| `configs/scoring.yaml` | Cấu hình quyết định | Cung cấp trọng số, ngưỡng và quality gates phiên bản `1.1.0`. | Aggregation và routing. | Đã duyệt cho pilot; tuning cuối thuộc Stage 6. |
| `configs/job_profiles/*.yaml` | Artifact nghiệp vụ được dùng lại | Hai Job Profile đã duyệt ở Stage 1. | Classification request và config loader. | Không duyệt lại ở Stage 4 nếu yêu cầu không đổi. |
| `configs/rubrics/*.yaml` | Artifact nghiệp vụ được dùng lại | Hai rubric năm tiêu chí, tổng 100 điểm. | L1, L2, L3 và annotation. | Không duyệt lại ở Stage 4 nếu tiêu chí không đổi. |
| `backend/app/contracts/classification.py` | Public contract được migration | Nâng boundary classify lên schema `1.1.0` và thêm phiên bản Job Profile artifact, L1 rules và models để truy vết. | API client, workflow, persistence và downstream reader của result. | Client classify cũ phải cập nhật payload; xem migration note bên dưới. |

### Classifier core và workflow

| Đường dẫn | Loại | Mục đích | Đầu vào hoặc thành phần sử dụng | Quyết định của người dùng |
| --- | --- | --- | --- | --- |
| `backend/app/domain/classification.py` | Source code nghiệp vụ | Định nghĩa các kiểu nội bộ bất biến cho assessment, policy, aggregation và routing. | Scoring modules và workflow. | Không có. |
| `backend/app/domain/errors.py` | Source code nghiệp vụ | Định nghĩa lỗi nghiệp vụ có kiểu thay cho lỗi chung chung. | Core và API error mapping. | Không có. |
| `backend/app/agents/classifier/scoring/l1.py` | Source code chấm điểm | Chấm yêu cầu và tiêu chí bằng quy tắc xác định từ `l1_rules.yaml`. | `CVProfile`, rubric và L1 policy; graph sử dụng. | Xem hành vi qua 30 case, không cần duyệt code dòng một. |
| `backend/app/agents/classifier/scoring/l2.py` | Source code chấm điểm | So khớp rubric với từng section CV bằng embedding; không embedding toàn CV. | Embedding adapter, CV, rubric và L2 policy. | Model cuối được chọn ở Stage 6. |
| `backend/app/agents/classifier/scoring/l3.py` | Source code chấm điểm | Gửi dữ liệu có giới hạn cho L3, kiểm tra score, confidence và structured output. | L3 provider và graph sử dụng. | Provider thật chưa bắt buộc ở Gate 4. |
| `backend/app/agents/classifier/scoring/aggregation.py` | Source code chấm điểm | Kết hợp L1/L2/L3 theo trọng số, kiểm tra score bounds và provider failure. | Ba level assessment và cấu hình aggregation. | Đối chiếu kết quả biên trong dataset review. |
| `backend/app/agents/classifier/routing.py` | Source code nghiệp vụ | Áp dụng precedence, ngưỡng và tất cả điều kiện `Needs Review`. | Aggregation, trạng thái yêu cầu và routing policy. | Xác nhận 30 nhãn dự thảo phản ánh đúng chính sách. |
| `backend/app/agents/classifier/state.py` | Source code workflow | Khai báo state có kiểu đi qua các node của classifier. | LangGraph workflow. | Không có. |
| `backend/app/agents/classifier/graph.py` | Source code workflow | Chạy L1/L2/L3 song song, rồi aggregate, route và tạo `ClassificationResult`. | Application use case gọi; phụ thuộc được inject. | Không có. |
| `backend/app/agents/classifier/prompts/l3.py` | Source code prompt | Tạo prompt L3 theo rubric và yêu cầu model chỉ dùng thông tin đã cung cấp. | LLM adapter sử dụng. | Prompt cuối được đóng băng ở Stage 6. |

### Application và API

| Đường dẫn | Loại | Mục đích | Đầu vào hoặc thành phần sử dụng | Quyết định của người dùng |
| --- | --- | --- | --- | --- |
| `backend/app/application/ports.py` | Source code kiến trúc | Định nghĩa interface cho workflow, repository, clock và identifier. | Use case và infrastructure adapters. | Không có. |
| `backend/app/application/classify_candidate.py` | Source code use case | Chạy classifier rồi lưu kết quả qua repository. | API route gọi. | Không có. |
| `backend/app/application/review_decision.py` | Source code use case | Lấy kết quả, ghi approval hoặc override và đọc lịch sử quyết định. | Decision API routes gọi. | Human review là bắt buộc trước downstream. |
| `backend/app/api/app.py` | Source code API | Tạo FastAPI app, health endpoint và ánh xạ lỗi sang HTTP status. | `backend/app/main.py`. | Không có. |
| `backend/app/api/dependencies.py` | Source code API | Cung cấp application container và kiểm tra `X-Classifier-API-Key`. | Tất cả route phân loại và quyết định. | Đặt API key cục bộ hoặc secret store. |
| `backend/app/api/routes/classifications.py` | Source code API | Tạo và truy xuất `ClassificationResult`. | Client hoặc frontend tương lai gọi. | Không có. |
| `backend/app/api/routes/decisions.py` | Source code API | Ghi và xem lịch sử `ApprovedDecision`. | Người phụ trách hoặc frontend tương lai gọi. | Override phải có lý do theo contract. |
| `backend/app/main.py` | Entry point | Khởi tạo app từ `RuntimeSettings` để Uvicorn chạy. | Lệnh `uv run uvicorn backend.app.main:app`. | Chọn runtime qua biến môi trường. |

### Infrastructure, model adapters và persistence

| Đường dẫn | Loại | Mục đích | Đầu vào hoặc thành phần sử dụng | Quyết định của người dùng |
| --- | --- | --- | --- | --- |
| `backend/app/core/settings.py` | Source code cấu hình | Đọc và kiểm tra biến môi trường cho storage, API, model và timeout. | Bootstrap sử dụng. | Chọn `memory` hoặc `postgres`; không đưa secret vào source. |
| `backend/app/core/errors.py` | Source code lỗi | Định nghĩa lỗi cấu hình và không tìm thấy dữ liệu ở cấp ứng dụng. | Bootstrap, loader và API. | Không có. |
| `backend/app/infrastructure/config/artifacts.py` | Source code cấu hình | Mô hình hóa chặt chẽ cấu trúc `models.yaml` và `l1_rules.yaml`. | Config loader. | Không có. |
| `backend/app/infrastructure/config/loaders.py` | Source code cấu hình | Đọc YAML, kiểm tra liên kết version và tạo policy runtime cho đúng vị trí. | Bootstrap và workflow. | Request không được tự thay artifact runtime. |
| `backend/app/infrastructure/embeddings/adapters.py` | Source code adapter | Cung cấp Sentence Transformers adapter thực và hashing fake xác định cho test/baseline. | L2 runtime, tests và baseline. | Chấp nhận lần tải model đầu tiên hoặc chuẩn bị model cục bộ. |
| `backend/app/infrastructure/llm/adapters.py` | Source code adapter | Cung cấp fake xác định và adapter HTTP tương thích OpenAI có structured validation. | L3 runtime và contract tests. | Chỉ cung cấp API key khi chủ động dùng provider thật. |
| `backend/app/infrastructure/runtime.py` | Source code hạ tầng | Cung cấp clock UTC và UUID generator để workflow không tự phụ thuộc hệ thống. | Graph và tests. | Không có. |
| `backend/app/infrastructure/bootstrap.py` | Source code lắp ghép | Kết nối config, scorer, model adapter, repository, use case và FastAPI. | `main.py` gọi. | Chọn adapter và storage bằng biến môi trường. |
| `backend/app/infrastructure/persistence/memory.py` | Source code persistence | Lưu tạm kết quả và quyết định trong tiến trình để test hoặc kiểm tra nhanh. | Runtime khi storage là `memory`. | Không dùng cho dữ liệu cần giữ sau restart. |
| `backend/app/infrastructure/persistence/models.py` | Source code database | Khai báo bảng classification run, embedding, decision và audit event. | SQLAlchemy repository và Alembic metadata. | Không có. |
| `backend/app/infrastructure/persistence/repositories.py` | Source code persistence | Cài đặt repository PostgreSQL, append-only invariants và truy xuất history. | Application use cases. | Không có. |
| `backend/app/infrastructure/persistence/session.py` | Source code database | Chuẩn hóa URL, tạo async engine và session factory. | Bootstrap, repository và migration tests. | Dùng URL database phù hợp môi trường. |
| `backend/alembic.ini` | Cấu hình migration | Chỉ vị trí migration và logging; URL lấy từ biến môi trường. | Alembic CLI. | Không ghi password vào file này. |
| `backend/migrations/env.py` | Source code migration | Dùng URL được truyền trực tiếp nếu có; nếu không, đọc runtime `CLASSIFIER_DATABASE_URL` từ environment hoặc `.env`, rồi chạy async migration. | Alembic CLI và tests. | Development migration không tự chọn test URL. |
| `backend/migrations/script.py.mako` | Template migration | Khuôn Alembic dùng khi tạo migration mới. | Alembic developer workflow. | Không có. |
| `backend/migrations/versions/20260726_0001_stage4_persistence.py` | Migration | Tạo pgvector, bốn bảng nghiệp vụ, vector 768 chiều và trigger append-only. | PostgreSQL development và test. | Phải chạy trên database cục bộ trước Gate 4. |
| `scripts/init_test_database.sh` | Script khởi tạo database | Tạo database test tách biệt khi PostgreSQL volume được khởi tạo lần đầu và từ chối tên trùng runtime DB. | Docker entrypoint sử dụng. | Đặt `CLASSIFIER_POSTGRES_TEST_DB` khác `CLASSIFIER_POSTGRES_DB`. |

### Dataset, evaluation và script

| Đường dẫn | Loại | Mục đích | Đầu vào hoặc thành phần sử dụng | Quyết định của người dùng |
| --- | --- | --- | --- | --- |
| `data/to_review/stage4_cv_profiles_v1.jsonl` | Dữ liệu tổng hợp | Chứa 30 `CVProfile`, mỗi dòng một hồ sơ; 15 cho mỗi vị trí. | Người duyệt đọc; classifier dùng làm input sau này. | Xác nhận nội dung hồ sơ đủ để chấm. |
| `data/to_review/stage4_annotations_v1.json` | Phiếu đánh giá dự thảo | Chứa trạng thái yêu cầu, năm nhóm điểm, nhãn, rationale và review fields cho 30 hồ sơ. | Người dùng duyệt; evaluation chỉ dùng sau approval. | Đây là quyết định chính để đóng Gate 4. |
| `scripts/generate_stage4_dataset.py` | Script dữ liệu | Sinh lại deterministically hai file Stage 4 từ 15 scenario cho mỗi vị trí. | Developer và dataset contract test. | Không chạy lại sau khi đã ghi review vì sẽ ghi đè bản nháp. |
| `evaluation/datasets/reviewed.py` | Source code evaluation | Chỉ nạp annotation pilot đã được người duyệt xác nhận. | Baseline runner. | Không nạp dữ liệu Stage 4 còn pending. |
| `evaluation/baselines/models.py` | Source code baseline | Định nghĩa output chung và cách đổi score baseline thành nhãn an toàn. | Ba baseline sử dụng. | Không có. |
| `evaluation/baselines/keyword.py` | Source code baseline | Mốc so sánh bằng quy tắc keyword L1. | Baseline experiment. | Không xem là classifier cuối. |
| `evaluation/baselines/tfidf.py` | Source code baseline | Mốc so sánh TF-IDF cosine giữa CV và yêu cầu vị trí. | Baseline experiment. | Không có. |
| `evaluation/baselines/embedding.py` | Source code baseline | Mốc chỉ dùng embedding với hashing xác định cho khả năng lặp lại. | Baseline experiment và tests. | Không đại diện model L2 production. |
| `evaluation/metrics/classification.py` | Source code metrics | Tính accuracy, precision, recall, F1, macro-F1, Cohen's kappa và confusion matrix. | Baseline và evaluation tests. | Chỉ diễn giải khi dataset đã có ground truth. |
| `evaluation/experiments/run_baselines.py` | Script evaluation | Chạy ba baseline trên mười pilot case đã review và in JSON report. | Người phát triển chạy ở Stage 4. | Kết quả chỉ diagnostic, không phải final performance. |
| `data/README.md` | Tài liệu dữ liệu | Giải thích phạm vi, trạng thái review, an toàn và lệnh kiểm tra dữ liệu. | Người dùng và contributor đọc. | Tuân theo trước khi thêm hoặc duyệt dữ liệu. |

### Automated tests

| Đường dẫn | Loại | Mục đích chính | Đầu vào hoặc thành phần sử dụng | Quyết định của người dùng |
| --- | --- | --- | --- | --- |
| `tests/unit/test_l1.py` | Unit test | Kiểm tra satisfied, unsatisfied, missing, conflicting và điểm L1. | pytest chạy scorer L1 cô lập. | Không có. |
| `tests/unit/test_l2.py` | Unit test | Kiểm tra section matching, score bounds và embedding failure. | pytest với fake embedding. | Không có. |
| `tests/unit/test_l3.py` | Unit test | Kiểm tra structured output, failure, criterion và confidence của L3. | pytest với fake provider. | Không có. |
| `tests/unit/test_aggregation.py` | Unit test | Kiểm tra trọng số, score bounds, provider fallback và điểm tổng. | pytest chạy aggregation. | Không có. |
| `tests/unit/test_routing.py` | Unit test | Kiểm tra Pass, Waitlist, Reject và mọi nhánh `Needs Review`. | pytest chạy routing. | Không có. |
| `tests/unit/test_graph.py` | Unit test | Kiểm tra thứ tự graph, kết quả và version traceability. | pytest với dependencies xác định. | Không có. |
| `tests/unit/test_application.py` | Unit test | Kiểm tra classify, lưu kết quả, approval và override use cases. | pytest với repository fake. | Không có. |
| `tests/unit/test_memory_repository.py` | Unit test | Kiểm tra lưu, lấy và audit history trong memory. | pytest. | Không có. |
| `tests/unit/test_runtime.py` | Unit test | Kiểm tra clock và identifier generator. | pytest. | Không có. |
| `tests/unit/test_settings.py` | Unit test | Kiểm tra biến môi trường, default và cấu hình không hợp lệ. | pytest. | Không có. |
| `tests/unit/test_evaluation.py` | Unit test | Kiểm tra metrics, baseline và ngăn dùng annotation chưa review. | pytest. | Không có. |
| `tests/contract/test_config_loaders.py` | Contract test | Kiểm tra YAML, version links, tổng trọng số và policy được load. | pytest và artifacts trong `configs/`. | Không có. |
| `tests/contract/test_database_configuration.py` | Contract test hạ tầng | Kiểm tra Compose bind localhost, runtime/test DB khác nhau, init script và URL mẫu nhất quán. | pytest đọc `.env.example`, Compose và init script. | Không có. |
| `tests/contract/test_embedding_adapters.py` | Contract test | Kiểm tra shape, normalization, model metadata và fake embedding. | pytest với model fake. | Không có. |
| `tests/contract/test_llm_adapters.py` | Contract test | Kiểm tra request, response validation, timeout và provider failure. | pytest với HTTP fake. | Không có. |
| `tests/contract/test_stage4_dataset.py` | Contract test dữ liệu | Kiểm tra đủ 30 hồ sơ, cân bằng vai trò, điểm, version, nhãn, protected fields và label-leakage markers. | pytest và generator. | Không thay thế human review. |
| `tests/contract/test_contracts.py` | Contract test được mở rộng | Bảo vệ contract v1 khi core sử dụng. | pytest. | Không có. |
| `tests/contract/test_pilot_dataset.py` | Regression test dữ liệu | Bảo đảm mười pilot case đã duyệt vẫn đúng. | pytest. | Không có. |
| `tests/integration/test_api.py` | Integration test | Kiểm tra validation, auth, classify, retrieve, approve, override và HTTP errors. | FastAPI test client với dependencies kiểm soát. | Không có. |
| `tests/integration/test_persistence.py` | Integration test | Kiểm tra PostgreSQL repository, vector dimension và append-only audit behavior. | PostgreSQL test database. | Test database phải tách biệt và có thể xóa. |
| `tests/integration/test_migrations.py` | Integration test | Downgrade/upgrade schema, pgvector, tables, triggers và `alembic check`. | `CLASSIFIER_TEST_DATABASE_URL`. | Tuyệt đối không trỏ vào database cần giữ dữ liệu. |
| `tests/integration/test_runtime_bootstrap.py` | Integration test | Kiểm tra bootstrap thật với config, API và repository. | pytest với adapter kiểm soát. | Không có. |

## Migration note cho public contract

Stage 4 thay đổi schema theo phạm vi sau:

| Contract | Schema trước Stage 4 | Schema hiện tại | Client cần làm gì |
| --- | --- | --- | --- |
| `CVProfile` | `1.0.0` | `1.0.0` | Không đổi. |
| `JobProfile` | `1.0.0` | `1.0.0` | Không đổi. |
| `ScoringRubric` | `1.0.0` | `1.0.0` | Không đổi. |
| `ApprovedDecision` | `1.0.0` | `1.0.0` | Không đổi. |
| `ClassificationConfig` | `1.0.0` | `1.1.0` | Thêm `job_profile_artifact_version`, `l1_rules_configuration_version`, `models_configuration_version`. |
| `ClassificationRequest` | `1.0.0` | `1.1.0` | Gửi schema `1.1.0` và configuration `1.1.0`. |
| `ClassificationResult` | `1.0.0` | `1.1.0` | Chấp nhận schema `1.1.0`, ba version field mới, embedding model identifier và LLM provider identifier trong `versions`. |

Các field mới là additive về mặt dữ liệu, nhưng payload classify `1.0.0` bị reject có chủ đích. Nếu tự chấp nhận payload cũ, một classification có thể thiếu phiên bản Job Profile artifact, L1 rules hoặc models và không thể tái hiện chính xác.

## Bộ 30 hồ sơ cần bạn duyệt

### Phân bố

- 15 hồ sơ Junior Data Analyst: `cv-s4-da-001` đến `cv-s4-da-015`.
- 15 hồ sơ Junior Python Backend Developer: `cv-s4-be-001` đến `cv-s4-be-015`.
- Nhãn dự thảo toàn bộ dataset: 6 `pass`, 6 `waitlist`, 2 `reject`, 16 `needs_review`.
- Cả 30 record hiện có `review.status: "pending"`; chưa record nào là ground truth.

Hai vị trí dùng cùng cấu trúc 15 scenario:

| Số cuối ID | Mục đích scenario | Nhãn dự thảo |
| --- | --- | --- |
| `001`–`003` | Đáp ứng rõ với ba mức điểm cao | `pass` |
| `004`–`006` | Đáp ứng yêu cầu bắt buộc nhưng chiều sâu thấp hơn | `waitlist` |
| `007`–`008` | Thiếu thông tin cho yêu cầu bắt buộc | `needs_review` |
| `009`–`010` | Thông tin bắt buộc mâu thuẫn | `needs_review` |
| `011` | Điểm dưới 60 và có yêu cầu bắt buộc không đạt rõ | `reject` |
| `012` | Điểm dưới 60 nhưng không có yêu cầu bắt buộc không đạt rõ | `needs_review` |
| `013` | Điểm trong vùng biên 58–62 | `needs_review` |
| `014` | Điểm trong vùng biên 73–77 | `needs_review` |
| `015` | Có yêu cầu bắt buộc không đạt nhưng điểm từ 60 trở lên | `needs_review` |

### Cách xem một hồ sơ và phiếu tương ứng

Ví dụ với `cv-s4-da-001`, chạy trong PowerShell ở thư mục gốc:

```powershell
$cvId = "cv-s4-da-001"
Get-Content data\to_review\stage4_cv_profiles_v1.jsonl |
  ForEach-Object { $_ | ConvertFrom-Json } |
  Where-Object cv_profile_id -eq $cvId |
  ConvertTo-Json -Depth 20
```

```powershell
$annotations = Get-Content -Raw data\to_review\stage4_annotations_v1.json | ConvertFrom-Json
$annotations.records |
  Where-Object cv_profile_id -eq $cvId |
  ConvertTo-Json -Depth 20
```

Bạn cũng có thể mở trực tiếp hai file trong editor và tìm theo `cv_profile_id`. Nên duyệt theo từng nhóm năm hồ sơ để dễ đối chiếu.

### Mỗi hồ sơ cần xác nhận năm nội dung

1. `critical_requirement_assessments`: trạng thái từng yêu cầu bắt buộc có đúng với thông tin trong CV không. `missing` chỉ là thiếu thông tin, không được tự hiểu thành `unsatisfied`.
2. `criterion_assessments`: năm mức điểm có hợp lý không; mỗi điểm không vượt mức tối đa `30/25/20/15/10` và `total_score` phải bằng tổng.
3. `draft_label`: nhãn có tuân theo ngưỡng và các quality gate không.
4. `rationale`, `review_reasons` và `ambiguity_notes`: lý do có ngắn gọn, truy được về thông tin trong hồ sơ và không suy diễn quá mức không.
5. An toàn dữ liệu: không chấm hoặc suy luận tuổi, giới tính, quê quán, tình trạng hôn nhân hay thuộc tính nhạy cảm khác.

### Khi nào phần review đạt yêu cầu

Gate 4 chỉ có thể đóng sau khi:

- bạn đã xem và chấp thuận hoặc yêu cầu sửa đủ 30 record;
- mọi record có quyết định cuối rõ ràng, không còn mơ hồ do cấu trúc rubric;
- coding agent ghi `review.status`, `reviewer_reference`, `final_label`, `reviewed_at`, score override và lý do nếu có mà không sửa mất `draft_label`;
- dataset đã review vượt qua contract tests và được chuẩn bị làm dữ liệu đánh giá có kiểm soát;
- classifier core tiếp tục vượt qua các check bắt buộc.

### Mẫu phản hồi

Nếu đồng ý toàn bộ:

```text
Tôi đã duyệt 30 hồ sơ Stage 4 và đồng ý với requirement status, năm nhóm điểm,
draft label và rationale. Hãy ghi nhận human review và hoàn tất Gate 4.
```

Nếu cần sửa:

```text
Tôi duyệt các hồ sơ còn lại, nhưng yêu cầu sửa:
- cv-s4-da-007: ...
- cv-s4-be-011: ...
Sau khi sửa, hãy đưa lại đúng các hồ sơ này để tôi xác nhận.
```

Chỉ nói “Stage 4 ổn” mà chưa xác nhận phạm vi 30 hồ sơ sẽ chưa đủ để biến các nhãn dự thảo thành ground truth.

## Xác minh kỹ thuật đã thực hiện

Tại lần bàn giao Stage 4 ngày 2026-07-26:

- Docker Desktop và WSL 2 hoạt động; cấu hình Compose mới được dựng bằng fresh volume trên port `55432`: service chỉ bind `127.0.0.1`, runtime DB và disposable test DB được tạo tách biệt. Container, network và volume test-only đã được xóa sau acceptance.
- Cơ chế fresh-volume isolation cũng được xác minh độc lập trên port tạm `55439`; tài nguyên tạm của lượt kiểm tra đó đã được dọn.
- Alembic `upgrade head` và `check` chạy thành công.
- Ruff check đạt; Ruff format xác nhận 88 file đúng định dạng.
- Pyright strict đạt `0 errors, 0 warnings, 0 informations`.
- Full pytest suite chạy qua `uv` với PostgreSQL thật và database test tách biệt: `213 passed, 0 skipped in 12.40s`.
- Stage 4 dataset tests còn kiểm tra L1 thực tế khớp trạng thái dự thảo cho đủ 30 hồ sơ, không chỉ kiểm tra JSON.
- Baseline pilot chạy trên 10 case đã review; report có scope `reviewed-pilot-diagnostic-only` và `is_final_performance: false`.

Kết quả baseline không được dùng để tuyên bố hiệu năng cuối, chọn model cuối hoặc tự thay nhãn người dùng.

Lượt acceptance này dùng deterministic fakes hoặc adapters được kiểm soát cho model-dependent tests. Nó không tuyên bố đã đánh giá chất lượng của một LLM provider thật, không coi hashing embedding là model L2 thật, và không phải final model evaluation. Provider thật, model cuối và cấu hình cuối được so sánh hoặc đóng băng ở Stage 6.
