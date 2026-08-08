# Phương án cải thiện demo Stage 8

## Mục tiêu

Demo phải phân biệt rõ việc kiểm tra luồng kỹ thuật với việc sử dụng LLM thật. Người xem không được hiểu điểm từ adapter offline là kết quả đánh giá ngữ nghĩa của AI, và mọi lần gọi provider trả phí phải xuất phát từ lựa chọn chủ động của người dùng.

Tài liệu này không hiển thị metric accuracy cố định trên giao diện. Kết quả đánh giá frozen thuộc báo cáo Stage 7 và không được trộn vào output của một lần demo riêng lẻ.

## Phương án 1: Chế độ offline

Chế độ offline là lựa chọn mặc định và dùng `deterministic_fake` cho L3. Chế độ này phục vụ kiểm tra frontend, API, L1, L2, aggregation, quality gate, human review và audit mà không gọi provider bên ngoài.

Giao diện phải:

- Hiển thị nhãn rõ ràng `Offline - L3 mô phỏng`.
- Nêu rằng điểm L3 được tính theo quy tắc độ phủ thông tin, không phải suy luận của LLM.
- Dùng rationale tiếng Việt theo từng tiêu chí, gồm tên và mô tả tiêu chí, số mục thông tin và số phần CV đã dùng để tính độ phủ.
- Gọi danh sách dẫn chiếu là thông tin được adapter offline sử dụng, không khẳng định tất cả đều chứng minh trực tiếp cho tiêu chí.
- Tiếp tục áp dụng quality gate và bắt buộc human review theo contract hiện hành.

Chế độ offline phù hợp để trình diễn hệ thống chạy ổn định và tái lập. Nó không được dùng để tuyên bố chất lượng đánh giá của LLM.

## Phương án 2: Chế độ LLM thật

Chế độ LLM thật dùng backend được khởi động với `CLASSIFIER_LLM_ADAPTER=environment_configured`. Runtime hiện tại khóa provider OpenAI và snapshot `gpt-5.4-mini-2026-03-17`; model này hỗ trợ Structured Outputs theo tài liệu chính thức của OpenAI.

Giao diện phải:

- Không tự động chọn chế độ LLM thật.
- Hiển thị cảnh báo rằng mỗi lần phân loại có thể phát sinh phí và độ trễ.
- Yêu cầu người dùng xác nhận trước khi nút chạy được bật.
- Hiển thị nhãn `LLM thật` và model/provider từ version trace của kết quả.
- Giữ nguyên schema validation, quality gate, human review và audit.
- Không fallback âm thầm sang offline khi provider lỗi; lỗi phải được hiển thị rõ để tránh nhầm nguồn kết quả.

GPT-5.4 mini có thể tạo rationale cụ thể hơn nhưng không được coi là ground truth. Output vẫn phải qua validation và chỉ là đề xuất cho người duyệt.

## Kiến trúc hai backend

Hai chế độ dùng hai tiến trình FastAPI độc lập:

| Tiến trình | Cổng gợi ý | L3 adapter | Mục đích |
| --- | ---: | --- | --- |
| Offline backend | `8000` | `deterministic_fake` | Demo ổn định, không tốn phí |
| LLM backend | `8001` | `environment_configured` | Demo suy luận của provider thật |

Frontend dùng Backend-for-Frontend để định tuyến theo mode. API key của cả hai backend chỉ tồn tại ở phía Next.js server và không được gửi vào bundle trình duyệt.

Việc tách tiến trình có các lợi ích:

- Không thay adapter trong một request đang chạy.
- Không trộn repository memory và audit history giữa hai mode.
- Không để lựa chọn offline vô tình gọi provider trả phí.
- Có thể tắt hoàn toàn backend LLM khi không cần demo.

## Cấu hình cục bộ

Backend offline:

