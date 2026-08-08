# Phiếu duyệt Development Runtime v2

## Mục đích

Tập `five-role-runtime-v2-development-v1` được tạo để cải thiện khả năng khái quát của L1, L2 và kiểm tra L3 trước khi đóng băng runtime v2. Tập này hoàn toàn tách khỏi 50 case frozen test Stage 7 v1.

Đây mới là dữ liệu Bronze. Nhãn, điểm và trạng thái requirement do script tạo chỉ là bản nháp. Không được dùng chúng làm ground truth hoặc tuning trước khi có human review.

## Các file cần đọc

| File | Loại | Ý nghĩa |
| --- | --- | --- |
| `data/runtime_v2/to_review/development_v1/review_sheet.md` | Tài liệu review | Phiếu chính để duyệt toàn bộ 75 case, gồm thông tin đánh giá, trạng thái requirement, năm nhóm điểm và nhãn nháp. |
| `data/runtime_v2/to_review/development_v1/pairs.jsonl` | Dữ liệu | Annotation có cấu trúc cho từng cặp CV–JD; hệ thống sẽ dùng file này sau khi được duyệt và chuyển thành Silver. |
| `data/runtime_v2/to_review/development_v1/cv_profiles.jsonl` | Dữ liệu | 75 CVProfile synthetic có cấu trúc; không phải PDF hoặc DOCX và không chứa PII. |
| `data/runtime_v2/to_review/development_v1/job_profiles.jsonl` | Dữ liệu | Năm Job Profile lấy từ runtime v1 để giữ nguyên ý nghĩa nghiệp vụ khi đo cải tiến kỹ thuật. |
| `data/runtime_v2/to_review/development_v1/rubrics.jsonl` | Dữ liệu | Năm rubric hiện hành dùng để tạo điểm nháp. |
| `data/runtime_v2/to_review/development_v1/manifest.json` | Metadata | Khóa nguồn gốc, số lượng, trạng thái Bronze và xác nhận chưa tuning hoặc gọi API. |
| `data/runtime_v2/to_review/development_v1/quality_report.json` | Báo cáo QC | Kết quả kiểm tra cấu trúc, PII, liên kết, trùng lặp và leakage. |

## Thành phần tập dữ liệu

- 75 cặp CV–JD, 15 cặp cho mỗi vai trò.
- 15 `Pass`, 10 `Waitlist`, 10 `Reject` và 40 `Needs Review` ở mức nháp.
- Có các trường hợp diễn đạt thay thế, chỉ học lý thuyết, có thao tác trực tiếp, thiếu thông tin, phủ định rõ, mâu thuẫn và sát ngưỡng.
- Nhiều case cố ý không lặp nguyên từ khóa trong JD để kiểm tra khả năng hiểu tín hiệu năng lực thay vì ghi nhớ chuỗi từ.
- 50 frozen case Stage 7 v1 không được sao chép hoặc dùng để tạo nhãn.

## Cách duyệt

Mở `review_sheet.md` và đọc theo từng vai trò. Với mỗi case, kiểm tra bốn phần:

1. `Requirement status`: `satisfied`, `unsatisfied`, `missing` hoặc `conflicting` có đúng với thông tin được liên kết không.
2. Năm nhóm điểm: điểm có hợp lý với độ sâu, mức sở hữu, đầu ra và giới hạn trong hồ sơ không.
3. Nhãn nháp: có đúng theo trạng thái requirement, tổng điểm và các tuyến `Needs Review` không.
4. Rationale: có giải thích đúng thông tin trong CV, không suy diễn năng lực và không sử dụng thuộc tính nhạy cảm không.

Bạn có thể duyệt theo năm nhóm để giảm tải:

1. `v2d-pair-da-01` đến `v2d-pair-da-15`.
2. `v2d-pair-be-01` đến `v2d-pair-be-15`.
3. `v2d-pair-fe-01` đến `v2d-pair-fe-15`.
4. `v2d-pair-qa-01` đến `v2d-pair-qa-15`.
5. `v2d-pair-de-01` đến `v2d-pair-de-15`.

Nếu không đồng ý với một case, chỉ cần ghi ID và nội dung cần sửa, ví dụ:

> `v2d-pair-be-06`: trạng thái `be-rest-api` nên là `missing`, không phải `conflicting`; giữ nguyên các phần khác.

## Điều kiện đạt checkpoint

Checkpoint dữ liệu đạt khi:

- Bạn xác nhận toàn bộ 75 case hoặc nêu rõ các case phải sửa.
- Mọi yêu cầu bắt buộc đều phân biệt đúng thiếu thông tin với phủ định rõ.
- Điểm không vượt `30/25/20/15/10` và tổng điểm bằng tổng năm tiêu chí.
- Nhãn tuân thủ ngưỡng và quy tắc `Needs Review` hiện hành; không nới rule để làm đẹp phân bố.
- Sau khi áp dụng mọi sửa đổi, QC vẫn có 0 lỗi và 0 cảnh báo.
- Dataset được chuyển từ Bronze sang Silver với review record truy vết được.

## Kết quả QC hiện tại

- 75 CV và 75 cặp hợp lệ.
- Mỗi vai trò có đúng 15 cặp.
- Không có PII hoặc thuộc tính được bảo vệ.
- Exact evidence overlap với dữ liệu trước: `0`.
- Maximum prior-CV token Jaccard: `0,3692`, thấp hơn ngưỡng loại `0,82`.
- QC: `0` lỗi, `0` cảnh báo.
- Classifier output: chưa tạo.
- API LLM: chưa gọi.

## Sau khi bạn duyệt

Tôi sẽ ghi nhận human review, tạo bản Silver bất biến, chia development và validation theo candidate, rồi mới chạy baseline offline của L1/L2. Chỉ khi L1/L2 đạt checkpoint mới tiến hành pilot L3 có giới hạn request.

Mẫu xác nhận nếu không có case cần sửa:

> Tôi duyệt toàn bộ 75 case của `five-role-runtime-v2-development-v1`, gồm requirement status, năm nhóm điểm, nhãn và rationale. Hãy chuyển dataset sang Silver và tiếp tục cải thiện L1/L2; chưa gọi API cho đến khi checkpoint offline đạt.
