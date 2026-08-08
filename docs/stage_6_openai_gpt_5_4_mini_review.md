# Review Stage 6 — GPT-5.4 mini trên development năm vai trò

Ngày ghi nhận: 2026-08-01

## Kết luận ngắn

GPT-5.4 mini đã hoạt động với Chat Completions và Structured Outputs. Experiment v4 khắc phục lỗi contract của panel: 5/5 output hợp lệ và requirement status khớp human review 100%. Tuy nhiên, total-score MAE của panel là `13.3`, vượt ngưỡng tối đa `12`, nên panel gate dừng batch đúng chính sách. Gate 6 vẫn mở và cấu hình năm vai trò chưa được freeze.

## Phạm vi đã chạy

- Dataset: `synthetic-cv-jd-expansion-v2-reviewed-silver` phiên bản `2.3.1`.
- Partition: chỉ 25 cặp development đã chọn trước; panel đầu gồm một case cho mỗi vai trò.
- Model cố định: `gpt-5.4-mini-2026-03-17`.
- Provider: OpenAI API qua `https://api.openai.com/v1/chat/completions`.
- Prompt: v9 cho thăm dò ban đầu và v10 cho panel đã hiệu chỉnh.
- L2 liên kết: `coverage-70-95-v1`, candidate set `1.3.1`.
- Không chạy 100 cặp held-out và không mở mười frozen-test case cũ.
- Không lưu API key hoặc raw provider response.

