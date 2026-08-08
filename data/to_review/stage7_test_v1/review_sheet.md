# Phiếu duyệt test set Stage 7 v1

Bộ này có 50 cặp mới, mỗi vai trò 10 cặp và chỉ dùng JD standard đã khóa. Tất cả nhãn hiện là draft; classifier chưa được chạy và chưa có API LLM nào được gọi.

Với mỗi case, hãy kiểm tra trạng thái từng yêu cầu bắt buộc, năm nhóm điểm, tổng điểm, nhãn dự kiến và lý do. Nếu đồng ý toàn bộ, có thể duyệt bằng một câu xác nhận chung; nếu không, ghi rõ ID case và giá trị cần sửa.

| Case | Vai trò | Tổng | Nhãn nháp | Lý do review |
| --- | --- | ---: | --- | --- |
| `s7-pair-da-01` | data_analyst | 95 | pass | không có |
| `s7-pair-da-02` | data_analyst | 89 | pass | không có |
| `s7-pair-da-03` | data_analyst | 78 | waitlist | không có |
| `s7-pair-da-04` | data_analyst | 64 | needs_review | missing-critical-evidence, low-score-without-explicit-critical-unsatisfied |
| `s7-pair-da-05` | data_analyst | 68 | needs_review | conflicting-critical-evidence, lower-threshold-boundary, low-score-without-explicit-critical-unsatisfied |
| `s7-pair-da-06` | data_analyst | 41 | reject | không có |
| `s7-pair-da-07` | data_analyst | 70 | needs_review | lower-threshold-boundary |
| `s7-pair-da-08` | data_analyst | 85 | needs_review | upper-threshold-boundary |
| `s7-pair-da-09` | data_analyst | 79 | waitlist | không có |
| `s7-pair-da-10` | data_analyst | 36 | needs_review | missing-critical-evidence, low-score-without-explicit-critical-unsatisfied |
| `s7-pair-be-01` | python_backend | 95 | pass | không có |
| `s7-pair-be-02` | python_backend | 89 | pass | không có |
| `s7-pair-be-03` | python_backend | 78 | waitlist | không có |
| `s7-pair-be-04` | python_backend | 64 | needs_review | missing-critical-evidence, low-score-without-explicit-critical-unsatisfied |
| `s7-pair-be-05` | python_backend | 68 | needs_review | conflicting-critical-evidence, lower-threshold-boundary, low-score-without-explicit-critical-unsatisfied |
| `s7-pair-be-06` | python_backend | 41 | reject | không có |
| `s7-pair-be-07` | python_backend | 70 | needs_review | lower-threshold-boundary |
| `s7-pair-be-08` | python_backend | 85 | needs_review | upper-threshold-boundary |
| `s7-pair-be-09` | python_backend | 79 | waitlist | không có |
| `s7-pair-be-10` | python_backend | 36 | needs_review | missing-critical-evidence, low-score-without-explicit-critical-unsatisfied |
| `s7-pair-fe-01` | frontend | 95 | pass | không có |
| `s7-pair-fe-02` | frontend | 89 | pass | không có |
| `s7-pair-fe-03` | frontend | 78 | waitlist | không có |
| `s7-pair-fe-04` | frontend | 64 | needs_review | missing-critical-evidence, low-score-without-explicit-critical-unsatisfied |
| `s7-pair-fe-05` | frontend | 68 | needs_review | conflicting-critical-evidence, lower-threshold-boundary, low-score-without-explicit-critical-unsatisfied |
| `s7-pair-fe-06` | frontend | 41 | reject | không có |
| `s7-pair-fe-07` | frontend | 70 | needs_review | lower-threshold-boundary |
| `s7-pair-fe-08` | frontend | 85 | needs_review | upper-threshold-boundary |
| `s7-pair-fe-09` | frontend | 79 | waitlist | không có |
| `s7-pair-fe-10` | frontend | 36 | needs_review | missing-critical-evidence, low-score-without-explicit-critical-unsatisfied |
| `s7-pair-qa-01` | qa_engineer | 95 | pass | không có |
| `s7-pair-qa-02` | qa_engineer | 89 | pass | không có |
| `s7-pair-qa-03` | qa_engineer | 78 | waitlist | không có |
| `s7-pair-qa-04` | qa_engineer | 64 | needs_review | missing-critical-evidence, low-score-without-explicit-critical-unsatisfied |
| `s7-pair-qa-05` | qa_engineer | 68 | needs_review | conflicting-critical-evidence, lower-threshold-boundary, low-score-without-explicit-critical-unsatisfied |
| `s7-pair-qa-06` | qa_engineer | 41 | reject | không có |
| `s7-pair-qa-07` | qa_engineer | 70 | needs_review | lower-threshold-boundary |
| `s7-pair-qa-08` | qa_engineer | 85 | needs_review | upper-threshold-boundary |
| `s7-pair-qa-09` | qa_engineer | 79 | waitlist | không có |
| `s7-pair-qa-10` | qa_engineer | 36 | needs_review | missing-critical-evidence, low-score-without-explicit-critical-unsatisfied |
| `s7-pair-de-01` | data_engineer | 95 | pass | không có |
| `s7-pair-de-02` | data_engineer | 89 | pass | không có |
| `s7-pair-de-03` | data_engineer | 78 | waitlist | không có |
| `s7-pair-de-04` | data_engineer | 64 | needs_review | missing-critical-evidence, low-score-without-explicit-critical-unsatisfied |
| `s7-pair-de-05` | data_engineer | 68 | needs_review | conflicting-critical-evidence, lower-threshold-boundary, low-score-without-explicit-critical-unsatisfied |
| `s7-pair-de-06` | data_engineer | 41 | reject | không có |
| `s7-pair-de-07` | data_engineer | 70 | needs_review | lower-threshold-boundary |
| `s7-pair-de-08` | data_engineer | 85 | needs_review | upper-threshold-boundary |
| `s7-pair-de-09` | data_engineer | 79 | waitlist | không có |
| `s7-pair-de-10` | data_engineer | 36 | needs_review | missing-critical-evidence, low-score-without-explicit-critical-unsatisfied |

## s7-pair-da-01

- Vị trí: Junior Data Analyst - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-da-01`
- Tóm tắt: Hồ sơ trình bày một sản phẩm hoàn chỉnh, có số liệu đối chiếu và tài liệu tái tạo. Mục tiêu ứng tuyển là Junior Data Analyst - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 95
- Nhãn nháp: `pass`
- Lý do review: không có

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `da-sql` | `satisfied` | Trong phân tích tỷ lệ khách hàng quay lại của nền tảng bán lẻ, ứng viên tự viết truy vấn nhiều bảng, dùng CTE và hàm cửa sổ để đối soát số liệu theo từng kỳ. |
| `da-analysis-language` | `satisfied` | Trong phân tích tỷ lệ khách hàng quay lại của nền tảng bán lẻ, ứng viên dùng pandas để chuẩn hóa kiểu dữ liệu, xử lý giá trị thiếu và đóng gói notebook có thể chạy lại. |
| `da-bi-reporting` | `satisfied` | Trong phân tích tỷ lệ khách hàng quay lại của nền tảng bán lẻ, ứng viên dựng dashboard có data model, bộ lọc chi tiết và tài liệu định nghĩa từng KPI. |
| `da-business-analysis` | `satisfied` | Trong phân tích tỷ lệ khách hàng quay lại của nền tảng bán lẻ, ứng viên chuyển câu hỏi kinh doanh thành chỉ số, phân tích nguyên nhân và nêu khuyến nghị kèm giới hạn. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `da-technical-specialization` | 24/25 |
| `da-role-capability` | 18/20 |
| `projects-and-impact` | 14/15 |
| `communication-and-evidence-quality` | 9/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-da-02

- Vị trí: Junior Data Analyst - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-da-02`
- Tóm tắt: Hồ sơ có dự án junior hoàn chỉnh, thông tin nhất quán và đầu ra có thể kiểm tra. Mục tiêu ứng tuyển là Junior Data Analyst - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 89
- Nhãn nháp: `pass`
- Lý do review: không có

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `da-sql` | `satisfied` | Trong theo dõi tồn kho và thời gian giao hàng tại ba kho mô phỏng, ứng viên tự viết truy vấn nhiều bảng, dùng CTE và hàm cửa sổ để đối soát số liệu theo từng kỳ. |
| `da-analysis-language` | `satisfied` | Trong theo dõi tồn kho và thời gian giao hàng tại ba kho mô phỏng, ứng viên dùng pandas để chuẩn hóa kiểu dữ liệu, xử lý giá trị thiếu và đóng gói notebook có thể chạy lại. |
| `da-bi-reporting` | `satisfied` | Trong theo dõi tồn kho và thời gian giao hàng tại ba kho mô phỏng, ứng viên dựng dashboard có data model, bộ lọc chi tiết và tài liệu định nghĩa từng KPI. |
| `da-business-analysis` | `satisfied` | Trong theo dõi tồn kho và thời gian giao hàng tại ba kho mô phỏng, ứng viên chuyển câu hỏi kinh doanh thành chỉ số, phân tích nguyên nhân và nêu khuyến nghị kèm giới hạn. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `da-technical-specialization` | 22/25 |
| `da-role-capability` | 17/20 |
| `projects-and-impact` | 12/15 |
| `communication-and-evidence-quality` | 8/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-da-03

- Vị trí: Junior Data Analyst - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-da-03`
- Tóm tắt: Hồ sơ đáp ứng phần cốt lõi nhưng dự án mới giới hạn ở một luồng nghiệp vụ. Mục tiêu ứng tuyển là Junior Data Analyst - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 78
- Nhãn nháp: `waitlist`
- Lý do review: không có

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `da-sql` | `satisfied` | Trong đánh giá phễu đăng ký của ứng dụng học trực tuyến, ứng viên tự viết truy vấn nhiều bảng, dùng CTE và hàm cửa sổ để đối soát số liệu theo từng kỳ. |
| `da-analysis-language` | `satisfied` | Trong đánh giá phễu đăng ký của ứng dụng học trực tuyến, ứng viên dùng pandas để chuẩn hóa kiểu dữ liệu, xử lý giá trị thiếu và đóng gói notebook có thể chạy lại. |
| `da-bi-reporting` | `satisfied` | Trong đánh giá phễu đăng ký của ứng dụng học trực tuyến, ứng viên dựng dashboard có data model, bộ lọc chi tiết và tài liệu định nghĩa từng KPI. |
| `da-business-analysis` | `satisfied` | Trong đánh giá phễu đăng ký của ứng dụng học trực tuyến, ứng viên chuyển câu hỏi kinh doanh thành chỉ số, phân tích nguyên nhân và nêu khuyến nghị kèm giới hạn. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `da-technical-specialization` | 17/25 |
| `da-role-capability` | 14/20 |
| `projects-and-impact` | 9/15 |
| `communication-and-evidence-quality` | 8/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-da-04

- Vị trí: Junior Data Analyst - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-da-04`
- Tóm tắt: Hồ sơ mô tả một số phần việc liên quan nhưng không đề cập đầy đủ toàn bộ năng lực cốt lõi. Mục tiêu ứng tuyển là Junior Data Analyst - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 64
- Nhãn nháp: `needs_review`
- Lý do review: missing-critical-evidence, low-score-without-explicit-critical-unsatisfied

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `da-sql` | `missing` | Không có thông tin |
| `da-analysis-language` | `satisfied` | Trong tìm nguyên nhân gia tăng đơn hoàn trả theo nhóm sản phẩm, ứng viên dùng pandas để chuẩn hóa kiểu dữ liệu, xử lý giá trị thiếu và đóng gói notebook có thể chạy lại. |
| `da-bi-reporting` | `satisfied` | Trong tìm nguyên nhân gia tăng đơn hoàn trả theo nhóm sản phẩm, ứng viên dựng dashboard có data model, bộ lọc chi tiết và tài liệu định nghĩa từng KPI. |
| `da-business-analysis` | `satisfied` | Trong tìm nguyên nhân gia tăng đơn hoàn trả theo nhóm sản phẩm, ứng viên chuyển câu hỏi kinh doanh thành chỉ số, phân tích nguyên nhân và nêu khuyến nghị kèm giới hạn. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 20/30 |
| `da-technical-specialization` | 17/25 |
| `da-role-capability` | 13/20 |
| `projects-and-impact` | 8/15 |
| `communication-and-evidence-quality` | 6/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-da-05

