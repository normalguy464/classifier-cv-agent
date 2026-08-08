# Duyệt test set mới cho Stage 7

## Trạng thái sau khi duyệt

Test set `stage7-five-role-test-v1` phiên bản `1.0.1` đã được duyệt theo hội đồng đồng thuận hai người và khóa thành Gold tại `data/frozen_test/stage7_v1/`. Đây là 50 CV synthetic mới hoàn toàn, gồm 10 CV cho mỗi vị trí:

- Junior Data Analyst;
- Junior Python Backend Developer;
- Junior Frontend Developer;
- Junior QA Engineer;
- Junior Data Engineer.

Mỗi CV chỉ được ghép với JD `standard` của vai trò tương ứng trong runtime `five-role-runtime-v1`. Không có CV, candidate reference hoặc pair cũ nào được đưa vào bộ này.

Sau khi bản Gold được khóa, classifier đã chạy đúng protocol. Kết quả nằm trong `evaluation/reports/stage7_frozen_evaluation_v1.json` và phiếu duyệt nằm tại `docs/stage_7_evaluation_review.md`.

Phiên bản `1.0.1` sửa năm case có mâu thuẫn xuyên requirement được phát hiện khi hai người đánh giá đọc bản `1.0.0`. Chi tiết nằm trong [biên bản remediation](stage_7_test_set_remediation_v1_0_1.md). Các case còn lại, phân bố điểm và nhãn không thay đổi.

## Phân bố có chủ đích

Mỗi vai trò có cùng 10 kịch bản để việc so sánh giữa vai trò không bị lệch:

| Kịch bản | Số case toàn bộ | Mục đích |
| --- | ---: | --- |
| `strong` | 5 | Hồ sơ mạnh, nằm rõ trong vùng Pass |
| `solid` | 5 | Hồ sơ junior tốt, nằm rõ trong vùng Pass |
| `moderate` | 5 | Đủ yêu cầu nhưng mức điểm phù hợp Waitlist |
| `missing_critical` | 5 | Thiếu thông tin về một yêu cầu bắt buộc |
| `conflicting_critical` | 5 | Hai thông tin mâu thuẫn về một yêu cầu bắt buộc |
| `explicit_failure` | 5 | Có thông tin rõ rằng một yêu cầu bắt buộc không đạt |
| `lower_boundary` | 5 | Điểm nằm trong vùng review quanh ngưỡng Waitlist |
| `upper_boundary` | 5 | Điểm nằm trong vùng review quanh ngưỡng Pass |
| `transferable` | 5 | Kinh nghiệm chuyển đổi từ lĩnh vực gần |
| `hard_negative` | 5 | Nhiều keyword nhưng không có ngữ cảnh thực hành |

Phân bố nhãn nháp là 10 Pass, 10 Waitlist, 5 Reject và 25 Needs Review. Tỷ lệ Needs Review cao là chủ đích vì test set phải kiểm tra các đường an toàn, không mô phỏng tỷ lệ ứng viên thật ngoài thị trường.

## Kết quả QC trước human review

- 50 CV, 5 JD, 5 rubric và 50 cặp đều hợp lệ theo contract.
- Mỗi vai trò có đủ 10 kịch bản.
- Không có candidate reference hoặc CV ID trùng dữ liệu Stage 3–6.
- Không có đoạn evidence nào trùng chính xác với dữ liệu cũ.
- Độ giống token Jaccard cao nhất với một CV cũ là `0.5403`, dưới ngưỡng chặn `0.82`.
- Job Profile và rubric khớp chính xác với runtime đã khóa.
- ID của CV, candidate, evidence và pair không chứa tên kịch bản hoặc nhãn.
- Không có PII, thuộc tính được bảo vệ, classifier output, raw provider response hoặc secret.
- Quality report có 0 errors và 0 warnings.

## Bạn cần duyệt những gì

Mở [phiếu duyệt 50 case](../data/to_review/stage7_test_v1/review_sheet.md) và kiểm tra với từng case:

1. Nội dung CV có đủ tự nhiên và phù hợp vị trí junior hay không.
2. Trạng thái từng yêu cầu bắt buộc là `satisfied`, `missing`, `unsatisfied` hoặc `conflicting` có đúng với thông tin được liên kết hay không.
3. Năm nhóm điểm có hợp lý và không vượt `30/25/20/15/10` hay không.
4. Tổng điểm có bằng tổng năm nhóm điểm hay không.
5. Nhãn Pass, Waitlist, Reject hoặc Needs Review có tuân theo runtime `70/85`, boundary `68–72` và `83–87`, cùng chính sách bảo vệ ứng viên hay không.
6. Lý do review có phản ánh đúng nguyên nhân thiếu, mâu thuẫn hoặc sát ngưỡng hay không.

Nếu có điểm chưa đúng, chỉ cần gửi ID case và nội dung cần sửa. Không cần tự chỉnh JSON.

## Điều kiện khóa test set

Để trở thành ground truth Gold dùng cho lần đánh giá này, mỗi case đã được hai người thảo luận và thống nhất quyết định cuối. Đây là hội đồng đồng thuận hai người theo xác nhận của người dùng, không được mô tả là hai lượt chấm độc lập. Bản nháp do coding agent tạo không được tính là human review.

Sau khi đủ review, coding agent sẽ:

1. ghi audit trail của từng reviewer;
2. áp dụng các chỉnh sửa đã thống nhất;
3. chạy lại QC và leakage check;
4. tạo manifest mới có trạng thái `human_reviewed_gold`;
5. khóa toàn bộ hash trước khi sinh classifier output;
6. xin xác nhận riêng trước khi thực hiện tối đa 60 HTTP request tới LLM provider.

## Protocol đánh giá sau khi khóa

Protocol nằm tại `evaluation/configs/stage7_frozen_evaluation_v1.yaml` và không cho phép tuning theo kết quả test. Nó yêu cầu:

- chạy ba baseline keyword, TF-IDF và embedding;
- chạy bảy ablation từ L1-only đến full L1-L2-L3;
- báo cáo accuracy, Macro-F1, confusion matrix và metric theo vai trò;
- Needs Review recall bằng 1, false Reject bằng 0 và unsafe Pass bằng 0;
- requirement-status accuracy ít nhất 0,95 và không có unsafe mismatch;
- criterion MAE không quá 3 và total-score MAE không quá 12;
- review rate không quá 0,80;
- kiểm tra stability trên năm case đại diện;
- dùng bootstrap 2.000 lần với seed cố định để báo cáo độ bất định.

50 request chính và 5 request lặp stability tạo thành 55 request dự kiến. Hard cap là 60 HTTP request, raw provider response không được lưu và việc gọi API vẫn cần bạn cho phép riêng.

## Câu xác nhận

Nếu bạn là reviewer thứ nhất và đồng ý toàn bộ 50 case:

> Tôi đã duyệt 50 case của stage7-five-role-test-v1, gồm nội dung CV, requirement status, năm nhóm điểm, tổng điểm, draft label và rationale; tôi đồng ý ghi nhận review thứ nhất và không chạy classifier cho đến khi test set đủ điều kiện khóa.

Nếu có reviewer thứ hai, hãy cho biết reviewer đó đã chấm độc lập hay chưa và liệt kê mọi case bất đồng. Không dùng AI-generated review thay cho reviewer con người thứ hai.
