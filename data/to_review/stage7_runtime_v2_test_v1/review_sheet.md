# Phiếu duyệt test set Stage 7 cho Runtime v2

Bộ này gồm 50 cặp CV–JD mới, 10 cặp cho mỗi vai trò. Tất cả nhãn đang là bản nháp Bronze; classifier và API LLM chưa được chạy trên bộ dữ liệu này.

Với mỗi case, hãy duyệt nội dung CV, trạng thái yêu cầu bắt buộc, năm nhóm điểm, tổng điểm, nhãn và lý do. Nếu một lỗi dự đoán sau này chỉ xuất hiện ở số ít case không liên quan an toàn, case vẫn phải được giữ trong báo cáo thay vì xóa khỏi test set.

## s7v2-pair-da-01 — Junior Data Analyst - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `strong`

Tóm tắt CV: Nhóm vận hành cần đối soát thất thoát đơn hàng giữa ba nguồn dữ liệu khác múi giờ. Hồ sơ trình bày một sản phẩm hoàn chỉnh, có số liệu đối chiếu và tài liệu tái tạo. Mục tiêu ứng tuyển là Junior Data Analyst - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-da-01-01`: Hoàn thành chương trình định hướng Phân tích dữ liệu và hệ thống thông tin với đồ án tổng hợp phân tích tỷ lệ khách hàng quay lại của nền tảng bán lẻ. Nhóm vận hành cần đối soát thất thoát đơn hàng giữa ba nguồn dữ liệu khác múi giờ. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-da-01-02`: Trong phân tích tỷ lệ khách hàng quay lại của nền tảng bán lẻ, ứng viên tự viết truy vấn nhiều bảng, dùng CTE và hàm cửa sổ để đối soát số liệu theo từng kỳ. Nhóm vận hành cần đối soát thất thoát đơn hàng giữa ba nguồn dữ liệu khác múi giờ. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-da-01-03`: Trong phân tích tỷ lệ khách hàng quay lại của nền tảng bán lẻ, ứng viên dùng pandas để chuẩn hóa kiểu dữ liệu, xử lý giá trị thiếu và đóng gói notebook có thể chạy lại. Nhóm vận hành cần đối soát thất thoát đơn hàng giữa ba nguồn dữ liệu khác múi giờ. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-da-01-04`: Trong phân tích tỷ lệ khách hàng quay lại của nền tảng bán lẻ, ứng viên dựng dashboard có data model, bộ lọc chi tiết và tài liệu định nghĩa từng KPI. Nhóm vận hành cần đối soát thất thoát đơn hàng giữa ba nguồn dữ liệu khác múi giờ. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-da-01-05`: Trong phân tích tỷ lệ khách hàng quay lại của nền tảng bán lẻ, ứng viên chuyển câu hỏi kinh doanh thành chỉ số, phân tích nguyên nhân và nêu khuyến nghị kèm giới hạn. Nhóm vận hành cần đối soát thất thoát đơn hàng giữa ba nguồn dữ liệu khác múi giờ. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-da-01-06`: Ở phần mở rộng của phân tích tỷ lệ khách hàng quay lại của nền tảng bán lẻ, ứng viên áp dụng Có thống kê ứng dụng hoặc A/B testing. và ghi lại kết quả thử nghiệm riêng. Nhóm vận hành cần đối soát thất thoát đơn hàng giữa ba nguồn dữ liệu khác múi giờ. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-da-01-07`: Ở phần mở rộng của phân tích tỷ lệ khách hàng quay lại của nền tảng bán lẻ, ứng viên áp dụng Có data warehouse, data modeling hoặc ETL/ELT. và ghi lại kết quả thử nghiệm riêng. Nhóm vận hành cần đối soát thất thoát đơn hàng giữa ba nguồn dữ liệu khác múi giờ. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-da-01-08`: Phạm vi kỹ thuật của phân tích tỷ lệ khách hàng quay lại của nền tảng bán lẻ: Luồng chính và các trường hợp lỗi được kiểm tra trên nhiều bộ dữ liệu hoặc tình huống đầu vào. Nhóm vận hành cần đối soát thất thoát đơn hàng giữa ba nguồn dữ liệu khác múi giờ. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-da-01-09`: Cách ra quyết định trong phân tích tỷ lệ khách hàng quay lại của nền tảng bán lẻ: Hai phương án được so sánh bằng tiêu chí đo được trước khi chọn cách triển khai. Nhóm vận hành cần đối soát thất thoát đơn hàng giữa ba nguồn dữ liệu khác múi giờ. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-da-01-10`: Bàn giao cho phân tích tỷ lệ khách hàng quay lại của nền tảng bán lẻ: Kết quả có chỉ số trước và sau, bộ kiểm tra hồi quy và hướng dẫn chạy độc lập. Nhóm vận hành cần đối soát thất thoát đơn hàng giữa ba nguồn dữ liệu khác múi giờ. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-da-01-11`: Tài liệu của phân tích tỷ lệ khách hàng quay lại của nền tảng bán lẻ: Tài liệu nêu rõ phạm vi cá nhân, giả định, giới hạn và quyết định kỹ thuật. Nhóm vận hành cần đối soát thất thoát đơn hàng giữa ba nguồn dữ liệu khác múi giờ. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.

Trạng thái yêu cầu bắt buộc:

- `da-sql`: `satisfied`; thông tin: ev-s7v2-da-01-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `da-analysis-language`: `satisfied`; thông tin: ev-s7v2-da-01-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `da-bi-reporting`: `satisfied`; thông tin: ev-s7v2-da-01-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `da-business-analysis`: `satisfied`; thông tin: ev-s7v2-da-01-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `da-technical-specialization` | 24/25 |
| `da-role-capability` | 18/20 |
| `projects-and-impact` | 14/15 |
| `communication-and-evidence-quality` | 9/10 |

Tổng điểm: **95/100**

Nhãn nháp: **pass**

Lý do vào review: không có

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-da-02 — Junior Data Analyst - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `solid`

Tóm tắt CV: Bộ phận tăng trưởng cần phân tách tác động của chiến dịch theo cohort và kênh thu hút. Hồ sơ có dự án junior hoàn chỉnh, thông tin nhất quán và đầu ra có thể kiểm tra. Mục tiêu ứng tuyển là Junior Data Analyst - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-da-02-01`: Hoàn thành chương trình định hướng Phân tích dữ liệu và hệ thống thông tin với đồ án tổng hợp theo dõi tồn kho và thời gian giao hàng tại ba kho mô phỏng. Bộ phận tăng trưởng cần phân tách tác động của chiến dịch theo cohort và kênh thu hút. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-da-02-02`: Trong theo dõi tồn kho và thời gian giao hàng tại ba kho mô phỏng, ứng viên tự viết truy vấn nhiều bảng, dùng CTE và hàm cửa sổ để đối soát số liệu theo từng kỳ. Bộ phận tăng trưởng cần phân tách tác động của chiến dịch theo cohort và kênh thu hút. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-da-02-03`: Trong theo dõi tồn kho và thời gian giao hàng tại ba kho mô phỏng, ứng viên dùng pandas để chuẩn hóa kiểu dữ liệu, xử lý giá trị thiếu và đóng gói notebook có thể chạy lại. Bộ phận tăng trưởng cần phân tách tác động của chiến dịch theo cohort và kênh thu hút. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-da-02-04`: Trong theo dõi tồn kho và thời gian giao hàng tại ba kho mô phỏng, ứng viên dựng dashboard có data model, bộ lọc chi tiết và tài liệu định nghĩa từng KPI. Bộ phận tăng trưởng cần phân tách tác động của chiến dịch theo cohort và kênh thu hút. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-da-02-05`: Trong theo dõi tồn kho và thời gian giao hàng tại ba kho mô phỏng, ứng viên chuyển câu hỏi kinh doanh thành chỉ số, phân tích nguyên nhân và nêu khuyến nghị kèm giới hạn. Bộ phận tăng trưởng cần phân tách tác động của chiến dịch theo cohort và kênh thu hút. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-da-02-06`: Ở phần mở rộng của theo dõi tồn kho và thời gian giao hàng tại ba kho mô phỏng, ứng viên áp dụng Có thống kê ứng dụng hoặc A/B testing. và ghi lại kết quả thử nghiệm riêng. Bộ phận tăng trưởng cần phân tách tác động của chiến dịch theo cohort và kênh thu hút. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-da-02-07`: Ở phần mở rộng của theo dõi tồn kho và thời gian giao hàng tại ba kho mô phỏng, ứng viên áp dụng Có data warehouse, data modeling hoặc ETL/ELT. và ghi lại kết quả thử nghiệm riêng. Bộ phận tăng trưởng cần phân tách tác động của chiến dịch theo cohort và kênh thu hút. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-da-02-08`: Phạm vi kỹ thuật của theo dõi tồn kho và thời gian giao hàng tại ba kho mô phỏng: Luồng nghiệp vụ chính và hai trường hợp lỗi phổ biến được triển khai và kiểm thử. Bộ phận tăng trưởng cần phân tách tác động của chiến dịch theo cohort và kênh thu hút. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-da-02-09`: Cách ra quyết định trong theo dõi tồn kho và thời gian giao hàng tại ba kho mô phỏng: Mục tiêu, giả định và cách đối chiếu kết quả được trình bày rõ. Bộ phận tăng trưởng cần phân tách tác động của chiến dịch theo cohort và kênh thu hút. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-da-02-10`: Bàn giao cho theo dõi tồn kho và thời gian giao hàng tại ba kho mô phỏng: Sản phẩm có dữ liệu mẫu, lệnh chạy và kết quả kiểm tra nhất quán. Bộ phận tăng trưởng cần phân tách tác động của chiến dịch theo cohort và kênh thu hút. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-da-02-11`: Tài liệu của theo dõi tồn kho và thời gian giao hàng tại ba kho mô phỏng: README mô tả phần việc cá nhân và các hạn chế chính. Bộ phận tăng trưởng cần phân tách tác động của chiến dịch theo cohort và kênh thu hút. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.

Trạng thái yêu cầu bắt buộc:

- `da-sql`: `satisfied`; thông tin: ev-s7v2-da-02-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `da-analysis-language`: `satisfied`; thông tin: ev-s7v2-da-02-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `da-bi-reporting`: `satisfied`; thông tin: ev-s7v2-da-02-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `da-business-analysis`: `satisfied`; thông tin: ev-s7v2-da-02-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `da-technical-specialization` | 22/25 |
| `da-role-capability` | 17/20 |
| `projects-and-impact` | 12/15 |
| `communication-and-evidence-quality` | 8/10 |

Tổng điểm: **89/100**

Nhãn nháp: **pass**

Lý do vào review: không có

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-da-03 — Junior Data Analyst - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `moderate`

Tóm tắt CV: Đội sản phẩm cần kiểm tra nguyên nhân tỷ lệ kích hoạt giảm sau một lần thay đổi giao diện. Hồ sơ đáp ứng phần cốt lõi nhưng dự án mới giới hạn ở một luồng nghiệp vụ. Mục tiêu ứng tuyển là Junior Data Analyst - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-da-03-01`: Hoàn thành chương trình định hướng Phân tích dữ liệu và hệ thống thông tin với đồ án tổng hợp đánh giá phễu đăng ký của ứng dụng học trực tuyến. Đội sản phẩm cần kiểm tra nguyên nhân tỷ lệ kích hoạt giảm sau một lần thay đổi giao diện. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-da-03-02`: Trong đánh giá phễu đăng ký của ứng dụng học trực tuyến, ứng viên tự viết truy vấn nhiều bảng, dùng CTE và hàm cửa sổ để đối soát số liệu theo từng kỳ. Đội sản phẩm cần kiểm tra nguyên nhân tỷ lệ kích hoạt giảm sau một lần thay đổi giao diện. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-da-03-03`: Trong đánh giá phễu đăng ký của ứng dụng học trực tuyến, ứng viên dùng pandas để chuẩn hóa kiểu dữ liệu, xử lý giá trị thiếu và đóng gói notebook có thể chạy lại. Đội sản phẩm cần kiểm tra nguyên nhân tỷ lệ kích hoạt giảm sau một lần thay đổi giao diện. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-da-03-04`: Trong đánh giá phễu đăng ký của ứng dụng học trực tuyến, ứng viên dựng dashboard có data model, bộ lọc chi tiết và tài liệu định nghĩa từng KPI. Đội sản phẩm cần kiểm tra nguyên nhân tỷ lệ kích hoạt giảm sau một lần thay đổi giao diện. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-da-03-05`: Trong đánh giá phễu đăng ký của ứng dụng học trực tuyến, ứng viên chuyển câu hỏi kinh doanh thành chỉ số, phân tích nguyên nhân và nêu khuyến nghị kèm giới hạn. Đội sản phẩm cần kiểm tra nguyên nhân tỷ lệ kích hoạt giảm sau một lần thay đổi giao diện. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-da-03-06`: Ở phần mở rộng của đánh giá phễu đăng ký của ứng dụng học trực tuyến, ứng viên áp dụng Có thống kê ứng dụng hoặc A/B testing. và ghi lại kết quả thử nghiệm riêng. Đội sản phẩm cần kiểm tra nguyên nhân tỷ lệ kích hoạt giảm sau một lần thay đổi giao diện. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-da-03-07`: Phạm vi kỹ thuật của đánh giá phễu đăng ký của ứng dụng học trực tuyến: Một luồng chính được hoàn thành trên tập dữ liệu hoặc chức năng có phạm vi vừa phải. Đội sản phẩm cần kiểm tra nguyên nhân tỷ lệ kích hoạt giảm sau một lần thay đổi giao diện. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-da-03-08`: Cách ra quyết định trong đánh giá phễu đăng ký của ứng dụng học trực tuyến: Phương pháp được giải thích nhưng phần so sánh phương án còn ngắn. Đội sản phẩm cần kiểm tra nguyên nhân tỷ lệ kích hoạt giảm sau một lần thay đổi giao diện. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-da-03-09`: Bàn giao cho đánh giá phễu đăng ký của ứng dụng học trực tuyến: Đầu ra chạy lại được cục bộ và có một số kiểm tra cơ bản. Đội sản phẩm cần kiểm tra nguyên nhân tỷ lệ kích hoạt giảm sau một lần thay đổi giao diện. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-da-03-10`: Tài liệu của đánh giá phễu đăng ký của ứng dụng học trực tuyến: Tài liệu đủ để chạy thử nhưng chưa mô tả đầy đủ rủi ro vận hành. Đội sản phẩm cần kiểm tra nguyên nhân tỷ lệ kích hoạt giảm sau một lần thay đổi giao diện. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.

Trạng thái yêu cầu bắt buộc:

- `da-sql`: `satisfied`; thông tin: ev-s7v2-da-03-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `da-analysis-language`: `satisfied`; thông tin: ev-s7v2-da-03-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `da-bi-reporting`: `satisfied`; thông tin: ev-s7v2-da-03-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `da-business-analysis`: `satisfied`; thông tin: ev-s7v2-da-03-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `da-technical-specialization` | 17/25 |
| `da-role-capability` | 14/20 |
| `projects-and-impact` | 9/15 |
| `communication-and-evidence-quality` | 8/10 |

Tổng điểm: **78/100**

Nhãn nháp: **waitlist**

Lý do vào review: không có

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-da-04 — Junior Data Analyst - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `missing_critical`

Tóm tắt CV: Nhóm tài chính cần tái lập báo cáo doanh thu với quy tắc hoàn tiền thay đổi theo kỳ. Hồ sơ mô tả một số phần việc liên quan nhưng không đề cập đầy đủ toàn bộ năng lực cốt lõi. Mục tiêu ứng tuyển là Junior Data Analyst - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-da-04-01`: Hoàn thành chương trình định hướng Phân tích dữ liệu và hệ thống thông tin với đồ án tổng hợp tìm nguyên nhân gia tăng đơn hoàn trả theo nhóm sản phẩm. Nhóm tài chính cần tái lập báo cáo doanh thu với quy tắc hoàn tiền thay đổi theo kỳ. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-da-04-02`: Trong tìm nguyên nhân gia tăng đơn hoàn trả theo nhóm sản phẩm, ứng viên dùng pandas để chuẩn hóa kiểu dữ liệu, xử lý giá trị thiếu và đóng gói notebook có thể chạy lại. Nhóm tài chính cần tái lập báo cáo doanh thu với quy tắc hoàn tiền thay đổi theo kỳ. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-da-04-03`: Trong tìm nguyên nhân gia tăng đơn hoàn trả theo nhóm sản phẩm, ứng viên dựng dashboard có data model, bộ lọc chi tiết và tài liệu định nghĩa từng KPI. Nhóm tài chính cần tái lập báo cáo doanh thu với quy tắc hoàn tiền thay đổi theo kỳ. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-da-04-04`: Trong tìm nguyên nhân gia tăng đơn hoàn trả theo nhóm sản phẩm, ứng viên chuyển câu hỏi kinh doanh thành chỉ số, phân tích nguyên nhân và nêu khuyến nghị kèm giới hạn. Nhóm tài chính cần tái lập báo cáo doanh thu với quy tắc hoàn tiền thay đổi theo kỳ. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-da-04-05`: Ở phần mở rộng của tìm nguyên nhân gia tăng đơn hoàn trả theo nhóm sản phẩm, ứng viên áp dụng Có thống kê ứng dụng hoặc A/B testing. và ghi lại kết quả thử nghiệm riêng. Nhóm tài chính cần tái lập báo cáo doanh thu với quy tắc hoàn tiền thay đổi theo kỳ. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-da-04-06`: Phạm vi kỹ thuật của tìm nguyên nhân gia tăng đơn hoàn trả theo nhóm sản phẩm: Các phần được nêu có thao tác kỹ thuật và kiểm tra đầu vào cơ bản. Nhóm tài chính cần tái lập báo cáo doanh thu với quy tắc hoàn tiền thay đổi theo kỳ. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-da-04-07`: Cách ra quyết định trong tìm nguyên nhân gia tăng đơn hoàn trả theo nhóm sản phẩm: Ứng viên giải thích mục tiêu và một giới hạn của giải pháp. Nhóm tài chính cần tái lập báo cáo doanh thu với quy tắc hoàn tiền thay đổi theo kỳ. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-da-04-08`: Bàn giao cho tìm nguyên nhân gia tăng đơn hoàn trả theo nhóm sản phẩm: Có bản chạy thử cùng dữ liệu hoặc tình huống minh họa. Nhóm tài chính cần tái lập báo cáo doanh thu với quy tắc hoàn tiền thay đổi theo kỳ. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-da-04-09`: Tài liệu của tìm nguyên nhân gia tăng đơn hoàn trả theo nhóm sản phẩm: Phạm vi đã làm được ghi rõ, không suy diễn cho phần chưa được mô tả. Nhóm tài chính cần tái lập báo cáo doanh thu với quy tắc hoàn tiền thay đổi theo kỳ. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.

Trạng thái yêu cầu bắt buộc:

- `da-sql`: `missing`; thông tin: không có thông tin liên kết; Hồ sơ không đề cập đủ thông tin để xác nhận yêu cầu này.
- `da-analysis-language`: `satisfied`; thông tin: ev-s7v2-da-04-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `da-bi-reporting`: `satisfied`; thông tin: ev-s7v2-da-04-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `da-business-analysis`: `satisfied`; thông tin: ev-s7v2-da-04-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 20/30 |
| `da-technical-specialization` | 17/25 |
| `da-role-capability` | 13/20 |
| `projects-and-impact` | 8/15 |
| `communication-and-evidence-quality` | 6/10 |

Tổng điểm: **64/100**

Nhãn nháp: **needs_review**

Lý do vào review: missing-critical-evidence, low-score-without-explicit-critical-unsatisfied

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-da-05 — Junior Data Analyst - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `conflicting_critical`

Tóm tắt CV: Trung tâm hỗ trợ cần phân tích thời gian xử lý và tỷ lệ mở lại theo loại yêu cầu. Hồ sơ kết hợp mô tả dự án và bản tự đánh giá có một điểm chưa nhất quán. Mục tiêu ứng tuyển là Junior Data Analyst - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-da-05-01`: Hoàn thành chương trình định hướng Phân tích dữ liệu và hệ thống thông tin với đồ án tổng hợp đối chiếu chất lượng phục vụ của trung tâm hỗ trợ. Trung tâm hỗ trợ cần phân tích thời gian xử lý và tỷ lệ mở lại theo loại yêu cầu. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-da-05-02`: Trong đối chiếu chất lượng phục vụ của trung tâm hỗ trợ, ứng viên tự viết truy vấn nhiều bảng, dùng CTE và hàm cửa sổ để đối soát số liệu theo từng kỳ. Trung tâm hỗ trợ cần phân tích thời gian xử lý và tỷ lệ mở lại theo loại yêu cầu. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-da-05-03`: Trong đối chiếu chất lượng phục vụ của trung tâm hỗ trợ, ứng viên dùng pandas để chuẩn hóa kiểu dữ liệu, xử lý giá trị thiếu và đóng gói notebook có thể chạy lại. Trung tâm hỗ trợ cần phân tích thời gian xử lý và tỷ lệ mở lại theo loại yêu cầu. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-da-05-04`: Ứng viên xác nhận chưa từng dùng Python hay R để xử lý dữ liệu. Trung tâm hỗ trợ cần phân tích thời gian xử lý và tỷ lệ mở lại theo loại yêu cầu. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-da-05-05`: Trong đối chiếu chất lượng phục vụ của trung tâm hỗ trợ, ứng viên dựng dashboard có data model, bộ lọc chi tiết và tài liệu định nghĩa từng KPI. Trung tâm hỗ trợ cần phân tích thời gian xử lý và tỷ lệ mở lại theo loại yêu cầu. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-da-05-06`: Trong đối chiếu chất lượng phục vụ của trung tâm hỗ trợ, ứng viên chuyển câu hỏi kinh doanh thành chỉ số, phân tích nguyên nhân và nêu khuyến nghị kèm giới hạn. Trung tâm hỗ trợ cần phân tích thời gian xử lý và tỷ lệ mở lại theo loại yêu cầu. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-da-05-07`: Ở phần mở rộng của đối chiếu chất lượng phục vụ của trung tâm hỗ trợ, ứng viên áp dụng Có thống kê ứng dụng hoặc A/B testing. và ghi lại kết quả thử nghiệm riêng. Trung tâm hỗ trợ cần phân tích thời gian xử lý và tỷ lệ mở lại theo loại yêu cầu. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-da-05-08`: Ở phần mở rộng của đối chiếu chất lượng phục vụ của trung tâm hỗ trợ, ứng viên áp dụng Có data warehouse, data modeling hoặc ETL/ELT. và ghi lại kết quả thử nghiệm riêng. Trung tâm hỗ trợ cần phân tích thời gian xử lý và tỷ lệ mở lại theo loại yêu cầu. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-da-05-09`: Phạm vi kỹ thuật của đối chiếu chất lượng phục vụ của trung tâm hỗ trợ: Một luồng kỹ thuật hoàn chỉnh được mô tả cùng cách kiểm tra sai lệch. Trung tâm hỗ trợ cần phân tích thời gian xử lý và tỷ lệ mở lại theo loại yêu cầu. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-da-05-10`: Cách ra quyết định trong đối chiếu chất lượng phục vụ của trung tâm hỗ trợ: Mục tiêu và kết quả được nêu nhưng một phát biểu năng lực cần xác minh lại. Trung tâm hỗ trợ cần phân tích thời gian xử lý và tỷ lệ mở lại theo loại yêu cầu. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-da-05-11`: Bàn giao cho đối chiếu chất lượng phục vụ của trung tâm hỗ trợ: Có đầu ra mẫu và danh sách vấn đề còn mở. Trung tâm hỗ trợ cần phân tích thời gian xử lý và tỷ lệ mở lại theo loại yêu cầu. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.
- `ev-s7v2-da-05-12`: Tài liệu của đối chiếu chất lượng phục vụ của trung tâm hỗ trợ: Tài liệu giữ nguyên cả hai phát biểu để người đánh giá xử lý mâu thuẫn. Trung tâm hỗ trợ cần phân tích thời gian xử lý và tỷ lệ mở lại theo loại yêu cầu. Kết luận chỉ giới hạn trong phạm vi mẫu đã quan sát và không suy diễn quá mức.

Trạng thái yêu cầu bắt buộc:

- `da-sql`: `satisfied`; thông tin: ev-s7v2-da-05-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `da-analysis-language`: `conflicting`; thông tin: ev-s7v2-da-05-03, ev-s7v2-da-05-04; Hồ sơ đồng thời có mô tả thực hành và phát biểu phủ định mâu thuẫn.
- `da-bi-reporting`: `satisfied`; thông tin: ev-s7v2-da-05-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `da-business-analysis`: `satisfied`; thông tin: ev-s7v2-da-05-06; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 22/30 |
| `da-technical-specialization` | 17/25 |
| `da-role-capability` | 13/20 |
| `projects-and-impact` | 9/15 |
| `communication-and-evidence-quality` | 7/10 |

Tổng điểm: **68/100**

Nhãn nháp: **needs_review**

Lý do vào review: conflicting-critical-evidence, lower-threshold-boundary

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-da-06 — Junior Data Analyst - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `explicit_failure`

