# Phiếu duyệt Runtime v2 candidate 3.0.0

## Kết quả duyệt

Người dùng đã phê duyệt đầy đủ candidate ngày 2026-08-08. Bản runtime cuối đã được khóa tại `configs/runtime/five_role_v2`; test set Stage 7 mới đang chờ human review tại `data/to_review/stage7_runtime_v2_test_v1`. Nội dung bên dưới được giữ làm biên bản của quyết định trước khi khóa.

Ngày lập: 2026-08-08

## Mục đích

Tài liệu này giúp người dùng duyệt cấu hình Classifier Agent Runtime v2 trước khi khóa cấu hình và tạo test set Stage 7 mới. Candidate hiện chỉ được xác nhận trên development; chưa phải kết quả cuối và chưa chứng minh khả năng xử lý CV thực tế.

## Những gì đã được chốt trong development

- Dataset `five-role-runtime-v2-development-v1` gồm 75 case đã được người dùng duyệt và chuyển sang Silver.
- L1 đạt 100% requirement status trên 50 development và 25 validation case của checkpoint offline, không có unsafe mismatch.
- L2 dùng multilingual E5 cục bộ, query profile `rubric-quality-v3` và Extra Trees calibrator. Trên validation offline, total MAE là 9,68 và correlation là 0,864.
- L3 dùng OpenAI `gpt-5.4-mini-2026-03-17`, prompt `l3-evidence-rubric-v15` và mapping `l3-deterministic-level-mapping-v3`.
- Ba panel L3 mapping v3 đều qua gate; total MAE lần lượt là 8,975, 10,7 và 11,7. Requirement status match đều là 1,0 và unsafe mismatch đều bằng 0.

## Candidate được đề xuất

| Thành phần | Giá trị |
| --- | --- |
| Cấu hình | `five-role-runtime-v2-development-candidate` |
| Scoring / Models / L1 rules | `3.0.0 / 3.0.0 / 3.0.0` |
| L1 / L2 / L3 | `20% / 30% / 50%` |
| Waitlist / Pass | `67 / 82` |
| Disagreement | `45` điểm |
| Review band dưới | `65-69` |
| Review band trên | `80-84` |
| L2 | `rubric-quality-v3-extra-trees-leaf3-v1` |
| L3 prompt | `l3-evidence-rubric-v15` |
| L3 mapping | `l3-deterministic-level-mapping-v3` |

## Kết quả 40 case development

| Chỉ số | Kết quả | Điều kiện |
| --- | ---: | ---: |
| Accuracy | 77,5% | Tối thiểu 70% theo xác nhận của người dùng |
| Macro-F1 | 74,2% | Tối thiểu 60% |
| Needs Review recall | 90% | Tối thiểu 90% |
| Review rate | 60% | Tối đa 80% |
| False Reject | 0 | Bắt buộc 0 |
| Unsafe Pass | 0 | Bắt buộc 0 |

Báo cáo nguồn là `evaluation/reports/runtime_v2_hybrid_waitlist_tuning_v6.json`. Candidate 67, 68 và 69 có metric bằng nhau; Waitlist 67 được chọn để bảo vệ ứng viên hơn ở sát ngưỡng.

## Hạn chế được chấp nhận ở thời điểm này

- Accuracy không phải 100%; 9/40 case còn lệch nhãn, chủ yếu là chuyển giữa `Waitlist`, `Pass` và `Needs Review` theo hướng thận trọng.
- Dữ liệu vẫn là synthetic và Silver, chưa phải CV thật hoặc Gold frozen test.
- Kết quả hybrid trên 25 case validation đã được xem trước khi aggregate tuning kết thúc, nên chỉ còn giá trị chẩn đoán.
- LLM có xu hướng chấm thấp một số hồ sơ mạnh. Mapping v3 giảm lỗi có hệ thống nhưng không cố ép từng case khớp human score.
- Chi phí ước tính cộng dồn từ usage của các Runtime v2 provider report là khoảng 0,7288493 USD; số này không thay thế hóa đơn của provider.

## Điều kiện duyệt

Đạt để khóa candidate nếu người dùng đồng ý cả bốn điểm:

1. Chấp nhận accuracy development 77,5% là đủ cho phạm vi Classifier Agent hiện tại.
2. Chấp nhận 9 case lệch nhãn còn lại vì không có false Reject hoặc unsafe Pass trong panel chọn cuối.
3. Chấp nhận cấu hình `20/30/50`, Waitlist 67, Pass 82, disagreement 45 và hai review band 65-69, 80-84.
4. Đồng ý tạo và khóa một test set Stage 7 mới trước khi chạy final evaluation; không dùng lại test Runtime v1 hoặc validation hybrid đã xem.

Nếu đồng ý, phản hồi:

> Tôi duyệt Runtime v2 candidate 3.0.0, gồm L1/L2/L3 20/30/50, Waitlist 67, Pass 82, disagreement 45, review bands 65-69 và 80-84; chấp nhận kết quả development 77,5% với zero false Reject/unsafe Pass. Hãy khóa runtime và tạo test set Stage 7 mới.

Nếu chưa đồng ý, ghi rõ tham số hoặc pair ID cần xem lại. Không cần gọi thêm API chỉ để giải thích các case đã có trong report.

## Lệnh kiểm tra không gọi API

```powershell
uv run python -m evaluation.experiments.run_runtime_v2_l3_rescore --generated-at 2026-08-08T23:30:00+07:00 --output evaluation/reports/runtime_v2_l3_fresh_confirmation_v2_rescore_v3.json
uv run python -m evaluation.experiments.run_runtime_v2_hybrid_selection --configuration-path evaluation/configs/runtime_v2_hybrid_waitlist_tuning_v6.yaml --generated-at 2026-08-08T23:50:00+07:00 --output evaluation/reports/runtime_v2_hybrid_waitlist_tuning_v6.json
uv run pytest -q tests/contract/test_five_role_runtime_v2_candidate.py tests/evaluation/test_runtime_v2_l3_rescore.py tests/evaluation/test_runtime_v2_hybrid_selection.py
```

Các lệnh trên dùng cache structured đã được làm sạch và mapping deterministic; chúng không gửi provider request mới.

## Acceptance đã chạy

- `.venv\Scripts\ruff.exe check backend evaluation scripts tests`: đạt, không có finding.
- `.venv\Scripts\ruff.exe format --check backend evaluation scripts tests`: đạt, 159 file đã đúng format.
- `uv run pyright backend evaluation scripts`: đạt, 0 error, 0 warning, 0 information.
- `.venv\Scripts\pytest.exe -q --basetemp .pytest_tmp_full_runtime_v2_candidate`: 487 passed, 7 skipped trong 224,84 giây.
- Audit comment và credential pattern: 0 kết quả sau khi loại trừ `.env` cục bộ và provider cache được tạo có chủ đích.

Bảy test bị skip là nhóm PostgreSQL integration dự kiến khi test database không hoạt động; không có test bắt buộc nào fail.
