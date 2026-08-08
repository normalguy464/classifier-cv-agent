# Quy trình tạo dataset CV-JD cho Classifier Agent

## Mục đích

Tài liệu này quy định cách tạo một dataset CV-JD có thể truy vết, kiểm tra và dùng đúng mục đích trong dự án. Dataset phải phân biệt dữ liệu tổng hợp với dữ liệu thực, phân biệt draft label với ground truth, và không được đưa thông tin cá nhân hoặc thuộc tính được bảo vệ vào scoring input.

## Bước 1: Xác định phạm vi nghề nghiệp

Chọn rõ các vị trí, cấp độ kinh nghiệm và ngôn ngữ cần hỗ trợ. Mỗi vị trí phải có mã ổn định và phạm vi không chồng lấn mơ hồ.

Phạm vi mở rộng hiện tại gồm năm vị trí junior 0–2 năm:

- Junior Data Analyst.
- Junior Python Backend Developer.
- Junior Frontend Developer.
- Junior QA Engineer.
- Junior Data Engineer.

Việc thêm vị trí mới không tự động có nghĩa classifier đã được validation cho vị trí đó. Mỗi vị trí phải đi qua các bước còn lại của quy trình.

## Bước 2: Xây Job Profile từ nguồn nghề nghiệp và thị trường

Dùng O*NET và ESCO làm nguồn tham khảo cho tên nghề, trách nhiệm, kỹ năng và quan hệ nghề–kỹ năng. Sau đó đối chiếu nhiều tin tuyển dụng trực tiếp, còn hiện hành và đúng thị trường mục tiêu để hiệu chỉnh chiều sâu Junior. Các nguồn này không cung cấp ground truth CV-JD và không thay thế phê duyệt nghiệp vụ.

Lần đối chiếu thị trường cho dataset v2 được ghi tại `docs/junior_market_requirements_v1.md`, gồm nguồn, ngày truy cập, tín hiệu yêu cầu, quyết định bắt buộc hoặc ưu tiên và giới hạn.

Mỗi Job Profile phải có:

- Tên vị trí và cấp độ kinh nghiệm.
- Trách nhiệm chính.
- Yêu cầu bắt buộc và yêu cầu ưu tiên.
- Loại thông tin được chấp nhận để đánh giá từng yêu cầu.
- Chính sách phân biệt `missing`, `conflicting` và `unsatisfied`.
- Quy định dự án học tập, dự án cá nhân và thực tập được tính tương đương ở cấp junior.

Nguồn tham khảo:

- O*NET Database: https://www.onetcenter.org/database.html
- ESCO downloadable datasets: https://esco.ec.europa.eu/en/structure-esco-downloadable-datasets

## Bước 3: Thu thập hoặc xây dựng JD cố định

Mỗi vị trí cần nhiều biến thể JD để phản ánh các hoàn cảnh tuyển dụng khác nhau. JD phải có ID và version, không thay đổi âm thầm sau khi annotation hoặc split đã được tạo.

Năm biến thể dùng trong dataset mở rộng:

1. `minimum`: chỉ tập trung vào yêu cầu cốt lõi.
2. `standard`: yêu cầu junior tiêu chuẩn.
3. `preferred_heavy`: có nhiều yêu cầu ưu tiên.
4. `ambiguous`: cố ý giữ một phần mô tả chưa rõ để kiểm tra routing.
5. `project_equivalent`: xác nhận dự án hoặc thực tập có thông tin cụ thể được tính tương đương kinh nghiệm chính thức.

JD lấy từ bên ngoài chỉ được lưu khi có quyền sử dụng rõ ràng. Nếu tự viết, phải ghi `synthetic` và không được mô tả là tin tuyển dụng thật.

## Bước 4: Xây rubric riêng cho từng vị trí

Rubric phải liên kết đúng Job Profile và dùng năm nhóm trọng số đã được dự án phê duyệt:

| Nhóm tiêu chí | Điểm tối đa |
| --- | ---: |
| Yêu cầu bắt buộc | 30 |
| Năng lực kỹ thuật chuyên môn | 25 |
| Năng lực theo vai trò | 20 |
| Dự án, thực tập và tác động | 15 |
| Độ rõ ràng và khả năng kiểm tra của thông tin trong CV | 10 |

Tổng phải bằng 100. Nội dung nhóm 2 và nhóm 3 thay đổi theo vị trí, nhưng ý nghĩa chung và giới hạn điểm không thay đổi.

Các điều kiện `Needs Review`, ngưỡng 60/75 và chính sách Reject phải lấy từ configuration có version. Không được tạo một bộ ngưỡng riêng chỉ để làm nhãn của dataset thuận lợi hơn.

## Bước 5: Chuẩn bị nguồn CV

Nguồn CV được chấp nhận:

- `synthetic`: CV tổng hợp có chủ đích.
- `real_consented`: CV thật có sự đồng ý phù hợp và được giảm thiểu dữ liệu.
- `irreversibly_anonymized`: CV đã ẩn danh không thể đảo ngược.
- `external_licensed`: dữ liệu ngoài có license và provenance kiểm chứng được.

Mọi CV phải được chuyển thành `CVProfile`. Classifier không trực tiếp đọc PDF, DOCX hoặc OCR.

Không đưa vào scoring input:

- Tên thật, email, số điện thoại, ảnh hoặc địa chỉ chính xác.
- Ngày sinh, tuổi, giới tính, dân tộc, tôn giáo hoặc tình trạng hôn nhân.
- Tình trạng sức khỏe, khuyết tật, quê quán hoặc thông tin định danh nhà nước.
- Nhãn, điểm, rationale hoặc review status.

CV synthetic phải có nhiều phong cách và mức độ rõ ràng. Không chỉ tạo các hồ sơ sạch, hoàn chỉnh và dùng đúng từ khóa của rubric.