Tóm tắt CV: Đơn vị bán lẻ cần theo dõi tồn kho chậm luân chuyển và cảnh báo sai lệch nhập xuất. Ứng viên chuyển hướng từ lĩnh vực gần và xác nhận chưa thực hành một năng lực bắt buộc. Mục tiêu ứng tuyển là Junior Data Analyst - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-da-06-01`: Hoàn thành chương trình định hướng Phân tích dữ liệu và hệ thống thông tin với đồ án tổng hợp kiểm tra chênh lệch doanh thu giữa hệ thống bán hàng và kế toán. Đơn vị bán lẻ cần theo dõi tồn kho chậm luân chuyển và cảnh báo sai lệch nhập xuất. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-da-06-02`: Ứng viên xác nhận chưa từng viết truy vấn SQL có JOIN hoặc phép tổng hợp. Đơn vị bán lẻ cần theo dõi tồn kho chậm luân chuyển và cảnh báo sai lệch nhập xuất. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-da-06-03`: Trong kiểm tra chênh lệch doanh thu giữa hệ thống bán hàng và kế toán, ứng viên dùng pandas để chuẩn hóa kiểu dữ liệu, xử lý giá trị thiếu và đóng gói notebook có thể chạy lại. Đơn vị bán lẻ cần theo dõi tồn kho chậm luân chuyển và cảnh báo sai lệch nhập xuất. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-da-06-04`: Trong kiểm tra chênh lệch doanh thu giữa hệ thống bán hàng và kế toán, ứng viên dựng dashboard có data model, bộ lọc chi tiết và tài liệu định nghĩa từng KPI. Đơn vị bán lẻ cần theo dõi tồn kho chậm luân chuyển và cảnh báo sai lệch nhập xuất. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-da-06-05`: Trong kiểm tra chênh lệch doanh thu giữa hệ thống bán hàng và kế toán, ứng viên chuyển câu hỏi kinh doanh thành chỉ số, phân tích nguyên nhân và nêu khuyến nghị kèm giới hạn. Đơn vị bán lẻ cần theo dõi tồn kho chậm luân chuyển và cảnh báo sai lệch nhập xuất. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-da-06-06`: Phạm vi kỹ thuật của kiểm tra chênh lệch doanh thu giữa hệ thống bán hàng và kế toán: Phần việc hiện có chỉ hỗ trợ gián tiếp cho vai trò mục tiêu. Đơn vị bán lẻ cần theo dõi tồn kho chậm luân chuyển và cảnh báo sai lệch nhập xuất. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-da-06-07`: Cách ra quyết định trong kiểm tra chênh lệch doanh thu giữa hệ thống bán hàng và kế toán: Kết quả mong muốn được nêu nhưng chưa có phương pháp đáp ứng yêu cầu chính. Đơn vị bán lẻ cần theo dõi tồn kho chậm luân chuyển và cảnh báo sai lệch nhập xuất. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-da-06-08`: Bàn giao cho kiểm tra chênh lệch doanh thu giữa hệ thống bán hàng và kế toán: Bài tập dừng ở bản minh họa một lần và chưa có kiểm tra đầy đủ. Đơn vị bán lẻ cần theo dõi tồn kho chậm luân chuyển và cảnh báo sai lệch nhập xuất. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-da-06-09`: Tài liệu của kiểm tra chênh lệch doanh thu giữa hệ thống bán hàng và kế toán: Hồ sơ diễn đạt rõ năng lực chưa từng sử dụng để tránh suy diễn sai. Đơn vị bán lẻ cần theo dõi tồn kho chậm luân chuyển và cảnh báo sai lệch nhập xuất. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.

Trạng thái yêu cầu bắt buộc:

- `da-sql`: `unsatisfied`; thông tin: ev-s7v2-da-06-02; Hồ sơ có phát biểu phủ định rõ ràng về yêu cầu này.
- `da-analysis-language`: `satisfied`; thông tin: ev-s7v2-da-06-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `da-bi-reporting`: `satisfied`; thông tin: ev-s7v2-da-06-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `da-business-analysis`: `satisfied`; thông tin: ev-s7v2-da-06-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 10/30 |
| `da-technical-specialization` | 12/25 |
| `da-role-capability` | 9/20 |
| `projects-and-impact` | 5/15 |
| `communication-and-evidence-quality` | 5/10 |

Tổng điểm: **41/100**

Nhãn nháp: **reject**

Lý do vào review: không có

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-da-07 — Junior Data Analyst - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `lower_boundary`

Tóm tắt CV: Nhóm giáo dục cần đo tiến trình học tập khi dữ liệu sự kiện có bản ghi đến muộn. Hồ sơ vừa đủ yêu cầu cốt lõi nhưng mức độ sâu và phạm vi dự án còn hạn chế. Mục tiêu ứng tuyển là Junior Data Analyst - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-da-07-01`: Hoàn thành chương trình định hướng Phân tích dữ liệu và hệ thống thông tin với đồ án tổng hợp xây báo cáo hiệu suất nhà bán hàng trên sàn thử nghiệm. Nhóm giáo dục cần đo tiến trình học tập khi dữ liệu sự kiện có bản ghi đến muộn. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-da-07-02`: Trong xây báo cáo hiệu suất nhà bán hàng trên sàn thử nghiệm, ứng viên tự viết truy vấn nhiều bảng, dùng CTE và hàm cửa sổ để đối soát số liệu theo từng kỳ. Nhóm giáo dục cần đo tiến trình học tập khi dữ liệu sự kiện có bản ghi đến muộn. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-da-07-03`: Trong xây báo cáo hiệu suất nhà bán hàng trên sàn thử nghiệm, ứng viên dùng pandas để chuẩn hóa kiểu dữ liệu, xử lý giá trị thiếu và đóng gói notebook có thể chạy lại. Nhóm giáo dục cần đo tiến trình học tập khi dữ liệu sự kiện có bản ghi đến muộn. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-da-07-04`: Trong xây báo cáo hiệu suất nhà bán hàng trên sàn thử nghiệm, ứng viên dựng dashboard có data model, bộ lọc chi tiết và tài liệu định nghĩa từng KPI. Nhóm giáo dục cần đo tiến trình học tập khi dữ liệu sự kiện có bản ghi đến muộn. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-da-07-05`: Trong xây báo cáo hiệu suất nhà bán hàng trên sàn thử nghiệm, ứng viên chuyển câu hỏi kinh doanh thành chỉ số, phân tích nguyên nhân và nêu khuyến nghị kèm giới hạn. Nhóm giáo dục cần đo tiến trình học tập khi dữ liệu sự kiện có bản ghi đến muộn. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-da-07-06`: Ở phần mở rộng của xây báo cáo hiệu suất nhà bán hàng trên sàn thử nghiệm, ứng viên áp dụng Có thống kê ứng dụng hoặc A/B testing. và ghi lại kết quả thử nghiệm riêng. Nhóm giáo dục cần đo tiến trình học tập khi dữ liệu sự kiện có bản ghi đến muộn. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-da-07-07`: Phạm vi kỹ thuật của xây báo cáo hiệu suất nhà bán hàng trên sàn thử nghiệm: Luồng cơ bản hoạt động nhưng mới kiểm tra một số trường hợp phổ biến. Nhóm giáo dục cần đo tiến trình học tập khi dữ liệu sự kiện có bản ghi đến muộn. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-da-07-08`: Cách ra quyết định trong xây báo cáo hiệu suất nhà bán hàng trên sàn thử nghiệm: Mục tiêu và kết quả được nêu, phần đối chiếu độc lập còn thiếu. Nhóm giáo dục cần đo tiến trình học tập khi dữ liệu sự kiện có bản ghi đến muộn. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-da-07-09`: Bàn giao cho xây báo cáo hiệu suất nhà bán hàng trên sàn thử nghiệm: Đầu ra chạy lại được trên một bộ mẫu cố định. Nhóm giáo dục cần đo tiến trình học tập khi dữ liệu sự kiện có bản ghi đến muộn. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-da-07-10`: Tài liệu của xây báo cáo hiệu suất nhà bán hàng trên sàn thử nghiệm: README rõ lệnh chính nhưng phần quyết định kỹ thuật còn ngắn. Nhóm giáo dục cần đo tiến trình học tập khi dữ liệu sự kiện có bản ghi đến muộn. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.

Trạng thái yêu cầu bắt buộc:

- `da-sql`: `satisfied`; thông tin: ev-s7v2-da-07-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `da-analysis-language`: `satisfied`; thông tin: ev-s7v2-da-07-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `da-bi-reporting`: `satisfied`; thông tin: ev-s7v2-da-07-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `da-business-analysis`: `satisfied`; thông tin: ev-s7v2-da-07-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 27/30 |
| `da-technical-specialization` | 13/25 |
| `da-role-capability` | 10/20 |
| `projects-and-impact` | 8/15 |
| `communication-and-evidence-quality` | 9/10 |

Tổng điểm: **67/100**

Nhãn nháp: **needs_review**

Lý do vào review: lower-threshold-boundary

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-da-08 — Junior Data Analyst - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `upper_boundary`

Tóm tắt CV: Đội marketplace cần xây định nghĩa thống nhất cho GMV, đơn hợp lệ và nhà bán hoạt động. Hồ sơ khá tốt và nằm gần ngưỡng Pass nên cần kiểm tra tính ổn định của quyết định. Mục tiêu ứng tuyển là Junior Data Analyst - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-da-08-01`: Hoàn thành chương trình định hướng Phân tích dữ liệu và hệ thống thông tin với đồ án tổng hợp đo mức kích hoạt tính năng mới theo cohort người dùng. Đội marketplace cần xây định nghĩa thống nhất cho GMV, đơn hợp lệ và nhà bán hoạt động. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-da-08-02`: Trong đo mức kích hoạt tính năng mới theo cohort người dùng, ứng viên tự viết truy vấn nhiều bảng, dùng CTE và hàm cửa sổ để đối soát số liệu theo từng kỳ. Đội marketplace cần xây định nghĩa thống nhất cho GMV, đơn hợp lệ và nhà bán hoạt động. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-da-08-03`: Trong đo mức kích hoạt tính năng mới theo cohort người dùng, ứng viên dùng pandas để chuẩn hóa kiểu dữ liệu, xử lý giá trị thiếu và đóng gói notebook có thể chạy lại. Đội marketplace cần xây định nghĩa thống nhất cho GMV, đơn hợp lệ và nhà bán hoạt động. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-da-08-04`: Trong đo mức kích hoạt tính năng mới theo cohort người dùng, ứng viên dựng dashboard có data model, bộ lọc chi tiết và tài liệu định nghĩa từng KPI. Đội marketplace cần xây định nghĩa thống nhất cho GMV, đơn hợp lệ và nhà bán hoạt động. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-da-08-05`: Trong đo mức kích hoạt tính năng mới theo cohort người dùng, ứng viên chuyển câu hỏi kinh doanh thành chỉ số, phân tích nguyên nhân và nêu khuyến nghị kèm giới hạn. Đội marketplace cần xây định nghĩa thống nhất cho GMV, đơn hợp lệ và nhà bán hoạt động. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-da-08-06`: Ở phần mở rộng của đo mức kích hoạt tính năng mới theo cohort người dùng, ứng viên áp dụng Có thống kê ứng dụng hoặc A/B testing. và ghi lại kết quả thử nghiệm riêng. Đội marketplace cần xây định nghĩa thống nhất cho GMV, đơn hợp lệ và nhà bán hoạt động. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-da-08-07`: Ở phần mở rộng của đo mức kích hoạt tính năng mới theo cohort người dùng, ứng viên áp dụng Có data warehouse, data modeling hoặc ETL/ELT. và ghi lại kết quả thử nghiệm riêng. Đội marketplace cần xây định nghĩa thống nhất cho GMV, đơn hợp lệ và nhà bán hoạt động. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-da-08-08`: Phạm vi kỹ thuật của đo mức kích hoạt tính năng mới theo cohort người dùng: Luồng chính và các lỗi thường gặp được xử lý bằng kiểm tra có thể chạy lại. Đội marketplace cần xây định nghĩa thống nhất cho GMV, đơn hợp lệ và nhà bán hoạt động. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-da-08-09`: Cách ra quyết định trong đo mức kích hoạt tính năng mới theo cohort người dùng: Lựa chọn kỹ thuật có lý do và ghi nhận một giới hạn đáng chú ý. Đội marketplace cần xây định nghĩa thống nhất cho GMV, đơn hợp lệ và nhà bán hoạt động. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-da-08-10`: Bàn giao cho đo mức kích hoạt tính năng mới theo cohort người dùng: Có dữ liệu mẫu, kết quả đối chiếu và hướng dẫn tái tạo. Đội marketplace cần xây định nghĩa thống nhất cho GMV, đơn hợp lệ và nhà bán hoạt động. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-da-08-11`: Tài liệu của đo mức kích hoạt tính năng mới theo cohort người dùng: Tài liệu rõ cách chạy nhưng phần giải thích một số quyết định còn cô đọng. Đội marketplace cần xây định nghĩa thống nhất cho GMV, đơn hợp lệ và nhà bán hoạt động. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.

Trạng thái yêu cầu bắt buộc:

- `da-sql`: `satisfied`; thông tin: ev-s7v2-da-08-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `da-analysis-language`: `satisfied`; thông tin: ev-s7v2-da-08-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `da-bi-reporting`: `satisfied`; thông tin: ev-s7v2-da-08-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `da-business-analysis`: `satisfied`; thông tin: ev-s7v2-da-08-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `da-technical-specialization` | 18/25 |
| `da-role-capability` | 15/20 |
| `projects-and-impact` | 12/15 |
| `communication-and-evidence-quality` | 7/10 |

Tổng điểm: **82/100**

Nhãn nháp: **needs_review**

Lý do vào review: upper-threshold-boundary

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-da-09 — Junior Data Analyst - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `transferable`

Tóm tắt CV: Ứng viên chuyển từ nghiên cứu định lượng sang bài toán phân tích hành vi người dùng. Ứng viên chuyển từ lĩnh vực gần và chứng minh được năng lực tương đương qua dự án mới. Mục tiêu ứng tuyển là Junior Data Analyst - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-da-09-01`: Hoàn thành chương trình định hướng Phân tích dữ liệu và hệ thống thông tin với đồ án tổng hợp chuyển kinh nghiệm nghiên cứu định lượng sang phân tích sản phẩm. Ứng viên chuyển từ nghiên cứu định lượng sang bài toán phân tích hành vi người dùng. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-da-09-02`: Trong chuyển kinh nghiệm nghiên cứu định lượng sang phân tích sản phẩm, ứng viên tự viết truy vấn nhiều bảng, dùng CTE và hàm cửa sổ để đối soát số liệu theo từng kỳ. Ứng viên chuyển từ nghiên cứu định lượng sang bài toán phân tích hành vi người dùng. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-da-09-03`: Trong chuyển kinh nghiệm nghiên cứu định lượng sang phân tích sản phẩm, ứng viên dùng pandas để chuẩn hóa kiểu dữ liệu, xử lý giá trị thiếu và đóng gói notebook có thể chạy lại. Ứng viên chuyển từ nghiên cứu định lượng sang bài toán phân tích hành vi người dùng. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-da-09-04`: Trong chuyển kinh nghiệm nghiên cứu định lượng sang phân tích sản phẩm, ứng viên dựng dashboard có data model, bộ lọc chi tiết và tài liệu định nghĩa từng KPI. Ứng viên chuyển từ nghiên cứu định lượng sang bài toán phân tích hành vi người dùng. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-da-09-05`: Trong chuyển kinh nghiệm nghiên cứu định lượng sang phân tích sản phẩm, ứng viên chuyển câu hỏi kinh doanh thành chỉ số, phân tích nguyên nhân và nêu khuyến nghị kèm giới hạn. Ứng viên chuyển từ nghiên cứu định lượng sang bài toán phân tích hành vi người dùng. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-da-09-06`: Ở phần mở rộng của chuyển kinh nghiệm nghiên cứu định lượng sang phân tích sản phẩm, ứng viên áp dụng Có thống kê ứng dụng hoặc A/B testing. và ghi lại kết quả thử nghiệm riêng. Ứng viên chuyển từ nghiên cứu định lượng sang bài toán phân tích hành vi người dùng. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-da-09-07`: Phạm vi kỹ thuật của chuyển kinh nghiệm nghiên cứu định lượng sang phân tích sản phẩm: Kiến thức nền từ lĩnh vực gần được áp dụng vào một sản phẩm đúng vai trò mục tiêu. Ứng viên chuyển từ nghiên cứu định lượng sang bài toán phân tích hành vi người dùng. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-da-09-08`: Cách ra quyết định trong chuyển kinh nghiệm nghiên cứu định lượng sang phân tích sản phẩm: Hồ sơ phân biệt rõ phần kinh nghiệm chuyển đổi và phần mới học. Ứng viên chuyển từ nghiên cứu định lượng sang bài toán phân tích hành vi người dùng. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-da-09-09`: Bàn giao cho chuyển kinh nghiệm nghiên cứu định lượng sang phân tích sản phẩm: Prototype chạy được, có kiểm tra và đầu ra đo được nhưng chưa qua môi trường thực tập. Ứng viên chuyển từ nghiên cứu định lượng sang bài toán phân tích hành vi người dùng. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-da-09-10`: Tài liệu của chuyển kinh nghiệm nghiên cứu định lượng sang phân tích sản phẩm: Tài liệu nêu rõ phạm vi kinh nghiệm trực tiếp và kinh nghiệm tương đương. Ứng viên chuyển từ nghiên cứu định lượng sang bài toán phân tích hành vi người dùng. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.

Trạng thái yêu cầu bắt buộc:

- `da-sql`: `satisfied`; thông tin: ev-s7v2-da-09-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `da-analysis-language`: `satisfied`; thông tin: ev-s7v2-da-09-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `da-bi-reporting`: `satisfied`; thông tin: ev-s7v2-da-09-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `da-business-analysis`: `satisfied`; thông tin: ev-s7v2-da-09-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `da-technical-specialization` | 16/25 |
| `da-role-capability` | 14/20 |
| `projects-and-impact` | 10/15 |
| `communication-and-evidence-quality` | 9/10 |

Tổng điểm: **79/100**

Nhãn nháp: **waitlist**

Lý do vào review: không có

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-da-10 — Junior Data Analyst - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `hard_negative`

Tóm tắt CV: Hồ sơ mô tả kiến thức khóa học nhưng chưa gắn với một quyết định kinh doanh cụ thể. Hồ sơ chủ yếu liệt kê khóa học và công cụ nhưng không mô tả nhiệm vụ hay sản phẩm đã làm. Mục tiêu ứng tuyển là Junior Data Analyst - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-da-10-01`: Hoàn thành chương trình định hướng Phân tích dữ liệu và hệ thống thông tin với đồ án tổng hợp tổng hợp danh sách công cụ từ các khóa học phân tích dữ liệu. Hồ sơ mô tả kiến thức khóa học nhưng chưa gắn với một quyết định kinh doanh cụ thể. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-da-10-02`: Đã hoàn thành bài học giới thiệu về SQL và tự ghi tên công cụ trong danh sách kỹ năng. Hồ sơ mô tả kiến thức khóa học nhưng chưa gắn với một quyết định kinh doanh cụ thể. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-da-10-03`: Đã hoàn thành bài học giới thiệu về Python hoặc R và tự ghi tên công cụ trong danh sách kỹ năng. Hồ sơ mô tả kiến thức khóa học nhưng chưa gắn với một quyết định kinh doanh cụ thể. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-da-10-04`: Đã hoàn thành bài học giới thiệu về Power BI hoặc Tableau và tự ghi tên công cụ trong danh sách kỹ năng. Hồ sơ mô tả kiến thức khóa học nhưng chưa gắn với một quyết định kinh doanh cụ thể. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-da-10-05`: Đã hoàn thành bài học giới thiệu về Phân tích nghiệp vụ end-to-end và tự ghi tên công cụ trong danh sách kỹ năng. Hồ sơ mô tả kiến thức khóa học nhưng chưa gắn với một quyết định kinh doanh cụ thể. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-da-10-06`: Ở phần mở rộng của tổng hợp danh sách công cụ từ các khóa học phân tích dữ liệu, ứng viên áp dụng Có thống kê ứng dụng hoặc A/B testing. và ghi lại kết quả thử nghiệm riêng. Hồ sơ mô tả kiến thức khóa học nhưng chưa gắn với một quyết định kinh doanh cụ thể. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-da-10-07`: Ở phần mở rộng của tổng hợp danh sách công cụ từ các khóa học phân tích dữ liệu, ứng viên áp dụng Có data warehouse, data modeling hoặc ETL/ELT. và ghi lại kết quả thử nghiệm riêng. Hồ sơ mô tả kiến thức khóa học nhưng chưa gắn với một quyết định kinh doanh cụ thể. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.

Trạng thái yêu cầu bắt buộc:

- `da-sql`: `missing`; thông tin: ev-s7v2-da-10-02; Hồ sơ không đề cập đủ thông tin để xác nhận yêu cầu này.
- `da-analysis-language`: `missing`; thông tin: ev-s7v2-da-10-03; Hồ sơ không đề cập đủ thông tin để xác nhận yêu cầu này.
- `da-bi-reporting`: `missing`; thông tin: ev-s7v2-da-10-04; Hồ sơ không đề cập đủ thông tin để xác nhận yêu cầu này.
- `da-business-analysis`: `missing`; thông tin: ev-s7v2-da-10-05; Hồ sơ không đề cập đủ thông tin để xác nhận yêu cầu này.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 14/30 |
| `da-technical-specialization` | 9/25 |
| `da-role-capability` | 6/20 |
| `projects-and-impact` | 3/15 |
| `communication-and-evidence-quality` | 4/10 |

Tổng điểm: **36/100**

Nhãn nháp: **needs_review**

Lý do vào review: missing-critical-evidence, low-score-without-explicit-critical-unsatisfied

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-be-01 — Junior Python Backend Developer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `strong`

Tóm tắt CV: Dịch vụ cần chống tạo trùng yêu cầu khi client gửi lại sau lỗi mạng. Hồ sơ trình bày một sản phẩm hoàn chỉnh, có số liệu đối chiếu và tài liệu tái tạo. Mục tiêu ứng tuyển là Junior Python Backend Developer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-be-01-01`: Hoàn thành chương trình định hướng Kỹ thuật phần mềm và hệ thống thông tin với đồ án tổng hợp xây dịch vụ xử lý đơn hàng có idempotency key. Dịch vụ cần chống tạo trùng yêu cầu khi client gửi lại sau lỗi mạng. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-be-01-02`: Trong xây dịch vụ xử lý đơn hàng có idempotency key, ứng viên tổ chức Python theo lớp dịch vụ, dùng type hint và xử lý ngoại lệ theo hợp đồng lỗi. Dịch vụ cần chống tạo trùng yêu cầu khi client gửi lại sau lỗi mạng. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-be-01-03`: Trong xây dịch vụ xử lý đơn hàng có idempotency key, ứng viên xây REST API bằng FastAPI với validation, phân trang và mã trạng thái nhất quán. Dịch vụ cần chống tạo trùng yêu cầu khi client gửi lại sau lỗi mạng. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-be-01-04`: Trong xây dịch vụ xử lý đơn hàng có idempotency key, ứng viên thiết kế bảng PostgreSQL, migration và truy vấn transaction cho luồng cập nhật dữ liệu. Dịch vụ cần chống tạo trùng yêu cầu khi client gửi lại sau lỗi mạng. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-be-01-05`: Trong xây dịch vụ xử lý đơn hàng có idempotency key, ứng viên viết pytest cho service và API, gồm luồng đúng, dữ liệu sai và dependency giả lập. Dịch vụ cần chống tạo trùng yêu cầu khi client gửi lại sau lỗi mạng. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-be-01-06`: Trong xây dịch vụ xử lý đơn hàng có idempotency key, ứng viên quản lý nhánh Git, đóng gói Docker và ghi lệnh khởi động môi trường phát triển. Dịch vụ cần chống tạo trùng yêu cầu khi client gửi lại sau lỗi mạng. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-be-01-07`: Ở phần mở rộng của xây dịch vụ xử lý đơn hàng có idempotency key, ứng viên áp dụng Có async, cache, message queue hoặc webhook. và ghi lại kết quả thử nghiệm riêng. Dịch vụ cần chống tạo trùng yêu cầu khi client gửi lại sau lỗi mạng. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-be-01-08`: Ở phần mở rộng của xây dịch vụ xử lý đơn hàng có idempotency key, ứng viên áp dụng Có CI/CD, logging và monitoring. và ghi lại kết quả thử nghiệm riêng. Dịch vụ cần chống tạo trùng yêu cầu khi client gửi lại sau lỗi mạng. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-be-01-09`: Phạm vi kỹ thuật của xây dịch vụ xử lý đơn hàng có idempotency key: Luồng chính và các trường hợp lỗi được kiểm tra trên nhiều bộ dữ liệu hoặc tình huống đầu vào. Dịch vụ cần chống tạo trùng yêu cầu khi client gửi lại sau lỗi mạng. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-be-01-10`: Cách ra quyết định trong xây dịch vụ xử lý đơn hàng có idempotency key: Hai phương án được so sánh bằng tiêu chí đo được trước khi chọn cách triển khai. Dịch vụ cần chống tạo trùng yêu cầu khi client gửi lại sau lỗi mạng. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-be-01-11`: Bàn giao cho xây dịch vụ xử lý đơn hàng có idempotency key: Kết quả có chỉ số trước và sau, bộ kiểm tra hồi quy và hướng dẫn chạy độc lập. Dịch vụ cần chống tạo trùng yêu cầu khi client gửi lại sau lỗi mạng. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.
- `ev-s7v2-be-01-12`: Tài liệu của xây dịch vụ xử lý đơn hàng có idempotency key: Tài liệu nêu rõ phạm vi cá nhân, giả định, giới hạn và quyết định kỹ thuật. Dịch vụ cần chống tạo trùng yêu cầu khi client gửi lại sau lỗi mạng. Kết luận chỉ giới hạn trong phạm vi mẫu đã quan sát và không suy diễn quá mức.

Trạng thái yêu cầu bắt buộc:

- `be-python`: `satisfied`; thông tin: ev-s7v2-be-01-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-rest-api`: `satisfied`; thông tin: ev-s7v2-be-01-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-relational-data`: `satisfied`; thông tin: ev-s7v2-be-01-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-testing`: `satisfied`; thông tin: ev-s7v2-be-01-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-delivery-workflow`: `satisfied`; thông tin: ev-s7v2-be-01-06; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `be-technical-specialization` | 24/25 |
| `be-role-capability` | 18/20 |
| `projects-and-impact` | 14/15 |
| `communication-and-evidence-quality` | 9/10 |

Tổng điểm: **95/100**

Nhãn nháp: **pass**

Lý do vào review: không có

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-be-02 — Junior Python Backend Developer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `solid`

Tóm tắt CV: API quản lý kho phải giữ nhất quán dữ liệu khi hai tiến trình cập nhật đồng thời. Hồ sơ có dự án junior hoàn chỉnh, thông tin nhất quán và đầu ra có thể kiểm tra. Mục tiêu ứng tuyển là Junior Python Backend Developer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-be-02-01`: Hoàn thành chương trình định hướng Kỹ thuật phần mềm và hệ thống thông tin với đồ án tổng hợp phát triển API tồn kho với kiểm soát transaction. API quản lý kho phải giữ nhất quán dữ liệu khi hai tiến trình cập nhật đồng thời. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-be-02-02`: Trong phát triển API tồn kho với kiểm soát transaction, ứng viên tổ chức Python theo lớp dịch vụ, dùng type hint và xử lý ngoại lệ theo hợp đồng lỗi. API quản lý kho phải giữ nhất quán dữ liệu khi hai tiến trình cập nhật đồng thời. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-be-02-03`: Trong phát triển API tồn kho với kiểm soát transaction, ứng viên xây REST API bằng FastAPI với validation, phân trang và mã trạng thái nhất quán. API quản lý kho phải giữ nhất quán dữ liệu khi hai tiến trình cập nhật đồng thời. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-be-02-04`: Trong phát triển API tồn kho với kiểm soát transaction, ứng viên thiết kế bảng PostgreSQL, migration và truy vấn transaction cho luồng cập nhật dữ liệu. API quản lý kho phải giữ nhất quán dữ liệu khi hai tiến trình cập nhật đồng thời. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-be-02-05`: Trong phát triển API tồn kho với kiểm soát transaction, ứng viên viết pytest cho service và API, gồm luồng đúng, dữ liệu sai và dependency giả lập. API quản lý kho phải giữ nhất quán dữ liệu khi hai tiến trình cập nhật đồng thời. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-be-02-06`: Trong phát triển API tồn kho với kiểm soát transaction, ứng viên quản lý nhánh Git, đóng gói Docker và ghi lệnh khởi động môi trường phát triển. API quản lý kho phải giữ nhất quán dữ liệu khi hai tiến trình cập nhật đồng thời. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-be-02-07`: Ở phần mở rộng của phát triển API tồn kho với kiểm soát transaction, ứng viên áp dụng Có async, cache, message queue hoặc webhook. và ghi lại kết quả thử nghiệm riêng. API quản lý kho phải giữ nhất quán dữ liệu khi hai tiến trình cập nhật đồng thời. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-be-02-08`: Ở phần mở rộng của phát triển API tồn kho với kiểm soát transaction, ứng viên áp dụng Có CI/CD, logging và monitoring. và ghi lại kết quả thử nghiệm riêng. API quản lý kho phải giữ nhất quán dữ liệu khi hai tiến trình cập nhật đồng thời. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-be-02-09`: Phạm vi kỹ thuật của phát triển API tồn kho với kiểm soát transaction: Luồng nghiệp vụ chính và hai trường hợp lỗi phổ biến được triển khai và kiểm thử. API quản lý kho phải giữ nhất quán dữ liệu khi hai tiến trình cập nhật đồng thời. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-be-02-10`: Cách ra quyết định trong phát triển API tồn kho với kiểm soát transaction: Mục tiêu, giả định và cách đối chiếu kết quả được trình bày rõ. API quản lý kho phải giữ nhất quán dữ liệu khi hai tiến trình cập nhật đồng thời. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-be-02-11`: Bàn giao cho phát triển API tồn kho với kiểm soát transaction: Sản phẩm có dữ liệu mẫu, lệnh chạy và kết quả kiểm tra nhất quán. API quản lý kho phải giữ nhất quán dữ liệu khi hai tiến trình cập nhật đồng thời. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.
- `ev-s7v2-be-02-12`: Tài liệu của phát triển API tồn kho với kiểm soát transaction: README mô tả phần việc cá nhân và các hạn chế chính. API quản lý kho phải giữ nhất quán dữ liệu khi hai tiến trình cập nhật đồng thời. Kết luận chỉ giới hạn trong phạm vi mẫu đã quan sát và không suy diễn quá mức.

Trạng thái yêu cầu bắt buộc:

- `be-python`: `satisfied`; thông tin: ev-s7v2-be-02-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-rest-api`: `satisfied`; thông tin: ev-s7v2-be-02-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-relational-data`: `satisfied`; thông tin: ev-s7v2-be-02-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-testing`: `satisfied`; thông tin: ev-s7v2-be-02-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-delivery-workflow`: `satisfied`; thông tin: ev-s7v2-be-02-06; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `be-technical-specialization` | 22/25 |
| `be-role-capability` | 17/20 |
| `projects-and-impact` | 12/15 |
| `communication-and-evidence-quality` | 8/10 |

Tổng điểm: **89/100**

Nhãn nháp: **pass**

Lý do vào review: không có

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-be-03 — Junior Python Backend Developer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `moderate`

Tóm tắt CV: Hệ thống đặt lịch cần phân quyền, audit log và chuẩn hóa phản hồi lỗi. Hồ sơ đáp ứng phần cốt lõi nhưng dự án mới giới hạn ở một luồng nghiệp vụ. Mục tiêu ứng tuyển là Junior Python Backend Developer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-be-03-01`: Hoàn thành chương trình định hướng Kỹ thuật phần mềm và hệ thống thông tin với đồ án tổng hợp tạo backend đặt lịch có phân quyền người dùng. Hệ thống đặt lịch cần phân quyền, audit log và chuẩn hóa phản hồi lỗi. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-be-03-02`: Trong tạo backend đặt lịch có phân quyền người dùng, ứng viên tổ chức Python theo lớp dịch vụ, dùng type hint và xử lý ngoại lệ theo hợp đồng lỗi. Hệ thống đặt lịch cần phân quyền, audit log và chuẩn hóa phản hồi lỗi. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-be-03-03`: Trong tạo backend đặt lịch có phân quyền người dùng, ứng viên xây REST API bằng FastAPI với validation, phân trang và mã trạng thái nhất quán. Hệ thống đặt lịch cần phân quyền, audit log và chuẩn hóa phản hồi lỗi. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-be-03-04`: Trong tạo backend đặt lịch có phân quyền người dùng, ứng viên thiết kế bảng PostgreSQL, migration và truy vấn transaction cho luồng cập nhật dữ liệu. Hệ thống đặt lịch cần phân quyền, audit log và chuẩn hóa phản hồi lỗi. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-be-03-05`: Trong tạo backend đặt lịch có phân quyền người dùng, ứng viên viết pytest cho service và API, gồm luồng đúng, dữ liệu sai và dependency giả lập. Hệ thống đặt lịch cần phân quyền, audit log và chuẩn hóa phản hồi lỗi. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-be-03-06`: Trong tạo backend đặt lịch có phân quyền người dùng, ứng viên quản lý nhánh Git, đóng gói Docker và ghi lệnh khởi động môi trường phát triển. Hệ thống đặt lịch cần phân quyền, audit log và chuẩn hóa phản hồi lỗi. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-be-03-07`: Ở phần mở rộng của tạo backend đặt lịch có phân quyền người dùng, ứng viên áp dụng Có async, cache, message queue hoặc webhook. và ghi lại kết quả thử nghiệm riêng. Hệ thống đặt lịch cần phân quyền, audit log và chuẩn hóa phản hồi lỗi. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-be-03-08`: Phạm vi kỹ thuật của tạo backend đặt lịch có phân quyền người dùng: Một luồng chính được hoàn thành trên tập dữ liệu hoặc chức năng có phạm vi vừa phải. Hệ thống đặt lịch cần phân quyền, audit log và chuẩn hóa phản hồi lỗi. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-be-03-09`: Cách ra quyết định trong tạo backend đặt lịch có phân quyền người dùng: Phương pháp được giải thích nhưng phần so sánh phương án còn ngắn. Hệ thống đặt lịch cần phân quyền, audit log và chuẩn hóa phản hồi lỗi. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-be-03-10`: Bàn giao cho tạo backend đặt lịch có phân quyền người dùng: Đầu ra chạy lại được cục bộ và có một số kiểm tra cơ bản. Hệ thống đặt lịch cần phân quyền, audit log và chuẩn hóa phản hồi lỗi. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-be-03-11`: Tài liệu của tạo backend đặt lịch có phân quyền người dùng: Tài liệu đủ để chạy thử nhưng chưa mô tả đầy đủ rủi ro vận hành. Hệ thống đặt lịch cần phân quyền, audit log và chuẩn hóa phản hồi lỗi. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.

