# Thử nghiệm CV thực tế đã ẩn danh tại Stage 8

## Mục đích

Artifact này minh họa cách một CV có nguồn từ bên ngoài được chuyển thủ công sang `CVProfile`, tương đương contract mà Parser Agent sẽ phải cung cấp. Nó phục vụ kiểm tra luồng kỹ thuật và thảo luận kết quả; không được dùng làm dữ liệu huấn luyện, nhãn chuẩn hoặc metric Stage 7.

## Chính sách riêng tư

Nội dung đã được diễn đạt lại và loại bỏ tên cá nhân, cơ sở đào tạo, tổ chức, liên kết tài khoản, tên dự án, ngày tháng chính xác, thành tích riêng và số liệu có khả năng nhận diện. Artifact chỉ giữ các tín hiệu nghề nghiệp cần cho việc đối chiếu rubric.

File `data/samples/external_trials/cv_external_anonymized_ai_data_engineering_v1.json` có `source_type=manual`, mọi thông tin đều `is_verified=false`, đồng thời mang cảnh báo `manual-anonymized-adaptation`. Vì vậy nó không được mô tả như output Parser thật hoặc thông tin ứng viên đã xác minh.

## Vị trí thử nghiệm

Vị trí đầu tiên được chọn là Junior Data Engineer vì hồ sơ có nền tảng Data Engineering, Python, database, pipeline nạp và truy hồi dữ liệu, automated testing và Docker. Các giới hạn phải được giữ nguyên khi đánh giá:

- Không mô tả trực tiếp SQL trung cấp như CTE, window function, execution plan hoặc index.
- Pipeline RAG không tự động tương đương pipeline ETL hoặc ELT theo batch.
- Không có mô tả rõ về warehouse model, fact/dimension hoặc data-quality checks.
- Docker và automated tests có căn cứ, nhưng Git/Linux/pull-request workflow chưa được nêu trực tiếp.

Do đó `Needs Review` sẽ là kết quả hợp lý nếu L1 hoặc L3 không thể xác nhận các yêu cầu bắt buộc này. Điểm cao ở Python, dự án và giao tiếp không được phép che khuất requirement còn thiếu.

## Phạm vi kết luận

Một lần chạy trên artifact này chỉ cho thấy hệ thống xử lý được CV gần với cách viết thực tế. Nó không đo accuracy, không đánh giá Parser và không thay thế một dataset thực tế đã có consent, ẩn danh, human review và phân chia development/test độc lập.

## Kết quả offline Runtime v2

Lần chạy bằng `deterministic_fake` không gọi provider và trả:

| Thành phần | Kết quả |
| --- | ---: |
| L1 | 60,00 |
| L2 | 38,62 |
| L3 mô phỏng | 100,00 |
| Điểm tổng | 73,59 |
| Đề xuất | `Needs Review` |

Quality gate được kích hoạt bởi `missing-critical-evidence` và `large-level-disagreement`. Điểm L3 bằng 100 chỉ phản ánh adapter offline thấy hồ sơ có nhiều mục thông tin và độ phủ phần CV cao; nó không có nghĩa ứng viên đáp ứng 100% yêu cầu Data Engineer.

L1 đánh dấu `de-python`, `de-sql` và `de-pipeline` là `satisfied`; `de-data-model-quality` và `de-delivery-workflow` là `missing`. Human review cho thấy hai kết quả L1 cần được hiểu thận trọng:

- `de-sql` bị nhận là đạt từ các tên database có chứa chuỗi SQL, dù CV chưa mô tả CTE, window function, execution plan, index hay truy vấn kiểm tra dữ liệu.
- `de-pipeline` bị nhận là đạt từ retrieval pipeline của RAG, dù đây chưa chắc là ETL/ELT hoặc batch data pipeline mà JD yêu cầu.

Vì vậy `Needs Review` là tuyến an toàn phù hợp cho case này, nhưng requirement status chi tiết chưa đủ chính xác để dùng tự động. Case cho thấy dữ liệu gần thực tế không mặc nhiên giúp accuracy cao hơn frozen test; cách diễn đạt nghề nghiệp chồng lấn có thể tiếp tục gây false positive ở L1.
