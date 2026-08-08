# Khóa Gold và preflight Stage 7 Runtime v2

## Kết quả

Human review của hai người đã được ghi nhận theo hình thức hội đồng đồng thuận. Test set `stage7-five-role-runtime-v2-test-v1` phiên bản `1.0.0` đã được khóa thành Gold tại `data/frozen_test/stage7_runtime_v2_v1`.

Không có nội dung CV, requirement status, điểm, tổng điểm, nhãn hoặc rationale nào bị thay đổi khi chuyển từ Bronze sang Gold. Mỗi record chỉ được bổ sung metadata review, reviewer reference ẩn danh và tầng Gold.

## Artifact đã khóa

- `cv_profiles.jsonl`: 50 CV đúng bằng nguồn đã duyệt.
- `job_profiles.jsonl`: 5 Job Profile đúng bằng Runtime v2.
- `rubrics.jsonl`: 5 rubric đúng bằng Runtime v2.
- `pairs.jsonl`: 50 annotation đã chuyển sang Gold, mỗi case có hai reviewer và final label bằng nhãn đã duyệt.
- `review_record.json`: lưu câu xác nhận, thời điểm review, hình thức hội đồng đồng thuận và hai reviewer reference ẩn danh.
- `manifest.json`: khóa dataset, runtime, nguồn Bronze, review record và hash của bốn file dữ liệu.
- `quality_report.json`: xác nhận 0 lỗi, 0 cảnh báo, 0 overlap và Jaccard tối đa `0,7479`.

## Protocol đã khóa

Protocol `stage7-five-role-runtime-v2-frozen-evaluation-v1` nằm tại `evaluation/configs/stage7_runtime_v2_frozen_evaluation_v1.yaml`.

Các điều kiện chính:

- accuracy tối thiểu `0,70`;
- Macro-F1 tối thiểu `0,60`;
- Needs Review recall tối thiểu `0,80`;
- false Reject, unsafe Pass và unsafe requirement mismatch đều bằng `0`;
- requirement-status accuracy tối thiểu `0,95`;
- criterion MAE không quá `3`, total-score MAE không quá `12`;
- review rate không quá `0,80`;
- valid structured output rate bằng `1,00`;
- tối đa 55 request dự kiến và hard cap 60 request;
- không lưu raw provider response;
- không tuning Runtime v2 theo kết quả test.

Một số ít mismatch không nguy hiểm được giữ trong error analysis nếu các điều kiện trên vẫn đạt. Không case nào được xóa sau khi xem prediction.

## Kết quả preflight

Report `evaluation/reports/stage7_runtime_v2_preflight_v1.json` đã đạt toàn bộ 10 kiểm tra:

1. Runtime v2 có trạng thái `frozen_for_stage7`.
2. Runtime nạp đủ năm vai trò.
3. Test set là Gold và khóa đủ 50 case.
4. Review record có hai reviewer khác nhau.
5. QC có 0 lỗi và 0 cảnh báo.
6. Không có classifier output hoặc LLM request trước khi khóa.
7. Protocol liên kết đúng runtime và dataset.
8. Accuracy floor và các safety gate không bị hạ.
9. Năm stability case đều tồn tại trong Gold.
10. Provider execution vẫn tách thành bước cần cho phép riêng, có hard cap và không lưu raw response.

Preflight ghi rõ:

- `passed: true`;
- `provider_execution_authorized: false`;
- `provider_requests_made: false`;
- `api_key_loaded: false`.

Acceptance repository sau khi khóa đạt: Ruff không có lỗi, 165 file Python đúng format, Pyright có 0 lỗi/cảnh báo và full pytest có `500 passed, 7 skipped`. Bảy test skip là kiểm tra PostgreSQL khi disposable test database đang tắt; thay đổi này không liên quan persistence.

## Bước tiếp theo

Chỉ sau khi người dùng cho phép riêng mới được chạy L3 provider. Trước request đầu tiên, runner phải dùng đúng Runtime v2, Gold manifest và protocol hash đã ghi trong preflight; nếu một hash thay đổi thì phải dừng.

Câu xác nhận đề xuất:

> Tôi xác nhận Gold lock và preflight Stage 7 Runtime v2 đã đạt; cho phép chạy final evaluation theo protocol version 1.0.0, tối đa 60 HTTP request, không lưu raw provider response và không tuning runtime theo test output.