Trạng thái yêu cầu bắt buộc:

- `be-python`: `satisfied`; thông tin: ev-s7v2-be-03-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-rest-api`: `satisfied`; thông tin: ev-s7v2-be-03-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-relational-data`: `satisfied`; thông tin: ev-s7v2-be-03-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-testing`: `satisfied`; thông tin: ev-s7v2-be-03-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-delivery-workflow`: `satisfied`; thông tin: ev-s7v2-be-03-06; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `be-technical-specialization` | 17/25 |
| `be-role-capability` | 14/20 |
| `projects-and-impact` | 9/15 |
| `communication-and-evidence-quality` | 8/10 |

Tổng điểm: **78/100**

Nhãn nháp: **waitlist**

Lý do vào review: không có

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-be-04 — Junior Python Backend Developer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `missing_critical`

Tóm tắt CV: Webhook thanh toán cần xác minh chữ ký và xử lý sự kiện không đúng thứ tự. Hồ sơ mô tả một số phần việc liên quan nhưng không đề cập đầy đủ toàn bộ năng lực cốt lõi. Mục tiêu ứng tuyển là Junior Python Backend Developer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-be-04-01`: Hoàn thành chương trình định hướng Kỹ thuật phần mềm và hệ thống thông tin với đồ án tổng hợp xử lý webhook thanh toán và chống gửi trùng. Webhook thanh toán cần xác minh chữ ký và xử lý sự kiện không đúng thứ tự. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-be-04-02`: Trong xử lý webhook thanh toán và chống gửi trùng, ứng viên tổ chức Python theo lớp dịch vụ, dùng type hint và xử lý ngoại lệ theo hợp đồng lỗi. Webhook thanh toán cần xác minh chữ ký và xử lý sự kiện không đúng thứ tự. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-be-04-03`: Trong xử lý webhook thanh toán và chống gửi trùng, ứng viên xây REST API bằng FastAPI với validation, phân trang và mã trạng thái nhất quán. Webhook thanh toán cần xác minh chữ ký và xử lý sự kiện không đúng thứ tự. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-be-04-04`: Trong xử lý webhook thanh toán và chống gửi trùng, ứng viên thiết kế bảng PostgreSQL, migration và truy vấn transaction cho luồng cập nhật dữ liệu. Webhook thanh toán cần xác minh chữ ký và xử lý sự kiện không đúng thứ tự. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-be-04-05`: Trong xử lý webhook thanh toán và chống gửi trùng, ứng viên viết pytest cho service và API, gồm luồng đúng, dữ liệu sai và dependency giả lập. Webhook thanh toán cần xác minh chữ ký và xử lý sự kiện không đúng thứ tự. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-be-04-06`: Ở phần mở rộng của xử lý webhook thanh toán và chống gửi trùng, ứng viên áp dụng Có async, cache, message queue hoặc webhook. và ghi lại kết quả thử nghiệm riêng. Webhook thanh toán cần xác minh chữ ký và xử lý sự kiện không đúng thứ tự. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-be-04-07`: Phạm vi kỹ thuật của xử lý webhook thanh toán và chống gửi trùng: Các phần được nêu có thao tác kỹ thuật và kiểm tra đầu vào cơ bản. Webhook thanh toán cần xác minh chữ ký và xử lý sự kiện không đúng thứ tự. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-be-04-08`: Cách ra quyết định trong xử lý webhook thanh toán và chống gửi trùng: Ứng viên giải thích mục tiêu và một giới hạn của giải pháp. Webhook thanh toán cần xác minh chữ ký và xử lý sự kiện không đúng thứ tự. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-be-04-09`: Bàn giao cho xử lý webhook thanh toán và chống gửi trùng: Có bản chạy thử cùng dữ liệu hoặc tình huống minh họa. Webhook thanh toán cần xác minh chữ ký và xử lý sự kiện không đúng thứ tự. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-be-04-10`: Tài liệu của xử lý webhook thanh toán và chống gửi trùng: Phạm vi đã làm được ghi rõ, không suy diễn cho phần chưa được mô tả. Webhook thanh toán cần xác minh chữ ký và xử lý sự kiện không đúng thứ tự. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.

Trạng thái yêu cầu bắt buộc:

- `be-python`: `satisfied`; thông tin: ev-s7v2-be-04-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-rest-api`: `satisfied`; thông tin: ev-s7v2-be-04-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-relational-data`: `satisfied`; thông tin: ev-s7v2-be-04-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-testing`: `satisfied`; thông tin: ev-s7v2-be-04-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-delivery-workflow`: `missing`; thông tin: không có thông tin liên kết; Hồ sơ không đề cập đủ thông tin để xác nhận yêu cầu này.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 20/30 |
| `be-technical-specialization` | 17/25 |
| `be-role-capability` | 13/20 |
| `projects-and-impact` | 8/15 |
| `communication-and-evidence-quality` | 6/10 |

Tổng điểm: **64/100**

Nhãn nháp: **needs_review**

Lý do vào review: missing-critical-evidence, low-score-without-explicit-critical-unsatisfied

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-be-05 — Junior Python Backend Developer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `conflicting_critical`

Tóm tắt CV: Dịch vụ thư viện số cần phân trang ổn định và giới hạn truy vấn tốn tài nguyên. Hồ sơ kết hợp mô tả dự án và bản tự đánh giá có một điểm chưa nhất quán. Mục tiêu ứng tuyển là Junior Python Backend Developer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-be-05-01`: Hoàn thành chương trình định hướng Kỹ thuật phần mềm và hệ thống thông tin với đồ án tổng hợp xây API thư viện số với tìm kiếm và phân trang. Dịch vụ thư viện số cần phân trang ổn định và giới hạn truy vấn tốn tài nguyên. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-be-05-02`: Trong xây API thư viện số với tìm kiếm và phân trang, ứng viên tổ chức Python theo lớp dịch vụ, dùng type hint và xử lý ngoại lệ theo hợp đồng lỗi. Dịch vụ thư viện số cần phân trang ổn định và giới hạn truy vấn tốn tài nguyên. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-be-05-03`: Trong xây API thư viện số với tìm kiếm và phân trang, ứng viên xây REST API bằng FastAPI với validation, phân trang và mã trạng thái nhất quán. Dịch vụ thư viện số cần phân trang ổn định và giới hạn truy vấn tốn tài nguyên. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-be-05-04`: Ứng viên xác nhận chưa từng xây hoặc tích hợp REST API. Dịch vụ thư viện số cần phân trang ổn định và giới hạn truy vấn tốn tài nguyên. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-be-05-05`: Trong xây API thư viện số với tìm kiếm và phân trang, ứng viên thiết kế bảng PostgreSQL, migration và truy vấn transaction cho luồng cập nhật dữ liệu. Dịch vụ thư viện số cần phân trang ổn định và giới hạn truy vấn tốn tài nguyên. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-be-05-06`: Trong xây API thư viện số với tìm kiếm và phân trang, ứng viên viết pytest cho service và API, gồm luồng đúng, dữ liệu sai và dependency giả lập. Dịch vụ thư viện số cần phân trang ổn định và giới hạn truy vấn tốn tài nguyên. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-be-05-07`: Trong xây API thư viện số với tìm kiếm và phân trang, ứng viên quản lý nhánh Git, đóng gói Docker và ghi lệnh khởi động môi trường phát triển. Dịch vụ thư viện số cần phân trang ổn định và giới hạn truy vấn tốn tài nguyên. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-be-05-08`: Ở phần mở rộng của xây API thư viện số với tìm kiếm và phân trang, ứng viên áp dụng Có async, cache, message queue hoặc webhook. và ghi lại kết quả thử nghiệm riêng. Dịch vụ thư viện số cần phân trang ổn định và giới hạn truy vấn tốn tài nguyên. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-be-05-09`: Ở phần mở rộng của xây API thư viện số với tìm kiếm và phân trang, ứng viên áp dụng Có CI/CD, logging và monitoring. và ghi lại kết quả thử nghiệm riêng. Dịch vụ thư viện số cần phân trang ổn định và giới hạn truy vấn tốn tài nguyên. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-be-05-10`: Phạm vi kỹ thuật của xây API thư viện số với tìm kiếm và phân trang: Một luồng kỹ thuật hoàn chỉnh được mô tả cùng cách kiểm tra sai lệch. Dịch vụ thư viện số cần phân trang ổn định và giới hạn truy vấn tốn tài nguyên. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-be-05-11`: Cách ra quyết định trong xây API thư viện số với tìm kiếm và phân trang: Mục tiêu và kết quả được nêu nhưng một phát biểu năng lực cần xác minh lại. Dịch vụ thư viện số cần phân trang ổn định và giới hạn truy vấn tốn tài nguyên. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.
- `ev-s7v2-be-05-12`: Bàn giao cho xây API thư viện số với tìm kiếm và phân trang: Có đầu ra mẫu và danh sách vấn đề còn mở. Dịch vụ thư viện số cần phân trang ổn định và giới hạn truy vấn tốn tài nguyên. Kết luận chỉ giới hạn trong phạm vi mẫu đã quan sát và không suy diễn quá mức.
- `ev-s7v2-be-05-13`: Tài liệu của xây API thư viện số với tìm kiếm và phân trang: Tài liệu giữ nguyên cả hai phát biểu để người đánh giá xử lý mâu thuẫn. Dịch vụ thư viện số cần phân trang ổn định và giới hạn truy vấn tốn tài nguyên. Cách đặt tên đầu ra giúp truy vết từ yêu cầu tới kết quả kiểm tra.

Trạng thái yêu cầu bắt buộc:

- `be-python`: `satisfied`; thông tin: ev-s7v2-be-05-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-rest-api`: `conflicting`; thông tin: ev-s7v2-be-05-03, ev-s7v2-be-05-04; Hồ sơ đồng thời có mô tả thực hành và phát biểu phủ định mâu thuẫn.
- `be-relational-data`: `satisfied`; thông tin: ev-s7v2-be-05-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-testing`: `satisfied`; thông tin: ev-s7v2-be-05-06; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-delivery-workflow`: `satisfied`; thông tin: ev-s7v2-be-05-07; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 22/30 |
| `be-technical-specialization` | 17/25 |
| `be-role-capability` | 13/20 |
| `projects-and-impact` | 9/15 |
| `communication-and-evidence-quality` | 7/10 |

Tổng điểm: **68/100**

Nhãn nháp: **needs_review**

Lý do vào review: conflicting-critical-evidence, lower-threshold-boundary

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-be-06 — Junior Python Backend Developer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `explicit_failure`

Tóm tắt CV: Ứng viên chuyển từ lập trình nhúng sang backend và công khai phạm vi chưa thành thạo. Ứng viên chuyển hướng từ lĩnh vực gần và xác nhận chưa thực hành một năng lực bắt buộc. Mục tiêu ứng tuyển là Junior Python Backend Developer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-be-06-01`: Hoàn thành chương trình định hướng Kỹ thuật phần mềm và hệ thống thông tin với đồ án tổng hợp chuyển từ lập trình nhúng sang dịch vụ web Python. Ứng viên chuyển từ lập trình nhúng sang backend và công khai phạm vi chưa thành thạo. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-be-06-02`: Trong chuyển từ lập trình nhúng sang dịch vụ web Python, ứng viên tổ chức Python theo lớp dịch vụ, dùng type hint và xử lý ngoại lệ theo hợp đồng lỗi. Ứng viên chuyển từ lập trình nhúng sang backend và công khai phạm vi chưa thành thạo. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-be-06-03`: Trong chuyển từ lập trình nhúng sang dịch vụ web Python, ứng viên xây REST API bằng FastAPI với validation, phân trang và mã trạng thái nhất quán. Ứng viên chuyển từ lập trình nhúng sang backend và công khai phạm vi chưa thành thạo. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-be-06-04`: Trong chuyển từ lập trình nhúng sang dịch vụ web Python, ứng viên thiết kế bảng PostgreSQL, migration và truy vấn transaction cho luồng cập nhật dữ liệu. Ứng viên chuyển từ lập trình nhúng sang backend và công khai phạm vi chưa thành thạo. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-be-06-05`: Trong chuyển từ lập trình nhúng sang dịch vụ web Python, ứng viên viết pytest cho service và API, gồm luồng đúng, dữ liệu sai và dependency giả lập. Ứng viên chuyển từ lập trình nhúng sang backend và công khai phạm vi chưa thành thạo. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-be-06-06`: Ứng viên xác nhận chưa từng dùng Git hoặc đóng gói ứng dụng bằng Docker. Ứng viên chuyển từ lập trình nhúng sang backend và công khai phạm vi chưa thành thạo. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-be-06-07`: Phạm vi kỹ thuật của chuyển từ lập trình nhúng sang dịch vụ web Python: Phần việc hiện có chỉ hỗ trợ gián tiếp cho vai trò mục tiêu. Ứng viên chuyển từ lập trình nhúng sang backend và công khai phạm vi chưa thành thạo. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-be-06-08`: Cách ra quyết định trong chuyển từ lập trình nhúng sang dịch vụ web Python: Kết quả mong muốn được nêu nhưng chưa có phương pháp đáp ứng yêu cầu chính. Ứng viên chuyển từ lập trình nhúng sang backend và công khai phạm vi chưa thành thạo. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-be-06-09`: Bàn giao cho chuyển từ lập trình nhúng sang dịch vụ web Python: Bài tập dừng ở bản minh họa một lần và chưa có kiểm tra đầy đủ. Ứng viên chuyển từ lập trình nhúng sang backend và công khai phạm vi chưa thành thạo. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-be-06-10`: Tài liệu của chuyển từ lập trình nhúng sang dịch vụ web Python: Hồ sơ diễn đạt rõ năng lực chưa từng sử dụng để tránh suy diễn sai. Ứng viên chuyển từ lập trình nhúng sang backend và công khai phạm vi chưa thành thạo. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.

Trạng thái yêu cầu bắt buộc:

- `be-python`: `satisfied`; thông tin: ev-s7v2-be-06-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-rest-api`: `satisfied`; thông tin: ev-s7v2-be-06-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-relational-data`: `satisfied`; thông tin: ev-s7v2-be-06-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-testing`: `satisfied`; thông tin: ev-s7v2-be-06-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-delivery-workflow`: `unsatisfied`; thông tin: ev-s7v2-be-06-06; Hồ sơ có phát biểu phủ định rõ ràng về yêu cầu này.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 10/30 |
| `be-technical-specialization` | 12/25 |
| `be-role-capability` | 9/20 |
| `projects-and-impact` | 5/15 |
| `communication-and-evidence-quality` | 5/10 |

Tổng điểm: **41/100**

Nhãn nháp: **reject**

Lý do vào review: không có

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-be-07 — Junior Python Backend Developer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `lower_boundary`

Tóm tắt CV: Ứng dụng quản lý công việc cần migration có thể rollback và health check riêng. Hồ sơ vừa đủ yêu cầu cốt lõi nhưng mức độ sâu và phạm vi dự án còn hạn chế. Mục tiêu ứng tuyển là Junior Python Backend Developer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-be-07-01`: Hoàn thành chương trình định hướng Kỹ thuật phần mềm và hệ thống thông tin với đồ án tổng hợp triển khai service quản lý công việc cho nhóm sinh viên. Ứng dụng quản lý công việc cần migration có thể rollback và health check riêng. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-be-07-02`: Trong triển khai service quản lý công việc cho nhóm sinh viên, ứng viên tổ chức Python theo lớp dịch vụ, dùng type hint và xử lý ngoại lệ theo hợp đồng lỗi. Ứng dụng quản lý công việc cần migration có thể rollback và health check riêng. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-be-07-03`: Trong triển khai service quản lý công việc cho nhóm sinh viên, ứng viên xây REST API bằng FastAPI với validation, phân trang và mã trạng thái nhất quán. Ứng dụng quản lý công việc cần migration có thể rollback và health check riêng. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-be-07-04`: Trong triển khai service quản lý công việc cho nhóm sinh viên, ứng viên thiết kế bảng PostgreSQL, migration và truy vấn transaction cho luồng cập nhật dữ liệu. Ứng dụng quản lý công việc cần migration có thể rollback và health check riêng. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-be-07-05`: Trong triển khai service quản lý công việc cho nhóm sinh viên, ứng viên viết pytest cho service và API, gồm luồng đúng, dữ liệu sai và dependency giả lập. Ứng dụng quản lý công việc cần migration có thể rollback và health check riêng. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-be-07-06`: Trong triển khai service quản lý công việc cho nhóm sinh viên, ứng viên quản lý nhánh Git, đóng gói Docker và ghi lệnh khởi động môi trường phát triển. Ứng dụng quản lý công việc cần migration có thể rollback và health check riêng. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-be-07-07`: Ở phần mở rộng của triển khai service quản lý công việc cho nhóm sinh viên, ứng viên áp dụng Có async, cache, message queue hoặc webhook. và ghi lại kết quả thử nghiệm riêng. Ứng dụng quản lý công việc cần migration có thể rollback và health check riêng. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-be-07-08`: Phạm vi kỹ thuật của triển khai service quản lý công việc cho nhóm sinh viên: Luồng cơ bản hoạt động nhưng mới kiểm tra một số trường hợp phổ biến. Ứng dụng quản lý công việc cần migration có thể rollback và health check riêng. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-be-07-09`: Cách ra quyết định trong triển khai service quản lý công việc cho nhóm sinh viên: Mục tiêu và kết quả được nêu, phần đối chiếu độc lập còn thiếu. Ứng dụng quản lý công việc cần migration có thể rollback và health check riêng. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-be-07-10`: Bàn giao cho triển khai service quản lý công việc cho nhóm sinh viên: Đầu ra chạy lại được trên một bộ mẫu cố định. Ứng dụng quản lý công việc cần migration có thể rollback và health check riêng. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-be-07-11`: Tài liệu của triển khai service quản lý công việc cho nhóm sinh viên: README rõ lệnh chính nhưng phần quyết định kỹ thuật còn ngắn. Ứng dụng quản lý công việc cần migration có thể rollback và health check riêng. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.

Trạng thái yêu cầu bắt buộc:

- `be-python`: `satisfied`; thông tin: ev-s7v2-be-07-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-rest-api`: `satisfied`; thông tin: ev-s7v2-be-07-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-relational-data`: `satisfied`; thông tin: ev-s7v2-be-07-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-testing`: `satisfied`; thông tin: ev-s7v2-be-07-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-delivery-workflow`: `satisfied`; thông tin: ev-s7v2-be-07-06; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 27/30 |
| `be-technical-specialization` | 13/25 |
| `be-role-capability` | 10/20 |
| `projects-and-impact` | 8/15 |
| `communication-and-evidence-quality` | 9/10 |

Tổng điểm: **67/100**

Nhãn nháp: **needs_review**

Lý do vào review: lower-threshold-boundary

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-be-08 — Junior Python Backend Developer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `upper_boundary`

Tóm tắt CV: API chi tiêu cần refresh token, thu hồi phiên và kiểm tra quyền sở hữu tài nguyên. Hồ sơ khá tốt và nằm gần ngưỡng Pass nên cần kiểm tra tính ổn định của quyết định. Mục tiêu ứng tuyển là Junior Python Backend Developer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-be-08-01`: Hoàn thành chương trình định hướng Kỹ thuật phần mềm và hệ thống thông tin với đồ án tổng hợp xây API theo dõi chi tiêu với refresh token. API chi tiêu cần refresh token, thu hồi phiên và kiểm tra quyền sở hữu tài nguyên. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-be-08-02`: Trong xây API theo dõi chi tiêu với refresh token, ứng viên tổ chức Python theo lớp dịch vụ, dùng type hint và xử lý ngoại lệ theo hợp đồng lỗi. API chi tiêu cần refresh token, thu hồi phiên và kiểm tra quyền sở hữu tài nguyên. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-be-08-03`: Trong xây API theo dõi chi tiêu với refresh token, ứng viên xây REST API bằng FastAPI với validation, phân trang và mã trạng thái nhất quán. API chi tiêu cần refresh token, thu hồi phiên và kiểm tra quyền sở hữu tài nguyên. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-be-08-04`: Trong xây API theo dõi chi tiêu với refresh token, ứng viên thiết kế bảng PostgreSQL, migration và truy vấn transaction cho luồng cập nhật dữ liệu. API chi tiêu cần refresh token, thu hồi phiên và kiểm tra quyền sở hữu tài nguyên. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-be-08-05`: Trong xây API theo dõi chi tiêu với refresh token, ứng viên viết pytest cho service và API, gồm luồng đúng, dữ liệu sai và dependency giả lập. API chi tiêu cần refresh token, thu hồi phiên và kiểm tra quyền sở hữu tài nguyên. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-be-08-06`: Trong xây API theo dõi chi tiêu với refresh token, ứng viên quản lý nhánh Git, đóng gói Docker và ghi lệnh khởi động môi trường phát triển. API chi tiêu cần refresh token, thu hồi phiên và kiểm tra quyền sở hữu tài nguyên. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-be-08-07`: Ở phần mở rộng của xây API theo dõi chi tiêu với refresh token, ứng viên áp dụng Có async, cache, message queue hoặc webhook. và ghi lại kết quả thử nghiệm riêng. API chi tiêu cần refresh token, thu hồi phiên và kiểm tra quyền sở hữu tài nguyên. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-be-08-08`: Ở phần mở rộng của xây API theo dõi chi tiêu với refresh token, ứng viên áp dụng Có CI/CD, logging và monitoring. và ghi lại kết quả thử nghiệm riêng. API chi tiêu cần refresh token, thu hồi phiên và kiểm tra quyền sở hữu tài nguyên. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-be-08-09`: Phạm vi kỹ thuật của xây API theo dõi chi tiêu với refresh token: Luồng chính và các lỗi thường gặp được xử lý bằng kiểm tra có thể chạy lại. API chi tiêu cần refresh token, thu hồi phiên và kiểm tra quyền sở hữu tài nguyên. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-be-08-10`: Cách ra quyết định trong xây API theo dõi chi tiêu với refresh token: Lựa chọn kỹ thuật có lý do và ghi nhận một giới hạn đáng chú ý. API chi tiêu cần refresh token, thu hồi phiên và kiểm tra quyền sở hữu tài nguyên. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-be-08-11`: Bàn giao cho xây API theo dõi chi tiêu với refresh token: Có dữ liệu mẫu, kết quả đối chiếu và hướng dẫn tái tạo. API chi tiêu cần refresh token, thu hồi phiên và kiểm tra quyền sở hữu tài nguyên. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.
- `ev-s7v2-be-08-12`: Tài liệu của xây API theo dõi chi tiêu với refresh token: Tài liệu rõ cách chạy nhưng phần giải thích một số quyết định còn cô đọng. API chi tiêu cần refresh token, thu hồi phiên và kiểm tra quyền sở hữu tài nguyên. Kết luận chỉ giới hạn trong phạm vi mẫu đã quan sát và không suy diễn quá mức.

Trạng thái yêu cầu bắt buộc:

- `be-python`: `satisfied`; thông tin: ev-s7v2-be-08-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-rest-api`: `satisfied`; thông tin: ev-s7v2-be-08-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-relational-data`: `satisfied`; thông tin: ev-s7v2-be-08-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-testing`: `satisfied`; thông tin: ev-s7v2-be-08-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-delivery-workflow`: `satisfied`; thông tin: ev-s7v2-be-08-06; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `be-technical-specialization` | 18/25 |
| `be-role-capability` | 15/20 |
| `projects-and-impact` | 12/15 |
| `communication-and-evidence-quality` | 7/10 |

Tổng điểm: **82/100**

Nhãn nháp: **needs_review**

Lý do vào review: upper-threshold-boundary

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-be-09 — Junior Python Backend Developer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `transferable`

Tóm tắt CV: Ứng viên chuyển từ Java sang FastAPI với bài tập đo tải và theo dõi lỗi. Ứng viên chuyển từ lĩnh vực gần và chứng minh được năng lực tương đương qua dự án mới. Mục tiêu ứng tuyển là Junior Python Backend Developer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-be-09-01`: Hoàn thành chương trình định hướng Kỹ thuật phần mềm và hệ thống thông tin với đồ án tổng hợp chuyển kinh nghiệm Java sang một microservice FastAPI. Ứng viên chuyển từ Java sang FastAPI với bài tập đo tải và theo dõi lỗi. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-be-09-02`: Trong chuyển kinh nghiệm Java sang một microservice FastAPI, ứng viên tổ chức Python theo lớp dịch vụ, dùng type hint và xử lý ngoại lệ theo hợp đồng lỗi. Ứng viên chuyển từ Java sang FastAPI với bài tập đo tải và theo dõi lỗi. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-be-09-03`: Trong chuyển kinh nghiệm Java sang một microservice FastAPI, ứng viên xây REST API bằng FastAPI với validation, phân trang và mã trạng thái nhất quán. Ứng viên chuyển từ Java sang FastAPI với bài tập đo tải và theo dõi lỗi. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-be-09-04`: Trong chuyển kinh nghiệm Java sang một microservice FastAPI, ứng viên thiết kế bảng PostgreSQL, migration và truy vấn transaction cho luồng cập nhật dữ liệu. Ứng viên chuyển từ Java sang FastAPI với bài tập đo tải và theo dõi lỗi. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-be-09-05`: Trong chuyển kinh nghiệm Java sang một microservice FastAPI, ứng viên viết pytest cho service và API, gồm luồng đúng, dữ liệu sai và dependency giả lập. Ứng viên chuyển từ Java sang FastAPI với bài tập đo tải và theo dõi lỗi. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-be-09-06`: Trong chuyển kinh nghiệm Java sang một microservice FastAPI, ứng viên quản lý nhánh Git, đóng gói Docker và ghi lệnh khởi động môi trường phát triển. Ứng viên chuyển từ Java sang FastAPI với bài tập đo tải và theo dõi lỗi. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-be-09-07`: Ở phần mở rộng của chuyển kinh nghiệm Java sang một microservice FastAPI, ứng viên áp dụng Có async, cache, message queue hoặc webhook. và ghi lại kết quả thử nghiệm riêng. Ứng viên chuyển từ Java sang FastAPI với bài tập đo tải và theo dõi lỗi. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-be-09-08`: Phạm vi kỹ thuật của chuyển kinh nghiệm Java sang một microservice FastAPI: Kiến thức nền từ lĩnh vực gần được áp dụng vào một sản phẩm đúng vai trò mục tiêu. Ứng viên chuyển từ Java sang FastAPI với bài tập đo tải và theo dõi lỗi. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-be-09-09`: Cách ra quyết định trong chuyển kinh nghiệm Java sang một microservice FastAPI: Hồ sơ phân biệt rõ phần kinh nghiệm chuyển đổi và phần mới học. Ứng viên chuyển từ Java sang FastAPI với bài tập đo tải và theo dõi lỗi. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-be-09-10`: Bàn giao cho chuyển kinh nghiệm Java sang một microservice FastAPI: Prototype chạy được, có kiểm tra và đầu ra đo được nhưng chưa qua môi trường thực tập. Ứng viên chuyển từ Java sang FastAPI với bài tập đo tải và theo dõi lỗi. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-be-09-11`: Tài liệu của chuyển kinh nghiệm Java sang một microservice FastAPI: Tài liệu nêu rõ phạm vi kinh nghiệm trực tiếp và kinh nghiệm tương đương. Ứng viên chuyển từ Java sang FastAPI với bài tập đo tải và theo dõi lỗi. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.

Trạng thái yêu cầu bắt buộc:

- `be-python`: `satisfied`; thông tin: ev-s7v2-be-09-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-rest-api`: `satisfied`; thông tin: ev-s7v2-be-09-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-relational-data`: `satisfied`; thông tin: ev-s7v2-be-09-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-testing`: `satisfied`; thông tin: ev-s7v2-be-09-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `be-delivery-workflow`: `satisfied`; thông tin: ev-s7v2-be-09-06; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `be-technical-specialization` | 16/25 |
| `be-role-capability` | 14/20 |
| `projects-and-impact` | 10/15 |
| `communication-and-evidence-quality` | 9/10 |