- Vị trí: Junior Data Analyst - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-da-05`
- Tóm tắt: Hồ sơ kết hợp mô tả dự án và bản tự đánh giá có một điểm chưa nhất quán. Mục tiêu ứng tuyển là Junior Data Analyst - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 68
- Nhãn nháp: `needs_review`
- Lý do review: conflicting-critical-evidence, lower-threshold-boundary, low-score-without-explicit-critical-unsatisfied

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `da-sql` | `satisfied` | Trong đối chiếu chất lượng phục vụ của trung tâm hỗ trợ, ứng viên tự viết truy vấn nhiều bảng, dùng CTE và hàm cửa sổ để đối soát số liệu theo từng kỳ. |
| `da-analysis-language` | `conflicting` | Trong đối chiếu chất lượng phục vụ của trung tâm hỗ trợ, ứng viên dùng pandas để chuẩn hóa kiểu dữ liệu, xử lý giá trị thiếu và đóng gói notebook có thể chạy lại. / Ứng viên xác nhận chưa từng dùng Python hay R để xử lý dữ liệu. |
| `da-bi-reporting` | `satisfied` | Trong đối chiếu chất lượng phục vụ của trung tâm hỗ trợ, ứng viên dựng dashboard có data model, bộ lọc chi tiết và tài liệu định nghĩa từng KPI. |
| `da-business-analysis` | `satisfied` | Trong đối chiếu chất lượng phục vụ của trung tâm hỗ trợ, ứng viên chuyển câu hỏi kinh doanh thành chỉ số, phân tích nguyên nhân và nêu khuyến nghị kèm giới hạn. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 22/30 |
| `da-technical-specialization` | 17/25 |
| `da-role-capability` | 13/20 |
| `projects-and-impact` | 9/15 |
| `communication-and-evidence-quality` | 7/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-da-06

- Vị trí: Junior Data Analyst - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-da-06`
- Tóm tắt: Ứng viên chuyển hướng từ lĩnh vực gần và xác nhận chưa thực hành một năng lực bắt buộc. Mục tiêu ứng tuyển là Junior Data Analyst - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 41
- Nhãn nháp: `reject`
- Lý do review: không có

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `da-sql` | `unsatisfied` | Ứng viên xác nhận chưa từng viết truy vấn SQL có JOIN hoặc phép tổng hợp. |
| `da-analysis-language` | `satisfied` | Trong kiểm tra chênh lệch doanh thu giữa hệ thống bán hàng và kế toán, ứng viên dùng pandas để chuẩn hóa kiểu dữ liệu, xử lý giá trị thiếu và đóng gói notebook có thể chạy lại. |
| `da-bi-reporting` | `satisfied` | Trong kiểm tra chênh lệch doanh thu giữa hệ thống bán hàng và kế toán, ứng viên dựng dashboard có data model, bộ lọc chi tiết và tài liệu định nghĩa từng KPI. |
| `da-business-analysis` | `satisfied` | Trong kiểm tra chênh lệch doanh thu giữa hệ thống bán hàng và kế toán, ứng viên chuyển câu hỏi kinh doanh thành chỉ số, phân tích nguyên nhân và nêu khuyến nghị kèm giới hạn. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 10/30 |
| `da-technical-specialization` | 12/25 |
| `da-role-capability` | 9/20 |
| `projects-and-impact` | 5/15 |
| `communication-and-evidence-quality` | 5/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-da-07

- Vị trí: Junior Data Analyst - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-da-07`
- Tóm tắt: Hồ sơ vừa đủ yêu cầu cốt lõi nhưng mức độ sâu và phạm vi dự án còn hạn chế. Mục tiêu ứng tuyển là Junior Data Analyst - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 70
- Nhãn nháp: `needs_review`
- Lý do review: lower-threshold-boundary

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `da-sql` | `satisfied` | Trong xây báo cáo hiệu suất nhà bán hàng trên sàn thử nghiệm, ứng viên tự viết truy vấn nhiều bảng, dùng CTE và hàm cửa sổ để đối soát số liệu theo từng kỳ. |
| `da-analysis-language` | `satisfied` | Trong xây báo cáo hiệu suất nhà bán hàng trên sàn thử nghiệm, ứng viên dùng pandas để chuẩn hóa kiểu dữ liệu, xử lý giá trị thiếu và đóng gói notebook có thể chạy lại. |
| `da-bi-reporting` | `satisfied` | Trong xây báo cáo hiệu suất nhà bán hàng trên sàn thử nghiệm, ứng viên dựng dashboard có data model, bộ lọc chi tiết và tài liệu định nghĩa từng KPI. |
| `da-business-analysis` | `satisfied` | Trong xây báo cáo hiệu suất nhà bán hàng trên sàn thử nghiệm, ứng viên chuyển câu hỏi kinh doanh thành chỉ số, phân tích nguyên nhân và nêu khuyến nghị kèm giới hạn. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 28/30 |
| `da-technical-specialization` | 14/25 |
| `da-role-capability` | 11/20 |
| `projects-and-impact` | 8/15 |
| `communication-and-evidence-quality` | 9/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-da-08

- Vị trí: Junior Data Analyst - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-da-08`
- Tóm tắt: Hồ sơ khá tốt và nằm gần ngưỡng Pass nên cần kiểm tra tính ổn định của quyết định. Mục tiêu ứng tuyển là Junior Data Analyst - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 85
- Nhãn nháp: `needs_review`
- Lý do review: upper-threshold-boundary

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `da-sql` | `satisfied` | Trong đo mức kích hoạt tính năng mới theo cohort người dùng, ứng viên tự viết truy vấn nhiều bảng, dùng CTE và hàm cửa sổ để đối soát số liệu theo từng kỳ. |
| `da-analysis-language` | `satisfied` | Trong đo mức kích hoạt tính năng mới theo cohort người dùng, ứng viên dùng pandas để chuẩn hóa kiểu dữ liệu, xử lý giá trị thiếu và đóng gói notebook có thể chạy lại. |
| `da-bi-reporting` | `satisfied` | Trong đo mức kích hoạt tính năng mới theo cohort người dùng, ứng viên dựng dashboard có data model, bộ lọc chi tiết và tài liệu định nghĩa từng KPI. |
| `da-business-analysis` | `satisfied` | Trong đo mức kích hoạt tính năng mới theo cohort người dùng, ứng viên chuyển câu hỏi kinh doanh thành chỉ số, phân tích nguyên nhân và nêu khuyến nghị kèm giới hạn. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `da-technical-specialization` | 20/25 |
| `da-role-capability` | 16/20 |
| `projects-and-impact` | 12/15 |
| `communication-and-evidence-quality` | 7/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-da-09

- Vị trí: Junior Data Analyst - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-da-09`
- Tóm tắt: Ứng viên chuyển từ lĩnh vực gần và chứng minh được năng lực tương đương qua dự án mới. Mục tiêu ứng tuyển là Junior Data Analyst - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 79
- Nhãn nháp: `waitlist`
- Lý do review: không có

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `da-sql` | `satisfied` | Trong chuyển kinh nghiệm nghiên cứu định lượng sang phân tích sản phẩm, ứng viên tự viết truy vấn nhiều bảng, dùng CTE và hàm cửa sổ để đối soát số liệu theo từng kỳ. |
| `da-analysis-language` | `satisfied` | Trong chuyển kinh nghiệm nghiên cứu định lượng sang phân tích sản phẩm, ứng viên dùng pandas để chuẩn hóa kiểu dữ liệu, xử lý giá trị thiếu và đóng gói notebook có thể chạy lại. |
| `da-bi-reporting` | `satisfied` | Trong chuyển kinh nghiệm nghiên cứu định lượng sang phân tích sản phẩm, ứng viên dựng dashboard có data model, bộ lọc chi tiết và tài liệu định nghĩa từng KPI. |
| `da-business-analysis` | `satisfied` | Trong chuyển kinh nghiệm nghiên cứu định lượng sang phân tích sản phẩm, ứng viên chuyển câu hỏi kinh doanh thành chỉ số, phân tích nguyên nhân và nêu khuyến nghị kèm giới hạn. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `da-technical-specialization` | 16/25 |
| `da-role-capability` | 14/20 |
| `projects-and-impact` | 10/15 |
| `communication-and-evidence-quality` | 9/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-da-10

- Vị trí: Junior Data Analyst - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-da-10`
- Tóm tắt: Hồ sơ chủ yếu liệt kê khóa học và công cụ nhưng không mô tả nhiệm vụ hay sản phẩm đã làm. Mục tiêu ứng tuyển là Junior Data Analyst - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 36
- Nhãn nháp: `needs_review`
- Lý do review: missing-critical-evidence, low-score-without-explicit-critical-unsatisfied

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `da-sql` | `missing` | Đã hoàn thành bài học giới thiệu về SQL và tự ghi tên công cụ trong danh sách kỹ năng. |
| `da-analysis-language` | `missing` | Đã hoàn thành bài học giới thiệu về Python hoặc R và tự ghi tên công cụ trong danh sách kỹ năng. |
| `da-bi-reporting` | `missing` | Đã hoàn thành bài học giới thiệu về Power BI hoặc Tableau và tự ghi tên công cụ trong danh sách kỹ năng. |
| `da-business-analysis` | `missing` | Đã hoàn thành bài học giới thiệu về Phân tích nghiệp vụ end-to-end và tự ghi tên công cụ trong danh sách kỹ năng. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 14/30 |
| `da-technical-specialization` | 9/25 |
| `da-role-capability` | 6/20 |
| `projects-and-impact` | 3/15 |
| `communication-and-evidence-quality` | 4/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-be-01