## Bước 6: Tạo cặp CV-JD

Ghép CV với nhiều JD cùng vai trò để kiểm tra mức độ nhạy với yêu cầu tuyển dụng. Các loại case tối thiểu gồm:

- Phù hợp mạnh.
- Phù hợp tốt ở mức junior.
- Phù hợp một phần.
- Thiếu thông tin quan trọng.
- Thông tin mâu thuẫn.
- Có xác nhận rõ không đạt yêu cầu bắt buộc.
- Sát ngưỡng thấp.
- Sát ngưỡng cao.
- Chuyển ngành có năng lực tương đương.
- Hard negative: nhiều từ khóa nhưng không có ngữ cảnh thực hành.

Nếu một CV được ghép với nhiều JD, mọi cặp của cùng ứng viên phải ở cùng partition khi dataset được chia để tránh leakage.

## Bước 7: Đánh giá lại theo rubric dự án

Mỗi cặp phải có:

- Trạng thái của từng yêu cầu bắt buộc.
- Năm criterion scores.
- Tổng điểm bằng tổng năm nhóm.
- Draft label.
- Rationale ngắn liên kết tới thông tin trong CV.
- Review reasons.
- Phiên bản CV schema, Job Profile, rubric và configuration.
- Trạng thái human review.

Nhãn từ dataset ngoài không được tự động chuyển thành nhãn của dự án. `Good Fit`, `Potential Fit` và `No Fit` không tương đương hoàn toàn với `Pass`, `Waitlist`, `Needs Review` và `Reject`.

Annotation do AI hoặc generator tạo chỉ là draft. Ground truth chỉ được hình thành sau khi con người xác nhận. Tốt nhất hai người đánh giá độc lập, sau đó thảo luận các trường hợp bất đồng.

## Bước 8: Kiểm tra chất lượng và chống leakage

QC phải kiểm tra tự động ít nhất các điều kiện sau:

- File đọc được bằng UTF-8 và hợp lệ theo Pydantic contract.
- ID của CV, JD, rubric và pair không trùng.
- Mọi liên kết giữa pair, CV, JD, rubric và evidence đều tồn tại.
- Mỗi rubric có tổng trọng số 100 và thứ tự điểm tối đa `30/25/20/15/10`.
- Không có criterion score âm hoặc vượt điểm tối đa.
- `total_score` bằng tổng năm criterion scores.
- Draft label tuân theo precedence, threshold và chính sách bảo vệ ứng viên.
- `missing` và `conflicting` không bị đổi thành `unsatisfied` hoặc Reject.
- Reject chỉ xuất hiện dưới 60 và có yêu cầu bắt buộc `unsatisfied` rõ ràng.
- Không có PII, protected field hoặc outcome leakage trong CV input.
- Không có cặp CV-JD trùng và không chia cùng ứng viên sang nhiều partition.
- Manifest count và SHA-256 khớp file dữ liệu.
- Dataset synthetic chưa được đánh dấu human-reviewed hoặc frozen.

Ngoại lệ nghiệp vụ không được bỏ qua âm thầm. Nếu cần override, phải có field và lý do có cấu trúc, sau đó được test riêng.

## Bước 9: Phân tầng Bronze, Silver và Gold

| Tầng | Điều kiện | Mục đích được phép |
| --- | --- | --- |
| Bronze | Dữ liệu synthetic, nhãn tự động hoặc dữ liệu ngoài chưa được đánh giá đầy đủ | Phát triển, stress test, regression test, thử nghiệm L2 |
| Silver | Đã có ít nhất một vòng human review nhưng chưa đủ điều kiện ground truth cuối | Tuning có kiểm soát và phân tích lỗi |
| Gold | Đã được đánh giá theo quy trình được phê duyệt, có reviewer và audit trail đầy đủ | Validation chính thức hoặc frozen test sau khi split được khóa |

`Bronze`, `Silver`, `Gold` mô tả mức xác thực của dữ liệu, không mô tả chất lượng ứng viên. Case `Pass` vẫn có thể ở tầng Bronze nếu nhãn chỉ do generator đề xuất.

Dataset không được tự động chuyển tầng. Việc chuyển Silver hoặc Gold phải tạo audit record, giữ lại draft ban đầu và chạy lại QC.

## Trạng thái áp dụng trong repository

`synthetic-cv-jd-expansion-v2` là bản Bronze giữ nguyên đề xuất ban đầu. Sau khi người dùng duyệt toàn bộ, bản `synthetic-cv-jd-expansion-v2-reviewed-silver` được tạo riêng để bảo toàn audit trail:

- 5 vị trí.
- 25 Job Profile/JD, 5 biến thể mỗi vị trí.
- 25 rubric liên kết với JD.
- 50 CV synthetic, 10 persona mỗi vị trí.
- 250 cặp CV-JD, 50 cặp mỗi vị trí.
- 250 cặp Bronze vẫn giữ `draft_label`, điểm và rationale ban đầu.
- 250 cặp đã duyệt nằm ở tầng Silver, có một reviewer giả danh, thời gian duyệt và `final_label`.
- Silver được group split theo ứng viên thành 150 cặp development và 100 cặp held-out diagnostic.
- Held-out Silver không phải frozen test và không được dùng làm kết quả cuối; muốn đánh giá chính thức vẫn cần Gold review.
- Không thay đổi 20 validation và 10 frozen-test case hiện tại của Stage 6.

Phiên bản v1 được giữ làm mốc truy vết và đã được thay thế trước khi human review. Không gộp v1 và v2 như hai tập ứng viên độc lập vì chúng dùng cùng ma trận persona–scenario và sẽ tạo leakage nội dung.