Tổng điểm: **79/100**

Nhãn nháp: **waitlist**

Lý do vào review: không có

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-be-10 — Junior Python Backend Developer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `hard_negative`

Tóm tắt CV: Hồ sơ liệt kê framework backend nhưng không nêu endpoint hay dữ liệu từng xử lý. Hồ sơ chủ yếu liệt kê khóa học và công cụ nhưng không mô tả nhiệm vụ hay sản phẩm đã làm. Mục tiêu ứng tuyển là Junior Python Backend Developer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-be-10-01`: Hoàn thành chương trình định hướng Kỹ thuật phần mềm và hệ thống thông tin với đồ án tổng hợp liệt kê framework và công cụ backend từ khóa học trực tuyến. Hồ sơ liệt kê framework backend nhưng không nêu endpoint hay dữ liệu từng xử lý. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-be-10-02`: Đã hoàn thành bài học giới thiệu về Python và tự ghi tên công cụ trong danh sách kỹ năng. Hồ sơ liệt kê framework backend nhưng không nêu endpoint hay dữ liệu từng xử lý. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-be-10-03`: Đã hoàn thành bài học giới thiệu về REST API và tự ghi tên công cụ trong danh sách kỹ năng. Hồ sơ liệt kê framework backend nhưng không nêu endpoint hay dữ liệu từng xử lý. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-be-10-04`: Đã hoàn thành bài học giới thiệu về PostgreSQL và SQL và tự ghi tên công cụ trong danh sách kỹ năng. Hồ sơ liệt kê framework backend nhưng không nêu endpoint hay dữ liệu từng xử lý. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-be-10-05`: Đã hoàn thành bài học giới thiệu về pytest và tự ghi tên công cụ trong danh sách kỹ năng. Hồ sơ liệt kê framework backend nhưng không nêu endpoint hay dữ liệu từng xử lý. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-be-10-06`: Đã hoàn thành bài học giới thiệu về Git và Docker và tự ghi tên công cụ trong danh sách kỹ năng. Hồ sơ liệt kê framework backend nhưng không nêu endpoint hay dữ liệu từng xử lý. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-be-10-07`: Ở phần mở rộng của liệt kê framework và công cụ backend từ khóa học trực tuyến, ứng viên áp dụng Có async, cache, message queue hoặc webhook. và ghi lại kết quả thử nghiệm riêng. Hồ sơ liệt kê framework backend nhưng không nêu endpoint hay dữ liệu từng xử lý. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-be-10-08`: Ở phần mở rộng của liệt kê framework và công cụ backend từ khóa học trực tuyến, ứng viên áp dụng Có CI/CD, logging và monitoring. và ghi lại kết quả thử nghiệm riêng. Hồ sơ liệt kê framework backend nhưng không nêu endpoint hay dữ liệu từng xử lý. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.

Trạng thái yêu cầu bắt buộc:

- `be-python`: `missing`; thông tin: ev-s7v2-be-10-02; Hồ sơ không đề cập đủ thông tin để xác nhận yêu cầu này.
- `be-rest-api`: `missing`; thông tin: ev-s7v2-be-10-03; Hồ sơ không đề cập đủ thông tin để xác nhận yêu cầu này.
- `be-relational-data`: `missing`; thông tin: ev-s7v2-be-10-04; Hồ sơ không đề cập đủ thông tin để xác nhận yêu cầu này.
- `be-testing`: `missing`; thông tin: ev-s7v2-be-10-05; Hồ sơ không đề cập đủ thông tin để xác nhận yêu cầu này.
- `be-delivery-workflow`: `missing`; thông tin: ev-s7v2-be-10-06; Hồ sơ không đề cập đủ thông tin để xác nhận yêu cầu này.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 14/30 |
| `be-technical-specialization` | 9/25 |
| `be-role-capability` | 6/20 |
| `projects-and-impact` | 3/15 |
| `communication-and-evidence-quality` | 4/10 |

Tổng điểm: **36/100**

Nhãn nháp: **needs_review**

Lý do vào review: missing-critical-evidence, low-score-without-explicit-critical-unsatisfied

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-fe-01 — Junior Frontend Developer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `strong`

Tóm tắt CV: Cổng học tập phải dùng được bằng bàn phím và giữ trạng thái khi quay lại trang. Hồ sơ trình bày một sản phẩm hoàn chỉnh, có số liệu đối chiếu và tài liệu tái tạo. Mục tiêu ứng tuyển là Junior Frontend Developer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-fe-01-01`: Hoàn thành chương trình định hướng Phát triển web và kỹ thuật phần mềm với đồ án tổng hợp xây trang quản lý khóa học hỗ trợ bàn phím. Cổng học tập phải dùng được bằng bàn phím và giữ trạng thái khi quay lại trang. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-fe-01-02`: Trong xây trang quản lý khóa học hỗ trợ bàn phím, ứng viên xây giao diện semantic HTML, CSS responsive và xử lý tương tác bằng JavaScript. Cổng học tập phải dùng được bằng bàn phím và giữ trạng thái khi quay lại trang. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-fe-01-03`: Trong xây trang quản lý khóa học hỗ trợ bàn phím, ứng viên dùng TypeScript strict, mô hình hóa dữ liệu và thu hẹp kiểu cho dữ liệu bên ngoài. Cổng học tập phải dùng được bằng bàn phím và giữ trạng thái khi quay lại trang. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-fe-01-04`: Trong xây trang quản lý khóa học hỗ trợ bàn phím, ứng viên tách React component, quản lý state và xử lý loading, empty cùng error state. Cổng học tập phải dùng được bằng bàn phím và giữ trạng thái khi quay lại trang. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-fe-01-05`: Trong xây trang quản lý khóa học hỗ trợ bàn phím, ứng viên tích hợp API có xác thực, hủy request cũ và hiển thị lỗi theo từng tình huống. Cổng học tập phải dùng được bằng bàn phím và giữ trạng thái khi quay lại trang. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-fe-01-06`: Trong xây trang quản lý khóa học hỗ trợ bàn phím, ứng viên dùng Git theo pull request và viết Testing Library cho hành vi người dùng chính. Cổng học tập phải dùng được bằng bàn phím và giữ trạng thái khi quay lại trang. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-fe-01-07`: Ở phần mở rộng của xây trang quản lý khóa học hỗ trợ bàn phím, ứng viên áp dụng Có Next.js hoặc rendering phía server. và ghi lại kết quả thử nghiệm riêng. Cổng học tập phải dùng được bằng bàn phím và giữ trạng thái khi quay lại trang. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-fe-01-08`: Ở phần mở rộng của xây trang quản lý khóa học hỗ trợ bàn phím, ứng viên áp dụng Có web performance và accessibility. và ghi lại kết quả thử nghiệm riêng. Cổng học tập phải dùng được bằng bàn phím và giữ trạng thái khi quay lại trang. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-fe-01-09`: Phạm vi kỹ thuật của xây trang quản lý khóa học hỗ trợ bàn phím: Luồng chính và các trường hợp lỗi được kiểm tra trên nhiều bộ dữ liệu hoặc tình huống đầu vào. Cổng học tập phải dùng được bằng bàn phím và giữ trạng thái khi quay lại trang. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-fe-01-10`: Cách ra quyết định trong xây trang quản lý khóa học hỗ trợ bàn phím: Hai phương án được so sánh bằng tiêu chí đo được trước khi chọn cách triển khai. Cổng học tập phải dùng được bằng bàn phím và giữ trạng thái khi quay lại trang. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-fe-01-11`: Bàn giao cho xây trang quản lý khóa học hỗ trợ bàn phím: Kết quả có chỉ số trước và sau, bộ kiểm tra hồi quy và hướng dẫn chạy độc lập. Cổng học tập phải dùng được bằng bàn phím và giữ trạng thái khi quay lại trang. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.
- `ev-s7v2-fe-01-12`: Tài liệu của xây trang quản lý khóa học hỗ trợ bàn phím: Tài liệu nêu rõ phạm vi cá nhân, giả định, giới hạn và quyết định kỹ thuật. Cổng học tập phải dùng được bằng bàn phím và giữ trạng thái khi quay lại trang. Kết luận chỉ giới hạn trong phạm vi mẫu đã quan sát và không suy diễn quá mức.

Trạng thái yêu cầu bắt buộc:

- `fe-web-foundations`: `satisfied`; thông tin: ev-s7v2-fe-01-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-language`: `satisfied`; thông tin: ev-s7v2-fe-01-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-framework`: `satisfied`; thông tin: ev-s7v2-fe-01-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-api`: `satisfied`; thông tin: ev-s7v2-fe-01-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-testing-workflow`: `satisfied`; thông tin: ev-s7v2-fe-01-06; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `fe-technical-specialization` | 24/25 |
| `fe-role-capability` | 18/20 |
| `projects-and-impact` | 14/15 |
| `communication-and-evidence-quality` | 9/10 |

Tổng điểm: **95/100**

Nhãn nháp: **pass**

Lý do vào review: không có

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-fe-02 — Junior Frontend Developer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `solid`

Tóm tắt CV: Giỏ hàng cần đồng bộ nhiều tab và giải quyết phản hồi API đến không đúng thứ tự. Hồ sơ có dự án junior hoàn chỉnh, thông tin nhất quán và đầu ra có thể kiểm tra. Mục tiêu ứng tuyển là Junior Frontend Developer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-fe-02-01`: Hoàn thành chương trình định hướng Phát triển web và kỹ thuật phần mềm với đồ án tổng hợp phát triển giỏ hàng responsive có lưu trạng thái. Giỏ hàng cần đồng bộ nhiều tab và giải quyết phản hồi API đến không đúng thứ tự. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-fe-02-02`: Trong phát triển giỏ hàng responsive có lưu trạng thái, ứng viên xây giao diện semantic HTML, CSS responsive và xử lý tương tác bằng JavaScript. Giỏ hàng cần đồng bộ nhiều tab và giải quyết phản hồi API đến không đúng thứ tự. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-fe-02-03`: Trong phát triển giỏ hàng responsive có lưu trạng thái, ứng viên dùng TypeScript strict, mô hình hóa dữ liệu và thu hẹp kiểu cho dữ liệu bên ngoài. Giỏ hàng cần đồng bộ nhiều tab và giải quyết phản hồi API đến không đúng thứ tự. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-fe-02-04`: Trong phát triển giỏ hàng responsive có lưu trạng thái, ứng viên tách React component, quản lý state và xử lý loading, empty cùng error state. Giỏ hàng cần đồng bộ nhiều tab và giải quyết phản hồi API đến không đúng thứ tự. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-fe-02-05`: Trong phát triển giỏ hàng responsive có lưu trạng thái, ứng viên tích hợp API có xác thực, hủy request cũ và hiển thị lỗi theo từng tình huống. Giỏ hàng cần đồng bộ nhiều tab và giải quyết phản hồi API đến không đúng thứ tự. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-fe-02-06`: Trong phát triển giỏ hàng responsive có lưu trạng thái, ứng viên dùng Git theo pull request và viết Testing Library cho hành vi người dùng chính. Giỏ hàng cần đồng bộ nhiều tab và giải quyết phản hồi API đến không đúng thứ tự. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-fe-02-07`: Ở phần mở rộng của phát triển giỏ hàng responsive có lưu trạng thái, ứng viên áp dụng Có Next.js hoặc rendering phía server. và ghi lại kết quả thử nghiệm riêng. Giỏ hàng cần đồng bộ nhiều tab và giải quyết phản hồi API đến không đúng thứ tự. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-fe-02-08`: Ở phần mở rộng của phát triển giỏ hàng responsive có lưu trạng thái, ứng viên áp dụng Có web performance và accessibility. và ghi lại kết quả thử nghiệm riêng. Giỏ hàng cần đồng bộ nhiều tab và giải quyết phản hồi API đến không đúng thứ tự. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-fe-02-09`: Phạm vi kỹ thuật của phát triển giỏ hàng responsive có lưu trạng thái: Luồng nghiệp vụ chính và hai trường hợp lỗi phổ biến được triển khai và kiểm thử. Giỏ hàng cần đồng bộ nhiều tab và giải quyết phản hồi API đến không đúng thứ tự. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-fe-02-10`: Cách ra quyết định trong phát triển giỏ hàng responsive có lưu trạng thái: Mục tiêu, giả định và cách đối chiếu kết quả được trình bày rõ. Giỏ hàng cần đồng bộ nhiều tab và giải quyết phản hồi API đến không đúng thứ tự. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-fe-02-11`: Bàn giao cho phát triển giỏ hàng responsive có lưu trạng thái: Sản phẩm có dữ liệu mẫu, lệnh chạy và kết quả kiểm tra nhất quán. Giỏ hàng cần đồng bộ nhiều tab và giải quyết phản hồi API đến không đúng thứ tự. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.
- `ev-s7v2-fe-02-12`: Tài liệu của phát triển giỏ hàng responsive có lưu trạng thái: README mô tả phần việc cá nhân và các hạn chế chính. Giỏ hàng cần đồng bộ nhiều tab và giải quyết phản hồi API đến không đúng thứ tự. Kết luận chỉ giới hạn trong phạm vi mẫu đã quan sát và không suy diễn quá mức.

Trạng thái yêu cầu bắt buộc:

- `fe-web-foundations`: `satisfied`; thông tin: ev-s7v2-fe-02-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-language`: `satisfied`; thông tin: ev-s7v2-fe-02-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-framework`: `satisfied`; thông tin: ev-s7v2-fe-02-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-api`: `satisfied`; thông tin: ev-s7v2-fe-02-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-testing-workflow`: `satisfied`; thông tin: ev-s7v2-fe-02-06; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `fe-technical-specialization` | 22/25 |
| `fe-role-capability` | 17/20 |
| `projects-and-impact` | 12/15 |
| `communication-and-evidence-quality` | 8/10 |

Tổng điểm: **89/100**

Nhãn nháp: **pass**

Lý do vào review: không có

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-fe-03 — Junior Frontend Developer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `moderate`

Tóm tắt CV: Dashboard vận hành cần tải dần biểu đồ lớn và hiển thị trạng thái dữ liệu cũ. Hồ sơ đáp ứng phần cốt lõi nhưng dự án mới giới hạn ở một luồng nghiệp vụ. Mục tiêu ứng tuyển là Junior Frontend Developer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-fe-03-01`: Hoàn thành chương trình định hướng Phát triển web và kỹ thuật phần mềm với đồ án tổng hợp tạo dashboard vận hành với biểu đồ và bộ lọc. Dashboard vận hành cần tải dần biểu đồ lớn và hiển thị trạng thái dữ liệu cũ. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-fe-03-02`: Trong tạo dashboard vận hành với biểu đồ và bộ lọc, ứng viên xây giao diện semantic HTML, CSS responsive và xử lý tương tác bằng JavaScript. Dashboard vận hành cần tải dần biểu đồ lớn và hiển thị trạng thái dữ liệu cũ. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-fe-03-03`: Trong tạo dashboard vận hành với biểu đồ và bộ lọc, ứng viên dùng TypeScript strict, mô hình hóa dữ liệu và thu hẹp kiểu cho dữ liệu bên ngoài. Dashboard vận hành cần tải dần biểu đồ lớn và hiển thị trạng thái dữ liệu cũ. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-fe-03-04`: Trong tạo dashboard vận hành với biểu đồ và bộ lọc, ứng viên tách React component, quản lý state và xử lý loading, empty cùng error state. Dashboard vận hành cần tải dần biểu đồ lớn và hiển thị trạng thái dữ liệu cũ. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-fe-03-05`: Trong tạo dashboard vận hành với biểu đồ và bộ lọc, ứng viên tích hợp API có xác thực, hủy request cũ và hiển thị lỗi theo từng tình huống. Dashboard vận hành cần tải dần biểu đồ lớn và hiển thị trạng thái dữ liệu cũ. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-fe-03-06`: Trong tạo dashboard vận hành với biểu đồ và bộ lọc, ứng viên dùng Git theo pull request và viết Testing Library cho hành vi người dùng chính. Dashboard vận hành cần tải dần biểu đồ lớn và hiển thị trạng thái dữ liệu cũ. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-fe-03-07`: Ở phần mở rộng của tạo dashboard vận hành với biểu đồ và bộ lọc, ứng viên áp dụng Có Next.js hoặc rendering phía server. và ghi lại kết quả thử nghiệm riêng. Dashboard vận hành cần tải dần biểu đồ lớn và hiển thị trạng thái dữ liệu cũ. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-fe-03-08`: Phạm vi kỹ thuật của tạo dashboard vận hành với biểu đồ và bộ lọc: Một luồng chính được hoàn thành trên tập dữ liệu hoặc chức năng có phạm vi vừa phải. Dashboard vận hành cần tải dần biểu đồ lớn và hiển thị trạng thái dữ liệu cũ. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-fe-03-09`: Cách ra quyết định trong tạo dashboard vận hành với biểu đồ và bộ lọc: Phương pháp được giải thích nhưng phần so sánh phương án còn ngắn. Dashboard vận hành cần tải dần biểu đồ lớn và hiển thị trạng thái dữ liệu cũ. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-fe-03-10`: Bàn giao cho tạo dashboard vận hành với biểu đồ và bộ lọc: Đầu ra chạy lại được cục bộ và có một số kiểm tra cơ bản. Dashboard vận hành cần tải dần biểu đồ lớn và hiển thị trạng thái dữ liệu cũ. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-fe-03-11`: Tài liệu của tạo dashboard vận hành với biểu đồ và bộ lọc: Tài liệu đủ để chạy thử nhưng chưa mô tả đầy đủ rủi ro vận hành. Dashboard vận hành cần tải dần biểu đồ lớn và hiển thị trạng thái dữ liệu cũ. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.

Trạng thái yêu cầu bắt buộc:

- `fe-web-foundations`: `satisfied`; thông tin: ev-s7v2-fe-03-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-language`: `satisfied`; thông tin: ev-s7v2-fe-03-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-framework`: `satisfied`; thông tin: ev-s7v2-fe-03-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-api`: `satisfied`; thông tin: ev-s7v2-fe-03-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-testing-workflow`: `satisfied`; thông tin: ev-s7v2-fe-03-06; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `fe-technical-specialization` | 17/25 |
| `fe-role-capability` | 14/20 |
| `projects-and-impact` | 9/15 |
| `communication-and-evidence-quality` | 8/10 |

Tổng điểm: **78/100**

Nhãn nháp: **waitlist**

Lý do vào review: không có

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-fe-04 — Junior Frontend Developer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `missing_critical`

Tóm tắt CV: Biểu mẫu sự kiện nhiều bước phải khôi phục bản nháp sau khi phiên đăng nhập hết hạn. Hồ sơ mô tả một số phần việc liên quan nhưng không đề cập đầy đủ toàn bộ năng lực cốt lõi. Mục tiêu ứng tuyển là Junior Frontend Developer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-fe-04-01`: Hoàn thành chương trình định hướng Phát triển web và kỹ thuật phần mềm với đồ án tổng hợp xây cổng đăng ký sự kiện có validation nhiều bước. Biểu mẫu sự kiện nhiều bước phải khôi phục bản nháp sau khi phiên đăng nhập hết hạn. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-fe-04-02`: Trong xây cổng đăng ký sự kiện có validation nhiều bước, ứng viên dùng TypeScript strict, mô hình hóa dữ liệu và thu hẹp kiểu cho dữ liệu bên ngoài. Biểu mẫu sự kiện nhiều bước phải khôi phục bản nháp sau khi phiên đăng nhập hết hạn. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-fe-04-03`: Trong xây cổng đăng ký sự kiện có validation nhiều bước, ứng viên tách React component, quản lý state và xử lý loading, empty cùng error state. Biểu mẫu sự kiện nhiều bước phải khôi phục bản nháp sau khi phiên đăng nhập hết hạn. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-fe-04-04`: Trong xây cổng đăng ký sự kiện có validation nhiều bước, ứng viên tích hợp API có xác thực, hủy request cũ và hiển thị lỗi theo từng tình huống. Biểu mẫu sự kiện nhiều bước phải khôi phục bản nháp sau khi phiên đăng nhập hết hạn. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-fe-04-05`: Trong xây cổng đăng ký sự kiện có validation nhiều bước, ứng viên dùng Git theo pull request và viết Testing Library cho hành vi người dùng chính. Biểu mẫu sự kiện nhiều bước phải khôi phục bản nháp sau khi phiên đăng nhập hết hạn. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-fe-04-06`: Ở phần mở rộng của xây cổng đăng ký sự kiện có validation nhiều bước, ứng viên áp dụng Có Next.js hoặc rendering phía server. và ghi lại kết quả thử nghiệm riêng. Biểu mẫu sự kiện nhiều bước phải khôi phục bản nháp sau khi phiên đăng nhập hết hạn. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-fe-04-07`: Phạm vi kỹ thuật của xây cổng đăng ký sự kiện có validation nhiều bước: Các phần được nêu có thao tác kỹ thuật và kiểm tra đầu vào cơ bản. Biểu mẫu sự kiện nhiều bước phải khôi phục bản nháp sau khi phiên đăng nhập hết hạn. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-fe-04-08`: Cách ra quyết định trong xây cổng đăng ký sự kiện có validation nhiều bước: Ứng viên giải thích mục tiêu và một giới hạn của giải pháp. Biểu mẫu sự kiện nhiều bước phải khôi phục bản nháp sau khi phiên đăng nhập hết hạn. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-fe-04-09`: Bàn giao cho xây cổng đăng ký sự kiện có validation nhiều bước: Có bản chạy thử cùng dữ liệu hoặc tình huống minh họa. Biểu mẫu sự kiện nhiều bước phải khôi phục bản nháp sau khi phiên đăng nhập hết hạn. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-fe-04-10`: Tài liệu của xây cổng đăng ký sự kiện có validation nhiều bước: Phạm vi đã làm được ghi rõ, không suy diễn cho phần chưa được mô tả. Biểu mẫu sự kiện nhiều bước phải khôi phục bản nháp sau khi phiên đăng nhập hết hạn. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.

Trạng thái yêu cầu bắt buộc:

- `fe-web-foundations`: `missing`; thông tin: không có thông tin liên kết; Hồ sơ không đề cập đủ thông tin để xác nhận yêu cầu này.
- `fe-language`: `satisfied`; thông tin: ev-s7v2-fe-04-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-framework`: `satisfied`; thông tin: ev-s7v2-fe-04-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-api`: `satisfied`; thông tin: ev-s7v2-fe-04-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-testing-workflow`: `satisfied`; thông tin: ev-s7v2-fe-04-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 20/30 |
| `fe-technical-specialization` | 17/25 |
| `fe-role-capability` | 13/20 |
| `projects-and-impact` | 8/15 |
| `communication-and-evidence-quality` | 6/10 |

Tổng điểm: **64/100**

Nhãn nháp: **needs_review**

Lý do vào review: missing-critical-evidence, low-score-without-explicit-critical-unsatisfied

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-fe-05 — Junior Frontend Developer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `conflicting_critical`

Tóm tắt CV: Trang quản trị cần ẩn thao tác theo quyền và vẫn xử lý phản hồi 403 từ máy chủ. Hồ sơ kết hợp mô tả dự án và bản tự đánh giá có một điểm chưa nhất quán. Mục tiêu ứng tuyển là Junior Frontend Developer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-fe-05-01`: Hoàn thành chương trình định hướng Phát triển web và kỹ thuật phần mềm với đồ án tổng hợp phát triển giao diện quản trị phân quyền theo vai trò. Trang quản trị cần ẩn thao tác theo quyền và vẫn xử lý phản hồi 403 từ máy chủ. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-fe-05-02`: Trong phát triển giao diện quản trị phân quyền theo vai trò, ứng viên xây giao diện semantic HTML, CSS responsive và xử lý tương tác bằng JavaScript. Trang quản trị cần ẩn thao tác theo quyền và vẫn xử lý phản hồi 403 từ máy chủ. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-fe-05-03`: Trong phát triển giao diện quản trị phân quyền theo vai trò, ứng viên dùng TypeScript strict, mô hình hóa dữ liệu và thu hẹp kiểu cho dữ liệu bên ngoài. Trang quản trị cần ẩn thao tác theo quyền và vẫn xử lý phản hồi 403 từ máy chủ. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-fe-05-04`: Ứng viên xác nhận chưa từng viết JavaScript hoặc TypeScript trong dự án. Trang quản trị cần ẩn thao tác theo quyền và vẫn xử lý phản hồi 403 từ máy chủ. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-fe-05-05`: Trong phát triển giao diện quản trị phân quyền theo vai trò, ứng viên tách React component, quản lý state và xử lý loading, empty cùng error state. Trang quản trị cần ẩn thao tác theo quyền và vẫn xử lý phản hồi 403 từ máy chủ. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-fe-05-06`: Trong phát triển giao diện quản trị phân quyền theo vai trò, ứng viên tích hợp API có xác thực, hủy request cũ và hiển thị lỗi theo từng tình huống. Trang quản trị cần ẩn thao tác theo quyền và vẫn xử lý phản hồi 403 từ máy chủ. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-fe-05-07`: Trong phát triển giao diện quản trị phân quyền theo vai trò, ứng viên dùng Git theo pull request và viết Testing Library cho hành vi người dùng chính. Trang quản trị cần ẩn thao tác theo quyền và vẫn xử lý phản hồi 403 từ máy chủ. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-fe-05-08`: Ở phần mở rộng của phát triển giao diện quản trị phân quyền theo vai trò, ứng viên áp dụng Có Next.js hoặc rendering phía server. và ghi lại kết quả thử nghiệm riêng. Trang quản trị cần ẩn thao tác theo quyền và vẫn xử lý phản hồi 403 từ máy chủ. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-fe-05-09`: Ở phần mở rộng của phát triển giao diện quản trị phân quyền theo vai trò, ứng viên áp dụng Có web performance và accessibility. và ghi lại kết quả thử nghiệm riêng. Trang quản trị cần ẩn thao tác theo quyền và vẫn xử lý phản hồi 403 từ máy chủ. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-fe-05-10`: Phạm vi kỹ thuật của phát triển giao diện quản trị phân quyền theo vai trò: Một luồng kỹ thuật hoàn chỉnh được mô tả cùng cách kiểm tra sai lệch. Trang quản trị cần ẩn thao tác theo quyền và vẫn xử lý phản hồi 403 từ máy chủ. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-fe-05-11`: Cách ra quyết định trong phát triển giao diện quản trị phân quyền theo vai trò: Mục tiêu và kết quả được nêu nhưng một phát biểu năng lực cần xác minh lại. Trang quản trị cần ẩn thao tác theo quyền và vẫn xử lý phản hồi 403 từ máy chủ. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.
- `ev-s7v2-fe-05-12`: Bàn giao cho phát triển giao diện quản trị phân quyền theo vai trò: Có đầu ra mẫu và danh sách vấn đề còn mở. Trang quản trị cần ẩn thao tác theo quyền và vẫn xử lý phản hồi 403 từ máy chủ. Kết luận chỉ giới hạn trong phạm vi mẫu đã quan sát và không suy diễn quá mức.
- `ev-s7v2-fe-05-13`: Tài liệu của phát triển giao diện quản trị phân quyền theo vai trò: Tài liệu giữ nguyên cả hai phát biểu để người đánh giá xử lý mâu thuẫn. Trang quản trị cần ẩn thao tác theo quyền và vẫn xử lý phản hồi 403 từ máy chủ. Cách đặt tên đầu ra giúp truy vết từ yêu cầu tới kết quả kiểm tra.

Trạng thái yêu cầu bắt buộc:

- `fe-web-foundations`: `satisfied`; thông tin: ev-s7v2-fe-05-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-language`: `conflicting`; thông tin: ev-s7v2-fe-05-03, ev-s7v2-fe-05-04; Hồ sơ đồng thời có mô tả thực hành và phát biểu phủ định mâu thuẫn.
- `fe-framework`: `satisfied`; thông tin: ev-s7v2-fe-05-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-api`: `satisfied`; thông tin: ev-s7v2-fe-05-06; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-testing-workflow`: `satisfied`; thông tin: ev-s7v2-fe-05-07; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 22/30 |
| `fe-technical-specialization` | 17/25 |
| `fe-role-capability` | 13/20 |
| `projects-and-impact` | 9/15 |
| `communication-and-evidence-quality` | 7/10 |

Tổng điểm: **68/100**

Nhãn nháp: **needs_review**

Lý do vào review: conflicting-critical-evidence, lower-threshold-boundary

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-fe-06 — Junior Frontend Developer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `explicit_failure`

