# Stage 3 Review: Pilot Dataset v1

## Trạng thái

Gate 2 đã được người dùng phê duyệt ngày 2026-07-25. Stage 3 đã có mười CV tổng hợp, phiếu đánh giá tham chiếu và contract tests. Gate 3 vẫn mở cho tới khi người dùng xác nhận hoặc sửa kết quả phân loại, điểm, lý do chấm và các trường hợp chưa rõ.

## Tổng quan pilot

| Case | Vị trí | Tình huống | Điểm | Nhãn đề xuất | Lý do chính |
| --- | --- | --- | ---: | --- | --- |
| `DA-001` | Junior Data Analyst | Strong fit, có thực tập và dự án | 94 | `pass` | Tất cả yêu cầu bắt buộc có căn cứ rõ từ CV |
| `DA-002` | Junior Data Analyst | Đủ yêu cầu, dự án học tập cơ bản | 70 | `waitlist` | Kỹ thuật, reasoning và tác động ở mức vừa |
| `DA-003` | Junior Data Analyst | Không có thông tin SQL | 70 | `needs_review` | `missing-critical-evidence` |
| `DA-004` | Junior Data Analyst | Xác nhận không có Python/R và dự án phân tích | 36 | `reject` | Dưới 60 và có thông tin rõ xác nhận `unsatisfied` |
| `DA-005` | Junior Data Analyst | Thông tin Python mâu thuẫn | 66 | `needs_review` | `conflicting-critical-evidence` |
| `BE-001` | Junior Python Backend Developer | Strong fit, có thực tập và dự án đầy đủ | 94 | `pass` | Tất cả yêu cầu bắt buộc, testing và delivery rõ |
| `BE-002` | Junior Python Backend Developer | Flask CRUD cá nhân cơ bản | 70 | `waitlist` | Đủ bắt buộc nhưng thiếu testing, security và deployment |
| `BE-003` | Junior Python Backend Developer | Không có thông tin Git | 72 | `needs_review` | `missing-critical-evidence` |
| `BE-004` | Junior Python Backend Developer | Xác nhận chưa từng xây API | 42 | `reject` | Dưới 60 và REST API `unsatisfied` rõ |
| `BE-005` | Junior Python Backend Developer | Đủ yêu cầu nhưng sát ngưỡng Pass | 76 | `needs_review` | `upper-threshold-boundary` 73–77 |

Phân bổ kết quả đề xuất là hai `pass`, hai `waitlist`, hai `reject` và bốn `needs_review`. Đây là kết quả do coding agent đề xuất, chưa phải kết quả chuẩn đã được người duyệt xác nhận.

## `Waitlist` khác `Needs Review` như thế nào

| Nội dung | `Waitlist` | `Needs Review` |
| --- | --- | --- |
| Bản chất | Một kết quả đánh giá mức độ phù hợp. | Một trạng thái workflow và quality gate. |
| Thông tin làm căn cứ | Đủ rõ và nhất quán để chấm; không có điều kiện bắt buộc kiểm tra thủ công. | Thiếu, mâu thuẫn hoặc có một điều kiện chất lượng khiến hệ thống chưa được tự kết luận. |
| Điểm | Thông thường từ 60 đến dưới 75, ngoài các vùng biên bắt buộc review. | Có thể thấp, trung bình hoặc cao; điểm không quyết định một mình. |
| Ý nghĩa | Ứng viên có mức phù hợp vừa và có thể được cân nhắc sau nhóm `pass`. | Chưa biết kết luận cuối; sau review có thể trở thành `pass`, `waitlist` hoặc `reject`. |

Ví dụ `DA-002` và `DA-003` đều có 70 điểm. `DA-002` là `waitlist` vì CV có đủ thông tin để xác nhận ba yêu cầu bắt buộc. `DA-003` là `needs_review` vì không có thông tin SQL; hệ thống không được phép biến thiếu thông tin thành không đáp ứng.

## Điều kiện quyết định hiện tại

Hệ thống phải xét điều kiện bắt buộc kiểm tra thủ công trước, sau đó mới xét điểm.

### Bước 1: Có điều kiện bắt buộc kiểm tra thủ công hay không

Nếu có ít nhất một điều kiện sau, kết quả luôn là `needs_review` dù tổng điểm cao hay thấp:

- Chưa đủ thông tin để xác định một yêu cầu bắt buộc.
- Thông tin về một yêu cầu bắt buộc không nhất quán.
- Tổng điểm dưới ngưỡng Waitlist nhưng không có thông tin rõ xác nhận yêu cầu bắt buộc chưa đáp ứng.
- Có yêu cầu bắt buộc đã xác nhận chưa đáp ứng nhưng tổng điểm từ ngưỡng Waitlist trở lên.
- Kết quả L2 hoặc L3 bị lỗi, không có hoặc sai cấu trúc.
- Điểm L1, L2 và L3 chênh nhau từ 25 điểm trở lên.
- Tổng điểm nằm trong vùng 58–62 hoặc 73–77, tính cả hai đầu.

Hai điều kiện về provider và chênh lệch L1/L2/L3 chỉ được áp dụng khi classifier core tồn tại từ Stage 4. Pilot Stage 3 hiện tập trung vào thông tin trong CV và vùng điểm sát ngưỡng.

### Bước 2: Nếu không có điều kiện bắt buộc kiểm tra thủ công

| Tổng điểm | Kết quả theo cấu hình hiện tại |
| ---: | --- |
| 77,01–100 | `pass` |
| 73–77 | `needs_review` vì sát ngưỡng |
| 62,01–72,99 | `waitlist` |
| 58–62 | `needs_review` vì sát ngưỡng |
| 0–57,99 | `reject` nếu CV xác nhận yêu cầu bắt buộc chưa đáp ứng; nếu không thì `needs_review` |

Với điểm nguyên, các khoảng tương ứng là `pass` từ 78, `waitlist` từ 63 đến 72 và `reject` từ 0 đến 57 khi đủ điều kiện. `Needs Review` có quyền ưu tiên cao hơn các ngưỡng điểm.

### Hai quy tắc bổ sung trong cấu hình 1.1.0

Rà soát Stage 3 phát hiện hai nhánh chưa được cấu hình 1.0.0 mô tả rõ:

1. Một yêu cầu bắt buộc đã xác nhận `unsatisfied`, nhưng tổng điểm vẫn từ 60 trở lên. Cấu hình hiện tại có thể để case này thành `waitlist` hoặc thậm chí `pass`.
2. Tổng điểm dưới 60 nhưng không có yêu cầu bắt buộc nào được xác nhận `unsatisfied`. Cấu hình nói không được tự động `reject`, nhưng chưa khai báo kết quả thay thế.

Người dùng đã phê duyệt chuyển cả hai tình huống sang `needs_review`. Quy tắc được ghi trong `configs/scoring.yaml` phiên bản `1.1.0`. Khi đó:

- Chỉ tự động `reject` nếu điểm dưới 58 và có thông tin rõ xác nhận một yêu cầu bắt buộc chưa đáp ứng.
- Điểm thấp nhưng chưa đủ căn cứ loại phải vào `needs_review`.
- Yêu cầu bắt buộc chưa đáp ứng nhưng tổng điểm lại cao cũng phải vào `needs_review` để người phụ trách kiểm tra sự bất thường.

Hai quy tắc này đã được kiểm thử riêng. Chúng không làm thay đổi điểm hoặc kết quả của mười hồ sơ pilot hiện tại.

## Bốn thành phần bạn đang duyệt

### Kết quả đối chiếu yêu cầu (`Evidence status`)

Đây là kết quả đối chiếu từng yêu cầu bắt buộc với thông tin trong CV, không phải trạng thái của toàn bộ CV:

- `satisfied`: đủ thông tin để xác nhận yêu cầu được đáp ứng.
- `unsatisfied`: có thông tin rõ để xác nhận yêu cầu chưa được đáp ứng.
- `missing`: chưa đủ thông tin để xác định.
- `conflicting`: có ít nhất hai thông tin dẫn tới kết luận trái nhau.

Bạn cần kiểm tra kết luận có đúng với các `evidence_ids`, tức mã của những đoạn thông tin được dẫn ra từ CV, hay không.

### Criterion scores

Đây là điểm của năm nhóm tiêu chí. Điểm tối đa lần lượt là 30, 25, 20, 15 và 10; tổng tối đa 100. Ví dụ `DA-002` nhận `30 + 15 + 11 + 8 + 6 = 70`.

Test tự động xác nhận phép cộng và giới hạn điểm. Bạn xác nhận phần quan trọng hơn: mức điểm đó có hợp lý về nghiệp vụ so với thông tin trong CV và cấp Junior 0–2 năm hay không.

### Nhãn

Nhãn là kết luận đề xuất cho một case:

- `pass`: đề xuất qua vòng đánh giá hồ sơ vì điểm cao và không có điều kiện bắt buộc kiểm tra thủ công.
- `waitlist`: đề xuất giữ lại để cân nhắc vì mức phù hợp trung bình và thông tin đủ để kết luận.
- `reject`: đề xuất không qua vòng đánh giá hồ sơ vì điểm thấp và có thông tin rõ về yêu cầu bắt buộc chưa đáp ứng.
- `needs_review`: phải có con người xử lý trước khi có kết luận cuối.

Nhãn Stage 3 là nhãn đề xuất dùng để kiểm tra rubric, chưa phải quyết định tuyển dụng.

### Rationale

Rationale là phần giải thích ngắn cho trạng thái, điểm hoặc kết quả. Một rationale đạt yêu cầu phải nói được thông tin nào trong CV dẫn tới kết luận nào, không dựa vào cảm tính hoặc thuộc tính được bảo vệ.

## File cần xem

- CV tổng hợp: `data/samples/cvs/cv_pilot_da_001.json` đến `cv_pilot_da_005.json` và `cv_pilot_be_001.json` đến `cv_pilot_be_005.json`.
- Annotation có thể chỉnh sửa: `data/annotations/pilot_annotations_v1.json`.
- Cách chấm và cách ghi quyết định: `docs/stage_3_annotation_guide.md`.

## Nội dung cần duyệt

Với từng case, xác nhận bốn điểm:

1. Kết quả đối chiếu của mọi yêu cầu bắt buộc có đúng là `satisfied`, `unsatisfied`, `missing` hoặc `conflicting` không.
2. Năm criterion scores có hợp lý với thông tin trong CV và cấp Junior 0–2 năm không.
3. `total_score` và `draft_label` có phản ánh đúng rubric, threshold và chính sách bảo vệ ứng viên không.
4. Rationale và ambiguity note có đủ rõ để một người khác đưa ra kết luận tương tự không.

Đặc biệt cần xác nhận:

- `DA-003` và `BE-003`: thiếu thông tin không bị đổi thành không đáp ứng.
- `DA-004` và `BE-004`: `reject` chỉ xuất hiện khi CV có thông tin xác nhận chưa đáp ứng rõ.
- `DA-005`: hai đoạn thông tin về Python thực sự đủ để gọi là `conflicting`.
- `BE-005`: điểm 76 phải vào `needs_review` do vùng biên 73–77.

## Khi nào việc duyệt được coi là đạt

Gate 3 đạt khi đồng thời thỏa các điều kiện sau:

1. Cả mười case đã được bạn xác nhận hoặc sửa.
2. Mọi yêu cầu bắt buộc có kết quả đối chiếu đúng và truy ngược được tới thông tin trong CV; `missing` không bị coi là `unsatisfied`.
3. Mỗi case có đủ năm criterion scores trong giới hạn, tổng điểm đúng và mức điểm hợp lý ở cấp junior.
4. Nhãn tuân thủ threshold và các điều kiện ưu tiên `needs_review`.
5. Rationale đủ rõ để một người khác có thể hiểu và kiểm tra lại kết luận.
6. Các trường hợp missing, conflicting, explicit unsatisfied và boundary score không còn ambiguity về cấu trúc rubric.
7. Hai quy tắc bổ sung của scoring configuration `1.1.0` được áp dụng nhất quán.
8. Human review được ghi bằng reviewer reference giả danh, final label và thời gian có timezone.
9. Toàn bộ contract và pilot dataset tests vẫn pass sau khi ghi kết quả duyệt.

Test tự động chứng minh dữ liệu đúng schema, phép tính đúng và policy không bị vi phạm. Sự phê duyệt của bạn chứng minh điểm và nhãn có ý nghĩa nghiệp vụ hợp lý. Gate 3 cần cả hai.

## Cách phản hồi

Nếu đồng ý toàn bộ mười hồ sơ, có thể trả lời:

> Tôi duyệt cả 10 case Stage 3, gồm kết quả đối chiếu yêu cầu, điểm theo tiêu chí, kết quả phân loại và lý do chấm. Hãy ghi kết quả duyệt và hoàn tất Gate 3.

Nếu cần sửa, ghi case và nội dung thay đổi, ví dụ:

> `DA-002`: giảm technical-analysis từ 15 xuống 13 vì thông tin kỹ thuật trong CV còn cơ bản; giữ kết quả Waitlist.

Sau phản hồi, coding agent sẽ cập nhật object `review` bằng reviewer reference giả danh, giữ nguyên đề xuất ban đầu để audit và chạy lại toàn bộ tests. Chỉ sau khi tất cả case được xác nhận mới đánh dấu Gate 3 hoàn tất và bắt đầu Stage 4.