- Vị trí: Junior Python Backend Developer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-be-01`
- Tóm tắt: Hồ sơ trình bày một sản phẩm hoàn chỉnh, có số liệu đối chiếu và tài liệu tái tạo. Mục tiêu ứng tuyển là Junior Python Backend Developer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 95
- Nhãn nháp: `pass`
- Lý do review: không có

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `be-python` | `satisfied` | Trong xây dịch vụ xử lý đơn hàng có idempotency key, ứng viên tổ chức Python theo lớp dịch vụ, dùng type hint và xử lý ngoại lệ theo hợp đồng lỗi. |
| `be-rest-api` | `satisfied` | Trong xây dịch vụ xử lý đơn hàng có idempotency key, ứng viên xây REST API bằng FastAPI với validation, phân trang và mã trạng thái nhất quán. |
| `be-relational-data` | `satisfied` | Trong xây dịch vụ xử lý đơn hàng có idempotency key, ứng viên thiết kế bảng PostgreSQL, migration và truy vấn transaction cho luồng cập nhật dữ liệu. |
| `be-testing` | `satisfied` | Trong xây dịch vụ xử lý đơn hàng có idempotency key, ứng viên viết pytest cho service và API, gồm luồng đúng, dữ liệu sai và dependency giả lập. |
| `be-delivery-workflow` | `satisfied` | Trong xây dịch vụ xử lý đơn hàng có idempotency key, ứng viên quản lý nhánh Git, đóng gói Docker và ghi lệnh khởi động môi trường phát triển. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `be-technical-specialization` | 24/25 |
| `be-role-capability` | 18/20 |
| `projects-and-impact` | 14/15 |
| `communication-and-evidence-quality` | 9/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-be-02

- Vị trí: Junior Python Backend Developer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-be-02`
- Tóm tắt: Hồ sơ có dự án junior hoàn chỉnh, thông tin nhất quán và đầu ra có thể kiểm tra. Mục tiêu ứng tuyển là Junior Python Backend Developer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 89
- Nhãn nháp: `pass`
- Lý do review: không có

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `be-python` | `satisfied` | Trong phát triển API tồn kho với kiểm soát transaction, ứng viên tổ chức Python theo lớp dịch vụ, dùng type hint và xử lý ngoại lệ theo hợp đồng lỗi. |
| `be-rest-api` | `satisfied` | Trong phát triển API tồn kho với kiểm soát transaction, ứng viên xây REST API bằng FastAPI với validation, phân trang và mã trạng thái nhất quán. |
| `be-relational-data` | `satisfied` | Trong phát triển API tồn kho với kiểm soát transaction, ứng viên thiết kế bảng PostgreSQL, migration và truy vấn transaction cho luồng cập nhật dữ liệu. |
| `be-testing` | `satisfied` | Trong phát triển API tồn kho với kiểm soát transaction, ứng viên viết pytest cho service và API, gồm luồng đúng, dữ liệu sai và dependency giả lập. |
| `be-delivery-workflow` | `satisfied` | Trong phát triển API tồn kho với kiểm soát transaction, ứng viên quản lý nhánh Git, đóng gói Docker và ghi lệnh khởi động môi trường phát triển. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `be-technical-specialization` | 22/25 |
| `be-role-capability` | 17/20 |
| `projects-and-impact` | 12/15 |
| `communication-and-evidence-quality` | 8/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-be-03

- Vị trí: Junior Python Backend Developer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-be-03`
- Tóm tắt: Hồ sơ đáp ứng phần cốt lõi nhưng dự án mới giới hạn ở một luồng nghiệp vụ. Mục tiêu ứng tuyển là Junior Python Backend Developer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 78
- Nhãn nháp: `waitlist`
- Lý do review: không có

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `be-python` | `satisfied` | Trong tạo backend đặt lịch có phân quyền người dùng, ứng viên tổ chức Python theo lớp dịch vụ, dùng type hint và xử lý ngoại lệ theo hợp đồng lỗi. |
| `be-rest-api` | `satisfied` | Trong tạo backend đặt lịch có phân quyền người dùng, ứng viên xây REST API bằng FastAPI với validation, phân trang và mã trạng thái nhất quán. |
| `be-relational-data` | `satisfied` | Trong tạo backend đặt lịch có phân quyền người dùng, ứng viên thiết kế bảng PostgreSQL, migration và truy vấn transaction cho luồng cập nhật dữ liệu. |
| `be-testing` | `satisfied` | Trong tạo backend đặt lịch có phân quyền người dùng, ứng viên viết pytest cho service và API, gồm luồng đúng, dữ liệu sai và dependency giả lập. |
| `be-delivery-workflow` | `satisfied` | Trong tạo backend đặt lịch có phân quyền người dùng, ứng viên quản lý nhánh Git, đóng gói Docker và ghi lệnh khởi động môi trường phát triển. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `be-technical-specialization` | 17/25 |
| `be-role-capability` | 14/20 |
| `projects-and-impact` | 9/15 |
| `communication-and-evidence-quality` | 8/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-be-04

- Vị trí: Junior Python Backend Developer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-be-04`
- Tóm tắt: Hồ sơ mô tả một số phần việc liên quan nhưng không đề cập đầy đủ toàn bộ năng lực cốt lõi. Mục tiêu ứng tuyển là Junior Python Backend Developer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 64
- Nhãn nháp: `needs_review`
- Lý do review: missing-critical-evidence, low-score-without-explicit-critical-unsatisfied

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `be-python` | `satisfied` | Trong xử lý webhook thanh toán và chống gửi trùng, ứng viên tổ chức Python theo lớp dịch vụ, dùng type hint và xử lý ngoại lệ theo hợp đồng lỗi. |
| `be-rest-api` | `satisfied` | Trong xử lý webhook thanh toán và chống gửi trùng, ứng viên xây REST API bằng FastAPI với validation, phân trang và mã trạng thái nhất quán. |
| `be-relational-data` | `satisfied` | Trong xử lý webhook thanh toán và chống gửi trùng, ứng viên thiết kế bảng PostgreSQL, migration và truy vấn transaction cho luồng cập nhật dữ liệu. |
| `be-testing` | `satisfied` | Trong xử lý webhook thanh toán và chống gửi trùng, ứng viên viết pytest cho service và API, gồm luồng đúng, dữ liệu sai và dependency giả lập. |
| `be-delivery-workflow` | `missing` | Không có thông tin |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 20/30 |
| `be-technical-specialization` | 17/25 |
| `be-role-capability` | 13/20 |
| `projects-and-impact` | 8/15 |
| `communication-and-evidence-quality` | 6/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-be-05

- Vị trí: Junior Python Backend Developer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-be-05`
- Tóm tắt: Hồ sơ kết hợp mô tả dự án và bản tự đánh giá có một điểm chưa nhất quán. Mục tiêu ứng tuyển là Junior Python Backend Developer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 68
- Nhãn nháp: `needs_review`
- Lý do review: conflicting-critical-evidence, lower-threshold-boundary, low-score-without-explicit-critical-unsatisfied

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `be-python` | `satisfied` | Trong xây API thư viện số với tìm kiếm và phân trang, ứng viên tổ chức Python theo lớp dịch vụ, dùng type hint và xử lý ngoại lệ theo hợp đồng lỗi. |
| `be-rest-api` | `conflicting` | Trong xây API thư viện số với tìm kiếm và phân trang, ứng viên xây REST API bằng FastAPI với validation, phân trang và mã trạng thái nhất quán. / Ứng viên xác nhận chưa từng xây hoặc tích hợp REST API. |
| `be-relational-data` | `satisfied` | Trong xây API thư viện số với tìm kiếm và phân trang, ứng viên thiết kế bảng PostgreSQL, migration và truy vấn transaction cho luồng cập nhật dữ liệu. |
| `be-testing` | `satisfied` | Trong xây API thư viện số với tìm kiếm và phân trang, ứng viên viết pytest cho service và API, gồm luồng đúng, dữ liệu sai và dependency giả lập. |
| `be-delivery-workflow` | `satisfied` | Trong xây API thư viện số với tìm kiếm và phân trang, ứng viên quản lý nhánh Git, đóng gói Docker và ghi lệnh khởi động môi trường phát triển. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 22/30 |
| `be-technical-specialization` | 17/25 |
| `be-role-capability` | 13/20 |
| `projects-and-impact` | 9/15 |
| `communication-and-evidence-quality` | 7/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-be-06

- Vị trí: Junior Python Backend Developer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-be-06`
- Tóm tắt: Ứng viên chuyển hướng từ lĩnh vực gần và xác nhận chưa thực hành một năng lực bắt buộc. Mục tiêu ứng tuyển là Junior Python Backend Developer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 41
- Nhãn nháp: `reject`
- Lý do review: không có

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `be-python` | `satisfied` | Trong chuyển từ lập trình nhúng sang dịch vụ web Python, ứng viên tổ chức Python theo lớp dịch vụ, dùng type hint và xử lý ngoại lệ theo hợp đồng lỗi. |
| `be-rest-api` | `satisfied` | Trong chuyển từ lập trình nhúng sang dịch vụ web Python, ứng viên xây REST API bằng FastAPI với validation, phân trang và mã trạng thái nhất quán. |
| `be-relational-data` | `satisfied` | Trong chuyển từ lập trình nhúng sang dịch vụ web Python, ứng viên thiết kế bảng PostgreSQL, migration và truy vấn transaction cho luồng cập nhật dữ liệu. |
| `be-testing` | `satisfied` | Trong chuyển từ lập trình nhúng sang dịch vụ web Python, ứng viên viết pytest cho service và API, gồm luồng đúng, dữ liệu sai và dependency giả lập. |
| `be-delivery-workflow` | `unsatisfied` | Ứng viên xác nhận chưa từng dùng Git hoặc đóng gói ứng dụng bằng Docker. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 10/30 |
| `be-technical-specialization` | 12/25 |
| `be-role-capability` | 9/20 |
| `projects-and-impact` | 5/15 |
| `communication-and-evidence-quality` | 5/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-be-07