Tóm tắt CV: Ứng viên chuyển từ thiết kế giao diện sang lập trình và mô tả rõ phần tự triển khai. Ứng viên chuyển hướng từ lĩnh vực gần và xác nhận chưa thực hành một năng lực bắt buộc. Mục tiêu ứng tuyển là Junior Frontend Developer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-fe-06-01`: Hoàn thành chương trình định hướng Phát triển web và kỹ thuật phần mềm với đồ án tổng hợp chuyển từ thiết kế UI sang lập trình frontend. Ứng viên chuyển từ thiết kế giao diện sang lập trình và mô tả rõ phần tự triển khai. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-fe-06-02`: Trong chuyển từ thiết kế UI sang lập trình frontend, ứng viên xây giao diện semantic HTML, CSS responsive và xử lý tương tác bằng JavaScript. Ứng viên chuyển từ thiết kế giao diện sang lập trình và mô tả rõ phần tự triển khai. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-fe-06-03`: Trong chuyển từ thiết kế UI sang lập trình frontend, ứng viên dùng TypeScript strict, mô hình hóa dữ liệu và thu hẹp kiểu cho dữ liệu bên ngoài. Ứng viên chuyển từ thiết kế giao diện sang lập trình và mô tả rõ phần tự triển khai. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-fe-06-04`: Trong chuyển từ thiết kế UI sang lập trình frontend, ứng viên tách React component, quản lý state và xử lý loading, empty cùng error state. Ứng viên chuyển từ thiết kế giao diện sang lập trình và mô tả rõ phần tự triển khai. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-fe-06-05`: Trong chuyển từ thiết kế UI sang lập trình frontend, ứng viên tích hợp API có xác thực, hủy request cũ và hiển thị lỗi theo từng tình huống. Ứng viên chuyển từ thiết kế giao diện sang lập trình và mô tả rõ phần tự triển khai. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-fe-06-06`: Ứng viên xác nhận chưa từng dùng Git hoặc viết kiểm thử giao diện. Ứng viên chuyển từ thiết kế giao diện sang lập trình và mô tả rõ phần tự triển khai. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-fe-06-07`: Phạm vi kỹ thuật của chuyển từ thiết kế UI sang lập trình frontend: Phần việc hiện có chỉ hỗ trợ gián tiếp cho vai trò mục tiêu. Ứng viên chuyển từ thiết kế giao diện sang lập trình và mô tả rõ phần tự triển khai. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-fe-06-08`: Cách ra quyết định trong chuyển từ thiết kế UI sang lập trình frontend: Kết quả mong muốn được nêu nhưng chưa có phương pháp đáp ứng yêu cầu chính. Ứng viên chuyển từ thiết kế giao diện sang lập trình và mô tả rõ phần tự triển khai. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-fe-06-09`: Bàn giao cho chuyển từ thiết kế UI sang lập trình frontend: Bài tập dừng ở bản minh họa một lần và chưa có kiểm tra đầy đủ. Ứng viên chuyển từ thiết kế giao diện sang lập trình và mô tả rõ phần tự triển khai. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-fe-06-10`: Tài liệu của chuyển từ thiết kế UI sang lập trình frontend: Hồ sơ diễn đạt rõ năng lực chưa từng sử dụng để tránh suy diễn sai. Ứng viên chuyển từ thiết kế giao diện sang lập trình và mô tả rõ phần tự triển khai. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.

Trạng thái yêu cầu bắt buộc:

- `fe-web-foundations`: `satisfied`; thông tin: ev-s7v2-fe-06-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-language`: `satisfied`; thông tin: ev-s7v2-fe-06-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-framework`: `satisfied`; thông tin: ev-s7v2-fe-06-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-api`: `satisfied`; thông tin: ev-s7v2-fe-06-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-testing-workflow`: `unsatisfied`; thông tin: ev-s7v2-fe-06-06; Hồ sơ có phát biểu phủ định rõ ràng về yêu cầu này.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 10/30 |
| `fe-technical-specialization` | 12/25 |
| `fe-role-capability` | 9/20 |
| `projects-and-impact` | 5/15 |
| `communication-and-evidence-quality` | 5/10 |

Tổng điểm: **41/100**

Nhãn nháp: **reject**

Lý do vào review: không có

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-fe-07 — Junior Frontend Developer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `lower_boundary`

Tóm tắt CV: Trang tra cứu thư viện cần responsive, hỗ trợ screen reader và điều hướng lịch sử. Hồ sơ vừa đủ yêu cầu cốt lõi nhưng mức độ sâu và phạm vi dự án còn hạn chế. Mục tiêu ứng tuyển là Junior Frontend Developer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-fe-07-01`: Hoàn thành chương trình định hướng Phát triển web và kỹ thuật phần mềm với đồ án tổng hợp xây trang tra cứu thư viện trên thiết bị di động. Trang tra cứu thư viện cần responsive, hỗ trợ screen reader và điều hướng lịch sử. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-fe-07-02`: Trong xây trang tra cứu thư viện trên thiết bị di động, ứng viên xây giao diện semantic HTML, CSS responsive và xử lý tương tác bằng JavaScript. Trang tra cứu thư viện cần responsive, hỗ trợ screen reader và điều hướng lịch sử. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-fe-07-03`: Trong xây trang tra cứu thư viện trên thiết bị di động, ứng viên dùng TypeScript strict, mô hình hóa dữ liệu và thu hẹp kiểu cho dữ liệu bên ngoài. Trang tra cứu thư viện cần responsive, hỗ trợ screen reader và điều hướng lịch sử. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-fe-07-04`: Trong xây trang tra cứu thư viện trên thiết bị di động, ứng viên tách React component, quản lý state và xử lý loading, empty cùng error state. Trang tra cứu thư viện cần responsive, hỗ trợ screen reader và điều hướng lịch sử. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-fe-07-05`: Trong xây trang tra cứu thư viện trên thiết bị di động, ứng viên tích hợp API có xác thực, hủy request cũ và hiển thị lỗi theo từng tình huống. Trang tra cứu thư viện cần responsive, hỗ trợ screen reader và điều hướng lịch sử. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-fe-07-06`: Trong xây trang tra cứu thư viện trên thiết bị di động, ứng viên dùng Git theo pull request và viết Testing Library cho hành vi người dùng chính. Trang tra cứu thư viện cần responsive, hỗ trợ screen reader và điều hướng lịch sử. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-fe-07-07`: Ở phần mở rộng của xây trang tra cứu thư viện trên thiết bị di động, ứng viên áp dụng Có Next.js hoặc rendering phía server. và ghi lại kết quả thử nghiệm riêng. Trang tra cứu thư viện cần responsive, hỗ trợ screen reader và điều hướng lịch sử. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-fe-07-08`: Phạm vi kỹ thuật của xây trang tra cứu thư viện trên thiết bị di động: Luồng cơ bản hoạt động nhưng mới kiểm tra một số trường hợp phổ biến. Trang tra cứu thư viện cần responsive, hỗ trợ screen reader và điều hướng lịch sử. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-fe-07-09`: Cách ra quyết định trong xây trang tra cứu thư viện trên thiết bị di động: Mục tiêu và kết quả được nêu, phần đối chiếu độc lập còn thiếu. Trang tra cứu thư viện cần responsive, hỗ trợ screen reader và điều hướng lịch sử. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-fe-07-10`: Bàn giao cho xây trang tra cứu thư viện trên thiết bị di động: Đầu ra chạy lại được trên một bộ mẫu cố định. Trang tra cứu thư viện cần responsive, hỗ trợ screen reader và điều hướng lịch sử. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-fe-07-11`: Tài liệu của xây trang tra cứu thư viện trên thiết bị di động: README rõ lệnh chính nhưng phần quyết định kỹ thuật còn ngắn. Trang tra cứu thư viện cần responsive, hỗ trợ screen reader và điều hướng lịch sử. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.

Trạng thái yêu cầu bắt buộc:

- `fe-web-foundations`: `satisfied`; thông tin: ev-s7v2-fe-07-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-language`: `satisfied`; thông tin: ev-s7v2-fe-07-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-framework`: `satisfied`; thông tin: ev-s7v2-fe-07-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-api`: `satisfied`; thông tin: ev-s7v2-fe-07-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-testing-workflow`: `satisfied`; thông tin: ev-s7v2-fe-07-06; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 27/30 |
| `fe-technical-specialization` | 13/25 |
| `fe-role-capability` | 10/20 |
| `projects-and-impact` | 8/15 |
| `communication-and-evidence-quality` | 9/10 |

Tổng điểm: **67/100**

Nhãn nháp: **needs_review**

Lý do vào review: lower-threshold-boundary

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-fe-08 — Junior Frontend Developer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `upper_boundary`

Tóm tắt CV: Ứng dụng thói quen cần optimistic update cùng cơ chế hoàn tác khi đồng bộ thất bại. Hồ sơ khá tốt và nằm gần ngưỡng Pass nên cần kiểm tra tính ổn định của quyết định. Mục tiêu ứng tuyển là Junior Frontend Developer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-fe-08-01`: Hoàn thành chương trình định hướng Phát triển web và kỹ thuật phần mềm với đồ án tổng hợp tạo ứng dụng theo dõi thói quen có đồng bộ API. Ứng dụng thói quen cần optimistic update cùng cơ chế hoàn tác khi đồng bộ thất bại. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-fe-08-02`: Trong tạo ứng dụng theo dõi thói quen có đồng bộ API, ứng viên xây giao diện semantic HTML, CSS responsive và xử lý tương tác bằng JavaScript. Ứng dụng thói quen cần optimistic update cùng cơ chế hoàn tác khi đồng bộ thất bại. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-fe-08-03`: Trong tạo ứng dụng theo dõi thói quen có đồng bộ API, ứng viên dùng TypeScript strict, mô hình hóa dữ liệu và thu hẹp kiểu cho dữ liệu bên ngoài. Ứng dụng thói quen cần optimistic update cùng cơ chế hoàn tác khi đồng bộ thất bại. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-fe-08-04`: Trong tạo ứng dụng theo dõi thói quen có đồng bộ API, ứng viên tách React component, quản lý state và xử lý loading, empty cùng error state. Ứng dụng thói quen cần optimistic update cùng cơ chế hoàn tác khi đồng bộ thất bại. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-fe-08-05`: Trong tạo ứng dụng theo dõi thói quen có đồng bộ API, ứng viên tích hợp API có xác thực, hủy request cũ và hiển thị lỗi theo từng tình huống. Ứng dụng thói quen cần optimistic update cùng cơ chế hoàn tác khi đồng bộ thất bại. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-fe-08-06`: Trong tạo ứng dụng theo dõi thói quen có đồng bộ API, ứng viên dùng Git theo pull request và viết Testing Library cho hành vi người dùng chính. Ứng dụng thói quen cần optimistic update cùng cơ chế hoàn tác khi đồng bộ thất bại. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-fe-08-07`: Ở phần mở rộng của tạo ứng dụng theo dõi thói quen có đồng bộ API, ứng viên áp dụng Có Next.js hoặc rendering phía server. và ghi lại kết quả thử nghiệm riêng. Ứng dụng thói quen cần optimistic update cùng cơ chế hoàn tác khi đồng bộ thất bại. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-fe-08-08`: Ở phần mở rộng của tạo ứng dụng theo dõi thói quen có đồng bộ API, ứng viên áp dụng Có web performance và accessibility. và ghi lại kết quả thử nghiệm riêng. Ứng dụng thói quen cần optimistic update cùng cơ chế hoàn tác khi đồng bộ thất bại. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-fe-08-09`: Phạm vi kỹ thuật của tạo ứng dụng theo dõi thói quen có đồng bộ API: Luồng chính và các lỗi thường gặp được xử lý bằng kiểm tra có thể chạy lại. Ứng dụng thói quen cần optimistic update cùng cơ chế hoàn tác khi đồng bộ thất bại. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-fe-08-10`: Cách ra quyết định trong tạo ứng dụng theo dõi thói quen có đồng bộ API: Lựa chọn kỹ thuật có lý do và ghi nhận một giới hạn đáng chú ý. Ứng dụng thói quen cần optimistic update cùng cơ chế hoàn tác khi đồng bộ thất bại. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-fe-08-11`: Bàn giao cho tạo ứng dụng theo dõi thói quen có đồng bộ API: Có dữ liệu mẫu, kết quả đối chiếu và hướng dẫn tái tạo. Ứng dụng thói quen cần optimistic update cùng cơ chế hoàn tác khi đồng bộ thất bại. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.
- `ev-s7v2-fe-08-12`: Tài liệu của tạo ứng dụng theo dõi thói quen có đồng bộ API: Tài liệu rõ cách chạy nhưng phần giải thích một số quyết định còn cô đọng. Ứng dụng thói quen cần optimistic update cùng cơ chế hoàn tác khi đồng bộ thất bại. Kết luận chỉ giới hạn trong phạm vi mẫu đã quan sát và không suy diễn quá mức.

Trạng thái yêu cầu bắt buộc:

- `fe-web-foundations`: `satisfied`; thông tin: ev-s7v2-fe-08-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-language`: `satisfied`; thông tin: ev-s7v2-fe-08-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-framework`: `satisfied`; thông tin: ev-s7v2-fe-08-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-api`: `satisfied`; thông tin: ev-s7v2-fe-08-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-testing-workflow`: `satisfied`; thông tin: ev-s7v2-fe-08-06; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `fe-technical-specialization` | 18/25 |
| `fe-role-capability` | 15/20 |
| `projects-and-impact` | 12/15 |
| `communication-and-evidence-quality` | 7/10 |

Tổng điểm: **82/100**

Nhãn nháp: **needs_review**

Lý do vào review: upper-threshold-boundary

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-fe-09 — Junior Frontend Developer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `transferable`

Tóm tắt CV: Ứng viên chuyển từ Vue sang React và so sánh cách quản lý state trong hai hệ sinh thái. Ứng viên chuyển từ lĩnh vực gần và chứng minh được năng lực tương đương qua dự án mới. Mục tiêu ứng tuyển là Junior Frontend Developer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-fe-09-01`: Hoàn thành chương trình định hướng Phát triển web và kỹ thuật phần mềm với đồ án tổng hợp chuyển kinh nghiệm Vue sang dự án React TypeScript. Ứng viên chuyển từ Vue sang React và so sánh cách quản lý state trong hai hệ sinh thái. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-fe-09-02`: Trong chuyển kinh nghiệm Vue sang dự án React TypeScript, ứng viên xây giao diện semantic HTML, CSS responsive và xử lý tương tác bằng JavaScript. Ứng viên chuyển từ Vue sang React và so sánh cách quản lý state trong hai hệ sinh thái. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-fe-09-03`: Trong chuyển kinh nghiệm Vue sang dự án React TypeScript, ứng viên dùng TypeScript strict, mô hình hóa dữ liệu và thu hẹp kiểu cho dữ liệu bên ngoài. Ứng viên chuyển từ Vue sang React và so sánh cách quản lý state trong hai hệ sinh thái. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-fe-09-04`: Trong chuyển kinh nghiệm Vue sang dự án React TypeScript, ứng viên tách React component, quản lý state và xử lý loading, empty cùng error state. Ứng viên chuyển từ Vue sang React và so sánh cách quản lý state trong hai hệ sinh thái. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-fe-09-05`: Trong chuyển kinh nghiệm Vue sang dự án React TypeScript, ứng viên tích hợp API có xác thực, hủy request cũ và hiển thị lỗi theo từng tình huống. Ứng viên chuyển từ Vue sang React và so sánh cách quản lý state trong hai hệ sinh thái. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-fe-09-06`: Trong chuyển kinh nghiệm Vue sang dự án React TypeScript, ứng viên dùng Git theo pull request và viết Testing Library cho hành vi người dùng chính. Ứng viên chuyển từ Vue sang React và so sánh cách quản lý state trong hai hệ sinh thái. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-fe-09-07`: Ở phần mở rộng của chuyển kinh nghiệm Vue sang dự án React TypeScript, ứng viên áp dụng Có Next.js hoặc rendering phía server. và ghi lại kết quả thử nghiệm riêng. Ứng viên chuyển từ Vue sang React và so sánh cách quản lý state trong hai hệ sinh thái. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-fe-09-08`: Phạm vi kỹ thuật của chuyển kinh nghiệm Vue sang dự án React TypeScript: Kiến thức nền từ lĩnh vực gần được áp dụng vào một sản phẩm đúng vai trò mục tiêu. Ứng viên chuyển từ Vue sang React và so sánh cách quản lý state trong hai hệ sinh thái. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-fe-09-09`: Cách ra quyết định trong chuyển kinh nghiệm Vue sang dự án React TypeScript: Hồ sơ phân biệt rõ phần kinh nghiệm chuyển đổi và phần mới học. Ứng viên chuyển từ Vue sang React và so sánh cách quản lý state trong hai hệ sinh thái. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-fe-09-10`: Bàn giao cho chuyển kinh nghiệm Vue sang dự án React TypeScript: Prototype chạy được, có kiểm tra và đầu ra đo được nhưng chưa qua môi trường thực tập. Ứng viên chuyển từ Vue sang React và so sánh cách quản lý state trong hai hệ sinh thái. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-fe-09-11`: Tài liệu của chuyển kinh nghiệm Vue sang dự án React TypeScript: Tài liệu nêu rõ phạm vi kinh nghiệm trực tiếp và kinh nghiệm tương đương. Ứng viên chuyển từ Vue sang React và so sánh cách quản lý state trong hai hệ sinh thái. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.

Trạng thái yêu cầu bắt buộc:

- `fe-web-foundations`: `satisfied`; thông tin: ev-s7v2-fe-09-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-language`: `satisfied`; thông tin: ev-s7v2-fe-09-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-framework`: `satisfied`; thông tin: ev-s7v2-fe-09-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-api`: `satisfied`; thông tin: ev-s7v2-fe-09-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `fe-testing-workflow`: `satisfied`; thông tin: ev-s7v2-fe-09-06; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `fe-technical-specialization` | 16/25 |
| `fe-role-capability` | 14/20 |
| `projects-and-impact` | 10/15 |
| `communication-and-evidence-quality` | 9/10 |

Tổng điểm: **79/100**

Nhãn nháp: **waitlist**

Lý do vào review: không có

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-fe-10 — Junior Frontend Developer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `hard_negative`

Tóm tắt CV: Hồ sơ chỉ nêu tên thư viện giao diện mà chưa có luồng người dùng hoàn chỉnh. Hồ sơ chủ yếu liệt kê khóa học và công cụ nhưng không mô tả nhiệm vụ hay sản phẩm đã làm. Mục tiêu ứng tuyển là Junior Frontend Developer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-fe-10-01`: Hoàn thành chương trình định hướng Phát triển web và kỹ thuật phần mềm với đồ án tổng hợp liệt kê thư viện frontend từ các bài thực hành ngắn. Hồ sơ chỉ nêu tên thư viện giao diện mà chưa có luồng người dùng hoàn chỉnh. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-fe-10-02`: Đã hoàn thành bài học giới thiệu về HTML CSS JavaScript và tự ghi tên công cụ trong danh sách kỹ năng. Hồ sơ chỉ nêu tên thư viện giao diện mà chưa có luồng người dùng hoàn chỉnh. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-fe-10-03`: Đã hoàn thành bài học giới thiệu về JavaScript hoặc TypeScript và tự ghi tên công cụ trong danh sách kỹ năng. Hồ sơ chỉ nêu tên thư viện giao diện mà chưa có luồng người dùng hoàn chỉnh. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-fe-10-04`: Đã hoàn thành bài học giới thiệu về React và tự ghi tên công cụ trong danh sách kỹ năng. Hồ sơ chỉ nêu tên thư viện giao diện mà chưa có luồng người dùng hoàn chỉnh. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-fe-10-05`: Đã hoàn thành bài học giới thiệu về Tích hợp API và tự ghi tên công cụ trong danh sách kỹ năng. Hồ sơ chỉ nêu tên thư viện giao diện mà chưa có luồng người dùng hoàn chỉnh. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-fe-10-06`: Đã hoàn thành bài học giới thiệu về Git và kiểm thử giao diện và tự ghi tên công cụ trong danh sách kỹ năng. Hồ sơ chỉ nêu tên thư viện giao diện mà chưa có luồng người dùng hoàn chỉnh. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-fe-10-07`: Ở phần mở rộng của liệt kê thư viện frontend từ các bài thực hành ngắn, ứng viên áp dụng Có Next.js hoặc rendering phía server. và ghi lại kết quả thử nghiệm riêng. Hồ sơ chỉ nêu tên thư viện giao diện mà chưa có luồng người dùng hoàn chỉnh. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-fe-10-08`: Ở phần mở rộng của liệt kê thư viện frontend từ các bài thực hành ngắn, ứng viên áp dụng Có web performance và accessibility. và ghi lại kết quả thử nghiệm riêng. Hồ sơ chỉ nêu tên thư viện giao diện mà chưa có luồng người dùng hoàn chỉnh. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.

Trạng thái yêu cầu bắt buộc:

- `fe-web-foundations`: `missing`; thông tin: ev-s7v2-fe-10-02; Hồ sơ không đề cập đủ thông tin để xác nhận yêu cầu này.
- `fe-language`: `missing`; thông tin: ev-s7v2-fe-10-03; Hồ sơ không đề cập đủ thông tin để xác nhận yêu cầu này.
- `fe-framework`: `missing`; thông tin: ev-s7v2-fe-10-04; Hồ sơ không đề cập đủ thông tin để xác nhận yêu cầu này.
- `fe-api`: `missing`; thông tin: ev-s7v2-fe-10-05; Hồ sơ không đề cập đủ thông tin để xác nhận yêu cầu này.
- `fe-testing-workflow`: `missing`; thông tin: ev-s7v2-fe-10-06; Hồ sơ không đề cập đủ thông tin để xác nhận yêu cầu này.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 14/30 |
| `fe-technical-specialization` | 9/25 |
| `fe-role-capability` | 6/20 |
| `projects-and-impact` | 3/15 |
| `communication-and-evidence-quality` | 4/10 |

Tổng điểm: **36/100**

Nhãn nháp: **needs_review**

Lý do vào review: missing-critical-evidence, low-score-without-explicit-critical-unsatisfied

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-qa-01 — Junior QA Engineer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `strong`

Tóm tắt CV: Luồng thanh toán cần ma trận kiểm thử cho retry, timeout và sự kiện gửi trùng. Hồ sơ trình bày một sản phẩm hoàn chỉnh, có số liệu đối chiếu và tài liệu tái tạo. Mục tiêu ứng tuyển là Junior QA Engineer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-qa-01-01`: Hoàn thành chương trình định hướng Đảm bảo chất lượng phần mềm với đồ án tổng hợp kiểm thử hệ thống đặt lịch có giới hạn khung giờ. Luồng thanh toán cần ma trận kiểm thử cho retry, timeout và sự kiện gửi trùng. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-qa-01-02`: Trong kiểm thử hệ thống đặt lịch có giới hạn khung giờ, ứng viên phân biệt test level, test type và áp dụng quy trình lỗi từ phát hiện đến xác nhận sửa. Luồng thanh toán cần ma trận kiểm thử cho retry, timeout và sự kiện gửi trùng. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-qa-01-03`: Trong kiểm thử hệ thống đặt lịch có giới hạn khung giờ, ứng viên thiết kế test case bằng phân vùng tương đương, giá trị biên và bảng quyết định. Luồng thanh toán cần ma trận kiểm thử cho retry, timeout và sự kiện gửi trùng. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-qa-01-04`: Trong kiểm thử hệ thống đặt lịch có giới hạn khung giờ, ứng viên dùng Postman kiểm tra status, schema, authentication và chuỗi request có biến môi trường. Luồng thanh toán cần ma trận kiểm thử cho retry, timeout và sự kiện gửi trùng. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-qa-01-05`: Trong kiểm thử hệ thống đặt lịch có giới hạn khung giờ, ứng viên viết SQL đối chiếu dữ liệu trước và sau thao tác, gồm bản ghi thiếu hoặc trùng. Luồng thanh toán cần ma trận kiểm thử cho retry, timeout và sự kiện gửi trùng. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-qa-01-06`: Trong kiểm thử hệ thống đặt lịch có giới hạn khung giờ, ứng viên tự động hóa luồng regression chính, có assertion ổn định và báo cáo kết quả. Luồng thanh toán cần ma trận kiểm thử cho retry, timeout và sự kiện gửi trùng. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-qa-01-07`: Ở phần mở rộng của kiểm thử hệ thống đặt lịch có giới hạn khung giờ, ứng viên áp dụng Có tích hợp test trong CI. và ghi lại kết quả thử nghiệm riêng. Luồng thanh toán cần ma trận kiểm thử cho retry, timeout và sự kiện gửi trùng. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-qa-01-08`: Ở phần mở rộng của kiểm thử hệ thống đặt lịch có giới hạn khung giờ, ứng viên áp dụng Có performance hoặc security testing cơ bản. và ghi lại kết quả thử nghiệm riêng. Luồng thanh toán cần ma trận kiểm thử cho retry, timeout và sự kiện gửi trùng. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-qa-01-09`: Phạm vi kỹ thuật của kiểm thử hệ thống đặt lịch có giới hạn khung giờ: Luồng chính và các trường hợp lỗi được kiểm tra trên nhiều bộ dữ liệu hoặc tình huống đầu vào. Luồng thanh toán cần ma trận kiểm thử cho retry, timeout và sự kiện gửi trùng. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-qa-01-10`: Cách ra quyết định trong kiểm thử hệ thống đặt lịch có giới hạn khung giờ: Hai phương án được so sánh bằng tiêu chí đo được trước khi chọn cách triển khai. Luồng thanh toán cần ma trận kiểm thử cho retry, timeout và sự kiện gửi trùng. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-qa-01-11`: Bàn giao cho kiểm thử hệ thống đặt lịch có giới hạn khung giờ: Kết quả có chỉ số trước và sau, bộ kiểm tra hồi quy và hướng dẫn chạy độc lập. Luồng thanh toán cần ma trận kiểm thử cho retry, timeout và sự kiện gửi trùng. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.
- `ev-s7v2-qa-01-12`: Tài liệu của kiểm thử hệ thống đặt lịch có giới hạn khung giờ: Tài liệu nêu rõ phạm vi cá nhân, giả định, giới hạn và quyết định kỹ thuật. Luồng thanh toán cần ma trận kiểm thử cho retry, timeout và sự kiện gửi trùng. Kết luận chỉ giới hạn trong phạm vi mẫu đã quan sát và không suy diễn quá mức.

Trạng thái yêu cầu bắt buộc:

- `qa-testing-foundations`: `satisfied`; thông tin: ev-s7v2-qa-01-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-test-cases`: `satisfied`; thông tin: ev-s7v2-qa-01-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-api-testing`: `satisfied`; thông tin: ev-s7v2-qa-01-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-data-check`: `satisfied`; thông tin: ev-s7v2-qa-01-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-automation-foundation`: `satisfied`; thông tin: ev-s7v2-qa-01-06; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `qa-technical-specialization` | 24/25 |
| `qa-role-capability` | 18/20 |
| `projects-and-impact` | 14/15 |
| `communication-and-evidence-quality` | 9/10 |

Tổng điểm: **95/100**

Nhãn nháp: **pass**

Lý do vào review: không có

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-qa-02 — Junior QA Engineer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `solid`

Tóm tắt CV: Ứng dụng đặt lịch cần kiểm tra xung đột thời gian trên trình duyệt và múi giờ khác nhau. Hồ sơ có dự án junior hoàn chỉnh, thông tin nhất quán và đầu ra có thể kiểm tra. Mục tiêu ứng tuyển là Junior QA Engineer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-qa-02-01`: Hoàn thành chương trình định hướng Đảm bảo chất lượng phần mềm với đồ án tổng hợp kiểm thử quy trình checkout với nhiều phương thức thanh toán. Ứng dụng đặt lịch cần kiểm tra xung đột thời gian trên trình duyệt và múi giờ khác nhau. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-qa-02-02`: Trong kiểm thử quy trình checkout với nhiều phương thức thanh toán, ứng viên phân biệt test level, test type và áp dụng quy trình lỗi từ phát hiện đến xác nhận sửa. Ứng dụng đặt lịch cần kiểm tra xung đột thời gian trên trình duyệt và múi giờ khác nhau. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-qa-02-03`: Trong kiểm thử quy trình checkout với nhiều phương thức thanh toán, ứng viên thiết kế test case bằng phân vùng tương đương, giá trị biên và bảng quyết định. Ứng dụng đặt lịch cần kiểm tra xung đột thời gian trên trình duyệt và múi giờ khác nhau. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-qa-02-04`: Trong kiểm thử quy trình checkout với nhiều phương thức thanh toán, ứng viên dùng Postman kiểm tra status, schema, authentication và chuỗi request có biến môi trường. Ứng dụng đặt lịch cần kiểm tra xung đột thời gian trên trình duyệt và múi giờ khác nhau. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-qa-02-05`: Trong kiểm thử quy trình checkout với nhiều phương thức thanh toán, ứng viên viết SQL đối chiếu dữ liệu trước và sau thao tác, gồm bản ghi thiếu hoặc trùng. Ứng dụng đặt lịch cần kiểm tra xung đột thời gian trên trình duyệt và múi giờ khác nhau. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-qa-02-06`: Trong kiểm thử quy trình checkout với nhiều phương thức thanh toán, ứng viên tự động hóa luồng regression chính, có assertion ổn định và báo cáo kết quả. Ứng dụng đặt lịch cần kiểm tra xung đột thời gian trên trình duyệt và múi giờ khác nhau. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-qa-02-07`: Ở phần mở rộng của kiểm thử quy trình checkout với nhiều phương thức thanh toán, ứng viên áp dụng Có tích hợp test trong CI. và ghi lại kết quả thử nghiệm riêng. Ứng dụng đặt lịch cần kiểm tra xung đột thời gian trên trình duyệt và múi giờ khác nhau. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-qa-02-08`: Ở phần mở rộng của kiểm thử quy trình checkout với nhiều phương thức thanh toán, ứng viên áp dụng Có performance hoặc security testing cơ bản. và ghi lại kết quả thử nghiệm riêng. Ứng dụng đặt lịch cần kiểm tra xung đột thời gian trên trình duyệt và múi giờ khác nhau. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-qa-02-09`: Phạm vi kỹ thuật của kiểm thử quy trình checkout với nhiều phương thức thanh toán: Luồng nghiệp vụ chính và hai trường hợp lỗi phổ biến được triển khai và kiểm thử. Ứng dụng đặt lịch cần kiểm tra xung đột thời gian trên trình duyệt và múi giờ khác nhau. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-qa-02-10`: Cách ra quyết định trong kiểm thử quy trình checkout với nhiều phương thức thanh toán: Mục tiêu, giả định và cách đối chiếu kết quả được trình bày rõ. Ứng dụng đặt lịch cần kiểm tra xung đột thời gian trên trình duyệt và múi giờ khác nhau. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-qa-02-11`: Bàn giao cho kiểm thử quy trình checkout với nhiều phương thức thanh toán: Sản phẩm có dữ liệu mẫu, lệnh chạy và kết quả kiểm tra nhất quán. Ứng dụng đặt lịch cần kiểm tra xung đột thời gian trên trình duyệt và múi giờ khác nhau. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.
- `ev-s7v2-qa-02-12`: Tài liệu của kiểm thử quy trình checkout với nhiều phương thức thanh toán: README mô tả phần việc cá nhân và các hạn chế chính. Ứng dụng đặt lịch cần kiểm tra xung đột thời gian trên trình duyệt và múi giờ khác nhau. Kết luận chỉ giới hạn trong phạm vi mẫu đã quan sát và không suy diễn quá mức.

