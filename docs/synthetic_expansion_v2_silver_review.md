# Kết quả review và chẩn đoán synthetic expansion v2

## Kết quả đã ghi nhận

Người dùng đã xác nhận yêu cầu, JD, CV, trạng thái yêu cầu, năm nhóm điểm, draft label và rationale cho toàn bộ 250 cặp. Bản Bronze được giữ nguyên; quyết định review được ghi vào bản Silver riêng để bảo toàn đề xuất ban đầu và audit trail.

| Thành phần | Kết quả |
| --- | ---: |
| CV synthetic | 50 |
| Job Profile/JD | 25 |
| Rubric | 25 |
| Cặp đã duyệt | 250 |
| Reviewer | 1 định danh giả danh |
| Silver | 250 |
| QC error | 0 |
| QC warning | 0 |

Phân bố nhãn sau review là 50 `Pass`, 25 `Waitlist`, 155 `Needs Review` và 20 `Reject`. Không có score override; `final_label` giữ nguyên nhãn dự thảo đã được người dùng xác nhận.

Tiêu chí thứ năm được đổi tên hiển thị thành `Độ rõ ràng và khả năng kiểm tra của thông tin trong CV`. ID `communication-and-evidence-quality`, trọng số 10, điểm và ý nghĩa nghiệp vụ không thay đổi. Artifact lịch sử của dataset cũ không bị sửa.

## Group split Silver

Split dùng SHA-256 ranking theo vai trò và ứng viên. Mọi cặp của cùng một ứng viên nằm trong cùng partition.

| Partition | Ứng viên | Cặp | Mục đích |
| --- | ---: | ---: | --- |
| Development | 30 | 150 | Tuning có kiểm soát và phân tích lỗi |
| Held-out diagnostic | 20 | 100 | Giữ riêng; chưa chạy và không phải kết quả cuối |

Mỗi vai trò có 6 ứng viên development và 4 ứng viên held-out. Split không tạo frozen test. Muốn dùng cho đánh giá chính thức phải hoàn thành điều kiện Gold và khóa kế hoạch đánh giá trước khi chạy held-out.

## Chẩn đoán development

Chẩn đoán đã chạy trên đúng 150 cặp development với L1 theo yêu cầu v2, E5 cục bộ và L3 fake xác định. Google AI Studio không được gọi.

| Chỉ số | Kết quả |
| --- | ---: |
| Accuracy | 0,547 |
| Macro-F1 | 0,291 |
| L1 requirement-status match | 1,000 |
| Trung bình L2 | 100,0 |
| Số cặp có L2 bằng 100 | 150/150 |
| L3 total-score MAE | 27,8 |
| Needs Review recall | 0,536 |
| Review rate | 0,400 |
| False Reject | 0 |
| Unsafe Pass | 45 |

Kết quả cho thấy pipeline chạy đủ năm vai trò nhưng chưa đạt chất lượng để đóng băng cấu hình mở rộng. L1 khớp hoàn toàn một phần vì rule và dữ liệu synthetic dùng cùng vocabulary của generator, nên chưa chứng minh khả năng khái quát. L2 bị bão hòa hoàn toàn. L3 fake phù hợp cho test xác định nhưng không phù hợp để đại diện cho chất lượng suy luận thực tế.

## Hiệu chỉnh L2 theo độ bao phủ

L2 mới tách mỗi tiêu chí thành các truy vấn theo từng yêu cầu hoặc trách nhiệm, chấm từng truy vấn riêng, áp dụng trọng số theo mục CV và tính cả yêu cầu không được tìm thấy là phần độ bao phủ còn thiếu. Chế độ L2 cũ vẫn được giữ để bảo toàn các luồng lịch sử; cấu hình mới chỉ được thử trên 150 cặp development.

| Chỉ số của phương án `coverage-70-95-v1` | Kết quả |
| --- | ---: |
| Trung bình L2 | 61,112 |
| Độ lệch chuẩn L2 | 14,095 |
| Khoảng điểm L2 | 28,12–72,00 |
| Số cặp có L2 bằng 100 | 0/150 |
| MAE giữa tổng điểm L2 và điểm người duyệt | 10,010 |
| Tương quan theo nhóm ứng viên | 0,757 |
| Vai trò có hồ sơ mạnh cao hơn hard negative | 5/5 |
| Biên phân tách mạnh–hard negative | 36,796–41,888 |

Lỗi bão hòa 150/150 điểm 100 đã được loại bỏ. L2 đã phân biệt rõ hồ sơ đúng vai trò với hard negative trong cả năm vai trò, nhưng chưa được xem là cấu hình hybrid đã đóng băng. Candidate floor 0,65 bị loại vì tạo 5 `unsafe Pass`; candidate 0,70 có zero `unsafe Pass` và zero false Reject. Diagnostic vẫn dùng L3 fake và cả 150 case của candidate được đề xuất đều vào `Needs Review`; 144 case có chênh lệch L1/L2/L3 từ 25 điểm trở lên, các case còn lại kích hoạt quality gate khác. Điều này không phải bằng chứng rằng L2 sai trong mọi case: L2 đo mức liên quan và độ bao phủ ngữ nghĩa, không xác minh tính đúng sai của lời khai hoặc tự xử lý phủ định thay cho L1/L3.

Report đầy đủ nằm tại `evaluation/reports/synthetic_expansion_v2_l2_tuning_v1.json`. Report ghi rõ `is_final_performance: false`, không gọi provider trả phí, không chạy held-out và không chạy frozen test cũ.

Người dùng đã duyệt `coverage-70-95-v1` làm L2 development candidate cho nhánh mở rộng năm vai trò. Quyết định này chấp nhận các hạn chế của synthetic Silver development nhưng không đóng băng cấu hình hybrid và không cho phép chạy held-out hoặc frozen test.

## Phạm vi không bị thay đổi

- 100 cặp held-out Silver chưa có classifier result.
- 10 frozen-test case Stage 6 cũ chưa được chạy.
- 30 CV cũ, annotation đã duyệt, split và report Stage 6 cũ không bị sửa.
- Kết quả này là development diagnostic, không phải số liệu hiệu năng cuối và không được dùng để tuyên bố hệ thống hỗ trợ production cho năm vai trò.

## Bước kế tiếp được khuyến nghị

Tiếp theo cần review phương án L2 được đề xuất, rồi so sánh với một reranker hoặc phương pháp semantic matching thứ hai nếu muốn tăng khả năng phân biệt các case cùng vai trò. Sau đó mới chạy L3 provider thật trên một mẫu development được chọn trước, có giới hạn request và chi phí. Chỉ sau khi ba vai trò mới có rubric/runtime configuration chính thức và dữ liệu đạt Gold mới được cân nhắc khóa một frozen test riêng cho nhánh mở rộng.