- Vị trí: Junior Python Backend Developer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-be-07`
- Tóm tắt: Hồ sơ vừa đủ yêu cầu cốt lõi nhưng mức độ sâu và phạm vi dự án còn hạn chế. Mục tiêu ứng tuyển là Junior Python Backend Developer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 70
- Nhãn nháp: `needs_review`
- Lý do review: lower-threshold-boundary

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `be-python` | `satisfied` | Trong triển khai service quản lý công việc cho nhóm sinh viên, ứng viên tổ chức Python theo lớp dịch vụ, dùng type hint và xử lý ngoại lệ theo hợp đồng lỗi. |
| `be-rest-api` | `satisfied` | Trong triển khai service quản lý công việc cho nhóm sinh viên, ứng viên xây REST API bằng FastAPI với validation, phân trang và mã trạng thái nhất quán. |
| `be-relational-data` | `satisfied` | Trong triển khai service quản lý công việc cho nhóm sinh viên, ứng viên thiết kế bảng PostgreSQL, migration và truy vấn transaction cho luồng cập nhật dữ liệu. |
| `be-testing` | `satisfied` | Trong triển khai service quản lý công việc cho nhóm sinh viên, ứng viên viết pytest cho service và API, gồm luồng đúng, dữ liệu sai và dependency giả lập. |
| `be-delivery-workflow` | `satisfied` | Trong triển khai service quản lý công việc cho nhóm sinh viên, ứng viên quản lý nhánh Git, đóng gói Docker và ghi lệnh khởi động môi trường phát triển. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 28/30 |
| `be-technical-specialization` | 14/25 |
| `be-role-capability` | 11/20 |
| `projects-and-impact` | 8/15 |
| `communication-and-evidence-quality` | 9/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-be-08

- Vị trí: Junior Python Backend Developer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-be-08`
- Tóm tắt: Hồ sơ khá tốt và nằm gần ngưỡng Pass nên cần kiểm tra tính ổn định của quyết định. Mục tiêu ứng tuyển là Junior Python Backend Developer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 85
- Nhãn nháp: `needs_review`
- Lý do review: upper-threshold-boundary

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `be-python` | `satisfied` | Trong xây API theo dõi chi tiêu với refresh token, ứng viên tổ chức Python theo lớp dịch vụ, dùng type hint và xử lý ngoại lệ theo hợp đồng lỗi. |
| `be-rest-api` | `satisfied` | Trong xây API theo dõi chi tiêu với refresh token, ứng viên xây REST API bằng FastAPI với validation, phân trang và mã trạng thái nhất quán. |
| `be-relational-data` | `satisfied` | Trong xây API theo dõi chi tiêu với refresh token, ứng viên thiết kế bảng PostgreSQL, migration và truy vấn transaction cho luồng cập nhật dữ liệu. |
| `be-testing` | `satisfied` | Trong xây API theo dõi chi tiêu với refresh token, ứng viên viết pytest cho service và API, gồm luồng đúng, dữ liệu sai và dependency giả lập. |
| `be-delivery-workflow` | `satisfied` | Trong xây API theo dõi chi tiêu với refresh token, ứng viên quản lý nhánh Git, đóng gói Docker và ghi lệnh khởi động môi trường phát triển. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `be-technical-specialization` | 20/25 |
| `be-role-capability` | 16/20 |
| `projects-and-impact` | 12/15 |
| `communication-and-evidence-quality` | 7/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-be-09

- Vị trí: Junior Python Backend Developer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-be-09`
- Tóm tắt: Ứng viên chuyển từ lĩnh vực gần và chứng minh được năng lực tương đương qua dự án mới. Mục tiêu ứng tuyển là Junior Python Backend Developer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 79
- Nhãn nháp: `waitlist`
- Lý do review: không có

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `be-python` | `satisfied` | Trong chuyển kinh nghiệm Java sang một microservice FastAPI, ứng viên tổ chức Python theo lớp dịch vụ, dùng type hint và xử lý ngoại lệ theo hợp đồng lỗi. |
| `be-rest-api` | `satisfied` | Trong chuyển kinh nghiệm Java sang một microservice FastAPI, ứng viên xây REST API bằng FastAPI với validation, phân trang và mã trạng thái nhất quán. |
| `be-relational-data` | `satisfied` | Trong chuyển kinh nghiệm Java sang một microservice FastAPI, ứng viên thiết kế bảng PostgreSQL, migration và truy vấn transaction cho luồng cập nhật dữ liệu. |
| `be-testing` | `satisfied` | Trong chuyển kinh nghiệm Java sang một microservice FastAPI, ứng viên viết pytest cho service và API, gồm luồng đúng, dữ liệu sai và dependency giả lập. |
| `be-delivery-workflow` | `satisfied` | Trong chuyển kinh nghiệm Java sang một microservice FastAPI, ứng viên quản lý nhánh Git, đóng gói Docker và ghi lệnh khởi động môi trường phát triển. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `be-technical-specialization` | 16/25 |
| `be-role-capability` | 14/20 |
| `projects-and-impact` | 10/15 |
| `communication-and-evidence-quality` | 9/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-be-10

- Vị trí: Junior Python Backend Developer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-be-10`
- Tóm tắt: Hồ sơ chủ yếu liệt kê khóa học và công cụ nhưng không mô tả nhiệm vụ hay sản phẩm đã làm. Mục tiêu ứng tuyển là Junior Python Backend Developer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 36
- Nhãn nháp: `needs_review`
- Lý do review: missing-critical-evidence, low-score-without-explicit-critical-unsatisfied

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `be-python` | `missing` | Đã hoàn thành bài học giới thiệu về Python và tự ghi tên công cụ trong danh sách kỹ năng. |
| `be-rest-api` | `missing` | Đã hoàn thành bài học giới thiệu về REST API và tự ghi tên công cụ trong danh sách kỹ năng. |
| `be-relational-data` | `missing` | Đã hoàn thành bài học giới thiệu về PostgreSQL và SQL và tự ghi tên công cụ trong danh sách kỹ năng. |
| `be-testing` | `missing` | Đã hoàn thành bài học giới thiệu về pytest và tự ghi tên công cụ trong danh sách kỹ năng. |
| `be-delivery-workflow` | `missing` | Đã hoàn thành bài học giới thiệu về Git và Docker và tự ghi tên công cụ trong danh sách kỹ năng. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 14/30 |
| `be-technical-specialization` | 9/25 |
| `be-role-capability` | 6/20 |
| `projects-and-impact` | 3/15 |
| `communication-and-evidence-quality` | 4/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-fe-01

- Vị trí: Junior Frontend Developer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-fe-01`
- Tóm tắt: Hồ sơ trình bày một sản phẩm hoàn chỉnh, có số liệu đối chiếu và tài liệu tái tạo. Mục tiêu ứng tuyển là Junior Frontend Developer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 95
- Nhãn nháp: `pass`
- Lý do review: không có

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `fe-web-foundations` | `satisfied` | Trong xây trang quản lý khóa học hỗ trợ bàn phím, ứng viên xây giao diện semantic HTML, CSS responsive và xử lý tương tác bằng JavaScript. |
| `fe-language` | `satisfied` | Trong xây trang quản lý khóa học hỗ trợ bàn phím, ứng viên dùng TypeScript strict, mô hình hóa dữ liệu và thu hẹp kiểu cho dữ liệu bên ngoài. |
| `fe-framework` | `satisfied` | Trong xây trang quản lý khóa học hỗ trợ bàn phím, ứng viên tách React component, quản lý state và xử lý loading, empty cùng error state. |
| `fe-api` | `satisfied` | Trong xây trang quản lý khóa học hỗ trợ bàn phím, ứng viên tích hợp API có xác thực, hủy request cũ và hiển thị lỗi theo từng tình huống. |
| `fe-testing-workflow` | `satisfied` | Trong xây trang quản lý khóa học hỗ trợ bàn phím, ứng viên dùng Git theo pull request và viết Testing Library cho hành vi người dùng chính. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `fe-technical-specialization` | 24/25 |
| `fe-role-capability` | 18/20 |
| `projects-and-impact` | 14/15 |
| `communication-and-evidence-quality` | 9/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-fe-02

- Vị trí: Junior Frontend Developer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-fe-02`
- Tóm tắt: Hồ sơ có dự án junior hoàn chỉnh, thông tin nhất quán và đầu ra có thể kiểm tra. Mục tiêu ứng tuyển là Junior Frontend Developer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 89
- Nhãn nháp: `pass`
- Lý do review: không có

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `fe-web-foundations` | `satisfied` | Trong phát triển giỏ hàng responsive có lưu trạng thái, ứng viên xây giao diện semantic HTML, CSS responsive và xử lý tương tác bằng JavaScript. |
| `fe-language` | `satisfied` | Trong phát triển giỏ hàng responsive có lưu trạng thái, ứng viên dùng TypeScript strict, mô hình hóa dữ liệu và thu hẹp kiểu cho dữ liệu bên ngoài. |
| `fe-framework` | `satisfied` | Trong phát triển giỏ hàng responsive có lưu trạng thái, ứng viên tách React component, quản lý state và xử lý loading, empty cùng error state. |
| `fe-api` | `satisfied` | Trong phát triển giỏ hàng responsive có lưu trạng thái, ứng viên tích hợp API có xác thực, hủy request cũ và hiển thị lỗi theo từng tình huống. |
| `fe-testing-workflow` | `satisfied` | Trong phát triển giỏ hàng responsive có lưu trạng thái, ứng viên dùng Git theo pull request và viết Testing Library cho hành vi người dùng chính. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `fe-technical-specialization` | 22/25 |
| `fe-role-capability` | 17/20 |
| `projects-and-impact` | 12/15 |
| `communication-and-evidence-quality` | 8/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-fe-03

- Vị trí: Junior Frontend Developer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-fe-03`
- Tóm tắt: Hồ sơ đáp ứng phần cốt lõi nhưng dự án mới giới hạn ở một luồng nghiệp vụ. Mục tiêu ứng tuyển là Junior Frontend Developer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 78
- Nhãn nháp: `waitlist`
- Lý do review: không có

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `fe-web-foundations` | `satisfied` | Trong tạo dashboard vận hành với biểu đồ và bộ lọc, ứng viên xây giao diện semantic HTML, CSS responsive và xử lý tương tác bằng JavaScript. |
| `fe-language` | `satisfied` | Trong tạo dashboard vận hành với biểu đồ và bộ lọc, ứng viên dùng TypeScript strict, mô hình hóa dữ liệu và thu hẹp kiểu cho dữ liệu bên ngoài. |
| `fe-framework` | `satisfied` | Trong tạo dashboard vận hành với biểu đồ và bộ lọc, ứng viên tách React component, quản lý state và xử lý loading, empty cùng error state. |
| `fe-api` | `satisfied` | Trong tạo dashboard vận hành với biểu đồ và bộ lọc, ứng viên tích hợp API có xác thực, hủy request cũ và hiển thị lỗi theo từng tình huống. |
| `fe-testing-workflow` | `satisfied` | Trong tạo dashboard vận hành với biểu đồ và bộ lọc, ứng viên dùng Git theo pull request và viết Testing Library cho hành vi người dùng chính. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `fe-technical-specialization` | 17/25 |
| `fe-role-capability` | 14/20 |
| `projects-and-impact` | 9/15 |
| `communication-and-evidence-quality` | 8/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-fe-04

- Vị trí: Junior Frontend Developer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-fe-04`
- Tóm tắt: Hồ sơ mô tả một số phần việc liên quan nhưng không đề cập đầy đủ toàn bộ năng lực cốt lõi. Mục tiêu ứng tuyển là Junior Frontend Developer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 64
- Nhãn nháp: `needs_review`
- Lý do review: missing-critical-evidence, low-score-without-explicit-critical-unsatisfied

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `fe-web-foundations` | `missing` | Không có thông tin |
| `fe-language` | `satisfied` | Trong xây cổng đăng ký sự kiện có validation nhiều bước, ứng viên dùng TypeScript strict, mô hình hóa dữ liệu và thu hẹp kiểu cho dữ liệu bên ngoài. |
| `fe-framework` | `satisfied` | Trong xây cổng đăng ký sự kiện có validation nhiều bước, ứng viên tách React component, quản lý state và xử lý loading, empty cùng error state. |
| `fe-api` | `satisfied` | Trong xây cổng đăng ký sự kiện có validation nhiều bước, ứng viên tích hợp API có xác thực, hủy request cũ và hiển thị lỗi theo từng tình huống. |
| `fe-testing-workflow` | `satisfied` | Trong xây cổng đăng ký sự kiện có validation nhiều bước, ứng viên dùng Git theo pull request và viết Testing Library cho hành vi người dùng chính. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 20/30 |
| `fe-technical-specialization` | 17/25 |
| `fe-role-capability` | 13/20 |
| `projects-and-impact` | 8/15 |
| `communication-and-evidence-quality` | 6/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-fe-05