Trạng thái yêu cầu bắt buộc:

- `qa-testing-foundations`: `satisfied`; thông tin: ev-s7v2-qa-02-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-test-cases`: `satisfied`; thông tin: ev-s7v2-qa-02-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-api-testing`: `satisfied`; thông tin: ev-s7v2-qa-02-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-data-check`: `satisfied`; thông tin: ev-s7v2-qa-02-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-automation-foundation`: `satisfied`; thông tin: ev-s7v2-qa-02-06; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `qa-technical-specialization` | 22/25 |
| `qa-role-capability` | 17/20 |
| `projects-and-impact` | 12/15 |
| `communication-and-evidence-quality` | 8/10 |

Tổng điểm: **89/100**

Nhãn nháp: **pass**

Lý do vào review: không có

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-qa-03 — Junior QA Engineer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `moderate`

Tóm tắt CV: API kho cần đối chiếu contract, dữ liệu biên và transaction chạy đồng thời. Hồ sơ đáp ứng phần cốt lõi nhưng dự án mới giới hạn ở một luồng nghiệp vụ. Mục tiêu ứng tuyển là Junior QA Engineer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-qa-03-01`: Hoàn thành chương trình định hướng Đảm bảo chất lượng phần mềm với đồ án tổng hợp đánh giá API quản lý tài khoản và phân quyền. API kho cần đối chiếu contract, dữ liệu biên và transaction chạy đồng thời. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-qa-03-02`: Trong đánh giá API quản lý tài khoản và phân quyền, ứng viên phân biệt test level, test type và áp dụng quy trình lỗi từ phát hiện đến xác nhận sửa. API kho cần đối chiếu contract, dữ liệu biên và transaction chạy đồng thời. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-qa-03-03`: Trong đánh giá API quản lý tài khoản và phân quyền, ứng viên thiết kế test case bằng phân vùng tương đương, giá trị biên và bảng quyết định. API kho cần đối chiếu contract, dữ liệu biên và transaction chạy đồng thời. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-qa-03-04`: Trong đánh giá API quản lý tài khoản và phân quyền, ứng viên dùng Postman kiểm tra status, schema, authentication và chuỗi request có biến môi trường. API kho cần đối chiếu contract, dữ liệu biên và transaction chạy đồng thời. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-qa-03-05`: Trong đánh giá API quản lý tài khoản và phân quyền, ứng viên viết SQL đối chiếu dữ liệu trước và sau thao tác, gồm bản ghi thiếu hoặc trùng. API kho cần đối chiếu contract, dữ liệu biên và transaction chạy đồng thời. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-qa-03-06`: Trong đánh giá API quản lý tài khoản và phân quyền, ứng viên tự động hóa luồng regression chính, có assertion ổn định và báo cáo kết quả. API kho cần đối chiếu contract, dữ liệu biên và transaction chạy đồng thời. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-qa-03-07`: Ở phần mở rộng của đánh giá API quản lý tài khoản và phân quyền, ứng viên áp dụng Có tích hợp test trong CI. và ghi lại kết quả thử nghiệm riêng. API kho cần đối chiếu contract, dữ liệu biên và transaction chạy đồng thời. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-qa-03-08`: Phạm vi kỹ thuật của đánh giá API quản lý tài khoản và phân quyền: Một luồng chính được hoàn thành trên tập dữ liệu hoặc chức năng có phạm vi vừa phải. API kho cần đối chiếu contract, dữ liệu biên và transaction chạy đồng thời. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-qa-03-09`: Cách ra quyết định trong đánh giá API quản lý tài khoản và phân quyền: Phương pháp được giải thích nhưng phần so sánh phương án còn ngắn. API kho cần đối chiếu contract, dữ liệu biên và transaction chạy đồng thời. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-qa-03-10`: Bàn giao cho đánh giá API quản lý tài khoản và phân quyền: Đầu ra chạy lại được cục bộ và có một số kiểm tra cơ bản. API kho cần đối chiếu contract, dữ liệu biên và transaction chạy đồng thời. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-qa-03-11`: Tài liệu của đánh giá API quản lý tài khoản và phân quyền: Tài liệu đủ để chạy thử nhưng chưa mô tả đầy đủ rủi ro vận hành. API kho cần đối chiếu contract, dữ liệu biên và transaction chạy đồng thời. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.

Trạng thái yêu cầu bắt buộc:

- `qa-testing-foundations`: `satisfied`; thông tin: ev-s7v2-qa-03-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-test-cases`: `satisfied`; thông tin: ev-s7v2-qa-03-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-api-testing`: `satisfied`; thông tin: ev-s7v2-qa-03-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-data-check`: `satisfied`; thông tin: ev-s7v2-qa-03-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-automation-foundation`: `satisfied`; thông tin: ev-s7v2-qa-03-06; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `qa-technical-specialization` | 17/25 |
| `qa-role-capability` | 14/20 |
| `projects-and-impact` | 9/15 |
| `communication-and-evidence-quality` | 8/10 |

Tổng điểm: **78/100**

Nhãn nháp: **waitlist**

Lý do vào review: không có

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-qa-04 — Junior QA Engineer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `missing_critical`

Tóm tắt CV: Ứng dụng học tập cần truy vết lỗi tiến trình bài học qua nhiều phiên đăng nhập. Hồ sơ mô tả một số phần việc liên quan nhưng không đề cập đầy đủ toàn bộ năng lực cốt lõi. Mục tiêu ứng tuyển là Junior QA Engineer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-qa-04-01`: Hoàn thành chương trình định hướng Đảm bảo chất lượng phần mềm với đồ án tổng hợp kiểm thử dữ liệu đồng bộ giữa đơn hàng và kho. Ứng dụng học tập cần truy vết lỗi tiến trình bài học qua nhiều phiên đăng nhập. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-qa-04-02`: Trong kiểm thử dữ liệu đồng bộ giữa đơn hàng và kho, ứng viên phân biệt test level, test type và áp dụng quy trình lỗi từ phát hiện đến xác nhận sửa. Ứng dụng học tập cần truy vết lỗi tiến trình bài học qua nhiều phiên đăng nhập. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-qa-04-03`: Trong kiểm thử dữ liệu đồng bộ giữa đơn hàng và kho, ứng viên thiết kế test case bằng phân vùng tương đương, giá trị biên và bảng quyết định. Ứng dụng học tập cần truy vết lỗi tiến trình bài học qua nhiều phiên đăng nhập. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-qa-04-04`: Trong kiểm thử dữ liệu đồng bộ giữa đơn hàng và kho, ứng viên dùng Postman kiểm tra status, schema, authentication và chuỗi request có biến môi trường. Ứng dụng học tập cần truy vết lỗi tiến trình bài học qua nhiều phiên đăng nhập. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-qa-04-05`: Trong kiểm thử dữ liệu đồng bộ giữa đơn hàng và kho, ứng viên viết SQL đối chiếu dữ liệu trước và sau thao tác, gồm bản ghi thiếu hoặc trùng. Ứng dụng học tập cần truy vết lỗi tiến trình bài học qua nhiều phiên đăng nhập. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-qa-04-06`: Ở phần mở rộng của kiểm thử dữ liệu đồng bộ giữa đơn hàng và kho, ứng viên áp dụng Có performance hoặc security testing cơ bản. và ghi lại kết quả thử nghiệm riêng. Ứng dụng học tập cần truy vết lỗi tiến trình bài học qua nhiều phiên đăng nhập. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-qa-04-07`: Phạm vi kỹ thuật của kiểm thử dữ liệu đồng bộ giữa đơn hàng và kho: Các phần được nêu có thao tác kỹ thuật và kiểm tra đầu vào cơ bản. Ứng dụng học tập cần truy vết lỗi tiến trình bài học qua nhiều phiên đăng nhập. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-qa-04-08`: Cách ra quyết định trong kiểm thử dữ liệu đồng bộ giữa đơn hàng và kho: Ứng viên giải thích mục tiêu và một giới hạn của giải pháp. Ứng dụng học tập cần truy vết lỗi tiến trình bài học qua nhiều phiên đăng nhập. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-qa-04-09`: Bàn giao cho kiểm thử dữ liệu đồng bộ giữa đơn hàng và kho: Có bản chạy thử cùng dữ liệu hoặc tình huống minh họa. Ứng dụng học tập cần truy vết lỗi tiến trình bài học qua nhiều phiên đăng nhập. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-qa-04-10`: Tài liệu của kiểm thử dữ liệu đồng bộ giữa đơn hàng và kho: Phạm vi đã làm được ghi rõ, không suy diễn cho phần chưa được mô tả. Ứng dụng học tập cần truy vết lỗi tiến trình bài học qua nhiều phiên đăng nhập. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.

Trạng thái yêu cầu bắt buộc:

- `qa-testing-foundations`: `satisfied`; thông tin: ev-s7v2-qa-04-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-test-cases`: `satisfied`; thông tin: ev-s7v2-qa-04-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-api-testing`: `satisfied`; thông tin: ev-s7v2-qa-04-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-data-check`: `satisfied`; thông tin: ev-s7v2-qa-04-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-automation-foundation`: `missing`; thông tin: không có thông tin liên kết; Hồ sơ không đề cập đủ thông tin để xác nhận yêu cầu này.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 20/30 |
| `qa-technical-specialization` | 17/25 |
| `qa-role-capability` | 13/20 |
| `projects-and-impact` | 8/15 |
| `communication-and-evidence-quality` | 6/10 |

Tổng điểm: **64/100**

Nhãn nháp: **needs_review**

Lý do vào review: missing-critical-evidence, low-score-without-explicit-critical-unsatisfied

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-qa-05 — Junior QA Engineer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `conflicting_critical`

Tóm tắt CV: Cổng quản trị cần kiểm tra quyền truy cập và lưu audit trail cho thao tác nhạy cảm. Hồ sơ kết hợp mô tả dự án và bản tự đánh giá có một điểm chưa nhất quán. Mục tiêu ứng tuyển là Junior QA Engineer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-qa-05-01`: Hoàn thành chương trình định hướng Đảm bảo chất lượng phần mềm với đồ án tổng hợp xây regression cho cổng đăng ký khóa học. Cổng quản trị cần kiểm tra quyền truy cập và lưu audit trail cho thao tác nhạy cảm. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-qa-05-02`: Trong xây regression cho cổng đăng ký khóa học, ứng viên phân biệt test level, test type và áp dụng quy trình lỗi từ phát hiện đến xác nhận sửa. Cổng quản trị cần kiểm tra quyền truy cập và lưu audit trail cho thao tác nhạy cảm. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-qa-05-03`: Trong xây regression cho cổng đăng ký khóa học, ứng viên thiết kế test case bằng phân vùng tương đương, giá trị biên và bảng quyết định. Cổng quản trị cần kiểm tra quyền truy cập và lưu audit trail cho thao tác nhạy cảm. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-qa-05-04`: Ứng viên xác nhận chưa từng viết test case từ yêu cầu nghiệp vụ. Cổng quản trị cần kiểm tra quyền truy cập và lưu audit trail cho thao tác nhạy cảm. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-qa-05-05`: Trong xây regression cho cổng đăng ký khóa học, ứng viên dùng Postman kiểm tra status, schema, authentication và chuỗi request có biến môi trường. Cổng quản trị cần kiểm tra quyền truy cập và lưu audit trail cho thao tác nhạy cảm. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-qa-05-06`: Trong xây regression cho cổng đăng ký khóa học, ứng viên viết SQL đối chiếu dữ liệu trước và sau thao tác, gồm bản ghi thiếu hoặc trùng. Cổng quản trị cần kiểm tra quyền truy cập và lưu audit trail cho thao tác nhạy cảm. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-qa-05-07`: Trong xây regression cho cổng đăng ký khóa học, ứng viên tự động hóa luồng regression chính, có assertion ổn định và báo cáo kết quả. Cổng quản trị cần kiểm tra quyền truy cập và lưu audit trail cho thao tác nhạy cảm. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-qa-05-08`: Ở phần mở rộng của xây regression cho cổng đăng ký khóa học, ứng viên áp dụng Có tích hợp test trong CI. và ghi lại kết quả thử nghiệm riêng. Cổng quản trị cần kiểm tra quyền truy cập và lưu audit trail cho thao tác nhạy cảm. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-qa-05-09`: Ở phần mở rộng của xây regression cho cổng đăng ký khóa học, ứng viên áp dụng Có performance hoặc security testing cơ bản. và ghi lại kết quả thử nghiệm riêng. Cổng quản trị cần kiểm tra quyền truy cập và lưu audit trail cho thao tác nhạy cảm. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-qa-05-10`: Phạm vi kỹ thuật của xây regression cho cổng đăng ký khóa học: Một luồng kỹ thuật hoàn chỉnh được mô tả cùng cách kiểm tra sai lệch. Cổng quản trị cần kiểm tra quyền truy cập và lưu audit trail cho thao tác nhạy cảm. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-qa-05-11`: Cách ra quyết định trong xây regression cho cổng đăng ký khóa học: Mục tiêu và kết quả được nêu nhưng một phát biểu năng lực cần xác minh lại. Cổng quản trị cần kiểm tra quyền truy cập và lưu audit trail cho thao tác nhạy cảm. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.
- `ev-s7v2-qa-05-12`: Bàn giao cho xây regression cho cổng đăng ký khóa học: Có đầu ra mẫu và danh sách vấn đề còn mở. Cổng quản trị cần kiểm tra quyền truy cập và lưu audit trail cho thao tác nhạy cảm. Kết luận chỉ giới hạn trong phạm vi mẫu đã quan sát và không suy diễn quá mức.
- `ev-s7v2-qa-05-13`: Tài liệu của xây regression cho cổng đăng ký khóa học: Tài liệu giữ nguyên cả hai phát biểu để người đánh giá xử lý mâu thuẫn. Cổng quản trị cần kiểm tra quyền truy cập và lưu audit trail cho thao tác nhạy cảm. Cách đặt tên đầu ra giúp truy vết từ yêu cầu tới kết quả kiểm tra.

Trạng thái yêu cầu bắt buộc:

- `qa-testing-foundations`: `satisfied`; thông tin: ev-s7v2-qa-05-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-test-cases`: `conflicting`; thông tin: ev-s7v2-qa-05-03, ev-s7v2-qa-05-04; Hồ sơ đồng thời có mô tả thực hành và phát biểu phủ định mâu thuẫn.
- `qa-api-testing`: `satisfied`; thông tin: ev-s7v2-qa-05-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-data-check`: `satisfied`; thông tin: ev-s7v2-qa-05-06; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-automation-foundation`: `satisfied`; thông tin: ev-s7v2-qa-05-07; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 22/30 |
| `qa-technical-specialization` | 17/25 |
| `qa-role-capability` | 13/20 |
| `projects-and-impact` | 9/15 |
| `communication-and-evidence-quality` | 7/10 |

Tổng điểm: **68/100**

Nhãn nháp: **needs_review**

Lý do vào review: conflicting-critical-evidence, lower-threshold-boundary

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-qa-06 — Junior QA Engineer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `explicit_failure`

Tóm tắt CV: Ứng viên chuyển từ hỗ trợ khách hàng sang QA với taxonomy lỗi có thể tái sử dụng. Ứng viên chuyển hướng từ lĩnh vực gần và xác nhận chưa thực hành một năng lực bắt buộc. Mục tiêu ứng tuyển là Junior QA Engineer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-qa-06-01`: Hoàn thành chương trình định hướng Đảm bảo chất lượng phần mềm với đồ án tổng hợp chuyển từ hỗ trợ khách hàng sang kiểm thử phần mềm. Ứng viên chuyển từ hỗ trợ khách hàng sang QA với taxonomy lỗi có thể tái sử dụng. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-qa-06-02`: Trong chuyển từ hỗ trợ khách hàng sang kiểm thử phần mềm, ứng viên phân biệt test level, test type và áp dụng quy trình lỗi từ phát hiện đến xác nhận sửa. Ứng viên chuyển từ hỗ trợ khách hàng sang QA với taxonomy lỗi có thể tái sử dụng. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-qa-06-03`: Trong chuyển từ hỗ trợ khách hàng sang kiểm thử phần mềm, ứng viên thiết kế test case bằng phân vùng tương đương, giá trị biên và bảng quyết định. Ứng viên chuyển từ hỗ trợ khách hàng sang QA với taxonomy lỗi có thể tái sử dụng. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-qa-06-04`: Trong chuyển từ hỗ trợ khách hàng sang kiểm thử phần mềm, ứng viên dùng Postman kiểm tra status, schema, authentication và chuỗi request có biến môi trường. Ứng viên chuyển từ hỗ trợ khách hàng sang QA với taxonomy lỗi có thể tái sử dụng. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-qa-06-05`: Trong chuyển từ hỗ trợ khách hàng sang kiểm thử phần mềm, ứng viên viết SQL đối chiếu dữ liệu trước và sau thao tác, gồm bản ghi thiếu hoặc trùng. Ứng viên chuyển từ hỗ trợ khách hàng sang QA với taxonomy lỗi có thể tái sử dụng. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-qa-06-06`: Ứng viên xác nhận chưa từng viết bất kỳ kiểm thử tự động nào. Ứng viên chuyển từ hỗ trợ khách hàng sang QA với taxonomy lỗi có thể tái sử dụng. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-qa-06-07`: Phạm vi kỹ thuật của chuyển từ hỗ trợ khách hàng sang kiểm thử phần mềm: Phần việc hiện có chỉ hỗ trợ gián tiếp cho vai trò mục tiêu. Ứng viên chuyển từ hỗ trợ khách hàng sang QA với taxonomy lỗi có thể tái sử dụng. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-qa-06-08`: Cách ra quyết định trong chuyển từ hỗ trợ khách hàng sang kiểm thử phần mềm: Kết quả mong muốn được nêu nhưng chưa có phương pháp đáp ứng yêu cầu chính. Ứng viên chuyển từ hỗ trợ khách hàng sang QA với taxonomy lỗi có thể tái sử dụng. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-qa-06-09`: Bàn giao cho chuyển từ hỗ trợ khách hàng sang kiểm thử phần mềm: Bài tập dừng ở bản minh họa một lần và chưa có kiểm tra đầy đủ. Ứng viên chuyển từ hỗ trợ khách hàng sang QA với taxonomy lỗi có thể tái sử dụng. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-qa-06-10`: Tài liệu của chuyển từ hỗ trợ khách hàng sang kiểm thử phần mềm: Hồ sơ diễn đạt rõ năng lực chưa từng sử dụng để tránh suy diễn sai. Ứng viên chuyển từ hỗ trợ khách hàng sang QA với taxonomy lỗi có thể tái sử dụng. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.

Trạng thái yêu cầu bắt buộc:

- `qa-testing-foundations`: `satisfied`; thông tin: ev-s7v2-qa-06-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-test-cases`: `satisfied`; thông tin: ev-s7v2-qa-06-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-api-testing`: `satisfied`; thông tin: ev-s7v2-qa-06-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-data-check`: `satisfied`; thông tin: ev-s7v2-qa-06-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-automation-foundation`: `unsatisfied`; thông tin: ev-s7v2-qa-06-06; Hồ sơ có phát biểu phủ định rõ ràng về yêu cầu này.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 10/30 |
| `qa-technical-specialization` | 12/25 |
| `qa-role-capability` | 9/20 |
| `projects-and-impact` | 5/15 |
| `communication-and-evidence-quality` | 5/10 |

Tổng điểm: **41/100**

Nhãn nháp: **reject**

Lý do vào review: không có

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-qa-07 — Junior QA Engineer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `lower_boundary`

Tóm tắt CV: Ứng dụng di động cần kiểm tra gián đoạn mạng và đồng bộ lại sau khi offline. Hồ sơ vừa đủ yêu cầu cốt lõi nhưng mức độ sâu và phạm vi dự án còn hạn chế. Mục tiêu ứng tuyển là Junior QA Engineer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-qa-07-01`: Hoàn thành chương trình định hướng Đảm bảo chất lượng phần mềm với đồ án tổng hợp kiểm thử ứng dụng quản lý công việc của nhóm sinh viên. Ứng dụng di động cần kiểm tra gián đoạn mạng và đồng bộ lại sau khi offline. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-qa-07-02`: Trong kiểm thử ứng dụng quản lý công việc của nhóm sinh viên, ứng viên phân biệt test level, test type và áp dụng quy trình lỗi từ phát hiện đến xác nhận sửa. Ứng dụng di động cần kiểm tra gián đoạn mạng và đồng bộ lại sau khi offline. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-qa-07-03`: Trong kiểm thử ứng dụng quản lý công việc của nhóm sinh viên, ứng viên thiết kế test case bằng phân vùng tương đương, giá trị biên và bảng quyết định. Ứng dụng di động cần kiểm tra gián đoạn mạng và đồng bộ lại sau khi offline. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-qa-07-04`: Trong kiểm thử ứng dụng quản lý công việc của nhóm sinh viên, ứng viên dùng Postman kiểm tra status, schema, authentication và chuỗi request có biến môi trường. Ứng dụng di động cần kiểm tra gián đoạn mạng và đồng bộ lại sau khi offline. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-qa-07-05`: Trong kiểm thử ứng dụng quản lý công việc của nhóm sinh viên, ứng viên viết SQL đối chiếu dữ liệu trước và sau thao tác, gồm bản ghi thiếu hoặc trùng. Ứng dụng di động cần kiểm tra gián đoạn mạng và đồng bộ lại sau khi offline. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-qa-07-06`: Trong kiểm thử ứng dụng quản lý công việc của nhóm sinh viên, ứng viên tự động hóa luồng regression chính, có assertion ổn định và báo cáo kết quả. Ứng dụng di động cần kiểm tra gián đoạn mạng và đồng bộ lại sau khi offline. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-qa-07-07`: Ở phần mở rộng của kiểm thử ứng dụng quản lý công việc của nhóm sinh viên, ứng viên áp dụng Có tích hợp test trong CI. và ghi lại kết quả thử nghiệm riêng. Ứng dụng di động cần kiểm tra gián đoạn mạng và đồng bộ lại sau khi offline. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-qa-07-08`: Phạm vi kỹ thuật của kiểm thử ứng dụng quản lý công việc của nhóm sinh viên: Luồng cơ bản hoạt động nhưng mới kiểm tra một số trường hợp phổ biến. Ứng dụng di động cần kiểm tra gián đoạn mạng và đồng bộ lại sau khi offline. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-qa-07-09`: Cách ra quyết định trong kiểm thử ứng dụng quản lý công việc của nhóm sinh viên: Mục tiêu và kết quả được nêu, phần đối chiếu độc lập còn thiếu. Ứng dụng di động cần kiểm tra gián đoạn mạng và đồng bộ lại sau khi offline. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-qa-07-10`: Bàn giao cho kiểm thử ứng dụng quản lý công việc của nhóm sinh viên: Đầu ra chạy lại được trên một bộ mẫu cố định. Ứng dụng di động cần kiểm tra gián đoạn mạng và đồng bộ lại sau khi offline. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-qa-07-11`: Tài liệu của kiểm thử ứng dụng quản lý công việc của nhóm sinh viên: README rõ lệnh chính nhưng phần quyết định kỹ thuật còn ngắn. Ứng dụng di động cần kiểm tra gián đoạn mạng và đồng bộ lại sau khi offline. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.

Trạng thái yêu cầu bắt buộc:

- `qa-testing-foundations`: `satisfied`; thông tin: ev-s7v2-qa-07-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-test-cases`: `satisfied`; thông tin: ev-s7v2-qa-07-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-api-testing`: `satisfied`; thông tin: ev-s7v2-qa-07-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-data-check`: `satisfied`; thông tin: ev-s7v2-qa-07-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-automation-foundation`: `satisfied`; thông tin: ev-s7v2-qa-07-06; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 27/30 |
| `qa-technical-specialization` | 13/25 |
| `qa-role-capability` | 10/20 |
| `projects-and-impact` | 8/15 |
| `communication-and-evidence-quality` | 9/10 |

Tổng điểm: **67/100**

Nhãn nháp: **needs_review**

Lý do vào review: lower-threshold-boundary

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-qa-08 — Junior QA Engineer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `upper_boundary`