```powershell
$env:CLASSIFIER_STORAGE_BACKEND="memory"
$env:CLASSIFIER_API_KEY="offline-demo-only"
$env:CLASSIFIER_CONFIG_DIRECTORY="configs/runtime/five_role_v2"
$env:CLASSIFIER_LLM_ADAPTER="deterministic_fake"
uv run uvicorn backend.app.main:app --reload --port 8000
```

Backend LLM thật trong PowerShell khác, sau khi provider secret đã nằm trong `.env` cục bộ:

```powershell
$env:CLASSIFIER_STORAGE_BACKEND="memory"
$env:CLASSIFIER_API_KEY="llm-demo-only"
$env:CLASSIFIER_CONFIG_DIRECTORY="configs/runtime/five_role_v2"
$env:CLASSIFIER_LLM_ADAPTER="environment_configured"
uv run uvicorn backend.app.main:app --reload --port 8001
```

Frontend server:

```powershell
pnpm --dir frontend dev
```

Lệnh `dev` và `start` của frontend tự đọc có chọn lọc cấu hình server từ `.env` ở thư mục gốc. `CLASSIFIER_API_KEY` được dùng làm khóa xác thực chung với cả hai backend; `CLASSIFIER_OFFLINE_BACKEND_API_KEY` và `CLASSIFIER_LLM_BACKEND_API_KEY` chỉ cần khi muốn đặt khóa riêng cho từng tiến trình. URL mặc định là `http://127.0.0.1:8000` cho offline và `http://127.0.0.1:8001` cho LLM.

Khi chọn LLM thật, BFF thay hai trường truy vết provider/model trong request demo bằng `CLASSIFIER_LLM_PROVIDER` và `CLASSIFIER_LLM_MODEL` từ `.env`. Việc này chỉ đồng bộ metadata với runtime của backend LLM; nội dung CV, Job Profile, rubric, các phiên bản còn lại và chính sách chấm không bị thay đổi.

`CLASSIFIER_LLM_API_KEY` là secret trả phí để FastAPI gọi provider. Frontend không đọc biến này và không dùng nó thay cho `CLASSIFIER_API_KEY`.

Không ghi provider secret hoặc backend API key thật vào source, tài liệu đã commit hay biến `NEXT_PUBLIC_*`.

## Điều kiện chấp nhận

- Mặc định mở giao diện ở mode offline.
- Offline không gọi backend LLM và có nhãn mô phỏng rõ ràng.
- Rationale offline khác nhau theo tiêu chí và không còn đoạn tiếng Anh cố định.
- Mode LLM chỉ chạy sau khi người dùng chọn và xác nhận khả năng phát sinh phí.
- Backend LLM chưa cấu hình hoặc provider lỗi không làm frontend fallback sang offline.
- Approve, override và audit history được gửi về đúng backend đã tạo classification result.
- API key không xuất hiện trong request từ trình duyệt hoặc output giao diện.

## Khắc phục lỗi `fetch failed`

`fetch failed` ở mode LLM có nghĩa BFF không kết nối được backend LLM, thường do tiến trình cổng `8001` chưa chạy. Khởi động backend từ thư mục gốc bằng:

```powershell
uv run uvicorn backend.app.main:app --reload --port 8001
```

Sau khi thay `.env` hoặc cập nhật frontend environment loader, phải dừng và chạy lại frontend để tiến trình Next.js nạp giá trị mới:

```powershell
pnpm --dir frontend dev
```

Hai địa chỉ kiểm tra không phát sinh request provider là `http://127.0.0.1:8001/health` và `http://127.0.0.1:3000/api/health?execution_mode=llm`. Nếu health đạt nhưng classify trả lỗi cấu hình, kiểm tra request demo đã dùng provider/model trace của mode LLM thay vì `deterministic_fake`.

## Phạm vi chưa thực hiện trong thay đổi này

- Không sửa Runtime v2 hoặc metric Stage 7.
- Không tuning prompt, model, L1, L2, trọng số hay threshold.
- Không gọi provider trả phí chỉ để kiểm thử giao diện.
- Không biến output demo thành quyết định tuyển dụng tự động.