- Vị trí: Junior Frontend Developer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-fe-05`
- Tóm tắt: Hồ sơ kết hợp mô tả dự án và bản tự đánh giá có một điểm chưa nhất quán. Mục tiêu ứng tuyển là Junior Frontend Developer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 68
- Nhãn nháp: `needs_review`
- Lý do review: conflicting-critical-evidence, lower-threshold-boundary, low-score-without-explicit-critical-unsatisfied

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `fe-web-foundations` | `satisfied` | Trong phát triển giao diện quản trị phân quyền theo vai trò, ứng viên xây giao diện semantic HTML, CSS responsive và xử lý tương tác bằng JavaScript. |
| `fe-language` | `conflicting` | Trong phát triển giao diện quản trị phân quyền theo vai trò, ứng viên dùng TypeScript strict, mô hình hóa dữ liệu và thu hẹp kiểu cho dữ liệu bên ngoài. / Ứng viên xác nhận chưa từng viết JavaScript hoặc TypeScript trong dự án. |
| `fe-framework` | `satisfied` | Trong phát triển giao diện quản trị phân quyền theo vai trò, ứng viên tách React component, quản lý state và xử lý loading, empty cùng error state. |
| `fe-api` | `satisfied` | Trong phát triển giao diện quản trị phân quyền theo vai trò, ứng viên tích hợp API có xác thực, hủy request cũ và hiển thị lỗi theo từng tình huống. |
| `fe-testing-workflow` | `satisfied` | Trong phát triển giao diện quản trị phân quyền theo vai trò, ứng viên dùng Git theo pull request và viết Testing Library cho hành vi người dùng chính. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 22/30 |
| `fe-technical-specialization` | 17/25 |
| `fe-role-capability` | 13/20 |
| `projects-and-impact` | 9/15 |
| `communication-and-evidence-quality` | 7/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-fe-06

- Vị trí: Junior Frontend Developer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-fe-06`
- Tóm tắt: Ứng viên chuyển hướng từ lĩnh vực gần và xác nhận chưa thực hành một năng lực bắt buộc. Mục tiêu ứng tuyển là Junior Frontend Developer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 41
- Nhãn nháp: `reject`
- Lý do review: không có

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `fe-web-foundations` | `satisfied` | Trong chuyển từ thiết kế UI sang lập trình frontend, ứng viên xây giao diện semantic HTML, CSS responsive và xử lý tương tác bằng JavaScript. |
| `fe-language` | `satisfied` | Trong chuyển từ thiết kế UI sang lập trình frontend, ứng viên dùng TypeScript strict, mô hình hóa dữ liệu và thu hẹp kiểu cho dữ liệu bên ngoài. |
| `fe-framework` | `satisfied` | Trong chuyển từ thiết kế UI sang lập trình frontend, ứng viên tách React component, quản lý state và xử lý loading, empty cùng error state. |
| `fe-api` | `satisfied` | Trong chuyển từ thiết kế UI sang lập trình frontend, ứng viên tích hợp API có xác thực, hủy request cũ và hiển thị lỗi theo từng tình huống. |
| `fe-testing-workflow` | `unsatisfied` | Ứng viên xác nhận chưa từng dùng Git hoặc viết kiểm thử giao diện. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 10/30 |
| `fe-technical-specialization` | 12/25 |
| `fe-role-capability` | 9/20 |
| `projects-and-impact` | 5/15 |
| `communication-and-evidence-quality` | 5/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-fe-07

- Vị trí: Junior Frontend Developer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-fe-07`
- Tóm tắt: Hồ sơ vừa đủ yêu cầu cốt lõi nhưng mức độ sâu và phạm vi dự án còn hạn chế. Mục tiêu ứng tuyển là Junior Frontend Developer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 70
- Nhãn nháp: `needs_review`
- Lý do review: lower-threshold-boundary

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `fe-web-foundations` | `satisfied` | Trong xây trang tra cứu thư viện trên thiết bị di động, ứng viên xây giao diện semantic HTML, CSS responsive và xử lý tương tác bằng JavaScript. |
| `fe-language` | `satisfied` | Trong xây trang tra cứu thư viện trên thiết bị di động, ứng viên dùng TypeScript strict, mô hình hóa dữ liệu và thu hẹp kiểu cho dữ liệu bên ngoài. |
| `fe-framework` | `satisfied` | Trong xây trang tra cứu thư viện trên thiết bị di động, ứng viên tách React component, quản lý state và xử lý loading, empty cùng error state. |
| `fe-api` | `satisfied` | Trong xây trang tra cứu thư viện trên thiết bị di động, ứng viên tích hợp API có xác thực, hủy request cũ và hiển thị lỗi theo từng tình huống. |
| `fe-testing-workflow` | `satisfied` | Trong xây trang tra cứu thư viện trên thiết bị di động, ứng viên dùng Git theo pull request và viết Testing Library cho hành vi người dùng chính. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 28/30 |
| `fe-technical-specialization` | 14/25 |
| `fe-role-capability` | 11/20 |
| `projects-and-impact` | 8/15 |
| `communication-and-evidence-quality` | 9/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-fe-08

- Vị trí: Junior Frontend Developer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-fe-08`
- Tóm tắt: Hồ sơ khá tốt và nằm gần ngưỡng Pass nên cần kiểm tra tính ổn định của quyết định. Mục tiêu ứng tuyển là Junior Frontend Developer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 85
- Nhãn nháp: `needs_review`
- Lý do review: upper-threshold-boundary

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `fe-web-foundations` | `satisfied` | Trong tạo ứng dụng theo dõi thói quen có đồng bộ API, ứng viên xây giao diện semantic HTML, CSS responsive và xử lý tương tác bằng JavaScript. |
| `fe-language` | `satisfied` | Trong tạo ứng dụng theo dõi thói quen có đồng bộ API, ứng viên dùng TypeScript strict, mô hình hóa dữ liệu và thu hẹp kiểu cho dữ liệu bên ngoài. |
| `fe-framework` | `satisfied` | Trong tạo ứng dụng theo dõi thói quen có đồng bộ API, ứng viên tách React component, quản lý state và xử lý loading, empty cùng error state. |
| `fe-api` | `satisfied` | Trong tạo ứng dụng theo dõi thói quen có đồng bộ API, ứng viên tích hợp API có xác thực, hủy request cũ và hiển thị lỗi theo từng tình huống. |
| `fe-testing-workflow` | `satisfied` | Trong tạo ứng dụng theo dõi thói quen có đồng bộ API, ứng viên dùng Git theo pull request và viết Testing Library cho hành vi người dùng chính. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `fe-technical-specialization` | 20/25 |
| `fe-role-capability` | 16/20 |
| `projects-and-impact` | 12/15 |
| `communication-and-evidence-quality` | 7/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-fe-09

- Vị trí: Junior Frontend Developer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-fe-09`
- Tóm tắt: Ứng viên chuyển từ lĩnh vực gần và chứng minh được năng lực tương đương qua dự án mới. Mục tiêu ứng tuyển là Junior Frontend Developer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 79
- Nhãn nháp: `waitlist`
- Lý do review: không có

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `fe-web-foundations` | `satisfied` | Trong chuyển kinh nghiệm Vue sang dự án React TypeScript, ứng viên xây giao diện semantic HTML, CSS responsive và xử lý tương tác bằng JavaScript. |
| `fe-language` | `satisfied` | Trong chuyển kinh nghiệm Vue sang dự án React TypeScript, ứng viên dùng TypeScript strict, mô hình hóa dữ liệu và thu hẹp kiểu cho dữ liệu bên ngoài. |
| `fe-framework` | `satisfied` | Trong chuyển kinh nghiệm Vue sang dự án React TypeScript, ứng viên tách React component, quản lý state và xử lý loading, empty cùng error state. |
| `fe-api` | `satisfied` | Trong chuyển kinh nghiệm Vue sang dự án React TypeScript, ứng viên tích hợp API có xác thực, hủy request cũ và hiển thị lỗi theo từng tình huống. |
| `fe-testing-workflow` | `satisfied` | Trong chuyển kinh nghiệm Vue sang dự án React TypeScript, ứng viên dùng Git theo pull request và viết Testing Library cho hành vi người dùng chính. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `fe-technical-specialization` | 16/25 |
| `fe-role-capability` | 14/20 |
| `projects-and-impact` | 10/15 |
| `communication-and-evidence-quality` | 9/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-fe-10

- Vị trí: Junior Frontend Developer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-fe-10`
- Tóm tắt: Hồ sơ chủ yếu liệt kê khóa học và công cụ nhưng không mô tả nhiệm vụ hay sản phẩm đã làm. Mục tiêu ứng tuyển là Junior Frontend Developer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 36
- Nhãn nháp: `needs_review`
- Lý do review: missing-critical-evidence, low-score-without-explicit-critical-unsatisfied

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `fe-web-foundations` | `missing` | Đã hoàn thành bài học giới thiệu về HTML CSS JavaScript và tự ghi tên công cụ trong danh sách kỹ năng. |
| `fe-language` | `missing` | Đã hoàn thành bài học giới thiệu về JavaScript hoặc TypeScript và tự ghi tên công cụ trong danh sách kỹ năng. |
| `fe-framework` | `missing` | Đã hoàn thành bài học giới thiệu về React và tự ghi tên công cụ trong danh sách kỹ năng. |
| `fe-api` | `missing` | Đã hoàn thành bài học giới thiệu về Tích hợp API và tự ghi tên công cụ trong danh sách kỹ năng. |
| `fe-testing-workflow` | `missing` | Đã hoàn thành bài học giới thiệu về Git và kiểm thử giao diện và tự ghi tên công cụ trong danh sách kỹ năng. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 14/30 |
| `fe-technical-specialization` | 9/25 |
| `fe-role-capability` | 6/20 |
| `projects-and-impact` | 3/15 |
| `communication-and-evidence-quality` | 4/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-qa-01