Tóm tắt CV: Pipeline phát hành cần smoke test, tiêu chí dừng và bằng chứng hồi quy tối thiểu. Hồ sơ khá tốt và nằm gần ngưỡng Pass nên cần kiểm tra tính ổn định của quyết định. Mục tiêu ứng tuyển là Junior QA Engineer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-qa-08-01`: Hoàn thành chương trình định hướng Đảm bảo chất lượng phần mềm với đồ án tổng hợp đánh giá tính ổn định của luồng đặt vé thử nghiệm. Pipeline phát hành cần smoke test, tiêu chí dừng và bằng chứng hồi quy tối thiểu. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-qa-08-02`: Trong đánh giá tính ổn định của luồng đặt vé thử nghiệm, ứng viên phân biệt test level, test type và áp dụng quy trình lỗi từ phát hiện đến xác nhận sửa. Pipeline phát hành cần smoke test, tiêu chí dừng và bằng chứng hồi quy tối thiểu. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-qa-08-03`: Trong đánh giá tính ổn định của luồng đặt vé thử nghiệm, ứng viên thiết kế test case bằng phân vùng tương đương, giá trị biên và bảng quyết định. Pipeline phát hành cần smoke test, tiêu chí dừng và bằng chứng hồi quy tối thiểu. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-qa-08-04`: Trong đánh giá tính ổn định của luồng đặt vé thử nghiệm, ứng viên dùng Postman kiểm tra status, schema, authentication và chuỗi request có biến môi trường. Pipeline phát hành cần smoke test, tiêu chí dừng và bằng chứng hồi quy tối thiểu. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-qa-08-05`: Trong đánh giá tính ổn định của luồng đặt vé thử nghiệm, ứng viên viết SQL đối chiếu dữ liệu trước và sau thao tác, gồm bản ghi thiếu hoặc trùng. Pipeline phát hành cần smoke test, tiêu chí dừng và bằng chứng hồi quy tối thiểu. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-qa-08-06`: Trong đánh giá tính ổn định của luồng đặt vé thử nghiệm, ứng viên tự động hóa luồng regression chính, có assertion ổn định và báo cáo kết quả. Pipeline phát hành cần smoke test, tiêu chí dừng và bằng chứng hồi quy tối thiểu. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-qa-08-07`: Ở phần mở rộng của đánh giá tính ổn định của luồng đặt vé thử nghiệm, ứng viên áp dụng Có tích hợp test trong CI. và ghi lại kết quả thử nghiệm riêng. Pipeline phát hành cần smoke test, tiêu chí dừng và bằng chứng hồi quy tối thiểu. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-qa-08-08`: Ở phần mở rộng của đánh giá tính ổn định của luồng đặt vé thử nghiệm, ứng viên áp dụng Có performance hoặc security testing cơ bản. và ghi lại kết quả thử nghiệm riêng. Pipeline phát hành cần smoke test, tiêu chí dừng và bằng chứng hồi quy tối thiểu. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-qa-08-09`: Phạm vi kỹ thuật của đánh giá tính ổn định của luồng đặt vé thử nghiệm: Luồng chính và các lỗi thường gặp được xử lý bằng kiểm tra có thể chạy lại. Pipeline phát hành cần smoke test, tiêu chí dừng và bằng chứng hồi quy tối thiểu. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-qa-08-10`: Cách ra quyết định trong đánh giá tính ổn định của luồng đặt vé thử nghiệm: Lựa chọn kỹ thuật có lý do và ghi nhận một giới hạn đáng chú ý. Pipeline phát hành cần smoke test, tiêu chí dừng và bằng chứng hồi quy tối thiểu. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-qa-08-11`: Bàn giao cho đánh giá tính ổn định của luồng đặt vé thử nghiệm: Có dữ liệu mẫu, kết quả đối chiếu và hướng dẫn tái tạo. Pipeline phát hành cần smoke test, tiêu chí dừng và bằng chứng hồi quy tối thiểu. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.
- `ev-s7v2-qa-08-12`: Tài liệu của đánh giá tính ổn định của luồng đặt vé thử nghiệm: Tài liệu rõ cách chạy nhưng phần giải thích một số quyết định còn cô đọng. Pipeline phát hành cần smoke test, tiêu chí dừng và bằng chứng hồi quy tối thiểu. Kết luận chỉ giới hạn trong phạm vi mẫu đã quan sát và không suy diễn quá mức.

Trạng thái yêu cầu bắt buộc:

- `qa-testing-foundations`: `satisfied`; thông tin: ev-s7v2-qa-08-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-test-cases`: `satisfied`; thông tin: ev-s7v2-qa-08-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-api-testing`: `satisfied`; thông tin: ev-s7v2-qa-08-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-data-check`: `satisfied`; thông tin: ev-s7v2-qa-08-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-automation-foundation`: `satisfied`; thông tin: ev-s7v2-qa-08-06; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `qa-technical-specialization` | 18/25 |
| `qa-role-capability` | 15/20 |
| `projects-and-impact` | 12/15 |
| `communication-and-evidence-quality` | 7/10 |

Tổng điểm: **82/100**

Nhãn nháp: **needs_review**

Lý do vào review: upper-threshold-boundary

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-qa-09 — Junior QA Engineer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `transferable`

Tóm tắt CV: Ứng viên chuyển từ phân tích nghiệp vụ sang QA và liên kết acceptance criteria với test. Ứng viên chuyển từ lĩnh vực gần và chứng minh được năng lực tương đương qua dự án mới. Mục tiêu ứng tuyển là Junior QA Engineer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-qa-09-01`: Hoàn thành chương trình định hướng Đảm bảo chất lượng phần mềm với đồ án tổng hợp chuyển kinh nghiệm phân tích nghiệp vụ sang QA. Ứng viên chuyển từ phân tích nghiệp vụ sang QA và liên kết acceptance criteria với test. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-qa-09-02`: Trong chuyển kinh nghiệm phân tích nghiệp vụ sang QA, ứng viên phân biệt test level, test type và áp dụng quy trình lỗi từ phát hiện đến xác nhận sửa. Ứng viên chuyển từ phân tích nghiệp vụ sang QA và liên kết acceptance criteria với test. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-qa-09-03`: Trong chuyển kinh nghiệm phân tích nghiệp vụ sang QA, ứng viên thiết kế test case bằng phân vùng tương đương, giá trị biên và bảng quyết định. Ứng viên chuyển từ phân tích nghiệp vụ sang QA và liên kết acceptance criteria với test. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-qa-09-04`: Trong chuyển kinh nghiệm phân tích nghiệp vụ sang QA, ứng viên dùng Postman kiểm tra status, schema, authentication và chuỗi request có biến môi trường. Ứng viên chuyển từ phân tích nghiệp vụ sang QA và liên kết acceptance criteria với test. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-qa-09-05`: Trong chuyển kinh nghiệm phân tích nghiệp vụ sang QA, ứng viên viết SQL đối chiếu dữ liệu trước và sau thao tác, gồm bản ghi thiếu hoặc trùng. Ứng viên chuyển từ phân tích nghiệp vụ sang QA và liên kết acceptance criteria với test. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-qa-09-06`: Trong chuyển kinh nghiệm phân tích nghiệp vụ sang QA, ứng viên tự động hóa luồng regression chính, có assertion ổn định và báo cáo kết quả. Ứng viên chuyển từ phân tích nghiệp vụ sang QA và liên kết acceptance criteria với test. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-qa-09-07`: Ở phần mở rộng của chuyển kinh nghiệm phân tích nghiệp vụ sang QA, ứng viên áp dụng Có tích hợp test trong CI. và ghi lại kết quả thử nghiệm riêng. Ứng viên chuyển từ phân tích nghiệp vụ sang QA và liên kết acceptance criteria với test. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-qa-09-08`: Phạm vi kỹ thuật của chuyển kinh nghiệm phân tích nghiệp vụ sang QA: Kiến thức nền từ lĩnh vực gần được áp dụng vào một sản phẩm đúng vai trò mục tiêu. Ứng viên chuyển từ phân tích nghiệp vụ sang QA và liên kết acceptance criteria với test. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-qa-09-09`: Cách ra quyết định trong chuyển kinh nghiệm phân tích nghiệp vụ sang QA: Hồ sơ phân biệt rõ phần kinh nghiệm chuyển đổi và phần mới học. Ứng viên chuyển từ phân tích nghiệp vụ sang QA và liên kết acceptance criteria với test. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-qa-09-10`: Bàn giao cho chuyển kinh nghiệm phân tích nghiệp vụ sang QA: Prototype chạy được, có kiểm tra và đầu ra đo được nhưng chưa qua môi trường thực tập. Ứng viên chuyển từ phân tích nghiệp vụ sang QA và liên kết acceptance criteria với test. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-qa-09-11`: Tài liệu của chuyển kinh nghiệm phân tích nghiệp vụ sang QA: Tài liệu nêu rõ phạm vi kinh nghiệm trực tiếp và kinh nghiệm tương đương. Ứng viên chuyển từ phân tích nghiệp vụ sang QA và liên kết acceptance criteria với test. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.

Trạng thái yêu cầu bắt buộc:

- `qa-testing-foundations`: `satisfied`; thông tin: ev-s7v2-qa-09-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-test-cases`: `satisfied`; thông tin: ev-s7v2-qa-09-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-api-testing`: `satisfied`; thông tin: ev-s7v2-qa-09-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-data-check`: `satisfied`; thông tin: ev-s7v2-qa-09-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `qa-automation-foundation`: `satisfied`; thông tin: ev-s7v2-qa-09-06; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `qa-technical-specialization` | 16/25 |
| `qa-role-capability` | 14/20 |
| `projects-and-impact` | 10/15 |
| `communication-and-evidence-quality` | 9/10 |

Tổng điểm: **79/100**

Nhãn nháp: **waitlist**

Lý do vào review: không có

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-qa-10 — Junior QA Engineer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `hard_negative`

Tóm tắt CV: Hồ sơ liệt kê công cụ kiểm thử nhưng không mô tả test case hoặc defect đã theo dõi. Hồ sơ chủ yếu liệt kê khóa học và công cụ nhưng không mô tả nhiệm vụ hay sản phẩm đã làm. Mục tiêu ứng tuyển là Junior QA Engineer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-qa-10-01`: Hoàn thành chương trình định hướng Đảm bảo chất lượng phần mềm với đồ án tổng hợp liệt kê công cụ kiểm thử từ các khóa học nhập môn. Hồ sơ liệt kê công cụ kiểm thử nhưng không mô tả test case hoặc defect đã theo dõi. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-qa-10-02`: Đã hoàn thành bài học giới thiệu về Nền tảng kiểm thử và tự ghi tên công cụ trong danh sách kỹ năng. Hồ sơ liệt kê công cụ kiểm thử nhưng không mô tả test case hoặc defect đã theo dõi. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-qa-10-03`: Đã hoàn thành bài học giới thiệu về Thiết kế test case và tự ghi tên công cụ trong danh sách kỹ năng. Hồ sơ liệt kê công cụ kiểm thử nhưng không mô tả test case hoặc defect đã theo dõi. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-qa-10-04`: Đã hoàn thành bài học giới thiệu về Kiểm thử API và tự ghi tên công cụ trong danh sách kỹ năng. Hồ sơ liệt kê công cụ kiểm thử nhưng không mô tả test case hoặc defect đã theo dõi. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-qa-10-05`: Đã hoàn thành bài học giới thiệu về SQL kiểm tra dữ liệu và tự ghi tên công cụ trong danh sách kỹ năng. Hồ sơ liệt kê công cụ kiểm thử nhưng không mô tả test case hoặc defect đã theo dõi. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-qa-10-06`: Đã hoàn thành bài học giới thiệu về Tự động hóa kiểm thử và tự ghi tên công cụ trong danh sách kỹ năng. Hồ sơ liệt kê công cụ kiểm thử nhưng không mô tả test case hoặc defect đã theo dõi. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-qa-10-07`: Ở phần mở rộng của liệt kê công cụ kiểm thử từ các khóa học nhập môn, ứng viên áp dụng Có tích hợp test trong CI. và ghi lại kết quả thử nghiệm riêng. Hồ sơ liệt kê công cụ kiểm thử nhưng không mô tả test case hoặc defect đã theo dõi. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-qa-10-08`: Ở phần mở rộng của liệt kê công cụ kiểm thử từ các khóa học nhập môn, ứng viên áp dụng Có performance hoặc security testing cơ bản. và ghi lại kết quả thử nghiệm riêng. Hồ sơ liệt kê công cụ kiểm thử nhưng không mô tả test case hoặc defect đã theo dõi. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.

Trạng thái yêu cầu bắt buộc:

- `qa-testing-foundations`: `missing`; thông tin: ev-s7v2-qa-10-02; Hồ sơ không đề cập đủ thông tin để xác nhận yêu cầu này.
- `qa-test-cases`: `missing`; thông tin: ev-s7v2-qa-10-03; Hồ sơ không đề cập đủ thông tin để xác nhận yêu cầu này.
- `qa-api-testing`: `missing`; thông tin: ev-s7v2-qa-10-04; Hồ sơ không đề cập đủ thông tin để xác nhận yêu cầu này.
- `qa-data-check`: `missing`; thông tin: ev-s7v2-qa-10-05; Hồ sơ không đề cập đủ thông tin để xác nhận yêu cầu này.
- `qa-automation-foundation`: `missing`; thông tin: ev-s7v2-qa-10-06; Hồ sơ không đề cập đủ thông tin để xác nhận yêu cầu này.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 14/30 |
| `qa-technical-specialization` | 9/25 |
| `qa-role-capability` | 6/20 |
| `projects-and-impact` | 3/15 |
| `communication-and-evidence-quality` | 4/10 |

Tổng điểm: **36/100**

Nhãn nháp: **needs_review**

Lý do vào review: missing-critical-evidence, low-score-without-explicit-critical-unsatisfied

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-de-01 — Junior Data Engineer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `strong`

Tóm tắt CV: Pipeline giao dịch cần checkpoint và khôi phục mà không nhân đôi bản ghi. Hồ sơ trình bày một sản phẩm hoàn chỉnh, có số liệu đối chiếu và tài liệu tái tạo. Mục tiêu ứng tuyển là Junior Data Engineer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-de-01-01`: Hoàn thành chương trình định hướng Kỹ thuật dữ liệu và hệ thống thông tin với đồ án tổng hợp xây pipeline giao dịch theo lô với checkpoint. Pipeline giao dịch cần checkpoint và khôi phục mà không nhân đôi bản ghi. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-de-01-02`: Trong xây pipeline giao dịch theo lô với checkpoint, ứng viên viết Python theo module để đọc nhiều nguồn, chuẩn hóa bản ghi và ghi log lỗi theo batch. Pipeline giao dịch cần checkpoint và khôi phục mà không nhân đôi bản ghi. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-de-01-03`: Trong xây pipeline giao dịch theo lô với checkpoint, ứng viên dùng SQL với CTE, hàm cửa sổ và execution plan để biến đổi dữ liệu dung lượng vừa. Pipeline giao dịch cần checkpoint và khôi phục mà không nhân đôi bản ghi. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-de-01-04`: Trong xây pipeline giao dịch theo lô với checkpoint, ứng viên xây pipeline incremental có checkpoint, retry và cơ chế chạy lại không tạo dữ liệu trùng. Pipeline giao dịch cần checkpoint và khôi phục mà không nhân đôi bản ghi. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-de-01-05`: Trong xây pipeline giao dịch theo lô với checkpoint, ứng viên thiết kế grain, khóa fact-dimension và kiểm tra null, unique cùng referential integrity. Pipeline giao dịch cần checkpoint và khôi phục mà không nhân đôi bản ghi. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-de-01-06`: Trong xây pipeline giao dịch theo lô với checkpoint, ứng viên quản lý mã bằng Git, chạy tác vụ trên Linux và đóng gói môi trường bằng Docker. Pipeline giao dịch cần checkpoint và khôi phục mà không nhân đôi bản ghi. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-de-01-07`: Ở phần mở rộng của xây pipeline giao dịch theo lô với checkpoint, ứng viên áp dụng Có orchestration. và ghi lại kết quả thử nghiệm riêng. Pipeline giao dịch cần checkpoint và khôi phục mà không nhân đôi bản ghi. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-de-01-08`: Ở phần mở rộng của xây pipeline giao dịch theo lô với checkpoint, ứng viên áp dụng Có cloud storage hoặc cloud warehouse. và ghi lại kết quả thử nghiệm riêng. Pipeline giao dịch cần checkpoint và khôi phục mà không nhân đôi bản ghi. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-de-01-09`: Phạm vi kỹ thuật của xây pipeline giao dịch theo lô với checkpoint: Luồng chính và các trường hợp lỗi được kiểm tra trên nhiều bộ dữ liệu hoặc tình huống đầu vào. Pipeline giao dịch cần checkpoint và khôi phục mà không nhân đôi bản ghi. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-de-01-10`: Cách ra quyết định trong xây pipeline giao dịch theo lô với checkpoint: Hai phương án được so sánh bằng tiêu chí đo được trước khi chọn cách triển khai. Pipeline giao dịch cần checkpoint và khôi phục mà không nhân đôi bản ghi. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-de-01-11`: Bàn giao cho xây pipeline giao dịch theo lô với checkpoint: Kết quả có chỉ số trước và sau, bộ kiểm tra hồi quy và hướng dẫn chạy độc lập. Pipeline giao dịch cần checkpoint và khôi phục mà không nhân đôi bản ghi. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.
- `ev-s7v2-de-01-12`: Tài liệu của xây pipeline giao dịch theo lô với checkpoint: Tài liệu nêu rõ phạm vi cá nhân, giả định, giới hạn và quyết định kỹ thuật. Pipeline giao dịch cần checkpoint và khôi phục mà không nhân đôi bản ghi. Kết luận chỉ giới hạn trong phạm vi mẫu đã quan sát và không suy diễn quá mức.

Trạng thái yêu cầu bắt buộc:

- `de-python`: `satisfied`; thông tin: ev-s7v2-de-01-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-sql`: `satisfied`; thông tin: ev-s7v2-de-01-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-pipeline`: `satisfied`; thông tin: ev-s7v2-de-01-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-data-model-quality`: `satisfied`; thông tin: ev-s7v2-de-01-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-delivery-workflow`: `satisfied`; thông tin: ev-s7v2-de-01-06; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `de-technical-specialization` | 24/25 |
| `de-role-capability` | 18/20 |
| `projects-and-impact` | 14/15 |
| `communication-and-evidence-quality` | 9/10 |

Tổng điểm: **95/100**

Nhãn nháp: **pass**

Lý do vào review: không có

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-de-02 — Junior Data Engineer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `solid`

Tóm tắt CV: Luồng đồng bộ sản phẩm phải xử lý schema thay đổi và giới hạn tốc độ API nguồn. Hồ sơ có dự án junior hoàn chỉnh, thông tin nhất quán và đầu ra có thể kiểm tra. Mục tiêu ứng tuyển là Junior Data Engineer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-de-02-01`: Hoàn thành chương trình định hướng Kỹ thuật dữ liệu và hệ thống thông tin với đồ án tổng hợp đồng bộ dữ liệu sản phẩm từ API vào kho phân tích. Luồng đồng bộ sản phẩm phải xử lý schema thay đổi và giới hạn tốc độ API nguồn. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-de-02-02`: Trong đồng bộ dữ liệu sản phẩm từ API vào kho phân tích, ứng viên viết Python theo module để đọc nhiều nguồn, chuẩn hóa bản ghi và ghi log lỗi theo batch. Luồng đồng bộ sản phẩm phải xử lý schema thay đổi và giới hạn tốc độ API nguồn. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-de-02-03`: Trong đồng bộ dữ liệu sản phẩm từ API vào kho phân tích, ứng viên dùng SQL với CTE, hàm cửa sổ và execution plan để biến đổi dữ liệu dung lượng vừa. Luồng đồng bộ sản phẩm phải xử lý schema thay đổi và giới hạn tốc độ API nguồn. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-de-02-04`: Trong đồng bộ dữ liệu sản phẩm từ API vào kho phân tích, ứng viên xây pipeline incremental có checkpoint, retry và cơ chế chạy lại không tạo dữ liệu trùng. Luồng đồng bộ sản phẩm phải xử lý schema thay đổi và giới hạn tốc độ API nguồn. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-de-02-05`: Trong đồng bộ dữ liệu sản phẩm từ API vào kho phân tích, ứng viên thiết kế grain, khóa fact-dimension và kiểm tra null, unique cùng referential integrity. Luồng đồng bộ sản phẩm phải xử lý schema thay đổi và giới hạn tốc độ API nguồn. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-de-02-06`: Trong đồng bộ dữ liệu sản phẩm từ API vào kho phân tích, ứng viên quản lý mã bằng Git, chạy tác vụ trên Linux và đóng gói môi trường bằng Docker. Luồng đồng bộ sản phẩm phải xử lý schema thay đổi và giới hạn tốc độ API nguồn. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-de-02-07`: Ở phần mở rộng của đồng bộ dữ liệu sản phẩm từ API vào kho phân tích, ứng viên áp dụng Có orchestration. và ghi lại kết quả thử nghiệm riêng. Luồng đồng bộ sản phẩm phải xử lý schema thay đổi và giới hạn tốc độ API nguồn. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-de-02-08`: Ở phần mở rộng của đồng bộ dữ liệu sản phẩm từ API vào kho phân tích, ứng viên áp dụng Có cloud storage hoặc cloud warehouse. và ghi lại kết quả thử nghiệm riêng. Luồng đồng bộ sản phẩm phải xử lý schema thay đổi và giới hạn tốc độ API nguồn. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-de-02-09`: Phạm vi kỹ thuật của đồng bộ dữ liệu sản phẩm từ API vào kho phân tích: Luồng nghiệp vụ chính và hai trường hợp lỗi phổ biến được triển khai và kiểm thử. Luồng đồng bộ sản phẩm phải xử lý schema thay đổi và giới hạn tốc độ API nguồn. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-de-02-10`: Cách ra quyết định trong đồng bộ dữ liệu sản phẩm từ API vào kho phân tích: Mục tiêu, giả định và cách đối chiếu kết quả được trình bày rõ. Luồng đồng bộ sản phẩm phải xử lý schema thay đổi và giới hạn tốc độ API nguồn. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-de-02-11`: Bàn giao cho đồng bộ dữ liệu sản phẩm từ API vào kho phân tích: Sản phẩm có dữ liệu mẫu, lệnh chạy và kết quả kiểm tra nhất quán. Luồng đồng bộ sản phẩm phải xử lý schema thay đổi và giới hạn tốc độ API nguồn. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.
- `ev-s7v2-de-02-12`: Tài liệu của đồng bộ dữ liệu sản phẩm từ API vào kho phân tích: README mô tả phần việc cá nhân và các hạn chế chính. Luồng đồng bộ sản phẩm phải xử lý schema thay đổi và giới hạn tốc độ API nguồn. Kết luận chỉ giới hạn trong phạm vi mẫu đã quan sát và không suy diễn quá mức.

Trạng thái yêu cầu bắt buộc:

- `de-python`: `satisfied`; thông tin: ev-s7v2-de-02-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-sql`: `satisfied`; thông tin: ev-s7v2-de-02-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-pipeline`: `satisfied`; thông tin: ev-s7v2-de-02-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-data-model-quality`: `satisfied`; thông tin: ev-s7v2-de-02-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-delivery-workflow`: `satisfied`; thông tin: ev-s7v2-de-02-06; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `de-technical-specialization` | 22/25 |
| `de-role-capability` | 17/20 |
| `projects-and-impact` | 12/15 |
| `communication-and-evidence-quality` | 8/10 |

Tổng điểm: **89/100**

Nhãn nháp: **pass**

Lý do vào review: không có

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-de-03 — Junior Data Engineer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `moderate`

Tóm tắt CV: Data mart doanh thu cần kiểm soát late-arriving dimension và lịch sử thay đổi. Hồ sơ đáp ứng phần cốt lõi nhưng dự án mới giới hạn ở một luồng nghiệp vụ. Mục tiêu ứng tuyển là Junior Data Engineer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-de-03-01`: Hoàn thành chương trình định hướng Kỹ thuật dữ liệu và hệ thống thông tin với đồ án tổng hợp tạo mart doanh thu theo mô hình sao. Data mart doanh thu cần kiểm soát late-arriving dimension và lịch sử thay đổi. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-de-03-02`: Trong tạo mart doanh thu theo mô hình sao, ứng viên viết Python theo module để đọc nhiều nguồn, chuẩn hóa bản ghi và ghi log lỗi theo batch. Data mart doanh thu cần kiểm soát late-arriving dimension và lịch sử thay đổi. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-de-03-03`: Trong tạo mart doanh thu theo mô hình sao, ứng viên dùng SQL với CTE, hàm cửa sổ và execution plan để biến đổi dữ liệu dung lượng vừa. Data mart doanh thu cần kiểm soát late-arriving dimension và lịch sử thay đổi. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-de-03-04`: Trong tạo mart doanh thu theo mô hình sao, ứng viên xây pipeline incremental có checkpoint, retry và cơ chế chạy lại không tạo dữ liệu trùng. Data mart doanh thu cần kiểm soát late-arriving dimension và lịch sử thay đổi. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-de-03-05`: Trong tạo mart doanh thu theo mô hình sao, ứng viên thiết kế grain, khóa fact-dimension và kiểm tra null, unique cùng referential integrity. Data mart doanh thu cần kiểm soát late-arriving dimension và lịch sử thay đổi. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-de-03-06`: Trong tạo mart doanh thu theo mô hình sao, ứng viên quản lý mã bằng Git, chạy tác vụ trên Linux và đóng gói môi trường bằng Docker. Data mart doanh thu cần kiểm soát late-arriving dimension và lịch sử thay đổi. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-de-03-07`: Ở phần mở rộng của tạo mart doanh thu theo mô hình sao, ứng viên áp dụng Có orchestration. và ghi lại kết quả thử nghiệm riêng. Data mart doanh thu cần kiểm soát late-arriving dimension và lịch sử thay đổi. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-de-03-08`: Phạm vi kỹ thuật của tạo mart doanh thu theo mô hình sao: Một luồng chính được hoàn thành trên tập dữ liệu hoặc chức năng có phạm vi vừa phải. Data mart doanh thu cần kiểm soát late-arriving dimension và lịch sử thay đổi. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-de-03-09`: Cách ra quyết định trong tạo mart doanh thu theo mô hình sao: Phương pháp được giải thích nhưng phần so sánh phương án còn ngắn. Data mart doanh thu cần kiểm soát late-arriving dimension và lịch sử thay đổi. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-de-03-10`: Bàn giao cho tạo mart doanh thu theo mô hình sao: Đầu ra chạy lại được cục bộ và có một số kiểm tra cơ bản. Data mart doanh thu cần kiểm soát late-arriving dimension và lịch sử thay đổi. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-de-03-11`: Tài liệu của tạo mart doanh thu theo mô hình sao: Tài liệu đủ để chạy thử nhưng chưa mô tả đầy đủ rủi ro vận hành. Data mart doanh thu cần kiểm soát late-arriving dimension và lịch sử thay đổi. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.

Trạng thái yêu cầu bắt buộc:

- `de-python`: `satisfied`; thông tin: ev-s7v2-de-03-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-sql`: `satisfied`; thông tin: ev-s7v2-de-03-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-pipeline`: `satisfied`; thông tin: ev-s7v2-de-03-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-data-model-quality`: `satisfied`; thông tin: ev-s7v2-de-03-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-delivery-workflow`: `satisfied`; thông tin: ev-s7v2-de-03-06; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `de-technical-specialization` | 17/25 |
| `de-role-capability` | 14/20 |
| `projects-and-impact` | 9/15 |
| `communication-and-evidence-quality` | 8/10 |

Tổng điểm: **78/100**

Nhãn nháp: **waitlist**

Lý do vào review: không có

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-de-04 — Junior Data Engineer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `missing_critical`

Tóm tắt CV: Luồng sự kiện cần watermark, dead-letter queue và phép đo độ trễ theo partition. Hồ sơ mô tả một số phần việc liên quan nhưng không đề cập đầy đủ toàn bộ năng lực cốt lõi. Mục tiêu ứng tuyển là Junior Data Engineer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-de-04-01`: Hoàn thành chương trình định hướng Kỹ thuật dữ liệu và hệ thống thông tin với đồ án tổng hợp xử lý file sự kiện đến muộn và bản ghi trùng. Luồng sự kiện cần watermark, dead-letter queue và phép đo độ trễ theo partition. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-de-04-02`: Trong xử lý file sự kiện đến muộn và bản ghi trùng, ứng viên dùng SQL với CTE, hàm cửa sổ và execution plan để biến đổi dữ liệu dung lượng vừa. Luồng sự kiện cần watermark, dead-letter queue và phép đo độ trễ theo partition. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-de-04-03`: Trong xử lý file sự kiện đến muộn và bản ghi trùng, ứng viên xây pipeline incremental có checkpoint, retry và cơ chế chạy lại không tạo dữ liệu trùng. Luồng sự kiện cần watermark, dead-letter queue và phép đo độ trễ theo partition. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-de-04-04`: Trong xử lý file sự kiện đến muộn và bản ghi trùng, ứng viên thiết kế grain, khóa fact-dimension và kiểm tra null, unique cùng referential integrity. Luồng sự kiện cần watermark, dead-letter queue và phép đo độ trễ theo partition. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-de-04-05`: Trong xử lý file sự kiện đến muộn và bản ghi trùng, ứng viên quản lý mã bằng Git, chạy tác vụ trên Linux và đóng gói môi trường bằng Docker. Luồng sự kiện cần watermark, dead-letter queue và phép đo độ trễ theo partition. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-de-04-06`: Ở phần mở rộng của xử lý file sự kiện đến muộn và bản ghi trùng, ứng viên áp dụng Có orchestration. và ghi lại kết quả thử nghiệm riêng. Luồng sự kiện cần watermark, dead-letter queue và phép đo độ trễ theo partition. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-de-04-07`: Phạm vi kỹ thuật của xử lý file sự kiện đến muộn và bản ghi trùng: Các phần được nêu có thao tác kỹ thuật và kiểm tra đầu vào cơ bản. Luồng sự kiện cần watermark, dead-letter queue và phép đo độ trễ theo partition. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-de-04-08`: Cách ra quyết định trong xử lý file sự kiện đến muộn và bản ghi trùng: Ứng viên giải thích mục tiêu và một giới hạn của giải pháp. Luồng sự kiện cần watermark, dead-letter queue và phép đo độ trễ theo partition. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-de-04-09`: Bàn giao cho xử lý file sự kiện đến muộn và bản ghi trùng: Có bản chạy thử cùng dữ liệu hoặc tình huống minh họa. Luồng sự kiện cần watermark, dead-letter queue và phép đo độ trễ theo partition. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-de-04-10`: Tài liệu của xử lý file sự kiện đến muộn và bản ghi trùng: Phạm vi đã làm được ghi rõ, không suy diễn cho phần chưa được mô tả. Luồng sự kiện cần watermark, dead-letter queue và phép đo độ trễ theo partition. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.

Trạng thái yêu cầu bắt buộc:

- `de-python`: `missing`; thông tin: không có thông tin liên kết; Hồ sơ không đề cập đủ thông tin để xác nhận yêu cầu này.
- `de-sql`: `satisfied`; thông tin: ev-s7v2-de-04-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-pipeline`: `satisfied`; thông tin: ev-s7v2-de-04-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-data-model-quality`: `satisfied`; thông tin: ev-s7v2-de-04-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-delivery-workflow`: `satisfied`; thông tin: ev-s7v2-de-04-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 20/30 |
| `de-technical-specialization` | 17/25 |
| `de-role-capability` | 13/20 |
| `projects-and-impact` | 8/15 |
| `communication-and-evidence-quality` | 6/10 |

Tổng điểm: **64/100**

Nhãn nháp: **needs_review**

Lý do vào review: missing-critical-evidence, low-score-without-explicit-critical-unsatisfied

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-de-05 — Junior Data Engineer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `conflicting_critical`

Tóm tắt CV: Pipeline chất lượng không khí cần kiểm tra sensor drift và dữ liệu thiếu theo trạm. Hồ sơ kết hợp mô tả dự án và bản tự đánh giá có một điểm chưa nhất quán. Mục tiêu ứng tuyển là Junior Data Engineer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-de-05-01`: Hoàn thành chương trình định hướng Kỹ thuật dữ liệu và hệ thống thông tin với đồ án tổng hợp xây luồng dữ liệu chất lượng không khí theo ngày. Pipeline chất lượng không khí cần kiểm tra sensor drift và dữ liệu thiếu theo trạm. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-de-05-02`: Trong xây luồng dữ liệu chất lượng không khí theo ngày, ứng viên viết Python theo module để đọc nhiều nguồn, chuẩn hóa bản ghi và ghi log lỗi theo batch. Pipeline chất lượng không khí cần kiểm tra sensor drift và dữ liệu thiếu theo trạm. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-de-05-03`: Trong xây luồng dữ liệu chất lượng không khí theo ngày, ứng viên dùng SQL với CTE, hàm cửa sổ và execution plan để biến đổi dữ liệu dung lượng vừa. Pipeline chất lượng không khí cần kiểm tra sensor drift và dữ liệu thiếu theo trạm. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-de-05-04`: Ứng viên xác nhận chưa từng viết truy vấn SQL có JOIN hoặc tổng hợp. Pipeline chất lượng không khí cần kiểm tra sensor drift và dữ liệu thiếu theo trạm. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-de-05-05`: Trong xây luồng dữ liệu chất lượng không khí theo ngày, ứng viên xây pipeline incremental có checkpoint, retry và cơ chế chạy lại không tạo dữ liệu trùng. Pipeline chất lượng không khí cần kiểm tra sensor drift và dữ liệu thiếu theo trạm. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-de-05-06`: Trong xây luồng dữ liệu chất lượng không khí theo ngày, ứng viên thiết kế grain, khóa fact-dimension và kiểm tra null, unique cùng referential integrity. Pipeline chất lượng không khí cần kiểm tra sensor drift và dữ liệu thiếu theo trạm. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-de-05-07`: Trong xây luồng dữ liệu chất lượng không khí theo ngày, ứng viên quản lý mã bằng Git, chạy tác vụ trên Linux và đóng gói môi trường bằng Docker. Pipeline chất lượng không khí cần kiểm tra sensor drift và dữ liệu thiếu theo trạm. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-de-05-08`: Ở phần mở rộng của xây luồng dữ liệu chất lượng không khí theo ngày, ứng viên áp dụng Có orchestration. và ghi lại kết quả thử nghiệm riêng. Pipeline chất lượng không khí cần kiểm tra sensor drift và dữ liệu thiếu theo trạm. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-de-05-09`: Ở phần mở rộng của xây luồng dữ liệu chất lượng không khí theo ngày, ứng viên áp dụng Có cloud storage hoặc cloud warehouse. và ghi lại kết quả thử nghiệm riêng. Pipeline chất lượng không khí cần kiểm tra sensor drift và dữ liệu thiếu theo trạm. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-de-05-10`: Phạm vi kỹ thuật của xây luồng dữ liệu chất lượng không khí theo ngày: Một luồng kỹ thuật hoàn chỉnh được mô tả cùng cách kiểm tra sai lệch. Pipeline chất lượng không khí cần kiểm tra sensor drift và dữ liệu thiếu theo trạm. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-de-05-11`: Cách ra quyết định trong xây luồng dữ liệu chất lượng không khí theo ngày: Mục tiêu và kết quả được nêu nhưng một phát biểu năng lực cần xác minh lại. Pipeline chất lượng không khí cần kiểm tra sensor drift và dữ liệu thiếu theo trạm. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.
- `ev-s7v2-de-05-12`: Bàn giao cho xây luồng dữ liệu chất lượng không khí theo ngày: Có đầu ra mẫu và danh sách vấn đề còn mở. Pipeline chất lượng không khí cần kiểm tra sensor drift và dữ liệu thiếu theo trạm. Kết luận chỉ giới hạn trong phạm vi mẫu đã quan sát và không suy diễn quá mức.
- `ev-s7v2-de-05-13`: Tài liệu của xây luồng dữ liệu chất lượng không khí theo ngày: Tài liệu giữ nguyên cả hai phát biểu để người đánh giá xử lý mâu thuẫn. Pipeline chất lượng không khí cần kiểm tra sensor drift và dữ liệu thiếu theo trạm. Cách đặt tên đầu ra giúp truy vết từ yêu cầu tới kết quả kiểm tra.

Trạng thái yêu cầu bắt buộc:

- `de-python`: `satisfied`; thông tin: ev-s7v2-de-05-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-sql`: `conflicting`; thông tin: ev-s7v2-de-05-03, ev-s7v2-de-05-04; Hồ sơ đồng thời có mô tả thực hành và phát biểu phủ định mâu thuẫn.
- `de-pipeline`: `satisfied`; thông tin: ev-s7v2-de-05-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-data-model-quality`: `satisfied`; thông tin: ev-s7v2-de-05-06; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-delivery-workflow`: `satisfied`; thông tin: ev-s7v2-de-05-07; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 22/30 |
| `de-technical-specialization` | 17/25 |
| `de-role-capability` | 13/20 |
| `projects-and-impact` | 9/15 |
| `communication-and-evidence-quality` | 7/10 |

Tổng điểm: **68/100**

Nhãn nháp: **needs_review**

Lý do vào review: conflicting-critical-evidence, lower-threshold-boundary

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-de-06 — Junior Data Engineer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `explicit_failure`

Tóm tắt CV: Ứng viên chuyển từ backend sang data engineering và mô tả rõ phần batch mới học. Ứng viên chuyển hướng từ lĩnh vực gần và xác nhận chưa thực hành một năng lực bắt buộc. Mục tiêu ứng tuyển là Junior Data Engineer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-de-06-01`: Hoàn thành chương trình định hướng Kỹ thuật dữ liệu và hệ thống thông tin với đồ án tổng hợp chuyển từ backend sang kỹ thuật dữ liệu. Ứng viên chuyển từ backend sang data engineering và mô tả rõ phần batch mới học. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-de-06-02`: Ứng viên xác nhận chưa từng dùng Python cho tác vụ xử lý dữ liệu. Ứng viên chuyển từ backend sang data engineering và mô tả rõ phần batch mới học. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-de-06-03`: Trong chuyển từ backend sang kỹ thuật dữ liệu, ứng viên dùng SQL với CTE, hàm cửa sổ và execution plan để biến đổi dữ liệu dung lượng vừa. Ứng viên chuyển từ backend sang data engineering và mô tả rõ phần batch mới học. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-de-06-04`: Trong chuyển từ backend sang kỹ thuật dữ liệu, ứng viên xây pipeline incremental có checkpoint, retry và cơ chế chạy lại không tạo dữ liệu trùng. Ứng viên chuyển từ backend sang data engineering và mô tả rõ phần batch mới học. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-de-06-05`: Trong chuyển từ backend sang kỹ thuật dữ liệu, ứng viên thiết kế grain, khóa fact-dimension và kiểm tra null, unique cùng referential integrity. Ứng viên chuyển từ backend sang data engineering và mô tả rõ phần batch mới học. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-de-06-06`: Trong chuyển từ backend sang kỹ thuật dữ liệu, ứng viên quản lý mã bằng Git, chạy tác vụ trên Linux và đóng gói môi trường bằng Docker. Ứng viên chuyển từ backend sang data engineering và mô tả rõ phần batch mới học. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-de-06-07`: Phạm vi kỹ thuật của chuyển từ backend sang kỹ thuật dữ liệu: Phần việc hiện có chỉ hỗ trợ gián tiếp cho vai trò mục tiêu. Ứng viên chuyển từ backend sang data engineering và mô tả rõ phần batch mới học. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-de-06-08`: Cách ra quyết định trong chuyển từ backend sang kỹ thuật dữ liệu: Kết quả mong muốn được nêu nhưng chưa có phương pháp đáp ứng yêu cầu chính. Ứng viên chuyển từ backend sang data engineering và mô tả rõ phần batch mới học. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-de-06-09`: Bàn giao cho chuyển từ backend sang kỹ thuật dữ liệu: Bài tập dừng ở bản minh họa một lần và chưa có kiểm tra đầy đủ. Ứng viên chuyển từ backend sang data engineering và mô tả rõ phần batch mới học. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-de-06-10`: Tài liệu của chuyển từ backend sang kỹ thuật dữ liệu: Hồ sơ diễn đạt rõ năng lực chưa từng sử dụng để tránh suy diễn sai. Ứng viên chuyển từ backend sang data engineering và mô tả rõ phần batch mới học. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.

Trạng thái yêu cầu bắt buộc:

- `de-python`: `unsatisfied`; thông tin: ev-s7v2-de-06-02; Hồ sơ có phát biểu phủ định rõ ràng về yêu cầu này.
- `de-sql`: `satisfied`; thông tin: ev-s7v2-de-06-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-pipeline`: `satisfied`; thông tin: ev-s7v2-de-06-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-data-model-quality`: `satisfied`; thông tin: ev-s7v2-de-06-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-delivery-workflow`: `satisfied`; thông tin: ev-s7v2-de-06-06; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 10/30 |
| `de-technical-specialization` | 12/25 |
| `de-role-capability` | 9/20 |
| `projects-and-impact` | 5/15 |
| `communication-and-evidence-quality` | 5/10 |

Tổng điểm: **41/100**

Nhãn nháp: **reject**

Lý do vào review: không có

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-de-07 — Junior Data Engineer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `lower_boundary`

Tóm tắt CV: Luồng log ứng dụng cần chuẩn hóa schema trước khi phục vụ dashboard vận hành. Hồ sơ vừa đủ yêu cầu cốt lõi nhưng mức độ sâu và phạm vi dự án còn hạn chế. Mục tiêu ứng tuyển là Junior Data Engineer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-de-07-01`: Hoàn thành chương trình định hướng Kỹ thuật dữ liệu và hệ thống thông tin với đồ án tổng hợp tạo pipeline log ứng dụng cho dashboard vận hành. Luồng log ứng dụng cần chuẩn hóa schema trước khi phục vụ dashboard vận hành. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-de-07-02`: Trong tạo pipeline log ứng dụng cho dashboard vận hành, ứng viên viết Python theo module để đọc nhiều nguồn, chuẩn hóa bản ghi và ghi log lỗi theo batch. Luồng log ứng dụng cần chuẩn hóa schema trước khi phục vụ dashboard vận hành. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-de-07-03`: Trong tạo pipeline log ứng dụng cho dashboard vận hành, ứng viên dùng SQL với CTE, hàm cửa sổ và execution plan để biến đổi dữ liệu dung lượng vừa. Luồng log ứng dụng cần chuẩn hóa schema trước khi phục vụ dashboard vận hành. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-de-07-04`: Trong tạo pipeline log ứng dụng cho dashboard vận hành, ứng viên xây pipeline incremental có checkpoint, retry và cơ chế chạy lại không tạo dữ liệu trùng. Luồng log ứng dụng cần chuẩn hóa schema trước khi phục vụ dashboard vận hành. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-de-07-05`: Trong tạo pipeline log ứng dụng cho dashboard vận hành, ứng viên thiết kế grain, khóa fact-dimension và kiểm tra null, unique cùng referential integrity. Luồng log ứng dụng cần chuẩn hóa schema trước khi phục vụ dashboard vận hành. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-de-07-06`: Trong tạo pipeline log ứng dụng cho dashboard vận hành, ứng viên quản lý mã bằng Git, chạy tác vụ trên Linux và đóng gói môi trường bằng Docker. Luồng log ứng dụng cần chuẩn hóa schema trước khi phục vụ dashboard vận hành. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-de-07-07`: Ở phần mở rộng của tạo pipeline log ứng dụng cho dashboard vận hành, ứng viên áp dụng Có orchestration. và ghi lại kết quả thử nghiệm riêng. Luồng log ứng dụng cần chuẩn hóa schema trước khi phục vụ dashboard vận hành. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-de-07-08`: Phạm vi kỹ thuật của tạo pipeline log ứng dụng cho dashboard vận hành: Luồng cơ bản hoạt động nhưng mới kiểm tra một số trường hợp phổ biến. Luồng log ứng dụng cần chuẩn hóa schema trước khi phục vụ dashboard vận hành. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-de-07-09`: Cách ra quyết định trong tạo pipeline log ứng dụng cho dashboard vận hành: Mục tiêu và kết quả được nêu, phần đối chiếu độc lập còn thiếu. Luồng log ứng dụng cần chuẩn hóa schema trước khi phục vụ dashboard vận hành. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-de-07-10`: Bàn giao cho tạo pipeline log ứng dụng cho dashboard vận hành: Đầu ra chạy lại được trên một bộ mẫu cố định. Luồng log ứng dụng cần chuẩn hóa schema trước khi phục vụ dashboard vận hành. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-de-07-11`: Tài liệu của tạo pipeline log ứng dụng cho dashboard vận hành: README rõ lệnh chính nhưng phần quyết định kỹ thuật còn ngắn. Luồng log ứng dụng cần chuẩn hóa schema trước khi phục vụ dashboard vận hành. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.

Trạng thái yêu cầu bắt buộc:

- `de-python`: `satisfied`; thông tin: ev-s7v2-de-07-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-sql`: `satisfied`; thông tin: ev-s7v2-de-07-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-pipeline`: `satisfied`; thông tin: ev-s7v2-de-07-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-data-model-quality`: `satisfied`; thông tin: ev-s7v2-de-07-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-delivery-workflow`: `satisfied`; thông tin: ev-s7v2-de-07-06; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 27/30 |
| `de-technical-specialization` | 13/25 |
| `de-role-capability` | 10/20 |
| `projects-and-impact` | 8/15 |
| `communication-and-evidence-quality` | 9/10 |

Tổng điểm: **67/100**

Nhãn nháp: **needs_review**

Lý do vào review: lower-threshold-boundary

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-de-08 — Junior Data Engineer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `upper_boundary`

Tóm tắt CV: Pipeline học tập cần incremental load và backfill không làm thay đổi kết quả cũ. Hồ sơ khá tốt và nằm gần ngưỡng Pass nên cần kiểm tra tính ổn định của quyết định. Mục tiêu ứng tuyển là Junior Data Engineer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-de-08-01`: Hoàn thành chương trình định hướng Kỹ thuật dữ liệu và hệ thống thông tin với đồ án tổng hợp xây luồng incremental cho dữ liệu học tập. Pipeline học tập cần incremental load và backfill không làm thay đổi kết quả cũ. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-de-08-02`: Trong xây luồng incremental cho dữ liệu học tập, ứng viên viết Python theo module để đọc nhiều nguồn, chuẩn hóa bản ghi và ghi log lỗi theo batch. Pipeline học tập cần incremental load và backfill không làm thay đổi kết quả cũ. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-de-08-03`: Trong xây luồng incremental cho dữ liệu học tập, ứng viên dùng SQL với CTE, hàm cửa sổ và execution plan để biến đổi dữ liệu dung lượng vừa. Pipeline học tập cần incremental load và backfill không làm thay đổi kết quả cũ. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-de-08-04`: Trong xây luồng incremental cho dữ liệu học tập, ứng viên xây pipeline incremental có checkpoint, retry và cơ chế chạy lại không tạo dữ liệu trùng. Pipeline học tập cần incremental load và backfill không làm thay đổi kết quả cũ. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-de-08-05`: Trong xây luồng incremental cho dữ liệu học tập, ứng viên thiết kế grain, khóa fact-dimension và kiểm tra null, unique cùng referential integrity. Pipeline học tập cần incremental load và backfill không làm thay đổi kết quả cũ. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-de-08-06`: Trong xây luồng incremental cho dữ liệu học tập, ứng viên quản lý mã bằng Git, chạy tác vụ trên Linux và đóng gói môi trường bằng Docker. Pipeline học tập cần incremental load và backfill không làm thay đổi kết quả cũ. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-de-08-07`: Ở phần mở rộng của xây luồng incremental cho dữ liệu học tập, ứng viên áp dụng Có orchestration. và ghi lại kết quả thử nghiệm riêng. Pipeline học tập cần incremental load và backfill không làm thay đổi kết quả cũ. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-de-08-08`: Ở phần mở rộng của xây luồng incremental cho dữ liệu học tập, ứng viên áp dụng Có cloud storage hoặc cloud warehouse. và ghi lại kết quả thử nghiệm riêng. Pipeline học tập cần incremental load và backfill không làm thay đổi kết quả cũ. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-de-08-09`: Phạm vi kỹ thuật của xây luồng incremental cho dữ liệu học tập: Luồng chính và các lỗi thường gặp được xử lý bằng kiểm tra có thể chạy lại. Pipeline học tập cần incremental load và backfill không làm thay đổi kết quả cũ. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-de-08-10`: Cách ra quyết định trong xây luồng incremental cho dữ liệu học tập: Lựa chọn kỹ thuật có lý do và ghi nhận một giới hạn đáng chú ý. Pipeline học tập cần incremental load và backfill không làm thay đổi kết quả cũ. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-de-08-11`: Bàn giao cho xây luồng incremental cho dữ liệu học tập: Có dữ liệu mẫu, kết quả đối chiếu và hướng dẫn tái tạo. Pipeline học tập cần incremental load và backfill không làm thay đổi kết quả cũ. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.
- `ev-s7v2-de-08-12`: Tài liệu của xây luồng incremental cho dữ liệu học tập: Tài liệu rõ cách chạy nhưng phần giải thích một số quyết định còn cô đọng. Pipeline học tập cần incremental load và backfill không làm thay đổi kết quả cũ. Kết luận chỉ giới hạn trong phạm vi mẫu đã quan sát và không suy diễn quá mức.

Trạng thái yêu cầu bắt buộc:

- `de-python`: `satisfied`; thông tin: ev-s7v2-de-08-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-sql`: `satisfied`; thông tin: ev-s7v2-de-08-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-pipeline`: `satisfied`; thông tin: ev-s7v2-de-08-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-data-model-quality`: `satisfied`; thông tin: ev-s7v2-de-08-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-delivery-workflow`: `satisfied`; thông tin: ev-s7v2-de-08-06; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `de-technical-specialization` | 18/25 |
| `de-role-capability` | 15/20 |
| `projects-and-impact` | 12/15 |
| `communication-and-evidence-quality` | 7/10 |

Tổng điểm: **82/100**

Nhãn nháp: **needs_review**

Lý do vào review: upper-threshold-boundary

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-de-09 — Junior Data Engineer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `transferable`

Tóm tắt CV: Ứng viên chuyển từ SQL phân tích sang xây pipeline có orchestration và quan sát lỗi. Ứng viên chuyển từ lĩnh vực gần và chứng minh được năng lực tương đương qua dự án mới. Mục tiêu ứng tuyển là Junior Data Engineer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-de-09-01`: Hoàn thành chương trình định hướng Kỹ thuật dữ liệu và hệ thống thông tin với đồ án tổng hợp chuyển kinh nghiệm SQL phân tích sang data engineering. Ứng viên chuyển từ SQL phân tích sang xây pipeline có orchestration và quan sát lỗi. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-de-09-02`: Trong chuyển kinh nghiệm SQL phân tích sang data engineering, ứng viên viết Python theo module để đọc nhiều nguồn, chuẩn hóa bản ghi và ghi log lỗi theo batch. Ứng viên chuyển từ SQL phân tích sang xây pipeline có orchestration và quan sát lỗi. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-de-09-03`: Trong chuyển kinh nghiệm SQL phân tích sang data engineering, ứng viên dùng SQL với CTE, hàm cửa sổ và execution plan để biến đổi dữ liệu dung lượng vừa. Ứng viên chuyển từ SQL phân tích sang xây pipeline có orchestration và quan sát lỗi. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-de-09-04`: Trong chuyển kinh nghiệm SQL phân tích sang data engineering, ứng viên xây pipeline incremental có checkpoint, retry và cơ chế chạy lại không tạo dữ liệu trùng. Ứng viên chuyển từ SQL phân tích sang xây pipeline có orchestration và quan sát lỗi. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-de-09-05`: Trong chuyển kinh nghiệm SQL phân tích sang data engineering, ứng viên thiết kế grain, khóa fact-dimension và kiểm tra null, unique cùng referential integrity. Ứng viên chuyển từ SQL phân tích sang xây pipeline có orchestration và quan sát lỗi. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-de-09-06`: Trong chuyển kinh nghiệm SQL phân tích sang data engineering, ứng viên quản lý mã bằng Git, chạy tác vụ trên Linux và đóng gói môi trường bằng Docker. Ứng viên chuyển từ SQL phân tích sang xây pipeline có orchestration và quan sát lỗi. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-de-09-07`: Ở phần mở rộng của chuyển kinh nghiệm SQL phân tích sang data engineering, ứng viên áp dụng Có orchestration. và ghi lại kết quả thử nghiệm riêng. Ứng viên chuyển từ SQL phân tích sang xây pipeline có orchestration và quan sát lỗi. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-de-09-08`: Phạm vi kỹ thuật của chuyển kinh nghiệm SQL phân tích sang data engineering: Kiến thức nền từ lĩnh vực gần được áp dụng vào một sản phẩm đúng vai trò mục tiêu. Ứng viên chuyển từ SQL phân tích sang xây pipeline có orchestration và quan sát lỗi. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.
- `ev-s7v2-de-09-09`: Cách ra quyết định trong chuyển kinh nghiệm SQL phân tích sang data engineering: Hồ sơ phân biệt rõ phần kinh nghiệm chuyển đổi và phần mới học. Ứng viên chuyển từ SQL phân tích sang xây pipeline có orchestration và quan sát lỗi. Ứng viên phân biệt rõ phần tự thực hiện với phần được hướng dẫn trong nhóm.
- `ev-s7v2-de-09-10`: Bàn giao cho chuyển kinh nghiệm SQL phân tích sang data engineering: Prototype chạy được, có kiểm tra và đầu ra đo được nhưng chưa qua môi trường thực tập. Ứng viên chuyển từ SQL phân tích sang xây pipeline có orchestration và quan sát lỗi. Một lần kiểm tra hồi quy được thực hiện sau khi thay đổi cách xử lý chính.
- `ev-s7v2-de-09-11`: Tài liệu của chuyển kinh nghiệm SQL phân tích sang data engineering: Tài liệu nêu rõ phạm vi kinh nghiệm trực tiếp và kinh nghiệm tương đương. Ứng viên chuyển từ SQL phân tích sang xây pipeline có orchestration và quan sát lỗi. Rủi ro sai lệch dữ liệu được ghi nhận và gắn với bước kiểm tra tương ứng.

Trạng thái yêu cầu bắt buộc:

- `de-python`: `satisfied`; thông tin: ev-s7v2-de-09-02; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-sql`: `satisfied`; thông tin: ev-s7v2-de-09-03; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-pipeline`: `satisfied`; thông tin: ev-s7v2-de-09-04; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-data-model-quality`: `satisfied`; thông tin: ev-s7v2-de-09-05; Có mô tả thao tác trực tiếp và đầu ra trong dự án.
- `de-delivery-workflow`: `satisfied`; thông tin: ev-s7v2-de-09-06; Có mô tả thao tác trực tiếp và đầu ra trong dự án.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `de-technical-specialization` | 16/25 |
| `de-role-capability` | 14/20 |
| `projects-and-impact` | 10/15 |
| `communication-and-evidence-quality` | 9/10 |

Tổng điểm: **79/100**

Nhãn nháp: **waitlist**

Lý do vào review: không có

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.

## s7v2-pair-de-10 — Junior Data Engineer - Yêu cầu tiêu chuẩn

Kịch bản kiểm thử: `hard_negative`

Tóm tắt CV: Hồ sơ chỉ liệt kê nền tảng dữ liệu mà chưa nêu nguồn, đích hoặc lịch chạy cụ thể. Hồ sơ chủ yếu liệt kê khóa học và công cụ nhưng không mô tả nhiệm vụ hay sản phẩm đã làm. Mục tiêu ứng tuyển là Junior Data Engineer - Yêu cầu tiêu chuẩn.

Thông tin đánh giá chính:

- `ev-s7v2-de-10-01`: Hoàn thành chương trình định hướng Kỹ thuật dữ liệu và hệ thống thông tin với đồ án tổng hợp liệt kê nền tảng dữ liệu từ các khóa học trực tuyến. Hồ sơ chỉ liệt kê nền tảng dữ liệu mà chưa nêu nguồn, đích hoặc lịch chạy cụ thể. Phạm vi dữ liệu và tiêu chí hoàn tất được ghi trước khi triển khai.
- `ev-s7v2-de-10-02`: Đã hoàn thành bài học giới thiệu về Python và tự ghi tên công cụ trong danh sách kỹ năng. Hồ sơ chỉ liệt kê nền tảng dữ liệu mà chưa nêu nguồn, đích hoặc lịch chạy cụ thể. Ứng viên lưu một bộ đầu vào nhỏ để người khác có thể tái hiện kết quả.
- `ev-s7v2-de-10-03`: Đã hoàn thành bài học giới thiệu về SQL và tự ghi tên công cụ trong danh sách kỹ năng. Hồ sơ chỉ liệt kê nền tảng dữ liệu mà chưa nêu nguồn, đích hoặc lịch chạy cụ thể. Một trường hợp biên được tách riêng và đối chiếu với kết quả mong đợi.
- `ev-s7v2-de-10-04`: Đã hoàn thành bài học giới thiệu về ETL hoặc ELT và tự ghi tên công cụ trong danh sách kỹ năng. Hồ sơ chỉ liệt kê nền tảng dữ liệu mà chưa nêu nguồn, đích hoặc lịch chạy cụ thể. Quyết định kỹ thuật có nêu phương án đã loại cùng lý do lựa chọn.
- `ev-s7v2-de-10-05`: Đã hoàn thành bài học giới thiệu về Mô hình dữ liệu và chất lượng và tự ghi tên công cụ trong danh sách kỹ năng. Hồ sơ chỉ liệt kê nền tảng dữ liệu mà chưa nêu nguồn, đích hoặc lịch chạy cụ thể. Số liệu trước và sau được tính bằng cùng một định nghĩa để tránh so sánh lệch.
- `ev-s7v2-de-10-06`: Đã hoàn thành bài học giới thiệu về Git Linux Docker và tự ghi tên công cụ trong danh sách kỹ năng. Hồ sơ chỉ liệt kê nền tảng dữ liệu mà chưa nêu nguồn, đích hoặc lịch chạy cụ thể. Luồng lỗi phổ biến được tái hiện bằng dữ liệu giả lập không chứa thông tin cá nhân.
- `ev-s7v2-de-10-07`: Ở phần mở rộng của liệt kê nền tảng dữ liệu từ các khóa học trực tuyến, ứng viên áp dụng Có orchestration. và ghi lại kết quả thử nghiệm riêng. Hồ sơ chỉ liệt kê nền tảng dữ liệu mà chưa nêu nguồn, đích hoặc lịch chạy cụ thể. Tài liệu bàn giao ghi lệnh chạy, giả định môi trường và giới hạn còn tồn tại.
- `ev-s7v2-de-10-08`: Ở phần mở rộng của liệt kê nền tảng dữ liệu từ các khóa học trực tuyến, ứng viên áp dụng Có cloud storage hoặc cloud warehouse. và ghi lại kết quả thử nghiệm riêng. Hồ sơ chỉ liệt kê nền tảng dữ liệu mà chưa nêu nguồn, đích hoặc lịch chạy cụ thể. Kết quả trung gian được lưu dưới dạng có thể kiểm tra thay vì chỉ chụp màn hình.

Trạng thái yêu cầu bắt buộc:

- `de-python`: `missing`; thông tin: ev-s7v2-de-10-02; Hồ sơ không đề cập đủ thông tin để xác nhận yêu cầu này.
- `de-sql`: `missing`; thông tin: ev-s7v2-de-10-03; Hồ sơ không đề cập đủ thông tin để xác nhận yêu cầu này.
- `de-pipeline`: `missing`; thông tin: ev-s7v2-de-10-04; Hồ sơ không đề cập đủ thông tin để xác nhận yêu cầu này.
- `de-data-model-quality`: `missing`; thông tin: ev-s7v2-de-10-05; Hồ sơ không đề cập đủ thông tin để xác nhận yêu cầu này.
- `de-delivery-workflow`: `missing`; thông tin: ev-s7v2-de-10-06; Hồ sơ không đề cập đủ thông tin để xác nhận yêu cầu này.

Điểm theo tiêu chí:

| Tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 14/30 |
| `de-technical-specialization` | 9/25 |
| `de-role-capability` | 6/20 |
| `projects-and-impact` | 3/15 |
| `communication-and-evidence-quality` | 4/10 |

Tổng điểm: **36/100**

Nhãn nháp: **needs_review**

Lý do vào review: missing-critical-evidence, low-score-without-explicit-critical-unsatisfied

Lý do tổng hợp: Điểm và nhãn nháp áp dụng Runtime v2 đã khóa với ngưỡng Waitlist 67, Pass 82, vùng review 65–69 và 80–84. Hồ sơ synthetic này chưa phải ground truth cho tới khi hoàn tất human review và khóa Gold.
