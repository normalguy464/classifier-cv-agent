# Phiếu duyệt test set Stage 7 cho Runtime v2

## Kết quả duyệt

Hai người đã xác nhận toàn bộ 50 case ngày 2026-08-08. Bộ dữ liệu đã được khóa thành Gold tại `data/frozen_test/stage7_runtime_v2_v1`; protocol và preflight đã đạt nhưng chưa gọi API. Biên bản tiếp theo nằm tại `docs/stage_7_runtime_v2_lock_and_preflight.md`.

## Trạng thái hiện tại

Runtime `five-role-runtime-v2` đã được khóa theo phê duyệt ngày 2026-08-08. Bộ test mới `stage7-five-role-runtime-v2-test-v1` phiên bản `1.0.0` đã được tạo ở tầng Bronze và chưa được classifier nhìn thấy.

Test set gồm 50 cặp CV–JD synthetic mới, mỗi vai trò 10 cặp:

- Junior Data Analyst;
- Junior Python Backend Developer;
- Junior Frontend Developer;
- Junior QA Engineer;
- Junior Data Engineer.

Mỗi vai trò có đủ 10 kịch bản: strong, solid, moderate, missing critical, conflicting critical, explicit failure, lower boundary, upper boundary, transferable và hard negative. Phân bố nhãn nháp là 10 Pass, 10 Waitlist, 5 Reject và 25 Needs Review.

## Kết quả QC trước human review

- 50 CV, 5 Job Profile, 5 rubric và 50 cặp đều hợp lệ theo contract.
- Mỗi vai trò có 10 case và mỗi kịch bản có 5 case.
- Không trùng candidate reference hoặc CV ID với dữ liệu cũ.
- Không có đoạn thông tin đánh giá nào trùng chính xác với dữ liệu cũ.
- Token Jaccard cao nhất với CV cũ là `0,7479`, dưới ngưỡng chặn `0,82`.
- Job Profile và rubric khớp với Runtime v2 đã khóa.
- Không có PII, thuộc tính được bảo vệ, classifier output, raw provider response hoặc secret.
- Quality report có 0 errors và 0 warnings.
- Không có API LLM nào được gọi khi tạo và kiểm tra bộ này.

## Những gì cần duyệt

Mở [phiếu 50 case](../data/to_review/stage7_runtime_v2_test_v1/review_sheet.md). Với mỗi case, kiểm tra:

1. Nội dung CV có tự nhiên, đủ chi tiết và phù hợp cấp Junior 0–2 năm hay không.
2. Trạng thái từng yêu cầu bắt buộc là `satisfied`, `missing`, `unsatisfied` hoặc `conflicting` có đúng với thông tin trong CV hay không.
3. Năm nhóm điểm có hợp lý và không vượt `30/25/20/15/10` hay không.
4. Tổng điểm có bằng tổng năm nhóm điểm hay không.
5. Nhãn có đúng Runtime v2 hay không: Waitlist từ 67, Pass từ 82; vùng 65–69 và 80–84 vào Needs Review; thiếu hoặc mâu thuẫn thông tin bắt buộc cũng vào Needs Review; Reject chỉ khi dưới 67 và có yêu cầu bắt buộc không đạt rõ ràng.
6. Lý do tổng hợp và lý do vào review có phản ánh đúng case hay không.

Hai nhóm boundary được đặt đúng ngay trên ngưỡng của Runtime v2: case số 07 có tổng 67 nhưng vào Needs Review vì vùng 65–69; case số 08 có tổng 82 nhưng vào Needs Review vì vùng 80–84.

Nếu phát hiện sai, chỉ cần gửi ID case và nội dung cần sửa. Không cần tự chỉnh JSON.

## Chính sách đối với một số ít case khó

Một số ít dự đoán sai sau final evaluation có thể được chấp nhận nếu toàn bộ quality gate vẫn đạt và lỗi không tạo false Reject, unsafe Pass hoặc sai lệch requirement nguy hiểm. Những case đó phải được giữ nguyên trong test set và ghi vào error analysis.

Không được xóa một case chỉ vì classifier dự đoán sai sau khi đã xem output. Xóa sau khi xem kết quả sẽ làm accuracy tăng giả tạo và khiến test set mất tính độc lập. Chỉ được sửa trước lần chạy classifier khi hai reviewer xác nhận ground truth hoặc nội dung CV thật sự sai.

## Gate dự kiến cho lần đánh giá cuối

Protocol sẽ được khóa trước khi chạy classifier, với mức tối thiểu đã thống nhất cho đồ án:

- accuracy ít nhất `0,70`;
- Macro-F1 ít nhất `0,60`;
- Needs Review recall ít nhất `0,80`;
- false Reject bằng `0`;
- unsafe Pass bằng `0`;
- requirement-status accuracy ít nhất `0,95` và unsafe requirement mismatch bằng `0`;
- criterion MAE không quá `3`, total-score MAE không quá `12`;
- review rate không quá `0,80`;
- valid structured output rate bằng `1,00`.

Không điều chỉnh runtime hoặc các ngưỡng này sau khi xem kết quả test. Nếu accuracy lớn hơn 70% và các điều kiện an toàn đạt, một số mismatch không nguy hiểm sẽ được báo cáo như hạn chế thay vì làm lại để ép mọi case đúng.

## Điều kiện chuyển sang Gold

Hai người cần cùng xem và thống nhất toàn bộ 50 case. Hình thức này được ghi đúng là hội đồng đồng thuận hai người, không mô tả thành hai lượt chấm độc lập nếu hai người cùng ngồi duyệt.

Sau khi nhận xác nhận, coding agent sẽ ghi review record, khóa hash thành Gold, chạy lại QC và tạo protocol cuối. Chỉ sau đó mới chạy classifier, baseline, ablation, stability và L3 provider trên test set.

## Câu xác nhận đề xuất

> Tôi và người thứ hai đã duyệt toàn bộ 50 case của stage7-five-role-runtime-v2-test-v1 phiên bản 1.0.0, gồm nội dung CV, requirement status, năm nhóm điểm, tổng điểm, nhãn và rationale; chúng tôi thống nhất dùng kết quả này làm human review cuối, chấp nhận protocol tối thiểu accuracy 70% cùng các điều kiện an toàn đã nêu, và cho phép khóa test set thành Gold. Chưa gọi API cho tới khi bước khóa và preflight hoàn tất.