- Vị trí: Junior QA Engineer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-qa-01`
- Tóm tắt: Hồ sơ trình bày một sản phẩm hoàn chỉnh, có số liệu đối chiếu và tài liệu tái tạo. Mục tiêu ứng tuyển là Junior QA Engineer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 95
- Nhãn nháp: `pass`
- Lý do review: không có

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `qa-testing-foundations` | `satisfied` | Trong kiểm thử hệ thống đặt lịch có giới hạn khung giờ, ứng viên phân biệt test level, test type và áp dụng quy trình lỗi từ phát hiện đến xác nhận sửa. |
| `qa-test-cases` | `satisfied` | Trong kiểm thử hệ thống đặt lịch có giới hạn khung giờ, ứng viên thiết kế test case bằng phân vùng tương đương, giá trị biên và bảng quyết định. |
| `qa-api-testing` | `satisfied` | Trong kiểm thử hệ thống đặt lịch có giới hạn khung giờ, ứng viên dùng Postman kiểm tra status, schema, authentication và chuỗi request có biến môi trường. |
| `qa-data-check` | `satisfied` | Trong kiểm thử hệ thống đặt lịch có giới hạn khung giờ, ứng viên viết SQL đối chiếu dữ liệu trước và sau thao tác, gồm bản ghi thiếu hoặc trùng. |
| `qa-automation-foundation` | `satisfied` | Trong kiểm thử hệ thống đặt lịch có giới hạn khung giờ, ứng viên tự động hóa luồng regression chính, có assertion ổn định và báo cáo kết quả. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `qa-technical-specialization` | 24/25 |
| `qa-role-capability` | 18/20 |
| `projects-and-impact` | 14/15 |
| `communication-and-evidence-quality` | 9/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-qa-02

- Vị trí: Junior QA Engineer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-qa-02`
- Tóm tắt: Hồ sơ có dự án junior hoàn chỉnh, thông tin nhất quán và đầu ra có thể kiểm tra. Mục tiêu ứng tuyển là Junior QA Engineer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 89
- Nhãn nháp: `pass`
- Lý do review: không có

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `qa-testing-foundations` | `satisfied` | Trong kiểm thử quy trình checkout với nhiều phương thức thanh toán, ứng viên phân biệt test level, test type và áp dụng quy trình lỗi từ phát hiện đến xác nhận sửa. |
| `qa-test-cases` | `satisfied` | Trong kiểm thử quy trình checkout với nhiều phương thức thanh toán, ứng viên thiết kế test case bằng phân vùng tương đương, giá trị biên và bảng quyết định. |
| `qa-api-testing` | `satisfied` | Trong kiểm thử quy trình checkout với nhiều phương thức thanh toán, ứng viên dùng Postman kiểm tra status, schema, authentication và chuỗi request có biến môi trường. |
| `qa-data-check` | `satisfied` | Trong kiểm thử quy trình checkout với nhiều phương thức thanh toán, ứng viên viết SQL đối chiếu dữ liệu trước và sau thao tác, gồm bản ghi thiếu hoặc trùng. |
| `qa-automation-foundation` | `satisfied` | Trong kiểm thử quy trình checkout với nhiều phương thức thanh toán, ứng viên tự động hóa luồng regression chính, có assertion ổn định và báo cáo kết quả. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `qa-technical-specialization` | 22/25 |
| `qa-role-capability` | 17/20 |
| `projects-and-impact` | 12/15 |
| `communication-and-evidence-quality` | 8/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-qa-03

- Vị trí: Junior QA Engineer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-qa-03`
- Tóm tắt: Hồ sơ đáp ứng phần cốt lõi nhưng dự án mới giới hạn ở một luồng nghiệp vụ. Mục tiêu ứng tuyển là Junior QA Engineer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 78
- Nhãn nháp: `waitlist`
- Lý do review: không có

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `qa-testing-foundations` | `satisfied` | Trong đánh giá API quản lý tài khoản và phân quyền, ứng viên phân biệt test level, test type và áp dụng quy trình lỗi từ phát hiện đến xác nhận sửa. |
| `qa-test-cases` | `satisfied` | Trong đánh giá API quản lý tài khoản và phân quyền, ứng viên thiết kế test case bằng phân vùng tương đương, giá trị biên và bảng quyết định. |
| `qa-api-testing` | `satisfied` | Trong đánh giá API quản lý tài khoản và phân quyền, ứng viên dùng Postman kiểm tra status, schema, authentication và chuỗi request có biến môi trường. |
| `qa-data-check` | `satisfied` | Trong đánh giá API quản lý tài khoản và phân quyền, ứng viên viết SQL đối chiếu dữ liệu trước và sau thao tác, gồm bản ghi thiếu hoặc trùng. |
| `qa-automation-foundation` | `satisfied` | Trong đánh giá API quản lý tài khoản và phân quyền, ứng viên tự động hóa luồng regression chính, có assertion ổn định và báo cáo kết quả. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `qa-technical-specialization` | 17/25 |
| `qa-role-capability` | 14/20 |
| `projects-and-impact` | 9/15 |
| `communication-and-evidence-quality` | 8/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-qa-04

- Vị trí: Junior QA Engineer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-qa-04`
- Tóm tắt: Hồ sơ mô tả một số phần việc liên quan nhưng không đề cập đầy đủ toàn bộ năng lực cốt lõi. Mục tiêu ứng tuyển là Junior QA Engineer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 64
- Nhãn nháp: `needs_review`
- Lý do review: missing-critical-evidence, low-score-without-explicit-critical-unsatisfied

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `qa-testing-foundations` | `satisfied` | Trong kiểm thử dữ liệu đồng bộ giữa đơn hàng và kho, ứng viên phân biệt test level, test type và áp dụng quy trình lỗi từ phát hiện đến xác nhận sửa. |
| `qa-test-cases` | `satisfied` | Trong kiểm thử dữ liệu đồng bộ giữa đơn hàng và kho, ứng viên thiết kế test case bằng phân vùng tương đương, giá trị biên và bảng quyết định. |
| `qa-api-testing` | `satisfied` | Trong kiểm thử dữ liệu đồng bộ giữa đơn hàng và kho, ứng viên dùng Postman kiểm tra status, schema, authentication và chuỗi request có biến môi trường. |
| `qa-data-check` | `satisfied` | Trong kiểm thử dữ liệu đồng bộ giữa đơn hàng và kho, ứng viên viết SQL đối chiếu dữ liệu trước và sau thao tác, gồm bản ghi thiếu hoặc trùng. |
| `qa-automation-foundation` | `missing` | Không có thông tin |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 20/30 |
| `qa-technical-specialization` | 17/25 |
| `qa-role-capability` | 13/20 |
| `projects-and-impact` | 8/15 |
| `communication-and-evidence-quality` | 6/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-qa-05

- Vị trí: Junior QA Engineer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-qa-05`
- Tóm tắt: Hồ sơ kết hợp mô tả dự án và bản tự đánh giá có một điểm chưa nhất quán. Mục tiêu ứng tuyển là Junior QA Engineer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 68
- Nhãn nháp: `needs_review`
- Lý do review: conflicting-critical-evidence, lower-threshold-boundary, low-score-without-explicit-critical-unsatisfied

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `qa-testing-foundations` | `satisfied` | Trong xây regression cho cổng đăng ký khóa học, ứng viên phân biệt test level, test type và áp dụng quy trình lỗi từ phát hiện đến xác nhận sửa. |
| `qa-test-cases` | `conflicting` | Trong xây regression cho cổng đăng ký khóa học, ứng viên thiết kế test case bằng phân vùng tương đương, giá trị biên và bảng quyết định. / Ứng viên xác nhận chưa từng viết test case từ yêu cầu nghiệp vụ. |
| `qa-api-testing` | `satisfied` | Trong xây regression cho cổng đăng ký khóa học, ứng viên dùng Postman kiểm tra status, schema, authentication và chuỗi request có biến môi trường. |
| `qa-data-check` | `satisfied` | Trong xây regression cho cổng đăng ký khóa học, ứng viên viết SQL đối chiếu dữ liệu trước và sau thao tác, gồm bản ghi thiếu hoặc trùng. |
| `qa-automation-foundation` | `satisfied` | Trong xây regression cho cổng đăng ký khóa học, ứng viên tự động hóa luồng regression chính, có assertion ổn định và báo cáo kết quả. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 22/30 |
| `qa-technical-specialization` | 17/25 |
| `qa-role-capability` | 13/20 |
| `projects-and-impact` | 9/15 |
| `communication-and-evidence-quality` | 7/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-qa-06

- Vị trí: Junior QA Engineer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-qa-06`
- Tóm tắt: Ứng viên chuyển hướng từ lĩnh vực gần và xác nhận chưa thực hành một năng lực bắt buộc. Mục tiêu ứng tuyển là Junior QA Engineer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 41
- Nhãn nháp: `reject`
- Lý do review: không có

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `qa-testing-foundations` | `satisfied` | Trong chuyển từ hỗ trợ khách hàng sang kiểm thử phần mềm, ứng viên phân biệt test level, test type và áp dụng quy trình lỗi từ phát hiện đến xác nhận sửa. |
| `qa-test-cases` | `satisfied` | Trong chuyển từ hỗ trợ khách hàng sang kiểm thử phần mềm, ứng viên thiết kế test case bằng phân vùng tương đương, giá trị biên và bảng quyết định. |
| `qa-api-testing` | `satisfied` | Trong chuyển từ hỗ trợ khách hàng sang kiểm thử phần mềm, ứng viên dùng Postman kiểm tra status, schema, authentication và chuỗi request có biến môi trường. |
| `qa-data-check` | `satisfied` | Trong chuyển từ hỗ trợ khách hàng sang kiểm thử phần mềm, ứng viên viết SQL đối chiếu dữ liệu trước và sau thao tác, gồm bản ghi thiếu hoặc trùng. |
| `qa-automation-foundation` | `unsatisfied` | Ứng viên xác nhận chưa từng viết bất kỳ kiểm thử tự động nào. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 10/30 |
| `qa-technical-specialization` | 12/25 |
| `qa-role-capability` | 9/20 |
| `projects-and-impact` | 5/15 |
| `communication-and-evidence-quality` | 5/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-qa-07

- Vị trí: Junior QA Engineer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-qa-07`
- Tóm tắt: Hồ sơ vừa đủ yêu cầu cốt lõi nhưng mức độ sâu và phạm vi dự án còn hạn chế. Mục tiêu ứng tuyển là Junior QA Engineer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 70
- Nhãn nháp: `needs_review`
- Lý do review: lower-threshold-boundary

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `qa-testing-foundations` | `satisfied` | Trong kiểm thử ứng dụng quản lý công việc của nhóm sinh viên, ứng viên phân biệt test level, test type và áp dụng quy trình lỗi từ phát hiện đến xác nhận sửa. |
| `qa-test-cases` | `satisfied` | Trong kiểm thử ứng dụng quản lý công việc của nhóm sinh viên, ứng viên thiết kế test case bằng phân vùng tương đương, giá trị biên và bảng quyết định. |
| `qa-api-testing` | `satisfied` | Trong kiểm thử ứng dụng quản lý công việc của nhóm sinh viên, ứng viên dùng Postman kiểm tra status, schema, authentication và chuỗi request có biến môi trường. |
| `qa-data-check` | `satisfied` | Trong kiểm thử ứng dụng quản lý công việc của nhóm sinh viên, ứng viên viết SQL đối chiếu dữ liệu trước và sau thao tác, gồm bản ghi thiếu hoặc trùng. |
| `qa-automation-foundation` | `satisfied` | Trong kiểm thử ứng dụng quản lý công việc của nhóm sinh viên, ứng viên tự động hóa luồng regression chính, có assertion ổn định và báo cáo kết quả. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 28/30 |
| `qa-technical-specialization` | 14/25 |
| `qa-role-capability` | 11/20 |
| `projects-and-impact` | 8/15 |
| `communication-and-evidence-quality` | 9/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-qa-08

- Vị trí: Junior QA Engineer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-qa-08`
- Tóm tắt: Hồ sơ khá tốt và nằm gần ngưỡng Pass nên cần kiểm tra tính ổn định của quyết định. Mục tiêu ứng tuyển là Junior QA Engineer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 85
- Nhãn nháp: `needs_review`
- Lý do review: upper-threshold-boundary

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `qa-testing-foundations` | `satisfied` | Trong đánh giá tính ổn định của luồng đặt vé thử nghiệm, ứng viên phân biệt test level, test type và áp dụng quy trình lỗi từ phát hiện đến xác nhận sửa. |
| `qa-test-cases` | `satisfied` | Trong đánh giá tính ổn định của luồng đặt vé thử nghiệm, ứng viên thiết kế test case bằng phân vùng tương đương, giá trị biên và bảng quyết định. |
| `qa-api-testing` | `satisfied` | Trong đánh giá tính ổn định của luồng đặt vé thử nghiệm, ứng viên dùng Postman kiểm tra status, schema, authentication và chuỗi request có biến môi trường. |
| `qa-data-check` | `satisfied` | Trong đánh giá tính ổn định của luồng đặt vé thử nghiệm, ứng viên viết SQL đối chiếu dữ liệu trước và sau thao tác, gồm bản ghi thiếu hoặc trùng. |
| `qa-automation-foundation` | `satisfied` | Trong đánh giá tính ổn định của luồng đặt vé thử nghiệm, ứng viên tự động hóa luồng regression chính, có assertion ổn định và báo cáo kết quả. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `qa-technical-specialization` | 20/25 |
| `qa-role-capability` | 16/20 |
| `projects-and-impact` | 12/15 |
| `communication-and-evidence-quality` | 7/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-qa-09