Model và giá tham chiếu được khóa theo trang chính thức của [GPT-5.4 mini](https://developers.openai.com/api/docs/models/gpt-5.4-mini): 0,75 USD cho một triệu input token, 0,075 USD cho cached input và 4,50 USD cho một triệu output token. Cách chuẩn hóa JSON Schema tuân theo yêu cầu mọi field phải là `required` trong [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs).

## Các phiên bản thử nghiệm

| Phiên bản | Thay đổi chính | Kết quả |
| --- | --- | --- |
| v1 / `23.0.0` | Prompt v9, schema Pydantic thô rồi schema OpenAI đã chuẩn hóa | Một HTTP 400 do schema ban đầu; retry qua API nhưng output sai invariant cấp root. Dừng, không dùng kết quả. |
| v2 / `24.0.0` | Schema OpenAI hợp lệ và `overall_score` được kiểm tra như tổng năm criterion score | Probe QA hợp lệ và khớp 5/5 requirement; bốn case tiếp theo sai contract nên không chạy batch. |
| v3 / `25.0.0` | Prompt v10 thêm checklist ID, evidence cardinality và phép cộng; tổng điểm được dẫn xuất từ năm điểm thành phần | 4/5 case panel hợp lệ; case Data Analyst sai contract ở cả request đầu và một retry. Experiment dừng sớm. |
| v4 / `26.0.0` | Giữ prompt v10; schema động khóa số requirement/criterion, enum ID và số evidence ID theo status; panel gate và series cap được ghi trong config | 5/5 output hợp lệ, requirement match 1.0, criterion MAE 2.78; total-score MAE 13.3 vượt ngưỡng 12 nên batch không được mở. |

Mọi cache cũ được giữ nguyên làm audit trail. Không sửa cache hoặc report cũ để làm đẹp tỷ lệ thành công.

## Kết quả v3

- HTTP request: 6 trên hard cap 35.
- Output hợp lệ: 4; output không hợp lệ: 2.
- Requirement-status match trên bốn output hợp lệ: `1.0`.
- Criterion MAE: `2.2`, đạt ngưỡng tối đa `3.5`.
- Total-score MAE: `7.5`, đạt ngưỡng tối đa `12`.
- Case không hợp lệ lần đầu: criterion ghi `missing` nhưng vẫn gắn evidence ID.
- Retry duy nhất: thiếu một requirement ID so với rubric.
- Trạng thái report: `stopped_quality_failure`.
- `quality_gate_passed`: `false`.
- `configuration_freeze_eligible`: `false`.

Các metric đạt chỉ mô tả bốn output hợp lệ. Chúng không được dùng để bỏ qua hai output sai contract hoặc tuyên bố toàn bộ panel đạt.

## Kết quả v4

- HTTP request mới: 5 trên hard cap v4 là 32; không có retry hoặc output lỗi.
- Tổng request của chuỗi v1-v4: 18 trên series cap 45.
- Output validity: `1.0` và requirement-status match: `1.0`, đều đạt.
- Criterion MAE: `2.78`, đạt ngưỡng tối đa `3.5`.
- Endpoint-score rate: `0`, đạt ngưỡng tối đa `0.4`.
- Total-score MAE: `13.3`, không đạt ngưỡng tối đa `12`.
- Ba độ lệch total score lớn nhất trong panel là QA explicit failure `14`, Python Backend explicit failure `21.5` và Frontend conflicting critical `24.5` điểm.
- Trạng thái report: `stopped_quality_failure`; batch 20 primary còn lại và năm stability repeat không chạy.
- `quality_gate_passed=false` và `configuration_freeze_eligible=false`.

V4 chứng minh schema động xử lý được lỗi cấu trúc từng xuất hiện ở v3. Nó chưa chứng minh calibration điểm đạt yêu cầu. Không được hạ ngưỡng, sửa human score hoặc chọn riêng hai case tốt để tuyên bố panel đạt.

## Chi phí và giới hạn

Config đặt `max_completion_tokens=4096`, `reasoning_effort=none`, hard cap 35 và trần chi phí lý thuyết 0,96012 USD cho một experiment nếu mỗi request có tối đa 12.000 input token theo giả định đã ghi.

Bốn experiment đã gửi tổng cộng 18 HTTP request. V4 có chi phí ước tính từ usage là `0.04468875` USD; cộng lower-bound của v1-v3, chuỗi có lower-bound khoảng `0.08372475` USD. Tám request lỗi cũ không có usage được giữ trong cache vì contract cấm gắn usage vào failure result, nên con số này không phải hóa đơn đầy đủ. OpenAI Usage Dashboard là nguồn cuối cùng để xác nhận chi phí thực.

## Điều đã được khắc phục

- Adapter gửi `max_completion_tokens` và `reasoning_effort` theo config.
- Schema OpenAI loại nhánh chuỗi số của Decimal, bắt buộc mọi field và không đổi contract Pydantic nội bộ.
- HTTP error chỉ lưu type, code và parameter đã allowlist; không lưu raw message.
- `overall_score` được dẫn xuất từ năm criterion score hợp lệ thay vì tin vào phép cộng dư thừa của model.
- Prompt v10 yêu cầu kiểm tra đủ ID, quan hệ giữa status và evidence IDs, và tổng điểm trước khi trả JSON.
- Report tính chi phí từ usage hợp lệ và tách request chưa định giá.
- Schema v4 khóa đúng số requirement/criterion assessment, giới hạn identifier bằng enum của request, và ràng buộc `missing=0`, `satisfied/unsatisfied>=1`, `conflicting>=2` evidence ID.
- Panel gate chặn batch trước request thứ sáu khi một ngưỡng chất lượng không đạt; series cap bảo đảm tổng v1-v4 không vượt 45 request.

## Hạn chế còn lại

- Schema động không thể tự bảo đảm model chấm điểm giống human review; Pydantic và request-consistency validation vẫn là lớp kiểm tra cuối cùng.
- Total-score MAE của panel vượt ngưỡng 1.3 điểm. Sai số tập trung ở ba case khó và theo cả hai hướng, nên chưa có căn cứ để áp dụng một offset đơn giản.
- Chưa có stability result cho v4 vì batch bị khóa sau panel; không được suy luận độ ổn định từ một output cho mỗi case.
- Dataset vẫn là Silver synthetic với một reviewer; ngay cả khi provider gate đạt, ba vai trò mới vẫn cần runtime artifact và review độc lập trước khi tuyên bố hỗ trợ chính thức.
- Ước tính chi phí trong report là lower bound khi request lỗi không có usage; phải đối chiếu dashboard.

## Kiểm tra bàn giao

- Focused tests cho prompt, adapter, config và runner: `88 passed` sau khi thêm regression cho schema động, series cap và panel gate.
- Ruff lint: đạt.
- Ruff format: 126 file đã đúng format.
- Pyright: 0 lỗi, 0 cảnh báo, 0 thông tin.
- Full pytest: `369 passed, 7 skipped in 119.99s`.
- Bảy test skip là PostgreSQL integration tests khi disposable database đang dừng; thay đổi này không sửa persistence.
- Secret scan: không có API key ngoài `.env` và các đường dẫn cache cục bộ bị loại; `.env` vẫn nằm trong `.gitignore`.
- Report xác nhận `raw_provider_response_persisted=false`, `held_out_evaluated=false` và `original_stage6_frozen_test_evaluated=false`.

## Quyết định người dùng cần chọn tiếp

Khuyến nghị — dừng nhánh trả phí năm vai trò ở checkpoint này và hoàn thiện controlled pilot hai vai trò:

> Tôi xác nhận GPT-5.4 mini v4 đã sửa được structured-output coverage nhưng không đạt total-score MAE của panel; không hạ quality gate và không chạy thêm API cho nhánh này. Hãy giữ ba vai trò mới ở development-only, hoàn thiện freeze proposal cho controlled pilot hai vai trò và trình tôi duyệt Gate 6.

Phương án nghiên cứu tiếp — giữ Gate 6 mở cho năm vai trò:

> Tôi xác nhận v4 là failed calibration experiment và cho phép đề xuất một thiết kế L3 version mới trên development. Trước khi gọi API, hãy trình prompt/model change, panel, request cap và trần chi phí mới; không sửa human label, rubric, held-out hoặc frozen test.