- Vị trí: Junior QA Engineer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-qa-09`
- Tóm tắt: Ứng viên chuyển từ lĩnh vực gần và chứng minh được năng lực tương đương qua dự án mới. Mục tiêu ứng tuyển là Junior QA Engineer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 79
- Nhãn nháp: `waitlist`
- Lý do review: không có

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `qa-testing-foundations` | `satisfied` | Trong chuyển kinh nghiệm phân tích nghiệp vụ sang QA, ứng viên phân biệt test level, test type và áp dụng quy trình lỗi từ phát hiện đến xác nhận sửa. |
| `qa-test-cases` | `satisfied` | Trong chuyển kinh nghiệm phân tích nghiệp vụ sang QA, ứng viên thiết kế test case bằng phân vùng tương đương, giá trị biên và bảng quyết định. |
| `qa-api-testing` | `satisfied` | Trong chuyển kinh nghiệm phân tích nghiệp vụ sang QA, ứng viên dùng Postman kiểm tra status, schema, authentication và chuỗi request có biến môi trường. |
| `qa-data-check` | `satisfied` | Trong chuyển kinh nghiệm phân tích nghiệp vụ sang QA, ứng viên viết SQL đối chiếu dữ liệu trước và sau thao tác, gồm bản ghi thiếu hoặc trùng. |
| `qa-automation-foundation` | `satisfied` | Trong chuyển kinh nghiệm phân tích nghiệp vụ sang QA, ứng viên tự động hóa luồng regression chính, có assertion ổn định và báo cáo kết quả. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `qa-technical-specialization` | 16/25 |
| `qa-role-capability` | 14/20 |
| `projects-and-impact` | 10/15 |
| `communication-and-evidence-quality` | 9/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-qa-10

- Vị trí: Junior QA Engineer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-qa-10`
- Tóm tắt: Hồ sơ chủ yếu liệt kê khóa học và công cụ nhưng không mô tả nhiệm vụ hay sản phẩm đã làm. Mục tiêu ứng tuyển là Junior QA Engineer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 36
- Nhãn nháp: `needs_review`
- Lý do review: missing-critical-evidence, low-score-without-explicit-critical-unsatisfied

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `qa-testing-foundations` | `missing` | Đã hoàn thành bài học giới thiệu về Nền tảng kiểm thử và tự ghi tên công cụ trong danh sách kỹ năng. |
| `qa-test-cases` | `missing` | Đã hoàn thành bài học giới thiệu về Thiết kế test case và tự ghi tên công cụ trong danh sách kỹ năng. |
| `qa-api-testing` | `missing` | Đã hoàn thành bài học giới thiệu về Kiểm thử API và tự ghi tên công cụ trong danh sách kỹ năng. |
| `qa-data-check` | `missing` | Đã hoàn thành bài học giới thiệu về SQL kiểm tra dữ liệu và tự ghi tên công cụ trong danh sách kỹ năng. |
| `qa-automation-foundation` | `missing` | Đã hoàn thành bài học giới thiệu về Tự động hóa kiểm thử và tự ghi tên công cụ trong danh sách kỹ năng. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 14/30 |
| `qa-technical-specialization` | 9/25 |
| `qa-role-capability` | 6/20 |
| `projects-and-impact` | 3/15 |
| `communication-and-evidence-quality` | 4/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-de-01

- Vị trí: Junior Data Engineer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-de-01`
- Tóm tắt: Hồ sơ trình bày một sản phẩm hoàn chỉnh, có số liệu đối chiếu và tài liệu tái tạo. Mục tiêu ứng tuyển là Junior Data Engineer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 95
- Nhãn nháp: `pass`
- Lý do review: không có

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `de-python` | `satisfied` | Trong xây pipeline giao dịch theo lô với checkpoint, ứng viên viết Python theo module để đọc nhiều nguồn, chuẩn hóa bản ghi và ghi log lỗi theo batch. |
| `de-sql` | `satisfied` | Trong xây pipeline giao dịch theo lô với checkpoint, ứng viên dùng SQL với CTE, hàm cửa sổ và execution plan để biến đổi dữ liệu dung lượng vừa. |
| `de-pipeline` | `satisfied` | Trong xây pipeline giao dịch theo lô với checkpoint, ứng viên xây pipeline incremental có checkpoint, retry và cơ chế chạy lại không tạo dữ liệu trùng. |
| `de-data-model-quality` | `satisfied` | Trong xây pipeline giao dịch theo lô với checkpoint, ứng viên thiết kế grain, khóa fact-dimension và kiểm tra null, unique cùng referential integrity. |
| `de-delivery-workflow` | `satisfied` | Trong xây pipeline giao dịch theo lô với checkpoint, ứng viên quản lý mã bằng Git, chạy tác vụ trên Linux và đóng gói môi trường bằng Docker. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `de-technical-specialization` | 24/25 |
| `de-role-capability` | 18/20 |
| `projects-and-impact` | 14/15 |
| `communication-and-evidence-quality` | 9/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-de-02

- Vị trí: Junior Data Engineer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-de-02`
- Tóm tắt: Hồ sơ có dự án junior hoàn chỉnh, thông tin nhất quán và đầu ra có thể kiểm tra. Mục tiêu ứng tuyển là Junior Data Engineer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 89
- Nhãn nháp: `pass`
- Lý do review: không có

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `de-python` | `satisfied` | Trong đồng bộ dữ liệu sản phẩm từ API vào kho phân tích, ứng viên viết Python theo module để đọc nhiều nguồn, chuẩn hóa bản ghi và ghi log lỗi theo batch. |
| `de-sql` | `satisfied` | Trong đồng bộ dữ liệu sản phẩm từ API vào kho phân tích, ứng viên dùng SQL với CTE, hàm cửa sổ và execution plan để biến đổi dữ liệu dung lượng vừa. |
| `de-pipeline` | `satisfied` | Trong đồng bộ dữ liệu sản phẩm từ API vào kho phân tích, ứng viên xây pipeline incremental có checkpoint, retry và cơ chế chạy lại không tạo dữ liệu trùng. |
| `de-data-model-quality` | `satisfied` | Trong đồng bộ dữ liệu sản phẩm từ API vào kho phân tích, ứng viên thiết kế grain, khóa fact-dimension và kiểm tra null, unique cùng referential integrity. |
| `de-delivery-workflow` | `satisfied` | Trong đồng bộ dữ liệu sản phẩm từ API vào kho phân tích, ứng viên quản lý mã bằng Git, chạy tác vụ trên Linux và đóng gói môi trường bằng Docker. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `de-technical-specialization` | 22/25 |
| `de-role-capability` | 17/20 |
| `projects-and-impact` | 12/15 |
| `communication-and-evidence-quality` | 8/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-de-03

- Vị trí: Junior Data Engineer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-de-03`
- Tóm tắt: Hồ sơ đáp ứng phần cốt lõi nhưng dự án mới giới hạn ở một luồng nghiệp vụ. Mục tiêu ứng tuyển là Junior Data Engineer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 78
- Nhãn nháp: `waitlist`
- Lý do review: không có

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `de-python` | `satisfied` | Trong tạo mart doanh thu theo mô hình sao, ứng viên viết Python theo module để đọc nhiều nguồn, chuẩn hóa bản ghi và ghi log lỗi theo batch. |
| `de-sql` | `satisfied` | Trong tạo mart doanh thu theo mô hình sao, ứng viên dùng SQL với CTE, hàm cửa sổ và execution plan để biến đổi dữ liệu dung lượng vừa. |
| `de-pipeline` | `satisfied` | Trong tạo mart doanh thu theo mô hình sao, ứng viên xây pipeline incremental có checkpoint, retry và cơ chế chạy lại không tạo dữ liệu trùng. |
| `de-data-model-quality` | `satisfied` | Trong tạo mart doanh thu theo mô hình sao, ứng viên thiết kế grain, khóa fact-dimension và kiểm tra null, unique cùng referential integrity. |
| `de-delivery-workflow` | `satisfied` | Trong tạo mart doanh thu theo mô hình sao, ứng viên quản lý mã bằng Git, chạy tác vụ trên Linux và đóng gói môi trường bằng Docker. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `de-technical-specialization` | 17/25 |
| `de-role-capability` | 14/20 |
| `projects-and-impact` | 9/15 |
| `communication-and-evidence-quality` | 8/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-de-04

- Vị trí: Junior Data Engineer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-de-04`
- Tóm tắt: Hồ sơ mô tả một số phần việc liên quan nhưng không đề cập đầy đủ toàn bộ năng lực cốt lõi. Mục tiêu ứng tuyển là Junior Data Engineer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 64
- Nhãn nháp: `needs_review`
- Lý do review: missing-critical-evidence, low-score-without-explicit-critical-unsatisfied

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `de-python` | `missing` | Không có thông tin |
| `de-sql` | `satisfied` | Trong xử lý file sự kiện đến muộn và bản ghi trùng, ứng viên dùng SQL với CTE, hàm cửa sổ và execution plan để biến đổi dữ liệu dung lượng vừa. |
| `de-pipeline` | `satisfied` | Trong xử lý file sự kiện đến muộn và bản ghi trùng, ứng viên xây pipeline incremental có checkpoint, retry và cơ chế chạy lại không tạo dữ liệu trùng. |
| `de-data-model-quality` | `satisfied` | Trong xử lý file sự kiện đến muộn và bản ghi trùng, ứng viên thiết kế grain, khóa fact-dimension và kiểm tra null, unique cùng referential integrity. |
| `de-delivery-workflow` | `satisfied` | Trong xử lý file sự kiện đến muộn và bản ghi trùng, ứng viên quản lý mã bằng Git, chạy tác vụ trên Linux và đóng gói môi trường bằng Docker. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 20/30 |
| `de-technical-specialization` | 17/25 |
| `de-role-capability` | 13/20 |
| `projects-and-impact` | 8/15 |
| `communication-and-evidence-quality` | 6/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-de-05

- Vị trí: Junior Data Engineer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-de-05`
- Tóm tắt: Hồ sơ kết hợp mô tả dự án và bản tự đánh giá có một điểm chưa nhất quán. Mục tiêu ứng tuyển là Junior Data Engineer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 68
- Nhãn nháp: `needs_review`
- Lý do review: conflicting-critical-evidence, lower-threshold-boundary, low-score-without-explicit-critical-unsatisfied

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `de-python` | `satisfied` | Trong xây luồng dữ liệu chất lượng không khí theo ngày, ứng viên viết Python theo module để đọc nhiều nguồn, chuẩn hóa bản ghi và ghi log lỗi theo batch. |
| `de-sql` | `conflicting` | Trong xây luồng dữ liệu chất lượng không khí theo ngày, ứng viên dùng SQL với CTE, hàm cửa sổ và execution plan để biến đổi dữ liệu dung lượng vừa. / Ứng viên xác nhận chưa từng viết truy vấn SQL có JOIN hoặc tổng hợp. |
| `de-pipeline` | `satisfied` | Trong xây luồng dữ liệu chất lượng không khí theo ngày, ứng viên xây pipeline incremental có checkpoint, retry và cơ chế chạy lại không tạo dữ liệu trùng. |
| `de-data-model-quality` | `satisfied` | Trong xây luồng dữ liệu chất lượng không khí theo ngày, ứng viên thiết kế grain, khóa fact-dimension và kiểm tra null, unique cùng referential integrity. |
| `de-delivery-workflow` | `satisfied` | Trong xây luồng dữ liệu chất lượng không khí theo ngày, ứng viên quản lý mã bằng Git, chạy tác vụ trên Linux và đóng gói môi trường bằng Docker. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 22/30 |
| `de-technical-specialization` | 17/25 |
| `de-role-capability` | 13/20 |
| `projects-and-impact` | 9/15 |
| `communication-and-evidence-quality` | 7/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-de-06

- Vị trí: Junior Data Engineer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-de-06`
- Tóm tắt: Ứng viên chuyển hướng từ lĩnh vực gần và xác nhận chưa thực hành một năng lực bắt buộc. Mục tiêu ứng tuyển là Junior Data Engineer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 41
- Nhãn nháp: `reject`
- Lý do review: không có

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `de-python` | `unsatisfied` | Ứng viên xác nhận chưa từng dùng Python cho tác vụ xử lý dữ liệu. |
| `de-sql` | `satisfied` | Trong chuyển từ backend sang kỹ thuật dữ liệu, ứng viên dùng SQL với CTE, hàm cửa sổ và execution plan để biến đổi dữ liệu dung lượng vừa. |
| `de-pipeline` | `satisfied` | Trong chuyển từ backend sang kỹ thuật dữ liệu, ứng viên xây pipeline incremental có checkpoint, retry và cơ chế chạy lại không tạo dữ liệu trùng. |
| `de-data-model-quality` | `satisfied` | Trong chuyển từ backend sang kỹ thuật dữ liệu, ứng viên thiết kế grain, khóa fact-dimension và kiểm tra null, unique cùng referential integrity. |
| `de-delivery-workflow` | `satisfied` | Trong chuyển từ backend sang kỹ thuật dữ liệu, ứng viên quản lý mã bằng Git, chạy tác vụ trên Linux và đóng gói môi trường bằng Docker. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 10/30 |
| `de-technical-specialization` | 12/25 |
| `de-role-capability` | 9/20 |
| `projects-and-impact` | 5/15 |
| `communication-and-evidence-quality` | 5/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-de-07

- Vị trí: Junior Data Engineer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-de-07`
- Tóm tắt: Hồ sơ vừa đủ yêu cầu cốt lõi nhưng mức độ sâu và phạm vi dự án còn hạn chế. Mục tiêu ứng tuyển là Junior Data Engineer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 70
- Nhãn nháp: `needs_review`
- Lý do review: lower-threshold-boundary

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `de-python` | `satisfied` | Trong tạo pipeline log ứng dụng cho dashboard vận hành, ứng viên viết Python theo module để đọc nhiều nguồn, chuẩn hóa bản ghi và ghi log lỗi theo batch. |
| `de-sql` | `satisfied` | Trong tạo pipeline log ứng dụng cho dashboard vận hành, ứng viên dùng SQL với CTE, hàm cửa sổ và execution plan để biến đổi dữ liệu dung lượng vừa. |
| `de-pipeline` | `satisfied` | Trong tạo pipeline log ứng dụng cho dashboard vận hành, ứng viên xây pipeline incremental có checkpoint, retry và cơ chế chạy lại không tạo dữ liệu trùng. |
| `de-data-model-quality` | `satisfied` | Trong tạo pipeline log ứng dụng cho dashboard vận hành, ứng viên thiết kế grain, khóa fact-dimension và kiểm tra null, unique cùng referential integrity. |
| `de-delivery-workflow` | `satisfied` | Trong tạo pipeline log ứng dụng cho dashboard vận hành, ứng viên quản lý mã bằng Git, chạy tác vụ trên Linux và đóng gói môi trường bằng Docker. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 28/30 |
| `de-technical-specialization` | 14/25 |
| `de-role-capability` | 11/20 |
| `projects-and-impact` | 8/15 |
| `communication-and-evidence-quality` | 9/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-de-08

- Vị trí: Junior Data Engineer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-de-08`
- Tóm tắt: Hồ sơ khá tốt và nằm gần ngưỡng Pass nên cần kiểm tra tính ổn định của quyết định. Mục tiêu ứng tuyển là Junior Data Engineer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 85
- Nhãn nháp: `needs_review`
- Lý do review: upper-threshold-boundary

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `de-python` | `satisfied` | Trong xây luồng incremental cho dữ liệu học tập, ứng viên viết Python theo module để đọc nhiều nguồn, chuẩn hóa bản ghi và ghi log lỗi theo batch. |
| `de-sql` | `satisfied` | Trong xây luồng incremental cho dữ liệu học tập, ứng viên dùng SQL với CTE, hàm cửa sổ và execution plan để biến đổi dữ liệu dung lượng vừa. |
| `de-pipeline` | `satisfied` | Trong xây luồng incremental cho dữ liệu học tập, ứng viên xây pipeline incremental có checkpoint, retry và cơ chế chạy lại không tạo dữ liệu trùng. |
| `de-data-model-quality` | `satisfied` | Trong xây luồng incremental cho dữ liệu học tập, ứng viên thiết kế grain, khóa fact-dimension và kiểm tra null, unique cùng referential integrity. |
| `de-delivery-workflow` | `satisfied` | Trong xây luồng incremental cho dữ liệu học tập, ứng viên quản lý mã bằng Git, chạy tác vụ trên Linux và đóng gói môi trường bằng Docker. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `de-technical-specialization` | 20/25 |
| `de-role-capability` | 16/20 |
| `projects-and-impact` | 12/15 |
| `communication-and-evidence-quality` | 7/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-de-09

- Vị trí: Junior Data Engineer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-de-09`
- Tóm tắt: Ứng viên chuyển từ lĩnh vực gần và chứng minh được năng lực tương đương qua dự án mới. Mục tiêu ứng tuyển là Junior Data Engineer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 79
- Nhãn nháp: `waitlist`
- Lý do review: không có

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `de-python` | `satisfied` | Trong chuyển kinh nghiệm SQL phân tích sang data engineering, ứng viên viết Python theo module để đọc nhiều nguồn, chuẩn hóa bản ghi và ghi log lỗi theo batch. |
| `de-sql` | `satisfied` | Trong chuyển kinh nghiệm SQL phân tích sang data engineering, ứng viên dùng SQL với CTE, hàm cửa sổ và execution plan để biến đổi dữ liệu dung lượng vừa. |
| `de-pipeline` | `satisfied` | Trong chuyển kinh nghiệm SQL phân tích sang data engineering, ứng viên xây pipeline incremental có checkpoint, retry và cơ chế chạy lại không tạo dữ liệu trùng. |
| `de-data-model-quality` | `satisfied` | Trong chuyển kinh nghiệm SQL phân tích sang data engineering, ứng viên thiết kế grain, khóa fact-dimension và kiểm tra null, unique cùng referential integrity. |
| `de-delivery-workflow` | `satisfied` | Trong chuyển kinh nghiệm SQL phân tích sang data engineering, ứng viên quản lý mã bằng Git, chạy tác vụ trên Linux và đóng gói môi trường bằng Docker. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 30/30 |
| `de-technical-specialization` | 16/25 |
| `de-role-capability` | 14/20 |
| `projects-and-impact` | 10/15 |
| `communication-and-evidence-quality` | 9/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.

## s7-pair-de-10

- Vị trí: Junior Data Engineer - Yêu cầu tiêu chuẩn
- Hồ sơ: `cv-s7-de-10`
- Tóm tắt: Hồ sơ chủ yếu liệt kê khóa học và công cụ nhưng không mô tả nhiệm vụ hay sản phẩm đã làm. Mục tiêu ứng tuyển là Junior Data Engineer - Yêu cầu tiêu chuẩn.
- Tổng điểm nháp: 36
- Nhãn nháp: `needs_review`
- Lý do review: missing-critical-evidence, low-score-without-explicit-critical-unsatisfied

| Yêu cầu bắt buộc | Trạng thái | Thông tin liên kết |
| --- | --- | --- |
| `de-python` | `missing` | Đã hoàn thành bài học giới thiệu về Python và tự ghi tên công cụ trong danh sách kỹ năng. |
| `de-sql` | `missing` | Đã hoàn thành bài học giới thiệu về SQL và tự ghi tên công cụ trong danh sách kỹ năng. |
| `de-pipeline` | `missing` | Đã hoàn thành bài học giới thiệu về ETL hoặc ELT và tự ghi tên công cụ trong danh sách kỹ năng. |
| `de-data-model-quality` | `missing` | Đã hoàn thành bài học giới thiệu về Mô hình dữ liệu và chất lượng và tự ghi tên công cụ trong danh sách kỹ năng. |
| `de-delivery-workflow` | `missing` | Đã hoàn thành bài học giới thiệu về Git Linux Docker và tự ghi tên công cụ trong danh sách kỹ năng. |

| Nhóm tiêu chí | Điểm |
| --- | ---: |
| `mandatory-requirements` | 14/30 |
| `de-technical-specialization` | 9/25 |
| `de-role-capability` | 6/20 |
| `projects-and-impact` | 3/15 |
| `communication-and-evidence-quality` | 4/10 |

Lý do tổng hợp: Nhãn và điểm được suy ra từ rubric runtime đã khóa và thông tin liên kết trong hồ sơ. Đây chỉ là bản nháp synthetic, chưa phải ground truth và chưa được dùng để đánh giá classifier.
