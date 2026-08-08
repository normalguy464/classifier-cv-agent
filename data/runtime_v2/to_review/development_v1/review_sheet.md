# Phiếu human review Development Runtime v2

Tập này có 75 case Bronze. Không case nào được dùng để tuning trước khi bạn duyệt.

## Tổng quan

| Pair | Vai trò | Tổng | Nhãn nháp | Lý do review |
| --- | --- | ---: | --- | --- |
| `v2d-pair-da-01` | `data_analyst` | 93 | `pass` | Không |
| `v2d-pair-da-02` | `data_analyst` | 88 | `pass` | Không |
| `v2d-pair-da-03` | `data_analyst` | 82 | `waitlist` | Không |
| `v2d-pair-da-04` | `data_analyst` | 75 | `waitlist` | Không |
| `v2d-pair-da-05` | `data_analyst` | 66 | `needs_review` | missing-critical-evidence, low-score-without-explicit-critical-unsatisfied |
| `v2d-pair-da-06` | `data_analyst` | 76 | `needs_review` | conflicting-critical-evidence |
| `v2d-pair-da-07` | `data_analyst` | 57 | `reject` | Không |
| `v2d-pair-da-08` | `data_analyst` | 24 | `reject` | Không |
| `v2d-pair-da-09` | `data_analyst` | 53 | `needs_review` | missing-critical-evidence, low-score-without-explicit-critical-unsatisfied |
| `v2d-pair-da-10` | `data_analyst` | 68 | `needs_review` | missing-critical-evidence, low-score-without-explicit-critical-unsatisfied, lower-threshold-boundary |
| `v2d-pair-da-11` | `data_analyst` | 85 | `needs_review` | conflicting-critical-evidence, upper-threshold-boundary |
| `v2d-pair-da-12` | `data_analyst` | 79 | `needs_review` | critical-unsatisfied-at-or-above-waitlist-threshold |
| `v2d-pair-da-13` | `data_analyst` | 45 | `needs_review` | missing-critical-evidence, low-score-without-explicit-critical-unsatisfied |
| `v2d-pair-da-14` | `data_analyst` | 89 | `pass` | Không |
| `v2d-pair-da-15` | `data_analyst` | 58 | `needs_review` | low-score-without-explicit-critical-unsatisfied |
| `v2d-pair-be-01` | `python_backend` | 93 | `pass` | Không |
| `v2d-pair-be-02` | `python_backend` | 88 | `pass` | Không |
| `v2d-pair-be-03` | `python_backend` | 82 | `waitlist` | Không |
| `v2d-pair-be-04` | `python_backend` | 75 | `waitlist` | Không |
| `v2d-pair-be-05` | `python_backend` | 66 | `needs_review` | missing-critical-evidence, low-score-without-explicit-critical-unsatisfied |
| `v2d-pair-be-06` | `python_backend` | 76 | `needs_review` | conflicting-critical-evidence |
| `v2d-pair-be-07` | `python_backend` | 57 | `reject` | Không |
| `v2d-pair-be-08` | `python_backend` | 24 | `reject` | Không |
| `v2d-pair-be-09` | `python_backend` | 53 | `needs_review` | missing-critical-evidence, low-score-without-explicit-critical-unsatisfied |
| `v2d-pair-be-10` | `python_backend` | 68 | `needs_review` | missing-critical-evidence, low-score-without-explicit-critical-unsatisfied, lower-threshold-boundary |
| `v2d-pair-be-11` | `python_backend` | 85 | `needs_review` | conflicting-critical-evidence, upper-threshold-boundary |
| `v2d-pair-be-12` | `python_backend` | 79 | `needs_review` | critical-unsatisfied-at-or-above-waitlist-threshold |
| `v2d-pair-be-13` | `python_backend` | 45 | `needs_review` | missing-critical-evidence, low-score-without-explicit-critical-unsatisfied |
| `v2d-pair-be-14` | `python_backend` | 89 | `pass` | Không |
| `v2d-pair-be-15` | `python_backend` | 58 | `needs_review` | low-score-without-explicit-critical-unsatisfied |
| `v2d-pair-fe-01` | `frontend` | 93 | `pass` | Không |
| `v2d-pair-fe-02` | `frontend` | 88 | `pass` | Không |
| `v2d-pair-fe-03` | `frontend` | 82 | `waitlist` | Không |
| `v2d-pair-fe-04` | `frontend` | 75 | `waitlist` | Không |
| `v2d-pair-fe-05` | `frontend` | 66 | `needs_review` | missing-critical-evidence, low-score-without-explicit-critical-unsatisfied |
| `v2d-pair-fe-06` | `frontend` | 76 | `needs_review` | conflicting-critical-evidence |
| `v2d-pair-fe-07` | `frontend` | 57 | `reject` | Không |
| `v2d-pair-fe-08` | `frontend` | 24 | `reject` | Không |
| `v2d-pair-fe-09` | `frontend` | 53 | `needs_review` | missing-critical-evidence, low-score-without-explicit-critical-unsatisfied |
| `v2d-pair-fe-10` | `frontend` | 68 | `needs_review` | missing-critical-evidence, low-score-without-explicit-critical-unsatisfied, lower-threshold-boundary |
| `v2d-pair-fe-11` | `frontend` | 85 | `needs_review` | conflicting-critical-evidence, upper-threshold-boundary |
| `v2d-pair-fe-12` | `frontend` | 79 | `needs_review` | critical-unsatisfied-at-or-above-waitlist-threshold |
| `v2d-pair-fe-13` | `frontend` | 45 | `needs_review` | missing-critical-evidence, low-score-without-explicit-critical-unsatisfied |
| `v2d-pair-fe-14` | `frontend` | 89 | `pass` | Không |
| `v2d-pair-fe-15` | `frontend` | 58 | `needs_review` | low-score-without-explicit-critical-unsatisfied |
| `v2d-pair-qa-01` | `qa_engineer` | 93 | `pass` | Không |
| `v2d-pair-qa-02` | `qa_engineer` | 88 | `pass` | Không |
| `v2d-pair-qa-03` | `qa_engineer` | 82 | `waitlist` | Không |
| `v2d-pair-qa-04` | `qa_engineer` | 75 | `waitlist` | Không |
| `v2d-pair-qa-05` | `qa_engineer` | 66 | `needs_review` | missing-critical-evidence, low-score-without-explicit-critical-unsatisfied |
| `v2d-pair-qa-06` | `qa_engineer` | 76 | `needs_review` | conflicting-critical-evidence |
| `v2d-pair-qa-07` | `qa_engineer` | 57 | `reject` | Không |
| `v2d-pair-qa-08` | `qa_engineer` | 24 | `reject` | Không |
| `v2d-pair-qa-09` | `qa_engineer` | 53 | `needs_review` | missing-critical-evidence, low-score-without-explicit-critical-unsatisfied |
| `v2d-pair-qa-10` | `qa_engineer` | 68 | `needs_review` | missing-critical-evidence, low-score-without-explicit-critical-unsatisfied, lower-threshold-boundary |
| `v2d-pair-qa-11` | `qa_engineer` | 85 | `needs_review` | conflicting-critical-evidence, upper-threshold-boundary |
| `v2d-pair-qa-12` | `qa_engineer` | 79 | `needs_review` | critical-unsatisfied-at-or-above-waitlist-threshold |
| `v2d-pair-qa-13` | `qa_engineer` | 45 | `needs_review` | missing-critical-evidence, low-score-without-explicit-critical-unsatisfied |
| `v2d-pair-qa-14` | `qa_engineer` | 89 | `pass` | Không |
| `v2d-pair-qa-15` | `qa_engineer` | 58 | `needs_review` | low-score-without-explicit-critical-unsatisfied |
| `v2d-pair-de-01` | `data_engineer` | 93 | `pass` | Không |
| `v2d-pair-de-02` | `data_engineer` | 88 | `pass` | Không |
| `v2d-pair-de-03` | `data_engineer` | 82 | `waitlist` | Không |
| `v2d-pair-de-04` | `data_engineer` | 75 | `waitlist` | Không |
| `v2d-pair-de-05` | `data_engineer` | 66 | `needs_review` | missing-critical-evidence, low-score-without-explicit-critical-unsatisfied |
| `v2d-pair-de-06` | `data_engineer` | 76 | `needs_review` | conflicting-critical-evidence |
| `v2d-pair-de-07` | `data_engineer` | 57 | `reject` | Không |
| `v2d-pair-de-08` | `data_engineer` | 24 | `reject` | Không |
| `v2d-pair-de-09` | `data_engineer` | 53 | `needs_review` | missing-critical-evidence, low-score-without-explicit-critical-unsatisfied |
| `v2d-pair-de-10` | `data_engineer` | 68 | `needs_review` | missing-critical-evidence, low-score-without-explicit-critical-unsatisfied, lower-threshold-boundary |
| `v2d-pair-de-11` | `data_engineer` | 85 | `needs_review` | conflicting-critical-evidence, upper-threshold-boundary |
| `v2d-pair-de-12` | `data_engineer` | 79 | `needs_review` | critical-unsatisfied-at-or-above-waitlist-threshold |
| `v2d-pair-de-13` | `data_engineer` | 45 | `needs_review` | missing-critical-evidence, low-score-without-explicit-critical-unsatisfied |
| `v2d-pair-de-14` | `data_engineer` | 89 | `pass` | Không |
| `v2d-pair-de-15` | `data_engineer` | 58 | `needs_review` | low-score-without-explicit-critical-unsatisfied |

## Chi tiết từng case

### v2d-pair-da-01 — Junior Data Analyst - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `93`
- Nhãn nháp: `pass`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `da-sql` | `satisfied` | Từ kho dữ liệu quan hệ, xây câu lệnh tổng hợp theo nhóm, kiểm tra bản ghi trùng và đối chiếu kết quả trước khi phân tích phân tích hành vi mua lại của khách hàng. |
| `da-analysis-language` | `satisfied` | Đóng gói các bước tiền xử lý bằng Python thành hàm có kiểm tra đầu vào để nhóm chạy lại phân tích phân tích hành vi mua lại của khách hàng. |
| `da-bi-reporting` | `satisfied` | Thiết kế dashboard Power BI có bộ lọc, mô hình quan hệ và trang theo dõi KPI cho phân tích hành vi mua lại của khách hàng. |
| `da-business-analysis` | `satisfied` | Làm rõ định nghĩa chỉ số với người dùng báo cáo, nêu giả định và đưa ra khuyến nghị nghiệp vụ từ phân tích hành vi mua lại của khách hàng. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 29/30 | Điểm nháp 29/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `da-technical-specialization` | 23/25 | Điểm nháp 23/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `da-role-capability` | 18/20 | Điểm nháp 18/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 14/15 | Điểm nháp 14/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 9/10 | Điểm nháp 9/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-da-01-01` (education): Chương trình học có bài tổng hợp về phân tích hành vi mua lại của khách hàng; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-da-01-02` (work_experience): Từ kho dữ liệu quan hệ, xây câu lệnh tổng hợp theo nhóm, kiểm tra bản ghi trùng và đối chiếu kết quả trước khi phân tích phân tích hành vi mua lại của khách hàng.
- `ev-v2d-da-01-03` (projects): Đóng gói các bước tiền xử lý bằng Python thành hàm có kiểm tra đầu vào để nhóm chạy lại phân tích phân tích hành vi mua lại của khách hàng.
- `ev-v2d-da-01-04` (work_experience): Thiết kế dashboard Power BI có bộ lọc, mô hình quan hệ và trang theo dõi KPI cho phân tích hành vi mua lại của khách hàng.
- `ev-v2d-da-01-05` (projects): Làm rõ định nghĩa chỉ số với người dùng báo cáo, nêu giả định và đưa ra khuyến nghị nghiệp vụ từ phân tích hành vi mua lại của khách hàng.
- `ev-v2d-da-01-06` (projects): Chiều sâu kỹ thuật của phân tích hành vi mua lại của khách hàng: Giải pháp bao phủ luồng chính, dữ liệu biên và bước kiểm tra lại.
- `ev-v2d-da-01-07` (projects): Lập luận trong phân tích hành vi mua lại của khách hàng: Nêu rõ lựa chọn kỹ thuật, giả định và một phương án đã loại bỏ.
- `ev-v2d-da-01-08` (projects): Bàn giao phân tích hành vi mua lại của khách hàng: Bàn giao source, hướng dẫn chạy và kết quả kiểm tra cho người dùng nội bộ.
- `ev-v2d-da-01-09` (other): Cách trình bày phân tích hành vi mua lại của khách hàng: Mô tả ngắn gọn phạm vi, kết quả định lượng và giới hạn còn lại.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-da-02 — Junior Data Analyst - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `88`
- Nhãn nháp: `pass`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `da-sql` | `satisfied` | Tối ưu câu truy vấn nhiều bước sau khi đọc execution plan, giảm thời gian lấy dữ liệu phục vụ theo dõi hiệu quả chiến dịch đa kênh. |
| `da-analysis-language` | `satisfied` | Dùng pandas để làm sạch kiểu dữ liệu, xử lý giá trị thiếu và tái tạo notebook phân tích theo dõi hiệu quả chiến dịch đa kênh. |
| `da-bi-reporting` | `satisfied` | Xây báo cáo Tableau, định nghĩa chỉ số và kiểm tra số tổng với nguồn trước khi bàn giao theo dõi hiệu quả chiến dịch đa kênh. |
| `da-business-analysis` | `satisfied` | Thực hiện luồng phân tích từ câu hỏi, dữ liệu, kiểm tra sai lệch đến kết luận và giới hạn cho theo dõi hiệu quả chiến dịch đa kênh. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 28/30 | Điểm nháp 28/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `da-technical-specialization` | 22/25 | Điểm nháp 22/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `da-role-capability` | 17/20 | Điểm nháp 17/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 13/15 | Điểm nháp 13/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 8/10 | Điểm nháp 8/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-da-02-01` (education): Chương trình học có bài tổng hợp về theo dõi hiệu quả chiến dịch đa kênh; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-da-02-02` (work_experience): Tối ưu câu truy vấn nhiều bước sau khi đọc execution plan, giảm thời gian lấy dữ liệu phục vụ theo dõi hiệu quả chiến dịch đa kênh.
- `ev-v2d-da-02-03` (projects): Dùng pandas để làm sạch kiểu dữ liệu, xử lý giá trị thiếu và tái tạo notebook phân tích theo dõi hiệu quả chiến dịch đa kênh.
- `ev-v2d-da-02-04` (work_experience): Xây báo cáo Tableau, định nghĩa chỉ số và kiểm tra số tổng với nguồn trước khi bàn giao theo dõi hiệu quả chiến dịch đa kênh.
- `ev-v2d-da-02-05` (projects): Thực hiện luồng phân tích từ câu hỏi, dữ liệu, kiểm tra sai lệch đến kết luận và giới hạn cho theo dõi hiệu quả chiến dịch đa kênh.
- `ev-v2d-da-02-06` (projects): Chiều sâu kỹ thuật của theo dõi hiệu quả chiến dịch đa kênh: Thực hiện phần cốt lõi và xử lý ít nhất một lỗi phát sinh.
- `ev-v2d-da-02-07` (projects): Lập luận trong theo dõi hiệu quả chiến dịch đa kênh: So sánh hai cách triển khai trước khi chọn giải pháp phù hợp phạm vi.
- `ev-v2d-da-02-08` (projects): Bàn giao theo dõi hiệu quả chiến dịch đa kênh: Có quy trình review và tài liệu để thành viên khác chạy lại.
- `ev-v2d-da-02-09` (other): Cách trình bày theo dõi hiệu quả chiến dịch đa kênh: Thông tin nhất quán, có đầu ra nhưng phần đo lường chưa hoàn toàn độc lập.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-da-03 — Junior Data Analyst - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `82`
- Nhãn nháp: `waitlist`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `da-sql` | `satisfied` | Tự viết chuỗi truy vấn kết hợp nhiều bảng, dùng CTE và hàm cửa sổ để tạo tập dữ liệu phân tích cho đối soát chất lượng đơn hàng. |
| `da-analysis-language` | `satisfied` | Viết script R với dplyr và ggplot2 để biến đổi dữ liệu, kiểm tra phân phối và trực quan hóa kết quả đối soát chất lượng đơn hàng. |
| `da-bi-reporting` | `satisfied` | Tạo dashboard tương tác trên Looker Studio, tách metric vận hành và metric kết quả cho đối soát chất lượng đơn hàng. |
| `da-business-analysis` | `satisfied` | Chuyển câu hỏi giữ chân khách hàng thành KPI, phân tích nguyên nhân và đề xuất hai hành động có thể kiểm chứng cho đối soát chất lượng đơn hàng. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 26/30 | Điểm nháp 26/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `da-technical-specialization` | 20/25 | Điểm nháp 20/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `da-role-capability` | 16/20 | Điểm nháp 16/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 12/15 | Điểm nháp 12/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 8/10 | Điểm nháp 8/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-da-03-01` (education): Chương trình học có bài tổng hợp về đối soát chất lượng đơn hàng; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-da-03-02` (work_experience): Tự viết chuỗi truy vấn kết hợp nhiều bảng, dùng CTE và hàm cửa sổ để tạo tập dữ liệu phân tích cho đối soát chất lượng đơn hàng.
- `ev-v2d-da-03-03` (projects): Viết script R với dplyr và ggplot2 để biến đổi dữ liệu, kiểm tra phân phối và trực quan hóa kết quả đối soát chất lượng đơn hàng.
- `ev-v2d-da-03-04` (work_experience): Tạo dashboard tương tác trên Looker Studio, tách metric vận hành và metric kết quả cho đối soát chất lượng đơn hàng.
- `ev-v2d-da-03-05` (projects): Chuyển câu hỏi giữ chân khách hàng thành KPI, phân tích nguyên nhân và đề xuất hai hành động có thể kiểm chứng cho đối soát chất lượng đơn hàng.
- `ev-v2d-da-03-06` (projects): Chiều sâu kỹ thuật của đối soát chất lượng đơn hàng: Hoàn thành luồng chính và kiểm tra dữ liệu đầu vào phổ biến.
- `ev-v2d-da-03-07` (projects): Lập luận trong đối soát chất lượng đơn hàng: Giải thích quyết định dựa trên yêu cầu và giới hạn thời gian.
- `ev-v2d-da-03-08` (projects): Bàn giao đối soát chất lượng đơn hàng: Bàn giao qua repository và checklist chạy thử.
- `ev-v2d-da-03-09` (other): Cách trình bày đối soát chất lượng đơn hàng: Nêu vai trò, kết quả và một giới hạn kỹ thuật.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-da-04 — Junior Data Analyst - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `75`
- Nhãn nháp: `waitlist`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `da-sql` | `satisfied` | Từ kho dữ liệu quan hệ, xây câu lệnh tổng hợp theo nhóm, kiểm tra bản ghi trùng và đối chiếu kết quả trước khi phân tích phân tích thời gian xử lý yêu cầu hỗ trợ. |
| `da-analysis-language` | `satisfied` | Đóng gói các bước tiền xử lý bằng Python thành hàm có kiểm tra đầu vào để nhóm chạy lại phân tích phân tích thời gian xử lý yêu cầu hỗ trợ. |
| `da-bi-reporting` | `satisfied` | Thiết kế dashboard Power BI có bộ lọc, mô hình quan hệ và trang theo dõi KPI cho phân tích thời gian xử lý yêu cầu hỗ trợ. |
| `da-business-analysis` | `satisfied` | Làm rõ định nghĩa chỉ số với người dùng báo cáo, nêu giả định và đưa ra khuyến nghị nghiệp vụ từ phân tích thời gian xử lý yêu cầu hỗ trợ. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 24/30 | Điểm nháp 24/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `da-technical-specialization` | 18/25 | Điểm nháp 18/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `da-role-capability` | 15/20 | Điểm nháp 15/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 11/15 | Điểm nháp 11/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 7/10 | Điểm nháp 7/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-da-04-01` (education): Chương trình học có bài tổng hợp về phân tích thời gian xử lý yêu cầu hỗ trợ; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-da-04-02` (projects): Từ kho dữ liệu quan hệ, xây câu lệnh tổng hợp theo nhóm, kiểm tra bản ghi trùng và đối chiếu kết quả trước khi phân tích phân tích thời gian xử lý yêu cầu hỗ trợ.
- `ev-v2d-da-04-03` (projects): Đóng gói các bước tiền xử lý bằng Python thành hàm có kiểm tra đầu vào để nhóm chạy lại phân tích phân tích thời gian xử lý yêu cầu hỗ trợ.
- `ev-v2d-da-04-04` (projects): Thiết kế dashboard Power BI có bộ lọc, mô hình quan hệ và trang theo dõi KPI cho phân tích thời gian xử lý yêu cầu hỗ trợ.
- `ev-v2d-da-04-05` (projects): Làm rõ định nghĩa chỉ số với người dùng báo cáo, nêu giả định và đưa ra khuyến nghị nghiệp vụ từ phân tích thời gian xử lý yêu cầu hỗ trợ.
- `ev-v2d-da-04-06` (projects): Chiều sâu kỹ thuật của phân tích thời gian xử lý yêu cầu hỗ trợ: Có sản phẩm chạy được trong phạm vi học tập hoặc cá nhân.
- `ev-v2d-da-04-07` (projects): Lập luận trong phân tích thời gian xử lý yêu cầu hỗ trợ: Nêu lý do lựa chọn chính nhưng chưa phân tích sâu trade-off.
- `ev-v2d-da-04-08` (projects): Bàn giao phân tích thời gian xử lý yêu cầu hỗ trợ: Có source và hướng dẫn cơ bản để tái chạy.
- `ev-v2d-da-04-09` (other): Cách trình bày phân tích thời gian xử lý yêu cầu hỗ trợ: Thông tin đủ hiểu nhưng thiếu số đo tác động độc lập.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-da-05 — Junior Data Analyst - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `66`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `missing-critical-evidence, low-score-without-explicit-critical-unsatisfied`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `da-sql` | `missing` | Không có thông tin trực tiếp |
| `da-analysis-language` | `satisfied` | Dùng pandas để làm sạch kiểu dữ liệu, xử lý giá trị thiếu và tái tạo notebook phân tích xây báo cáo vận hành cho chuỗi bán lẻ. |
| `da-bi-reporting` | `satisfied` | Xây báo cáo Tableau, định nghĩa chỉ số và kiểm tra số tổng với nguồn trước khi bàn giao xây báo cáo vận hành cho chuỗi bán lẻ. |
| `da-business-analysis` | `satisfied` | Thực hiện luồng phân tích từ câu hỏi, dữ liệu, kiểm tra sai lệch đến kết luận và giới hạn cho xây báo cáo vận hành cho chuỗi bán lẻ. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 18/30 | Điểm nháp 18/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `da-technical-specialization` | 17/25 | Điểm nháp 17/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `da-role-capability` | 14/20 | Điểm nháp 14/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 10/15 | Điểm nháp 10/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 7/10 | Điểm nháp 7/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-da-05-01` (education): Chương trình học có bài tổng hợp về xây báo cáo vận hành cho chuỗi bán lẻ; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-da-05-02` (education): Có đọc tài liệu về kho dữ liệu; không có ví dụ sử dụng câu lệnh truy xuất hay biến đổi bảng.
- `ev-v2d-da-05-03` (projects): Dùng pandas để làm sạch kiểu dữ liệu, xử lý giá trị thiếu và tái tạo notebook phân tích xây báo cáo vận hành cho chuỗi bán lẻ.
- `ev-v2d-da-05-04` (projects): Xây báo cáo Tableau, định nghĩa chỉ số và kiểm tra số tổng với nguồn trước khi bàn giao xây báo cáo vận hành cho chuỗi bán lẻ.
- `ev-v2d-da-05-05` (projects): Thực hiện luồng phân tích từ câu hỏi, dữ liệu, kiểm tra sai lệch đến kết luận và giới hạn cho xây báo cáo vận hành cho chuỗi bán lẻ.
- `ev-v2d-da-05-06` (projects): Chiều sâu kỹ thuật của xây báo cáo vận hành cho chuỗi bán lẻ: Các phần được mô tả có thao tác thực hành nhưng độ bao phủ chưa đầy đủ.
- `ev-v2d-da-05-07` (projects): Lập luận trong xây báo cáo vận hành cho chuỗi bán lẻ: Có giải thích cho phần đã làm, không suy diễn phần còn thiếu.
- `ev-v2d-da-05-08` (projects): Bàn giao xây báo cáo vận hành cho chuỗi bán lẻ: Bàn giao được phạm vi hiện có và ghi rõ giới hạn.
- `ev-v2d-da-05-09` (other): Cách trình bày xây báo cáo vận hành cho chuỗi bán lẻ: Hồ sơ phân biệt rõ điều đã làm và điều chưa có thông tin.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-da-06 — Junior Data Analyst - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `76`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `conflicting-critical-evidence`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `da-sql` | `satisfied` | Tự viết chuỗi truy vấn kết hợp nhiều bảng, dùng CTE và hàm cửa sổ để tạo tập dữ liệu phân tích cho phân tích hành vi mua lại của khách hàng. |
| `da-analysis-language` | `conflicting` | Viết script R với dplyr và ggplot2 để biến đổi dữ liệu, kiểm tra phân phối và trực quan hóa kết quả phân tích hành vi mua lại của khách hàng.<br>Không thể chỉnh sửa notebook phân tích và chưa viết mã biến đổi dữ liệu cho phân tích hành vi mua lại của khách hàng. |
| `da-bi-reporting` | `satisfied` | Tạo dashboard tương tác trên Looker Studio, tách metric vận hành và metric kết quả cho phân tích hành vi mua lại của khách hàng. |
| `da-business-analysis` | `satisfied` | Chuyển câu hỏi giữ chân khách hàng thành KPI, phân tích nguyên nhân và đề xuất hai hành động có thể kiểm chứng cho phân tích hành vi mua lại của khách hàng. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 22/30 | Điểm nháp 22/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `da-technical-specialization` | 19/25 | Điểm nháp 19/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `da-role-capability` | 15/20 | Điểm nháp 15/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 12/15 | Điểm nháp 12/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 8/10 | Điểm nháp 8/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-da-06-01` (education): Chương trình học có bài tổng hợp về phân tích hành vi mua lại của khách hàng; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-da-06-02` (projects): Tự viết chuỗi truy vấn kết hợp nhiều bảng, dùng CTE và hàm cửa sổ để tạo tập dữ liệu phân tích cho phân tích hành vi mua lại của khách hàng.
- `ev-v2d-da-06-03` (projects): Viết script R với dplyr và ggplot2 để biến đổi dữ liệu, kiểm tra phân phối và trực quan hóa kết quả phân tích hành vi mua lại của khách hàng.
- `ev-v2d-da-06-04` (other): Không thể chỉnh sửa notebook phân tích và chưa viết mã biến đổi dữ liệu cho phân tích hành vi mua lại của khách hàng.
- `ev-v2d-da-06-05` (projects): Tạo dashboard tương tác trên Looker Studio, tách metric vận hành và metric kết quả cho phân tích hành vi mua lại của khách hàng.
- `ev-v2d-da-06-06` (projects): Chuyển câu hỏi giữ chân khách hàng thành KPI, phân tích nguyên nhân và đề xuất hai hành động có thể kiểm chứng cho phân tích hành vi mua lại của khách hàng.
- `ev-v2d-da-06-07` (projects): Chiều sâu kỹ thuật của phân tích hành vi mua lại của khách hàng: Có đầu ra kỹ thuật nhưng trạng thái một năng lực chưa thể kết luận.
- `ev-v2d-da-06-08` (projects): Lập luận trong phân tích hành vi mua lại của khách hàng: Ghi lại quyết định của dự án nhưng chưa giải thích được mâu thuẫn trong hồ sơ.
- `ev-v2d-da-06-09` (projects): Bàn giao phân tích hành vi mua lại của khách hàng: Có artifact bàn giao và một cảnh báo cần xác minh.
- `ev-v2d-da-06-10` (other): Cách trình bày phân tích hành vi mua lại của khách hàng: Thông tin khá rõ ngoài điểm mâu thuẫn cần human review.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-da-07 — Junior Data Analyst - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `57`
- Nhãn nháp: `reject`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `da-sql` | `satisfied` | Từ kho dữ liệu quan hệ, xây câu lệnh tổng hợp theo nhóm, kiểm tra bản ghi trùng và đối chiếu kết quả trước khi phân tích theo dõi hiệu quả chiến dịch đa kênh. |
| `da-analysis-language` | `satisfied` | Đóng gói các bước tiền xử lý bằng Python thành hàm có kiểm tra đầu vào để nhóm chạy lại phân tích theo dõi hiệu quả chiến dịch đa kênh. |
| `da-bi-reporting` | `unsatisfied` | Không sử dụng được công cụ trực quan hóa dữ liệu để bàn giao kết quả theo dõi hiệu quả chiến dịch đa kênh. |
| `da-business-analysis` | `satisfied` | Làm rõ định nghĩa chỉ số với người dùng báo cáo, nêu giả định và đưa ra khuyến nghị nghiệp vụ từ theo dõi hiệu quả chiến dịch đa kênh. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 16/30 | Điểm nháp 16/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `da-technical-specialization` | 15/25 | Điểm nháp 15/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `da-role-capability` | 12/20 | Điểm nháp 12/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 8/15 | Điểm nháp 8/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 6/10 | Điểm nháp 6/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-da-07-01` (education): Chương trình học có bài tổng hợp về theo dõi hiệu quả chiến dịch đa kênh; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-da-07-02` (projects): Từ kho dữ liệu quan hệ, xây câu lệnh tổng hợp theo nhóm, kiểm tra bản ghi trùng và đối chiếu kết quả trước khi phân tích theo dõi hiệu quả chiến dịch đa kênh.
- `ev-v2d-da-07-03` (projects): Đóng gói các bước tiền xử lý bằng Python thành hàm có kiểm tra đầu vào để nhóm chạy lại phân tích theo dõi hiệu quả chiến dịch đa kênh.
- `ev-v2d-da-07-04` (other): Không sử dụng được công cụ trực quan hóa dữ liệu để bàn giao kết quả theo dõi hiệu quả chiến dịch đa kênh.
- `ev-v2d-da-07-05` (projects): Làm rõ định nghĩa chỉ số với người dùng báo cáo, nêu giả định và đưa ra khuyến nghị nghiệp vụ từ theo dõi hiệu quả chiến dịch đa kênh.
- `ev-v2d-da-07-06` (projects): Chiều sâu kỹ thuật của theo dõi hiệu quả chiến dịch đa kênh: Một phần công việc phụ thuộc vào thành viên khác và không có khả năng thay thế.
- `ev-v2d-da-07-07` (projects): Lập luận trong theo dõi hiệu quả chiến dịch đa kênh: Nêu đúng giới hạn hiện tại nhưng chưa có kế hoạch kiểm chứng năng lực thiếu.
- `ev-v2d-da-07-08` (projects): Bàn giao theo dõi hiệu quả chiến dịch đa kênh: Chỉ bàn giao được phần việc hẹp.
- `ev-v2d-da-07-09` (other): Cách trình bày theo dõi hiệu quả chiến dịch đa kênh: Thông tin phủ định rõ và không bị che bởi danh sách từ khóa.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-da-08 — Junior Data Analyst - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `24`
- Nhãn nháp: `reject`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `da-sql` | `unsatisfied` | Mới học cú pháp truy vấn cơ bản và chưa tự xử lý bài toán nối nhiều bảng trong sản phẩm nào. |
| `da-analysis-language` | `unsatisfied` | Không thể chỉnh sửa notebook phân tích và chưa viết mã biến đổi dữ liệu cho đối soát chất lượng đơn hàng. |
| `da-bi-reporting` | `unsatisfied` | Chưa từng tự xây dashboard hoặc báo cáo BI; chỉ xem báo cáo đã được người khác xuất. |
| `da-business-analysis` | `unsatisfied` | Không thể giải thích chỉ số hoặc đưa ra khuyến nghị từ kết quả đối soát chất lượng đơn hàng. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 5/30 | Điểm nháp 5/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `da-technical-specialization` | 5/25 | Điểm nháp 5/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `da-role-capability` | 6/20 | Điểm nháp 6/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 4/15 | Điểm nháp 4/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 4/10 | Điểm nháp 4/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-da-08-01` (education): Chương trình học có bài tổng hợp về đối soát chất lượng đơn hàng; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-da-08-02` (other): Mới học cú pháp truy vấn cơ bản và chưa tự xử lý bài toán nối nhiều bảng trong sản phẩm nào.
- `ev-v2d-da-08-03` (other): Không thể chỉnh sửa notebook phân tích và chưa viết mã biến đổi dữ liệu cho đối soát chất lượng đơn hàng.
- `ev-v2d-da-08-04` (other): Chưa từng tự xây dashboard hoặc báo cáo BI; chỉ xem báo cáo đã được người khác xuất.
- `ev-v2d-da-08-05` (other): Không thể giải thích chỉ số hoặc đưa ra khuyến nghị từ kết quả đối soát chất lượng đơn hàng.
- `ev-v2d-da-08-06` (projects): Chiều sâu kỹ thuật của đối soát chất lượng đơn hàng: Không có artifact hoặc tác vụ chuyên môn do ứng viên tự hoàn thành.
- `ev-v2d-da-08-07` (projects): Lập luận trong đối soát chất lượng đơn hàng: Chưa có quyết định kỹ thuật để đánh giá.
- `ev-v2d-da-08-08` (projects): Bàn giao đối soát chất lượng đơn hàng: Không có quy trình bàn giao có thể tái tạo.
- `ev-v2d-da-08-09` (other): Cách trình bày đối soát chất lượng đơn hàng: Giới hạn được phát biểu rõ, không tạo ấn tượng sai về kinh nghiệm.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-da-09 — Junior Data Analyst - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `53`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `missing-critical-evidence, low-score-without-explicit-critical-unsatisfied`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `da-sql` | `missing` | Không có thông tin trực tiếp |
| `da-analysis-language` | `satisfied` | Viết script R với dplyr và ggplot2 để biến đổi dữ liệu, kiểm tra phân phối và trực quan hóa kết quả phân tích thời gian xử lý yêu cầu hỗ trợ. |
| `da-bi-reporting` | `missing` | Không có thông tin trực tiếp |
| `da-business-analysis` | `satisfied` | Chuyển câu hỏi giữ chân khách hàng thành KPI, phân tích nguyên nhân và đề xuất hai hành động có thể kiểm chứng cho phân tích thời gian xử lý yêu cầu hỗ trợ. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 14/30 | Điểm nháp 14/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `da-technical-specialization` | 13/25 | Điểm nháp 13/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `da-role-capability` | 12/20 | Điểm nháp 12/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 8/15 | Điểm nháp 8/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 6/10 | Điểm nháp 6/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-da-09-01` (education): Chương trình học có bài tổng hợp về phân tích thời gian xử lý yêu cầu hỗ trợ; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-da-09-02` (education): Có đọc tài liệu về kho dữ liệu; không có ví dụ sử dụng câu lệnh truy xuất hay biến đổi bảng.
- `ev-v2d-da-09-03` (projects): Viết script R với dplyr và ggplot2 để biến đổi dữ liệu, kiểm tra phân phối và trực quan hóa kết quả phân tích thời gian xử lý yêu cầu hỗ trợ.
- `ev-v2d-da-09-04` (education): Theo dõi buổi demo dashboard của nhóm; không nêu phần việc trực tiếp của ứng viên.
- `ev-v2d-da-09-05` (projects): Chuyển câu hỏi giữ chân khách hàng thành KPI, phân tích nguyên nhân và đề xuất hai hành động có thể kiểm chứng cho phân tích thời gian xử lý yêu cầu hỗ trợ.
- `ev-v2d-da-09-06` (projects): Chiều sâu kỹ thuật của phân tích thời gian xử lý yêu cầu hỗ trợ: Có một số thao tác đơn lẻ nhưng chưa thành luồng hoàn chỉnh.
- `ev-v2d-da-09-07` (projects): Lập luận trong phân tích thời gian xử lý yêu cầu hỗ trợ: Lý do thực hiện chưa gắn với tiêu chí thành công.
- `ev-v2d-da-09-08` (projects): Bàn giao phân tích thời gian xử lý yêu cầu hỗ trợ: Artifact rời rạc và chưa có hướng dẫn tái chạy.
- `ev-v2d-da-09-09` (other): Cách trình bày phân tích thời gian xử lý yêu cầu hỗ trợ: Hồ sơ không khẳng định các năng lực chưa được chứng minh.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-da-10 — Junior Data Analyst - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `68`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `missing-critical-evidence, low-score-without-explicit-critical-unsatisfied, lower-threshold-boundary`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `da-sql` | `satisfied` | Từ kho dữ liệu quan hệ, xây câu lệnh tổng hợp theo nhóm, kiểm tra bản ghi trùng và đối chiếu kết quả trước khi phân tích xây báo cáo vận hành cho chuỗi bán lẻ. |
| `da-analysis-language` | `satisfied` | Đóng gói các bước tiền xử lý bằng Python thành hàm có kiểm tra đầu vào để nhóm chạy lại phân tích xây báo cáo vận hành cho chuỗi bán lẻ. |
| `da-bi-reporting` | `satisfied` | Thiết kế dashboard Power BI có bộ lọc, mô hình quan hệ và trang theo dõi KPI cho xây báo cáo vận hành cho chuỗi bán lẻ. |
| `da-business-analysis` | `missing` | Không có thông tin trực tiếp |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 20/30 | Điểm nháp 20/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `da-technical-specialization` | 17/25 | Điểm nháp 17/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `da-role-capability` | 13/20 | Điểm nháp 13/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 10/15 | Điểm nháp 10/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 8/10 | Điểm nháp 8/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-da-10-01` (education): Chương trình học có bài tổng hợp về xây báo cáo vận hành cho chuỗi bán lẻ; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-da-10-02` (projects): Từ kho dữ liệu quan hệ, xây câu lệnh tổng hợp theo nhóm, kiểm tra bản ghi trùng và đối chiếu kết quả trước khi phân tích xây báo cáo vận hành cho chuỗi bán lẻ.
- `ev-v2d-da-10-03` (projects): Đóng gói các bước tiền xử lý bằng Python thành hàm có kiểm tra đầu vào để nhóm chạy lại phân tích xây báo cáo vận hành cho chuỗi bán lẻ.
- `ev-v2d-da-10-04` (projects): Thiết kế dashboard Power BI có bộ lọc, mô hình quan hệ và trang theo dõi KPI cho xây báo cáo vận hành cho chuỗi bán lẻ.
- `ev-v2d-da-10-05` (other): Liệt kê khái niệm KPI mà không gắn với dữ liệu, giả định hay kết luận cụ thể.
- `ev-v2d-da-10-06` (projects): Chiều sâu kỹ thuật của xây báo cáo vận hành cho chuỗi bán lẻ: Phần lớn năng lực có ví dụ nhưng chiều sâu chưa đồng đều.
- `ev-v2d-da-10-07` (projects): Lập luận trong xây báo cáo vận hành cho chuỗi bán lẻ: Có giải thích lựa chọn chính và một giả định chưa kiểm tra.
- `ev-v2d-da-10-08` (projects): Bàn giao xây báo cáo vận hành cho chuỗi bán lẻ: Có bản chạy thử và ghi chú vận hành cơ bản.
- `ev-v2d-da-10-09` (other): Cách trình bày xây báo cáo vận hành cho chuỗi bán lẻ: Thông tin tương đối rõ nhưng cần xác minh phần còn thiếu.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-da-11 — Junior Data Analyst - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `85`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `conflicting-critical-evidence, upper-threshold-boundary`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `da-sql` | `conflicting` | Tối ưu câu truy vấn nhiều bước sau khi đọc execution plan, giảm thời gian lấy dữ liệu phục vụ phân tích hành vi mua lại của khách hàng.<br>Không thể tự viết câu lệnh lấy dữ liệu quan hệ; phần truy xuất cho phân tích hành vi mua lại của khách hàng do người khác chuẩn bị. |
| `da-analysis-language` | `satisfied` | Dùng pandas để làm sạch kiểu dữ liệu, xử lý giá trị thiếu và tái tạo notebook phân tích phân tích hành vi mua lại của khách hàng. |
| `da-bi-reporting` | `satisfied` | Xây báo cáo Tableau, định nghĩa chỉ số và kiểm tra số tổng với nguồn trước khi bàn giao phân tích hành vi mua lại của khách hàng. |
| `da-business-analysis` | `satisfied` | Thực hiện luồng phân tích từ câu hỏi, dữ liệu, kiểm tra sai lệch đến kết luận và giới hạn cho phân tích hành vi mua lại của khách hàng. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 25/30 | Điểm nháp 25/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `da-technical-specialization` | 21/25 | Điểm nháp 21/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `da-role-capability` | 17/20 | Điểm nháp 17/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 13/15 | Điểm nháp 13/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 9/10 | Điểm nháp 9/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-da-11-01` (education): Chương trình học có bài tổng hợp về phân tích hành vi mua lại của khách hàng; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-da-11-02` (work_experience): Tối ưu câu truy vấn nhiều bước sau khi đọc execution plan, giảm thời gian lấy dữ liệu phục vụ phân tích hành vi mua lại của khách hàng.
- `ev-v2d-da-11-03` (other): Không thể tự viết câu lệnh lấy dữ liệu quan hệ; phần truy xuất cho phân tích hành vi mua lại của khách hàng do người khác chuẩn bị.
- `ev-v2d-da-11-04` (projects): Dùng pandas để làm sạch kiểu dữ liệu, xử lý giá trị thiếu và tái tạo notebook phân tích phân tích hành vi mua lại của khách hàng.
- `ev-v2d-da-11-05` (work_experience): Xây báo cáo Tableau, định nghĩa chỉ số và kiểm tra số tổng với nguồn trước khi bàn giao phân tích hành vi mua lại của khách hàng.
- `ev-v2d-da-11-06` (projects): Thực hiện luồng phân tích từ câu hỏi, dữ liệu, kiểm tra sai lệch đến kết luận và giới hạn cho phân tích hành vi mua lại của khách hàng.
- `ev-v2d-da-11-07` (projects): Chiều sâu kỹ thuật của phân tích hành vi mua lại của khách hàng: Artifact kỹ thuật khá hoàn chỉnh ngoài điểm cần xác minh.
- `ev-v2d-da-11-08` (projects): Lập luận trong phân tích hành vi mua lại của khách hàng: Nêu trade-off và cách kiểm tra kết quả.
- `ev-v2d-da-11-09` (projects): Bàn giao phân tích hành vi mua lại của khách hàng: Bàn giao có review, test và hướng dẫn sử dụng.
- `ev-v2d-da-11-10` (other): Cách trình bày phân tích hành vi mua lại của khách hàng: Trình bày tốt nhưng chưa giải quyết được phát biểu mâu thuẫn.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-da-12 — Junior Data Analyst - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `79`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `critical-unsatisfied-at-or-above-waitlist-threshold`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `da-sql` | `satisfied` | Tự viết chuỗi truy vấn kết hợp nhiều bảng, dùng CTE và hàm cửa sổ để tạo tập dữ liệu phân tích cho theo dõi hiệu quả chiến dịch đa kênh. |
| `da-analysis-language` | `satisfied` | Viết script R với dplyr và ggplot2 để biến đổi dữ liệu, kiểm tra phân phối và trực quan hóa kết quả theo dõi hiệu quả chiến dịch đa kênh. |
| `da-bi-reporting` | `satisfied` | Tạo dashboard tương tác trên Looker Studio, tách metric vận hành và metric kết quả cho theo dõi hiệu quả chiến dịch đa kênh. |
| `da-business-analysis` | `unsatisfied` | Không thể giải thích chỉ số hoặc đưa ra khuyến nghị từ kết quả theo dõi hiệu quả chiến dịch đa kênh. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 23/30 | Điểm nháp 23/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `da-technical-specialization` | 20/25 | Điểm nháp 20/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `da-role-capability` | 16/20 | Điểm nháp 16/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 12/15 | Điểm nháp 12/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 8/10 | Điểm nháp 8/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-da-12-01` (education): Chương trình học có bài tổng hợp về theo dõi hiệu quả chiến dịch đa kênh; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-da-12-02` (projects): Tự viết chuỗi truy vấn kết hợp nhiều bảng, dùng CTE và hàm cửa sổ để tạo tập dữ liệu phân tích cho theo dõi hiệu quả chiến dịch đa kênh.
- `ev-v2d-da-12-03` (projects): Viết script R với dplyr và ggplot2 để biến đổi dữ liệu, kiểm tra phân phối và trực quan hóa kết quả theo dõi hiệu quả chiến dịch đa kênh.
- `ev-v2d-da-12-04` (projects): Tạo dashboard tương tác trên Looker Studio, tách metric vận hành và metric kết quả cho theo dõi hiệu quả chiến dịch đa kênh.
- `ev-v2d-da-12-05` (other): Không thể giải thích chỉ số hoặc đưa ra khuyến nghị từ kết quả theo dõi hiệu quả chiến dịch đa kênh.
- `ev-v2d-da-12-06` (projects): Chiều sâu kỹ thuật của theo dõi hiệu quả chiến dịch đa kênh: Các năng lực còn lại có thực hành và đầu ra cụ thể.
- `ev-v2d-da-12-07` (projects): Lập luận trong theo dõi hiệu quả chiến dịch đa kênh: Nêu cách xử lý trong phạm vi đã biết và giới hạn cần hỗ trợ.
- `ev-v2d-da-12-08` (projects): Bàn giao theo dõi hiệu quả chiến dịch đa kênh: Có artifact bàn giao cho phần việc đã hoàn thành.
- `ev-v2d-da-12-09` (other): Cách trình bày theo dõi hiệu quả chiến dịch đa kênh: Hồ sơ minh bạch về năng lực chưa đạt.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-da-13 — Junior Data Analyst - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `45`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `missing-critical-evidence, low-score-without-explicit-critical-unsatisfied`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `da-sql` | `missing` | Không có thông tin trực tiếp |
| `da-analysis-language` | `missing` | Không có thông tin trực tiếp |
| `da-bi-reporting` | `missing` | Không có thông tin trực tiếp |
| `da-business-analysis` | `missing` | Không có thông tin trực tiếp |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 12/30 | Điểm nháp 12/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `da-technical-specialization` | 10/25 | Điểm nháp 10/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `da-role-capability` | 10/20 | Điểm nháp 10/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 7/15 | Điểm nháp 7/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 6/10 | Điểm nháp 6/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-da-13-01` (education): Chương trình học có bài tổng hợp về đối soát chất lượng đơn hàng; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-da-13-02` (education): Có đọc tài liệu về kho dữ liệu; không có ví dụ sử dụng câu lệnh truy xuất hay biến đổi bảng.
- `ev-v2d-da-13-03` (other): Hoàn thành bài nhập môn lập trình nhưng không trình bày mã nguồn hoặc đầu ra phân tích dữ liệu.
- `ev-v2d-da-13-04` (education): Theo dõi buổi demo dashboard của nhóm; không nêu phần việc trực tiếp của ứng viên.
- `ev-v2d-da-13-05` (other): Có tham dự cuộc họp nghiệp vụ nhưng không nêu câu hỏi, phân tích hoặc quyết định do mình thực hiện.
- `ev-v2d-da-13-06` (projects): Chiều sâu kỹ thuật của đối soát chất lượng đơn hàng: Chỉ có nội dung học tập và quan sát, chưa có sản phẩm áp dụng.
- `ev-v2d-da-13-07` (projects): Lập luận trong đối soát chất lượng đơn hàng: Không có quyết định kỹ thuật thuộc trách nhiệm ứng viên.
- `ev-v2d-da-13-08` (projects): Bàn giao đối soát chất lượng đơn hàng: Không có artifact có thể kiểm tra độc lập.
- `ev-v2d-da-13-09` (other): Cách trình bày đối soát chất lượng đơn hàng: Không suy diễn từ tên khóa học hoặc công cụ được nhắc tới.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-da-14 — Junior Data Analyst - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `89`
- Nhãn nháp: `pass`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `da-sql` | `satisfied` | Tối ưu câu truy vấn nhiều bước sau khi đọc execution plan, giảm thời gian lấy dữ liệu phục vụ phân tích thời gian xử lý yêu cầu hỗ trợ. |
| `da-analysis-language` | `satisfied` | Dùng pandas để làm sạch kiểu dữ liệu, xử lý giá trị thiếu và tái tạo notebook phân tích phân tích thời gian xử lý yêu cầu hỗ trợ. |
| `da-bi-reporting` | `satisfied` | Xây báo cáo Tableau, định nghĩa chỉ số và kiểm tra số tổng với nguồn trước khi bàn giao phân tích thời gian xử lý yêu cầu hỗ trợ. |
| `da-business-analysis` | `satisfied` | Thực hiện luồng phân tích từ câu hỏi, dữ liệu, kiểm tra sai lệch đến kết luận và giới hạn cho phân tích thời gian xử lý yêu cầu hỗ trợ. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 27/30 | Điểm nháp 27/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `da-technical-specialization` | 22/25 | Điểm nháp 22/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `da-role-capability` | 18/20 | Điểm nháp 18/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 13/15 | Điểm nháp 13/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 9/10 | Điểm nháp 9/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-da-14-01` (education): Chương trình học có bài tổng hợp về phân tích thời gian xử lý yêu cầu hỗ trợ; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-da-14-02` (work_experience): Tối ưu câu truy vấn nhiều bước sau khi đọc execution plan, giảm thời gian lấy dữ liệu phục vụ phân tích thời gian xử lý yêu cầu hỗ trợ.
- `ev-v2d-da-14-03` (projects): Dùng pandas để làm sạch kiểu dữ liệu, xử lý giá trị thiếu và tái tạo notebook phân tích phân tích thời gian xử lý yêu cầu hỗ trợ.
- `ev-v2d-da-14-04` (work_experience): Xây báo cáo Tableau, định nghĩa chỉ số và kiểm tra số tổng với nguồn trước khi bàn giao phân tích thời gian xử lý yêu cầu hỗ trợ.
- `ev-v2d-da-14-05` (projects): Thực hiện luồng phân tích từ câu hỏi, dữ liệu, kiểm tra sai lệch đến kết luận và giới hạn cho phân tích thời gian xử lý yêu cầu hỗ trợ.
- `ev-v2d-da-14-06` (projects): Chiều sâu kỹ thuật của phân tích thời gian xử lý yêu cầu hỗ trợ: Chứng minh năng lực qua nhiệm vụ tương đương thay vì lặp lại từ khóa JD.
- `ev-v2d-da-14-07` (projects): Lập luận trong phân tích thời gian xử lý yêu cầu hỗ trợ: Giải thích mục tiêu, cách đo và một giới hạn của giải pháp.
- `ev-v2d-da-14-08` (projects): Bàn giao phân tích thời gian xử lý yêu cầu hỗ trợ: Có source, kết quả kiểm tra và hướng dẫn tái tạo.
- `ev-v2d-da-14-09` (other): Cách trình bày phân tích thời gian xử lý yêu cầu hỗ trợ: Thông tin có cấu trúc, nhất quán và truy ngược được tới artifact.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-da-15 — Junior Data Analyst - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `58`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `low-score-without-explicit-critical-unsatisfied`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `da-sql` | `satisfied` | Trong một bài tập nhỏ có hướng dẫn từng bước, tự viết chuỗi truy vấn kết hợp nhiều bảng, dùng CTE và hàm cửa sổ để tạo tập dữ liệu phân tích cho xây báo cáo vận hành cho chuỗi bán lẻ. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác. |
| `da-analysis-language` | `satisfied` | Trong một bài tập nhỏ có hướng dẫn từng bước, viết script R với dplyr và ggplot2 để biến đổi dữ liệu, kiểm tra phân phối và trực quan hóa kết quả xây báo cáo vận hành cho chuỗi bán lẻ. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác. |
| `da-bi-reporting` | `satisfied` | Trong một bài tập nhỏ có hướng dẫn từng bước, tạo dashboard tương tác trên Looker Studio, tách metric vận hành và metric kết quả cho xây báo cáo vận hành cho chuỗi bán lẻ. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác. |
| `da-business-analysis` | `satisfied` | Trong một bài tập nhỏ có hướng dẫn từng bước, chuyển câu hỏi giữ chân khách hàng thành KPI, phân tích nguyên nhân và đề xuất hai hành động có thể kiểm chứng cho xây báo cáo vận hành cho chuỗi bán lẻ. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 18/30 | Điểm nháp 18/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `da-technical-specialization` | 14/25 | Điểm nháp 14/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `da-role-capability` | 11/20 | Điểm nháp 11/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 9/15 | Điểm nháp 9/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 6/10 | Điểm nháp 6/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-da-15-01` (education): Chương trình học có bài tổng hợp về xây báo cáo vận hành cho chuỗi bán lẻ; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-da-15-02` (projects): Trong một bài tập nhỏ có hướng dẫn từng bước, tự viết chuỗi truy vấn kết hợp nhiều bảng, dùng CTE và hàm cửa sổ để tạo tập dữ liệu phân tích cho xây báo cáo vận hành cho chuỗi bán lẻ. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác.
- `ev-v2d-da-15-03` (projects): Trong một bài tập nhỏ có hướng dẫn từng bước, viết script R với dplyr và ggplot2 để biến đổi dữ liệu, kiểm tra phân phối và trực quan hóa kết quả xây báo cáo vận hành cho chuỗi bán lẻ. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác.
- `ev-v2d-da-15-04` (projects): Trong một bài tập nhỏ có hướng dẫn từng bước, tạo dashboard tương tác trên Looker Studio, tách metric vận hành và metric kết quả cho xây báo cáo vận hành cho chuỗi bán lẻ. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác.
- `ev-v2d-da-15-05` (projects): Trong một bài tập nhỏ có hướng dẫn từng bước, chuyển câu hỏi giữ chân khách hàng thành KPI, phân tích nguyên nhân và đề xuất hai hành động có thể kiểm chứng cho xây báo cáo vận hành cho chuỗi bán lẻ. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác.
- `ev-v2d-da-15-06` (projects): Chiều sâu kỹ thuật của xây báo cáo vận hành cho chuỗi bán lẻ: Mỗi năng lực chỉ xuất hiện trong một bài tập nhỏ có hướng dẫn.
- `ev-v2d-da-15-07` (projects): Lập luận trong xây báo cáo vận hành cho chuỗi bán lẻ: Quyết định chủ yếu theo mẫu, chưa có so sánh hoặc kiểm chứng độc lập.
- `ev-v2d-da-15-08` (projects): Bàn giao xây báo cáo vận hành cho chuỗi bán lẻ: Có tệp kết quả nhưng hướng dẫn bàn giao còn tối thiểu.
- `ev-v2d-da-15-09` (other): Cách trình bày xây báo cáo vận hành cho chuỗi bán lẻ: Nêu đúng phạm vi hạn chế, tổng điểm thấp không đồng nghĩa yêu cầu bị phủ định.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-be-01 — Junior Python Backend Developer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `93`
- Nhãn nháp: `pass`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `be-python` | `satisfied` | Viết service Python có type hints, logging và kiểm tra dữ liệu đầu vào cho dịch vụ quản lý đơn đặt hàng. |
| `be-rest-api` | `satisfied` | Triển khai dịch vụ Flask, xử lý lỗi nhất quán và kiểm thử hợp đồng HTTP cho dịch vụ quản lý đơn đặt hàng. |
| `be-relational-data` | `satisfied` | Thiết kế schema PostgreSQL, tạo migration và dùng transaction cho luồng cập nhật dịch vụ quản lý đơn đặt hàng. |
| `be-testing` | `satisfied` | Tạo fixture cơ sở dữ liệu, mock dịch vụ ngoài và chạy bộ kiểm thử tự động cho dịch vụ quản lý đơn đặt hàng. |
| `be-delivery-workflow` | `satisfied` | Thiết lập pipeline kiểm tra mã, build container và ghi hướng dẫn triển khai cho dịch vụ quản lý đơn đặt hàng. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 29/30 | Điểm nháp 29/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `be-technical-specialization` | 23/25 | Điểm nháp 23/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `be-role-capability` | 18/20 | Điểm nháp 18/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 14/15 | Điểm nháp 14/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 9/10 | Điểm nháp 9/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-be-01-01` (education): Chương trình học có bài tổng hợp về dịch vụ quản lý đơn đặt hàng; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-be-01-02` (work_experience): Viết service Python có type hints, logging và kiểm tra dữ liệu đầu vào cho dịch vụ quản lý đơn đặt hàng.
- `ev-v2d-be-01-03` (projects): Triển khai dịch vụ Flask, xử lý lỗi nhất quán và kiểm thử hợp đồng HTTP cho dịch vụ quản lý đơn đặt hàng.
- `ev-v2d-be-01-04` (work_experience): Thiết kế schema PostgreSQL, tạo migration và dùng transaction cho luồng cập nhật dịch vụ quản lý đơn đặt hàng.
- `ev-v2d-be-01-05` (projects): Tạo fixture cơ sở dữ liệu, mock dịch vụ ngoài và chạy bộ kiểm thử tự động cho dịch vụ quản lý đơn đặt hàng.
- `ev-v2d-be-01-06` (work_experience): Thiết lập pipeline kiểm tra mã, build container và ghi hướng dẫn triển khai cho dịch vụ quản lý đơn đặt hàng.
- `ev-v2d-be-01-07` (projects): Chiều sâu kỹ thuật của dịch vụ quản lý đơn đặt hàng: Giải pháp bao phủ luồng chính, dữ liệu biên và bước kiểm tra lại.
- `ev-v2d-be-01-08` (projects): Lập luận trong dịch vụ quản lý đơn đặt hàng: Nêu rõ lựa chọn kỹ thuật, giả định và một phương án đã loại bỏ.
- `ev-v2d-be-01-09` (projects): Bàn giao dịch vụ quản lý đơn đặt hàng: Bàn giao source, hướng dẫn chạy và kết quả kiểm tra cho người dùng nội bộ.
- `ev-v2d-be-01-10` (other): Cách trình bày dịch vụ quản lý đơn đặt hàng: Mô tả ngắn gọn phạm vi, kết quả định lượng và giới hạn còn lại.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-be-02 — Junior Python Backend Developer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `88`
- Nhãn nháp: `pass`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `be-python` | `satisfied` | Dùng Python xây luồng xử lý bất đồng bộ và theo dõi lỗi trong hệ thống đăng ký lịch học. |
| `be-rest-api` | `satisfied` | Thiết kế endpoint theo tài nguyên, mã trạng thái và schema request/response cho hệ thống đăng ký lịch học bằng FastAPI. |
| `be-relational-data` | `satisfied` | Xây quan hệ bảng, index và câu truy vấn MySQL cho hệ thống đăng ký lịch học, sau đó kiểm tra tính toàn vẹn dữ liệu. |
| `be-testing` | `satisfied` | Bổ sung test hồi quy cho lỗi production và đo coverage của module trọng yếu trong hệ thống đăng ký lịch học. |
| `be-delivery-workflow` | `satisfied` | Quản lý thay đổi bằng Git, mở pull request có review và đóng gói hệ thống đăng ký lịch học bằng Docker. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 28/30 | Điểm nháp 28/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `be-technical-specialization` | 22/25 | Điểm nháp 22/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `be-role-capability` | 17/20 | Điểm nháp 17/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 13/15 | Điểm nháp 13/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 8/10 | Điểm nháp 8/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-be-02-01` (education): Chương trình học có bài tổng hợp về hệ thống đăng ký lịch học; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-be-02-02` (work_experience): Dùng Python xây luồng xử lý bất đồng bộ và theo dõi lỗi trong hệ thống đăng ký lịch học.
- `ev-v2d-be-02-03` (projects): Thiết kế endpoint theo tài nguyên, mã trạng thái và schema request/response cho hệ thống đăng ký lịch học bằng FastAPI.
- `ev-v2d-be-02-04` (work_experience): Xây quan hệ bảng, index và câu truy vấn MySQL cho hệ thống đăng ký lịch học, sau đó kiểm tra tính toàn vẹn dữ liệu.
- `ev-v2d-be-02-05` (projects): Bổ sung test hồi quy cho lỗi production và đo coverage của module trọng yếu trong hệ thống đăng ký lịch học.
- `ev-v2d-be-02-06` (work_experience): Quản lý thay đổi bằng Git, mở pull request có review và đóng gói hệ thống đăng ký lịch học bằng Docker.
- `ev-v2d-be-02-07` (projects): Chiều sâu kỹ thuật của hệ thống đăng ký lịch học: Thực hiện phần cốt lõi và xử lý ít nhất một lỗi phát sinh.
- `ev-v2d-be-02-08` (projects): Lập luận trong hệ thống đăng ký lịch học: So sánh hai cách triển khai trước khi chọn giải pháp phù hợp phạm vi.
- `ev-v2d-be-02-09` (projects): Bàn giao hệ thống đăng ký lịch học: Có quy trình review và tài liệu để thành viên khác chạy lại.
- `ev-v2d-be-02-10` (other): Cách trình bày hệ thống đăng ký lịch học: Thông tin nhất quán, có đầu ra nhưng phần đo lường chưa hoàn toàn độc lập.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-be-03 — Junior Python Backend Developer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `82`
- Nhãn nháp: `waitlist`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `be-python` | `satisfied` | Tự triển khai tầng nghiệp vụ bằng Python, tách module và xử lý ngoại lệ cho API quản lý kho thiết bị. |
| `be-rest-api` | `satisfied` | Xây API Django REST có phân trang, xác thực dữ liệu và tài liệu OpenAPI cho API quản lý kho thiết bị. |
| `be-relational-data` | `satisfied` | Dùng SQLAlchemy quản lý phiên giao dịch và migration khi thay đổi mô hình dữ liệu của API quản lý kho thiết bị. |
| `be-testing` | `satisfied` | Viết unit test và integration test bằng pytest cho luồng lỗi và luồng thành công của API quản lý kho thiết bị. |
| `be-delivery-workflow` | `satisfied` | Dùng nhánh tính năng, xử lý góp ý code review và viết Dockerfile chạy dịch vụ API quản lý kho thiết bị. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 26/30 | Điểm nháp 26/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `be-technical-specialization` | 20/25 | Điểm nháp 20/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `be-role-capability` | 16/20 | Điểm nháp 16/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 12/15 | Điểm nháp 12/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 8/10 | Điểm nháp 8/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-be-03-01` (education): Chương trình học có bài tổng hợp về API quản lý kho thiết bị; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-be-03-02` (work_experience): Tự triển khai tầng nghiệp vụ bằng Python, tách module và xử lý ngoại lệ cho API quản lý kho thiết bị.
- `ev-v2d-be-03-03` (projects): Xây API Django REST có phân trang, xác thực dữ liệu và tài liệu OpenAPI cho API quản lý kho thiết bị.
- `ev-v2d-be-03-04` (work_experience): Dùng SQLAlchemy quản lý phiên giao dịch và migration khi thay đổi mô hình dữ liệu của API quản lý kho thiết bị.
- `ev-v2d-be-03-05` (projects): Viết unit test và integration test bằng pytest cho luồng lỗi và luồng thành công của API quản lý kho thiết bị.
- `ev-v2d-be-03-06` (work_experience): Dùng nhánh tính năng, xử lý góp ý code review và viết Dockerfile chạy dịch vụ API quản lý kho thiết bị.
- `ev-v2d-be-03-07` (projects): Chiều sâu kỹ thuật của API quản lý kho thiết bị: Hoàn thành luồng chính và kiểm tra dữ liệu đầu vào phổ biến.
- `ev-v2d-be-03-08` (projects): Lập luận trong API quản lý kho thiết bị: Giải thích quyết định dựa trên yêu cầu và giới hạn thời gian.
- `ev-v2d-be-03-09` (projects): Bàn giao API quản lý kho thiết bị: Bàn giao qua repository và checklist chạy thử.
- `ev-v2d-be-03-10` (other): Cách trình bày API quản lý kho thiết bị: Nêu vai trò, kết quả và một giới hạn kỹ thuật.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-be-04 — Junior Python Backend Developer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `75`
- Nhãn nháp: `waitlist`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `be-python` | `satisfied` | Viết service Python có type hints, logging và kiểm tra dữ liệu đầu vào cho dịch vụ theo dõi yêu cầu hỗ trợ. |
| `be-rest-api` | `satisfied` | Triển khai dịch vụ Flask, xử lý lỗi nhất quán và kiểm thử hợp đồng HTTP cho dịch vụ theo dõi yêu cầu hỗ trợ. |
| `be-relational-data` | `satisfied` | Thiết kế schema PostgreSQL, tạo migration và dùng transaction cho luồng cập nhật dịch vụ theo dõi yêu cầu hỗ trợ. |
| `be-testing` | `satisfied` | Tạo fixture cơ sở dữ liệu, mock dịch vụ ngoài và chạy bộ kiểm thử tự động cho dịch vụ theo dõi yêu cầu hỗ trợ. |
| `be-delivery-workflow` | `satisfied` | Thiết lập pipeline kiểm tra mã, build container và ghi hướng dẫn triển khai cho dịch vụ theo dõi yêu cầu hỗ trợ. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 24/30 | Điểm nháp 24/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `be-technical-specialization` | 18/25 | Điểm nháp 18/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `be-role-capability` | 15/20 | Điểm nháp 15/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 11/15 | Điểm nháp 11/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 7/10 | Điểm nháp 7/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-be-04-01` (education): Chương trình học có bài tổng hợp về dịch vụ theo dõi yêu cầu hỗ trợ; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-be-04-02` (projects): Viết service Python có type hints, logging và kiểm tra dữ liệu đầu vào cho dịch vụ theo dõi yêu cầu hỗ trợ.
- `ev-v2d-be-04-03` (projects): Triển khai dịch vụ Flask, xử lý lỗi nhất quán và kiểm thử hợp đồng HTTP cho dịch vụ theo dõi yêu cầu hỗ trợ.
- `ev-v2d-be-04-04` (projects): Thiết kế schema PostgreSQL, tạo migration và dùng transaction cho luồng cập nhật dịch vụ theo dõi yêu cầu hỗ trợ.
- `ev-v2d-be-04-05` (projects): Tạo fixture cơ sở dữ liệu, mock dịch vụ ngoài và chạy bộ kiểm thử tự động cho dịch vụ theo dõi yêu cầu hỗ trợ.
- `ev-v2d-be-04-06` (projects): Thiết lập pipeline kiểm tra mã, build container và ghi hướng dẫn triển khai cho dịch vụ theo dõi yêu cầu hỗ trợ.
- `ev-v2d-be-04-07` (projects): Chiều sâu kỹ thuật của dịch vụ theo dõi yêu cầu hỗ trợ: Có sản phẩm chạy được trong phạm vi học tập hoặc cá nhân.
- `ev-v2d-be-04-08` (projects): Lập luận trong dịch vụ theo dõi yêu cầu hỗ trợ: Nêu lý do lựa chọn chính nhưng chưa phân tích sâu trade-off.
- `ev-v2d-be-04-09` (projects): Bàn giao dịch vụ theo dõi yêu cầu hỗ trợ: Có source và hướng dẫn cơ bản để tái chạy.
- `ev-v2d-be-04-10` (other): Cách trình bày dịch vụ theo dõi yêu cầu hỗ trợ: Thông tin đủ hiểu nhưng thiếu số đo tác động độc lập.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-be-05 — Junior Python Backend Developer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `66`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `missing-critical-evidence, low-score-without-explicit-critical-unsatisfied`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `be-python` | `missing` | Không có thông tin trực tiếp |
| `be-rest-api` | `satisfied` | Thiết kế endpoint theo tài nguyên, mã trạng thái và schema request/response cho backend cho ứng dụng quản lý chi tiêu bằng FastAPI. |
| `be-relational-data` | `satisfied` | Xây quan hệ bảng, index và câu truy vấn MySQL cho backend cho ứng dụng quản lý chi tiêu, sau đó kiểm tra tính toàn vẹn dữ liệu. |
| `be-testing` | `satisfied` | Bổ sung test hồi quy cho lỗi production và đo coverage của module trọng yếu trong backend cho ứng dụng quản lý chi tiêu. |
| `be-delivery-workflow` | `satisfied` | Quản lý thay đổi bằng Git, mở pull request có review và đóng gói backend cho ứng dụng quản lý chi tiêu bằng Docker. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 18/30 | Điểm nháp 18/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `be-technical-specialization` | 17/25 | Điểm nháp 17/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `be-role-capability` | 14/20 | Điểm nháp 14/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 10/15 | Điểm nháp 10/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 7/10 | Điểm nháp 7/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-be-05-01` (education): Chương trình học có bài tổng hợp về backend cho ứng dụng quản lý chi tiêu; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-be-05-02` (education): Có đọc source Python của nhóm; hồ sơ không xác định phần mã do ứng viên thực hiện.
- `ev-v2d-be-05-03` (projects): Thiết kế endpoint theo tài nguyên, mã trạng thái và schema request/response cho backend cho ứng dụng quản lý chi tiêu bằng FastAPI.
- `ev-v2d-be-05-04` (projects): Xây quan hệ bảng, index và câu truy vấn MySQL cho backend cho ứng dụng quản lý chi tiêu, sau đó kiểm tra tính toàn vẹn dữ liệu.
- `ev-v2d-be-05-05` (projects): Bổ sung test hồi quy cho lỗi production và đo coverage của module trọng yếu trong backend cho ứng dụng quản lý chi tiêu.
- `ev-v2d-be-05-06` (projects): Quản lý thay đổi bằng Git, mở pull request có review và đóng gói backend cho ứng dụng quản lý chi tiêu bằng Docker.
- `ev-v2d-be-05-07` (projects): Chiều sâu kỹ thuật của backend cho ứng dụng quản lý chi tiêu: Các phần được mô tả có thao tác thực hành nhưng độ bao phủ chưa đầy đủ.
- `ev-v2d-be-05-08` (projects): Lập luận trong backend cho ứng dụng quản lý chi tiêu: Có giải thích cho phần đã làm, không suy diễn phần còn thiếu.
- `ev-v2d-be-05-09` (projects): Bàn giao backend cho ứng dụng quản lý chi tiêu: Bàn giao được phạm vi hiện có và ghi rõ giới hạn.
- `ev-v2d-be-05-10` (other): Cách trình bày backend cho ứng dụng quản lý chi tiêu: Hồ sơ phân biệt rõ điều đã làm và điều chưa có thông tin.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-be-06 — Junior Python Backend Developer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `76`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `conflicting-critical-evidence`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `be-python` | `satisfied` | Tự triển khai tầng nghiệp vụ bằng Python, tách module và xử lý ngoại lệ cho dịch vụ quản lý đơn đặt hàng. |
| `be-rest-api` | `conflicting` | Xây API Django REST có phân trang, xác thực dữ liệu và tài liệu OpenAPI cho dịch vụ quản lý đơn đặt hàng.<br>Không thể thiết kế route hoặc schema request/response cho dịch vụ quản lý đơn đặt hàng. |
| `be-relational-data` | `satisfied` | Dùng SQLAlchemy quản lý phiên giao dịch và migration khi thay đổi mô hình dữ liệu của dịch vụ quản lý đơn đặt hàng. |
| `be-testing` | `satisfied` | Viết unit test và integration test bằng pytest cho luồng lỗi và luồng thành công của dịch vụ quản lý đơn đặt hàng. |
| `be-delivery-workflow` | `satisfied` | Dùng nhánh tính năng, xử lý góp ý code review và viết Dockerfile chạy dịch vụ dịch vụ quản lý đơn đặt hàng. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 22/30 | Điểm nháp 22/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `be-technical-specialization` | 19/25 | Điểm nháp 19/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `be-role-capability` | 15/20 | Điểm nháp 15/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 12/15 | Điểm nháp 12/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 8/10 | Điểm nháp 8/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-be-06-01` (education): Chương trình học có bài tổng hợp về dịch vụ quản lý đơn đặt hàng; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-be-06-02` (projects): Tự triển khai tầng nghiệp vụ bằng Python, tách module và xử lý ngoại lệ cho dịch vụ quản lý đơn đặt hàng.
- `ev-v2d-be-06-03` (projects): Xây API Django REST có phân trang, xác thực dữ liệu và tài liệu OpenAPI cho dịch vụ quản lý đơn đặt hàng.
- `ev-v2d-be-06-04` (other): Không thể thiết kế route hoặc schema request/response cho dịch vụ quản lý đơn đặt hàng.
- `ev-v2d-be-06-05` (projects): Dùng SQLAlchemy quản lý phiên giao dịch và migration khi thay đổi mô hình dữ liệu của dịch vụ quản lý đơn đặt hàng.
- `ev-v2d-be-06-06` (projects): Viết unit test và integration test bằng pytest cho luồng lỗi và luồng thành công của dịch vụ quản lý đơn đặt hàng.
- `ev-v2d-be-06-07` (projects): Dùng nhánh tính năng, xử lý góp ý code review và viết Dockerfile chạy dịch vụ dịch vụ quản lý đơn đặt hàng.
- `ev-v2d-be-06-08` (projects): Chiều sâu kỹ thuật của dịch vụ quản lý đơn đặt hàng: Có đầu ra kỹ thuật nhưng trạng thái một năng lực chưa thể kết luận.
- `ev-v2d-be-06-09` (projects): Lập luận trong dịch vụ quản lý đơn đặt hàng: Ghi lại quyết định của dự án nhưng chưa giải thích được mâu thuẫn trong hồ sơ.
- `ev-v2d-be-06-10` (projects): Bàn giao dịch vụ quản lý đơn đặt hàng: Có artifact bàn giao và một cảnh báo cần xác minh.
- `ev-v2d-be-06-11` (other): Cách trình bày dịch vụ quản lý đơn đặt hàng: Thông tin khá rõ ngoài điểm mâu thuẫn cần human review.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-be-07 — Junior Python Backend Developer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `57`
- Nhãn nháp: `reject`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `be-python` | `satisfied` | Viết service Python có type hints, logging và kiểm tra dữ liệu đầu vào cho hệ thống đăng ký lịch học. |
| `be-rest-api` | `satisfied` | Triển khai dịch vụ Flask, xử lý lỗi nhất quán và kiểm thử hợp đồng HTTP cho hệ thống đăng ký lịch học. |
| `be-relational-data` | `unsatisfied` | Không có kiến thức SQL; dữ liệu của hệ thống đăng ký lịch học được thành viên khác chuẩn bị sẵn. |
| `be-testing` | `satisfied` | Tạo fixture cơ sở dữ liệu, mock dịch vụ ngoài và chạy bộ kiểm thử tự động cho hệ thống đăng ký lịch học. |
| `be-delivery-workflow` | `satisfied` | Thiết lập pipeline kiểm tra mã, build container và ghi hướng dẫn triển khai cho hệ thống đăng ký lịch học. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 16/30 | Điểm nháp 16/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `be-technical-specialization` | 15/25 | Điểm nháp 15/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `be-role-capability` | 12/20 | Điểm nháp 12/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 8/15 | Điểm nháp 8/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 6/10 | Điểm nháp 6/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-be-07-01` (education): Chương trình học có bài tổng hợp về hệ thống đăng ký lịch học; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-be-07-02` (projects): Viết service Python có type hints, logging và kiểm tra dữ liệu đầu vào cho hệ thống đăng ký lịch học.
- `ev-v2d-be-07-03` (projects): Triển khai dịch vụ Flask, xử lý lỗi nhất quán và kiểm thử hợp đồng HTTP cho hệ thống đăng ký lịch học.
- `ev-v2d-be-07-04` (other): Không có kiến thức SQL; dữ liệu của hệ thống đăng ký lịch học được thành viên khác chuẩn bị sẵn.
- `ev-v2d-be-07-05` (projects): Tạo fixture cơ sở dữ liệu, mock dịch vụ ngoài và chạy bộ kiểm thử tự động cho hệ thống đăng ký lịch học.
- `ev-v2d-be-07-06` (projects): Thiết lập pipeline kiểm tra mã, build container và ghi hướng dẫn triển khai cho hệ thống đăng ký lịch học.
- `ev-v2d-be-07-07` (projects): Chiều sâu kỹ thuật của hệ thống đăng ký lịch học: Một phần công việc phụ thuộc vào thành viên khác và không có khả năng thay thế.
- `ev-v2d-be-07-08` (projects): Lập luận trong hệ thống đăng ký lịch học: Nêu đúng giới hạn hiện tại nhưng chưa có kế hoạch kiểm chứng năng lực thiếu.
- `ev-v2d-be-07-09` (projects): Bàn giao hệ thống đăng ký lịch học: Chỉ bàn giao được phần việc hẹp.
- `ev-v2d-be-07-10` (other): Cách trình bày hệ thống đăng ký lịch học: Thông tin phủ định rõ và không bị che bởi danh sách từ khóa.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-be-08 — Junior Python Backend Developer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `24`
- Nhãn nháp: `reject`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `be-python` | `unsatisfied` | Chưa từng dùng Python để xây phần mềm backend; chỉ chạy lại đoạn mã mẫu của lớp. |
| `be-rest-api` | `unsatisfied` | Không thể thiết kế route hoặc schema request/response cho API quản lý kho thiết bị. |
| `be-relational-data` | `unsatisfied` | Chưa thể thiết kế bảng hoặc viết truy vấn cho cơ sở dữ liệu quan hệ. |
| `be-testing` | `unsatisfied` | Không có unit test hay integration test cho phần việc trong API quản lý kho thiết bị. |
| `be-delivery-workflow` | `unsatisfied` | Chưa dùng quản lý phiên bản và chưa thể đóng gói dịch vụ để người khác chạy lại. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 5/30 | Điểm nháp 5/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `be-technical-specialization` | 5/25 | Điểm nháp 5/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `be-role-capability` | 6/20 | Điểm nháp 6/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 4/15 | Điểm nháp 4/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 4/10 | Điểm nháp 4/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-be-08-01` (education): Chương trình học có bài tổng hợp về API quản lý kho thiết bị; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-be-08-02` (other): Chưa từng dùng Python để xây phần mềm backend; chỉ chạy lại đoạn mã mẫu của lớp.
- `ev-v2d-be-08-03` (other): Không thể thiết kế route hoặc schema request/response cho API quản lý kho thiết bị.
- `ev-v2d-be-08-04` (other): Chưa thể thiết kế bảng hoặc viết truy vấn cho cơ sở dữ liệu quan hệ.
- `ev-v2d-be-08-05` (other): Không có unit test hay integration test cho phần việc trong API quản lý kho thiết bị.
- `ev-v2d-be-08-06` (other): Chưa dùng quản lý phiên bản và chưa thể đóng gói dịch vụ để người khác chạy lại.
- `ev-v2d-be-08-07` (projects): Chiều sâu kỹ thuật của API quản lý kho thiết bị: Không có artifact hoặc tác vụ chuyên môn do ứng viên tự hoàn thành.
- `ev-v2d-be-08-08` (projects): Lập luận trong API quản lý kho thiết bị: Chưa có quyết định kỹ thuật để đánh giá.
- `ev-v2d-be-08-09` (projects): Bàn giao API quản lý kho thiết bị: Không có quy trình bàn giao có thể tái tạo.
- `ev-v2d-be-08-10` (other): Cách trình bày API quản lý kho thiết bị: Giới hạn được phát biểu rõ, không tạo ấn tượng sai về kinh nghiệm.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-be-09 — Junior Python Backend Developer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `53`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `missing-critical-evidence, low-score-without-explicit-critical-unsatisfied`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `be-python` | `missing` | Không có thông tin trực tiếp |
| `be-rest-api` | `satisfied` | Xây API Django REST có phân trang, xác thực dữ liệu và tài liệu OpenAPI cho dịch vụ theo dõi yêu cầu hỗ trợ. |
| `be-relational-data` | `missing` | Không có thông tin trực tiếp |
| `be-testing` | `satisfied` | Viết unit test và integration test bằng pytest cho luồng lỗi và luồng thành công của dịch vụ theo dõi yêu cầu hỗ trợ. |
| `be-delivery-workflow` | `missing` | Không có thông tin trực tiếp |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 14/30 | Điểm nháp 14/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `be-technical-specialization` | 13/25 | Điểm nháp 13/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `be-role-capability` | 12/20 | Điểm nháp 12/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 8/15 | Điểm nháp 8/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 6/10 | Điểm nháp 6/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-be-09-01` (education): Chương trình học có bài tổng hợp về dịch vụ theo dõi yêu cầu hỗ trợ; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-be-09-02` (education): Có đọc source Python của nhóm; hồ sơ không xác định phần mã do ứng viên thực hiện.
- `ev-v2d-be-09-03` (projects): Xây API Django REST có phân trang, xác thực dữ liệu và tài liệu OpenAPI cho dịch vụ theo dõi yêu cầu hỗ trợ.
- `ev-v2d-be-09-04` (education): Biết tên PostgreSQL nhưng chưa kết nối hoặc lưu dữ liệu từ ứng dụng backend.
- `ev-v2d-be-09-05` (projects): Viết unit test và integration test bằng pytest cho luồng lỗi và luồng thành công của dịch vụ theo dõi yêu cầu hỗ trợ.
- `ev-v2d-be-09-06` (education): Đã tải source dạng tệp nén; hồ sơ không nêu pull request, review hoặc cách đóng gói.
- `ev-v2d-be-09-07` (projects): Chiều sâu kỹ thuật của dịch vụ theo dõi yêu cầu hỗ trợ: Có một số thao tác đơn lẻ nhưng chưa thành luồng hoàn chỉnh.
- `ev-v2d-be-09-08` (projects): Lập luận trong dịch vụ theo dõi yêu cầu hỗ trợ: Lý do thực hiện chưa gắn với tiêu chí thành công.
- `ev-v2d-be-09-09` (projects): Bàn giao dịch vụ theo dõi yêu cầu hỗ trợ: Artifact rời rạc và chưa có hướng dẫn tái chạy.
- `ev-v2d-be-09-10` (other): Cách trình bày dịch vụ theo dõi yêu cầu hỗ trợ: Hồ sơ không khẳng định các năng lực chưa được chứng minh.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-be-10 — Junior Python Backend Developer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `68`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `missing-critical-evidence, low-score-without-explicit-critical-unsatisfied, lower-threshold-boundary`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `be-python` | `satisfied` | Viết service Python có type hints, logging và kiểm tra dữ liệu đầu vào cho backend cho ứng dụng quản lý chi tiêu. |
| `be-rest-api` | `satisfied` | Triển khai dịch vụ Flask, xử lý lỗi nhất quán và kiểm thử hợp đồng HTTP cho backend cho ứng dụng quản lý chi tiêu. |
| `be-relational-data` | `satisfied` | Thiết kế schema PostgreSQL, tạo migration và dùng transaction cho luồng cập nhật backend cho ứng dụng quản lý chi tiêu. |
| `be-testing` | `satisfied` | Tạo fixture cơ sở dữ liệu, mock dịch vụ ngoài và chạy bộ kiểm thử tự động cho backend cho ứng dụng quản lý chi tiêu. |
| `be-delivery-workflow` | `missing` | Không có thông tin trực tiếp |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 20/30 | Điểm nháp 20/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `be-technical-specialization` | 17/25 | Điểm nháp 17/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `be-role-capability` | 13/20 | Điểm nháp 13/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 10/15 | Điểm nháp 10/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 8/10 | Điểm nháp 8/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-be-10-01` (education): Chương trình học có bài tổng hợp về backend cho ứng dụng quản lý chi tiêu; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-be-10-02` (projects): Viết service Python có type hints, logging và kiểm tra dữ liệu đầu vào cho backend cho ứng dụng quản lý chi tiêu.
- `ev-v2d-be-10-03` (projects): Triển khai dịch vụ Flask, xử lý lỗi nhất quán và kiểm thử hợp đồng HTTP cho backend cho ứng dụng quản lý chi tiêu.
- `ev-v2d-be-10-04` (projects): Thiết kế schema PostgreSQL, tạo migration và dùng transaction cho luồng cập nhật backend cho ứng dụng quản lý chi tiêu.
- `ev-v2d-be-10-05` (projects): Tạo fixture cơ sở dữ liệu, mock dịch vụ ngoài và chạy bộ kiểm thử tự động cho backend cho ứng dụng quản lý chi tiêu.
- `ev-v2d-be-10-06` (education): Biết khái niệm repository và container nhưng không có lịch sử commit hay cấu hình chạy được.
- `ev-v2d-be-10-07` (projects): Chiều sâu kỹ thuật của backend cho ứng dụng quản lý chi tiêu: Phần lớn năng lực có ví dụ nhưng chiều sâu chưa đồng đều.
- `ev-v2d-be-10-08` (projects): Lập luận trong backend cho ứng dụng quản lý chi tiêu: Có giải thích lựa chọn chính và một giả định chưa kiểm tra.
- `ev-v2d-be-10-09` (projects): Bàn giao backend cho ứng dụng quản lý chi tiêu: Có bản chạy thử và ghi chú vận hành cơ bản.
- `ev-v2d-be-10-10` (other): Cách trình bày backend cho ứng dụng quản lý chi tiêu: Thông tin tương đối rõ nhưng cần xác minh phần còn thiếu.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-be-11 — Junior Python Backend Developer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `85`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `conflicting-critical-evidence, upper-threshold-boundary`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `be-python` | `conflicting` | Dùng Python xây luồng xử lý bất đồng bộ và theo dõi lỗi trong dịch vụ quản lý đơn đặt hàng.<br>Không thể tự viết module Python cho dịch vụ quản lý đơn đặt hàng; phần mã nguồn do thành viên khác phụ trách. |
| `be-rest-api` | `satisfied` | Thiết kế endpoint theo tài nguyên, mã trạng thái và schema request/response cho dịch vụ quản lý đơn đặt hàng bằng FastAPI. |
| `be-relational-data` | `satisfied` | Xây quan hệ bảng, index và câu truy vấn MySQL cho dịch vụ quản lý đơn đặt hàng, sau đó kiểm tra tính toàn vẹn dữ liệu. |
| `be-testing` | `satisfied` | Bổ sung test hồi quy cho lỗi production và đo coverage của module trọng yếu trong dịch vụ quản lý đơn đặt hàng. |
| `be-delivery-workflow` | `satisfied` | Quản lý thay đổi bằng Git, mở pull request có review và đóng gói dịch vụ quản lý đơn đặt hàng bằng Docker. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 25/30 | Điểm nháp 25/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `be-technical-specialization` | 21/25 | Điểm nháp 21/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `be-role-capability` | 17/20 | Điểm nháp 17/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 13/15 | Điểm nháp 13/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 9/10 | Điểm nháp 9/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-be-11-01` (education): Chương trình học có bài tổng hợp về dịch vụ quản lý đơn đặt hàng; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-be-11-02` (work_experience): Dùng Python xây luồng xử lý bất đồng bộ và theo dõi lỗi trong dịch vụ quản lý đơn đặt hàng.
- `ev-v2d-be-11-03` (other): Không thể tự viết module Python cho dịch vụ quản lý đơn đặt hàng; phần mã nguồn do thành viên khác phụ trách.
- `ev-v2d-be-11-04` (projects): Thiết kế endpoint theo tài nguyên, mã trạng thái và schema request/response cho dịch vụ quản lý đơn đặt hàng bằng FastAPI.
- `ev-v2d-be-11-05` (work_experience): Xây quan hệ bảng, index và câu truy vấn MySQL cho dịch vụ quản lý đơn đặt hàng, sau đó kiểm tra tính toàn vẹn dữ liệu.
- `ev-v2d-be-11-06` (projects): Bổ sung test hồi quy cho lỗi production và đo coverage của module trọng yếu trong dịch vụ quản lý đơn đặt hàng.
- `ev-v2d-be-11-07` (work_experience): Quản lý thay đổi bằng Git, mở pull request có review và đóng gói dịch vụ quản lý đơn đặt hàng bằng Docker.
- `ev-v2d-be-11-08` (projects): Chiều sâu kỹ thuật của dịch vụ quản lý đơn đặt hàng: Artifact kỹ thuật khá hoàn chỉnh ngoài điểm cần xác minh.
- `ev-v2d-be-11-09` (projects): Lập luận trong dịch vụ quản lý đơn đặt hàng: Nêu trade-off và cách kiểm tra kết quả.
- `ev-v2d-be-11-10` (projects): Bàn giao dịch vụ quản lý đơn đặt hàng: Bàn giao có review, test và hướng dẫn sử dụng.
- `ev-v2d-be-11-11` (other): Cách trình bày dịch vụ quản lý đơn đặt hàng: Trình bày tốt nhưng chưa giải quyết được phát biểu mâu thuẫn.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-be-12 — Junior Python Backend Developer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `79`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `critical-unsatisfied-at-or-above-waitlist-threshold`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `be-python` | `satisfied` | Tự triển khai tầng nghiệp vụ bằng Python, tách module và xử lý ngoại lệ cho hệ thống đăng ký lịch học. |
| `be-rest-api` | `satisfied` | Xây API Django REST có phân trang, xác thực dữ liệu và tài liệu OpenAPI cho hệ thống đăng ký lịch học. |
| `be-relational-data` | `satisfied` | Dùng SQLAlchemy quản lý phiên giao dịch và migration khi thay đổi mô hình dữ liệu của hệ thống đăng ký lịch học. |
| `be-testing` | `satisfied` | Viết unit test và integration test bằng pytest cho luồng lỗi và luồng thành công của hệ thống đăng ký lịch học. |
| `be-delivery-workflow` | `unsatisfied` | Chưa dùng quản lý phiên bản và chưa thể đóng gói dịch vụ để người khác chạy lại. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 23/30 | Điểm nháp 23/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `be-technical-specialization` | 20/25 | Điểm nháp 20/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `be-role-capability` | 16/20 | Điểm nháp 16/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 12/15 | Điểm nháp 12/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 8/10 | Điểm nháp 8/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-be-12-01` (education): Chương trình học có bài tổng hợp về hệ thống đăng ký lịch học; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-be-12-02` (projects): Tự triển khai tầng nghiệp vụ bằng Python, tách module và xử lý ngoại lệ cho hệ thống đăng ký lịch học.
- `ev-v2d-be-12-03` (projects): Xây API Django REST có phân trang, xác thực dữ liệu và tài liệu OpenAPI cho hệ thống đăng ký lịch học.
- `ev-v2d-be-12-04` (projects): Dùng SQLAlchemy quản lý phiên giao dịch và migration khi thay đổi mô hình dữ liệu của hệ thống đăng ký lịch học.
- `ev-v2d-be-12-05` (projects): Viết unit test và integration test bằng pytest cho luồng lỗi và luồng thành công của hệ thống đăng ký lịch học.
- `ev-v2d-be-12-06` (other): Chưa dùng quản lý phiên bản và chưa thể đóng gói dịch vụ để người khác chạy lại.
- `ev-v2d-be-12-07` (projects): Chiều sâu kỹ thuật của hệ thống đăng ký lịch học: Các năng lực còn lại có thực hành và đầu ra cụ thể.
- `ev-v2d-be-12-08` (projects): Lập luận trong hệ thống đăng ký lịch học: Nêu cách xử lý trong phạm vi đã biết và giới hạn cần hỗ trợ.
- `ev-v2d-be-12-09` (projects): Bàn giao hệ thống đăng ký lịch học: Có artifact bàn giao cho phần việc đã hoàn thành.
- `ev-v2d-be-12-10` (other): Cách trình bày hệ thống đăng ký lịch học: Hồ sơ minh bạch về năng lực chưa đạt.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-be-13 — Junior Python Backend Developer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `45`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `missing-critical-evidence, low-score-without-explicit-critical-unsatisfied`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `be-python` | `missing` | Không có thông tin trực tiếp |
| `be-rest-api` | `missing` | Không có thông tin trực tiếp |
| `be-relational-data` | `missing` | Không có thông tin trực tiếp |
| `be-testing` | `missing` | Không có thông tin trực tiếp |
| `be-delivery-workflow` | `missing` | Không có thông tin trực tiếp |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 12/30 | Điểm nháp 12/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `be-technical-specialization` | 10/25 | Điểm nháp 10/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `be-role-capability` | 10/20 | Điểm nháp 10/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 7/15 | Điểm nháp 7/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 6/10 | Điểm nháp 6/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-be-13-01` (education): Chương trình học có bài tổng hợp về API quản lý kho thiết bị; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-be-13-02` (education): Có đọc source Python của nhóm; hồ sơ không xác định phần mã do ứng viên thực hiện.
- `ev-v2d-be-13-03` (other): Biết khái niệm REST và đã xem Swagger nhưng chưa triển khai endpoint nào.
- `ev-v2d-be-13-04` (education): Biết tên PostgreSQL nhưng chưa kết nối hoặc lưu dữ liệu từ ứng dụng backend.
- `ev-v2d-be-13-05` (other): Đã đọc tài liệu pytest nhưng không có test case tự động hoặc kết quả chạy test.
- `ev-v2d-be-13-06` (education): Đã tải source dạng tệp nén; hồ sơ không nêu pull request, review hoặc cách đóng gói.
- `ev-v2d-be-13-07` (projects): Chiều sâu kỹ thuật của API quản lý kho thiết bị: Chỉ có nội dung học tập và quan sát, chưa có sản phẩm áp dụng.
- `ev-v2d-be-13-08` (projects): Lập luận trong API quản lý kho thiết bị: Không có quyết định kỹ thuật thuộc trách nhiệm ứng viên.
- `ev-v2d-be-13-09` (projects): Bàn giao API quản lý kho thiết bị: Không có artifact có thể kiểm tra độc lập.
- `ev-v2d-be-13-10` (other): Cách trình bày API quản lý kho thiết bị: Không suy diễn từ tên khóa học hoặc công cụ được nhắc tới.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-be-14 — Junior Python Backend Developer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `89`
- Nhãn nháp: `pass`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `be-python` | `satisfied` | Dùng Python xây luồng xử lý bất đồng bộ và theo dõi lỗi trong dịch vụ theo dõi yêu cầu hỗ trợ. |
| `be-rest-api` | `satisfied` | Thiết kế endpoint theo tài nguyên, mã trạng thái và schema request/response cho dịch vụ theo dõi yêu cầu hỗ trợ bằng FastAPI. |
| `be-relational-data` | `satisfied` | Xây quan hệ bảng, index và câu truy vấn MySQL cho dịch vụ theo dõi yêu cầu hỗ trợ, sau đó kiểm tra tính toàn vẹn dữ liệu. |
| `be-testing` | `satisfied` | Bổ sung test hồi quy cho lỗi production và đo coverage của module trọng yếu trong dịch vụ theo dõi yêu cầu hỗ trợ. |
| `be-delivery-workflow` | `satisfied` | Quản lý thay đổi bằng Git, mở pull request có review và đóng gói dịch vụ theo dõi yêu cầu hỗ trợ bằng Docker. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 27/30 | Điểm nháp 27/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `be-technical-specialization` | 22/25 | Điểm nháp 22/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `be-role-capability` | 18/20 | Điểm nháp 18/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 13/15 | Điểm nháp 13/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 9/10 | Điểm nháp 9/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-be-14-01` (education): Chương trình học có bài tổng hợp về dịch vụ theo dõi yêu cầu hỗ trợ; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-be-14-02` (work_experience): Dùng Python xây luồng xử lý bất đồng bộ và theo dõi lỗi trong dịch vụ theo dõi yêu cầu hỗ trợ.
- `ev-v2d-be-14-03` (projects): Thiết kế endpoint theo tài nguyên, mã trạng thái và schema request/response cho dịch vụ theo dõi yêu cầu hỗ trợ bằng FastAPI.
- `ev-v2d-be-14-04` (work_experience): Xây quan hệ bảng, index và câu truy vấn MySQL cho dịch vụ theo dõi yêu cầu hỗ trợ, sau đó kiểm tra tính toàn vẹn dữ liệu.
- `ev-v2d-be-14-05` (projects): Bổ sung test hồi quy cho lỗi production và đo coverage của module trọng yếu trong dịch vụ theo dõi yêu cầu hỗ trợ.
- `ev-v2d-be-14-06` (work_experience): Quản lý thay đổi bằng Git, mở pull request có review và đóng gói dịch vụ theo dõi yêu cầu hỗ trợ bằng Docker.
- `ev-v2d-be-14-07` (projects): Chiều sâu kỹ thuật của dịch vụ theo dõi yêu cầu hỗ trợ: Chứng minh năng lực qua nhiệm vụ tương đương thay vì lặp lại từ khóa JD.
- `ev-v2d-be-14-08` (projects): Lập luận trong dịch vụ theo dõi yêu cầu hỗ trợ: Giải thích mục tiêu, cách đo và một giới hạn của giải pháp.
- `ev-v2d-be-14-09` (projects): Bàn giao dịch vụ theo dõi yêu cầu hỗ trợ: Có source, kết quả kiểm tra và hướng dẫn tái tạo.
- `ev-v2d-be-14-10` (other): Cách trình bày dịch vụ theo dõi yêu cầu hỗ trợ: Thông tin có cấu trúc, nhất quán và truy ngược được tới artifact.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-be-15 — Junior Python Backend Developer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `58`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `low-score-without-explicit-critical-unsatisfied`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `be-python` | `satisfied` | Trong một bài tập nhỏ có hướng dẫn từng bước, tự triển khai tầng nghiệp vụ bằng Python, tách module và xử lý ngoại lệ cho backend cho ứng dụng quản lý chi tiêu. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác. |
| `be-rest-api` | `satisfied` | Trong một bài tập nhỏ có hướng dẫn từng bước, xây API Django REST có phân trang, xác thực dữ liệu và tài liệu OpenAPI cho backend cho ứng dụng quản lý chi tiêu. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác. |
| `be-relational-data` | `satisfied` | Trong một bài tập nhỏ có hướng dẫn từng bước, dùng SQLAlchemy quản lý phiên giao dịch và migration khi thay đổi mô hình dữ liệu của backend cho ứng dụng quản lý chi tiêu. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác. |
| `be-testing` | `satisfied` | Trong một bài tập nhỏ có hướng dẫn từng bước, viết unit test và integration test bằng pytest cho luồng lỗi và luồng thành công của backend cho ứng dụng quản lý chi tiêu. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác. |
| `be-delivery-workflow` | `satisfied` | Trong một bài tập nhỏ có hướng dẫn từng bước, dùng nhánh tính năng, xử lý góp ý code review và viết Dockerfile chạy dịch vụ backend cho ứng dụng quản lý chi tiêu. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 18/30 | Điểm nháp 18/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `be-technical-specialization` | 14/25 | Điểm nháp 14/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `be-role-capability` | 11/20 | Điểm nháp 11/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 9/15 | Điểm nháp 9/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 6/10 | Điểm nháp 6/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-be-15-01` (education): Chương trình học có bài tổng hợp về backend cho ứng dụng quản lý chi tiêu; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-be-15-02` (projects): Trong một bài tập nhỏ có hướng dẫn từng bước, tự triển khai tầng nghiệp vụ bằng Python, tách module và xử lý ngoại lệ cho backend cho ứng dụng quản lý chi tiêu. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác.
- `ev-v2d-be-15-03` (projects): Trong một bài tập nhỏ có hướng dẫn từng bước, xây API Django REST có phân trang, xác thực dữ liệu và tài liệu OpenAPI cho backend cho ứng dụng quản lý chi tiêu. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác.
- `ev-v2d-be-15-04` (projects): Trong một bài tập nhỏ có hướng dẫn từng bước, dùng SQLAlchemy quản lý phiên giao dịch và migration khi thay đổi mô hình dữ liệu của backend cho ứng dụng quản lý chi tiêu. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác.
- `ev-v2d-be-15-05` (projects): Trong một bài tập nhỏ có hướng dẫn từng bước, viết unit test và integration test bằng pytest cho luồng lỗi và luồng thành công của backend cho ứng dụng quản lý chi tiêu. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác.
- `ev-v2d-be-15-06` (projects): Trong một bài tập nhỏ có hướng dẫn từng bước, dùng nhánh tính năng, xử lý góp ý code review và viết Dockerfile chạy dịch vụ backend cho ứng dụng quản lý chi tiêu. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác.
- `ev-v2d-be-15-07` (projects): Chiều sâu kỹ thuật của backend cho ứng dụng quản lý chi tiêu: Mỗi năng lực chỉ xuất hiện trong một bài tập nhỏ có hướng dẫn.
- `ev-v2d-be-15-08` (projects): Lập luận trong backend cho ứng dụng quản lý chi tiêu: Quyết định chủ yếu theo mẫu, chưa có so sánh hoặc kiểm chứng độc lập.
- `ev-v2d-be-15-09` (projects): Bàn giao backend cho ứng dụng quản lý chi tiêu: Có tệp kết quả nhưng hướng dẫn bàn giao còn tối thiểu.
- `ev-v2d-be-15-10` (other): Cách trình bày backend cho ứng dụng quản lý chi tiêu: Nêu đúng phạm vi hạn chế, tổng điểm thấp không đồng nghĩa yêu cầu bị phủ định.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-fe-01 — Junior Frontend Developer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `93`
- Nhãn nháp: `pass`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `fe-web-foundations` | `satisfied` | Triển khai layout bằng Grid và Flexbox, xử lý keyboard focus và breakpoint cho cổng tra cứu khóa học. |
| `fe-language` | `satisfied` | Bật kiểm tra kiểu nghiêm ngặt, loại bỏ kiểu không xác định và xử lý promise cho cổng tra cứu khóa học. |
| `fe-framework` | `satisfied` | Xây component React tái sử dụng, tách state và tối ưu render cho cổng tra cứu khóa học. |
| `fe-api` | `satisfied` | Dùng fetch với token xác thực, ánh xạ lỗi HTTP và đồng bộ dữ liệu màn hình cổng tra cứu khóa học. |
| `fe-testing-workflow` | `satisfied` | Thiết lập lint, unit test và quy trình merge có kiểm tra tự động cho cổng tra cứu khóa học. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 29/30 | Điểm nháp 29/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `fe-technical-specialization` | 23/25 | Điểm nháp 23/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `fe-role-capability` | 18/20 | Điểm nháp 18/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 14/15 | Điểm nháp 14/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 9/10 | Điểm nháp 9/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-fe-01-01` (education): Chương trình học có bài tổng hợp về cổng tra cứu khóa học; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-fe-01-02` (work_experience): Triển khai layout bằng Grid và Flexbox, xử lý keyboard focus và breakpoint cho cổng tra cứu khóa học.
- `ev-v2d-fe-01-03` (projects): Bật kiểm tra kiểu nghiêm ngặt, loại bỏ kiểu không xác định và xử lý promise cho cổng tra cứu khóa học.
- `ev-v2d-fe-01-04` (work_experience): Xây component React tái sử dụng, tách state và tối ưu render cho cổng tra cứu khóa học.
- `ev-v2d-fe-01-05` (projects): Dùng fetch với token xác thực, ánh xạ lỗi HTTP và đồng bộ dữ liệu màn hình cổng tra cứu khóa học.
- `ev-v2d-fe-01-06` (work_experience): Thiết lập lint, unit test và quy trình merge có kiểm tra tự động cho cổng tra cứu khóa học.
- `ev-v2d-fe-01-07` (projects): Chiều sâu kỹ thuật của cổng tra cứu khóa học: Giải pháp bao phủ luồng chính, dữ liệu biên và bước kiểm tra lại.
- `ev-v2d-fe-01-08` (projects): Lập luận trong cổng tra cứu khóa học: Nêu rõ lựa chọn kỹ thuật, giả định và một phương án đã loại bỏ.
- `ev-v2d-fe-01-09` (projects): Bàn giao cổng tra cứu khóa học: Bàn giao source, hướng dẫn chạy và kết quả kiểm tra cho người dùng nội bộ.
- `ev-v2d-fe-01-10` (other): Cách trình bày cổng tra cứu khóa học: Mô tả ngắn gọn phạm vi, kết quả định lượng và giới hạn còn lại.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-fe-02 — Junior Frontend Developer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `88`
- Nhãn nháp: `pass`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `fe-web-foundations` | `satisfied` | Chuyển thiết kế thành trang web thích ứng, giữ cấu trúc heading và biểu mẫu có nhãn trong giao diện quản lý đơn hàng. |
| `fe-language` | `satisfied` | Viết TypeScript quản lý state, kiểu dữ liệu API và xử lý lỗi phía client cho giao diện quản lý đơn hàng. |
| `fe-framework` | `satisfied` | Dùng Vue Composition API tổ chức màn hình và luồng dữ liệu cho giao diện quản lý đơn hàng. |
| `fe-api` | `satisfied` | Tạo lớp gọi API có validation response và retry có giới hạn cho giao diện quản lý đơn hàng. |
| `fe-testing-workflow` | `satisfied` | Dùng Git theo pull request và viết component test cho tương tác chính của giao diện quản lý đơn hàng. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 28/30 | Điểm nháp 28/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `fe-technical-specialization` | 22/25 | Điểm nháp 22/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `fe-role-capability` | 17/20 | Điểm nháp 17/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 13/15 | Điểm nháp 13/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 8/10 | Điểm nháp 8/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-fe-02-01` (education): Chương trình học có bài tổng hợp về giao diện quản lý đơn hàng; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-fe-02-02` (work_experience): Chuyển thiết kế thành trang web thích ứng, giữ cấu trúc heading và biểu mẫu có nhãn trong giao diện quản lý đơn hàng.
- `ev-v2d-fe-02-03` (projects): Viết TypeScript quản lý state, kiểu dữ liệu API và xử lý lỗi phía client cho giao diện quản lý đơn hàng.
- `ev-v2d-fe-02-04` (work_experience): Dùng Vue Composition API tổ chức màn hình và luồng dữ liệu cho giao diện quản lý đơn hàng.
- `ev-v2d-fe-02-05` (projects): Tạo lớp gọi API có validation response và retry có giới hạn cho giao diện quản lý đơn hàng.
- `ev-v2d-fe-02-06` (work_experience): Dùng Git theo pull request và viết component test cho tương tác chính của giao diện quản lý đơn hàng.
- `ev-v2d-fe-02-07` (projects): Chiều sâu kỹ thuật của giao diện quản lý đơn hàng: Thực hiện phần cốt lõi và xử lý ít nhất một lỗi phát sinh.
- `ev-v2d-fe-02-08` (projects): Lập luận trong giao diện quản lý đơn hàng: So sánh hai cách triển khai trước khi chọn giải pháp phù hợp phạm vi.
- `ev-v2d-fe-02-09` (projects): Bàn giao giao diện quản lý đơn hàng: Có quy trình review và tài liệu để thành viên khác chạy lại.
- `ev-v2d-fe-02-10` (other): Cách trình bày giao diện quản lý đơn hàng: Thông tin nhất quán, có đầu ra nhưng phần đo lường chưa hoàn toàn độc lập.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-fe-03 — Junior Frontend Developer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `82`
- Nhãn nháp: `waitlist`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `fe-web-foundations` | `satisfied` | Dựng giao diện semantic HTML và CSS responsive, kiểm tra ở nhiều kích thước màn hình cho ứng dụng theo dõi thói quen. |
| `fe-language` | `satisfied` | Dùng JavaScript module hóa logic tương tác và kiểm tra dữ liệu biểu mẫu trong ứng dụng theo dõi thói quen. |
| `fe-framework` | `satisfied` | Thiết kế cây component, route và trạng thái tải/lỗi cho ứng dụng ứng dụng theo dõi thói quen. |
| `fe-api` | `satisfied` | Tích hợp REST API, xử lý loading, empty, error và hủy request cho ứng dụng theo dõi thói quen. |
| `fe-testing-workflow` | `satisfied` | Bổ sung test bằng Testing Library, xử lý góp ý review và cấu hình build cho ứng dụng theo dõi thói quen. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 26/30 | Điểm nháp 26/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `fe-technical-specialization` | 20/25 | Điểm nháp 20/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `fe-role-capability` | 16/20 | Điểm nháp 16/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 12/15 | Điểm nháp 12/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 8/10 | Điểm nháp 8/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-fe-03-01` (education): Chương trình học có bài tổng hợp về ứng dụng theo dõi thói quen; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-fe-03-02` (work_experience): Dựng giao diện semantic HTML và CSS responsive, kiểm tra ở nhiều kích thước màn hình cho ứng dụng theo dõi thói quen.
- `ev-v2d-fe-03-03` (projects): Dùng JavaScript module hóa logic tương tác và kiểm tra dữ liệu biểu mẫu trong ứng dụng theo dõi thói quen.
- `ev-v2d-fe-03-04` (work_experience): Thiết kế cây component, route và trạng thái tải/lỗi cho ứng dụng ứng dụng theo dõi thói quen.
- `ev-v2d-fe-03-05` (projects): Tích hợp REST API, xử lý loading, empty, error và hủy request cho ứng dụng theo dõi thói quen.
- `ev-v2d-fe-03-06` (work_experience): Bổ sung test bằng Testing Library, xử lý góp ý review và cấu hình build cho ứng dụng theo dõi thói quen.
- `ev-v2d-fe-03-07` (projects): Chiều sâu kỹ thuật của ứng dụng theo dõi thói quen: Hoàn thành luồng chính và kiểm tra dữ liệu đầu vào phổ biến.
- `ev-v2d-fe-03-08` (projects): Lập luận trong ứng dụng theo dõi thói quen: Giải thích quyết định dựa trên yêu cầu và giới hạn thời gian.
- `ev-v2d-fe-03-09` (projects): Bàn giao ứng dụng theo dõi thói quen: Bàn giao qua repository và checklist chạy thử.
- `ev-v2d-fe-03-10` (other): Cách trình bày ứng dụng theo dõi thói quen: Nêu vai trò, kết quả và một giới hạn kỹ thuật.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-fe-04 — Junior Frontend Developer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `75`
- Nhãn nháp: `waitlist`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `fe-web-foundations` | `satisfied` | Triển khai layout bằng Grid và Flexbox, xử lý keyboard focus và breakpoint cho trang điều hành câu lạc bộ. |
| `fe-language` | `satisfied` | Bật kiểm tra kiểu nghiêm ngặt, loại bỏ kiểu không xác định và xử lý promise cho trang điều hành câu lạc bộ. |
| `fe-framework` | `satisfied` | Xây component React tái sử dụng, tách state và tối ưu render cho trang điều hành câu lạc bộ. |
| `fe-api` | `satisfied` | Dùng fetch với token xác thực, ánh xạ lỗi HTTP và đồng bộ dữ liệu màn hình trang điều hành câu lạc bộ. |
| `fe-testing-workflow` | `satisfied` | Thiết lập lint, unit test và quy trình merge có kiểm tra tự động cho trang điều hành câu lạc bộ. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 24/30 | Điểm nháp 24/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `fe-technical-specialization` | 18/25 | Điểm nháp 18/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `fe-role-capability` | 15/20 | Điểm nháp 15/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 11/15 | Điểm nháp 11/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 7/10 | Điểm nháp 7/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-fe-04-01` (education): Chương trình học có bài tổng hợp về trang điều hành câu lạc bộ; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-fe-04-02` (projects): Triển khai layout bằng Grid và Flexbox, xử lý keyboard focus và breakpoint cho trang điều hành câu lạc bộ.
- `ev-v2d-fe-04-03` (projects): Bật kiểm tra kiểu nghiêm ngặt, loại bỏ kiểu không xác định và xử lý promise cho trang điều hành câu lạc bộ.
- `ev-v2d-fe-04-04` (projects): Xây component React tái sử dụng, tách state và tối ưu render cho trang điều hành câu lạc bộ.
- `ev-v2d-fe-04-05` (projects): Dùng fetch với token xác thực, ánh xạ lỗi HTTP và đồng bộ dữ liệu màn hình trang điều hành câu lạc bộ.
- `ev-v2d-fe-04-06` (projects): Thiết lập lint, unit test và quy trình merge có kiểm tra tự động cho trang điều hành câu lạc bộ.
- `ev-v2d-fe-04-07` (projects): Chiều sâu kỹ thuật của trang điều hành câu lạc bộ: Có sản phẩm chạy được trong phạm vi học tập hoặc cá nhân.
- `ev-v2d-fe-04-08` (projects): Lập luận trong trang điều hành câu lạc bộ: Nêu lý do lựa chọn chính nhưng chưa phân tích sâu trade-off.
- `ev-v2d-fe-04-09` (projects): Bàn giao trang điều hành câu lạc bộ: Có source và hướng dẫn cơ bản để tái chạy.
- `ev-v2d-fe-04-10` (other): Cách trình bày trang điều hành câu lạc bộ: Thông tin đủ hiểu nhưng thiếu số đo tác động độc lập.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-fe-05 — Junior Frontend Developer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `66`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `missing-critical-evidence, low-score-without-explicit-critical-unsatisfied`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `fe-web-foundations` | `missing` | Không có thông tin trực tiếp |
| `fe-language` | `satisfied` | Viết TypeScript quản lý state, kiểu dữ liệu API và xử lý lỗi phía client cho website đặt lịch dịch vụ. |
| `fe-framework` | `satisfied` | Dùng Vue Composition API tổ chức màn hình và luồng dữ liệu cho website đặt lịch dịch vụ. |
| `fe-api` | `satisfied` | Tạo lớp gọi API có validation response và retry có giới hạn cho website đặt lịch dịch vụ. |
| `fe-testing-workflow` | `satisfied` | Dùng Git theo pull request và viết component test cho tương tác chính của website đặt lịch dịch vụ. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 18/30 | Điểm nháp 18/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `fe-technical-specialization` | 17/25 | Điểm nháp 17/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `fe-role-capability` | 14/20 | Điểm nháp 14/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 10/15 | Điểm nháp 10/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 7/10 | Điểm nháp 7/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-fe-05-01` (education): Chương trình học có bài tổng hợp về website đặt lịch dịch vụ; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-fe-05-02` (education): Có chỉnh màu trong template; không trình bày cấu trúc semantic hay xử lý responsive.
- `ev-v2d-fe-05-03` (projects): Viết TypeScript quản lý state, kiểu dữ liệu API và xử lý lỗi phía client cho website đặt lịch dịch vụ.
- `ev-v2d-fe-05-04` (projects): Dùng Vue Composition API tổ chức màn hình và luồng dữ liệu cho website đặt lịch dịch vụ.
- `ev-v2d-fe-05-05` (projects): Tạo lớp gọi API có validation response và retry có giới hạn cho website đặt lịch dịch vụ.
- `ev-v2d-fe-05-06` (projects): Dùng Git theo pull request và viết component test cho tương tác chính của website đặt lịch dịch vụ.
- `ev-v2d-fe-05-07` (projects): Chiều sâu kỹ thuật của website đặt lịch dịch vụ: Các phần được mô tả có thao tác thực hành nhưng độ bao phủ chưa đầy đủ.
- `ev-v2d-fe-05-08` (projects): Lập luận trong website đặt lịch dịch vụ: Có giải thích cho phần đã làm, không suy diễn phần còn thiếu.
- `ev-v2d-fe-05-09` (projects): Bàn giao website đặt lịch dịch vụ: Bàn giao được phạm vi hiện có và ghi rõ giới hạn.
- `ev-v2d-fe-05-10` (other): Cách trình bày website đặt lịch dịch vụ: Hồ sơ phân biệt rõ điều đã làm và điều chưa có thông tin.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-fe-06 — Junior Frontend Developer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `76`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `conflicting-critical-evidence`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `fe-web-foundations` | `satisfied` | Dựng giao diện semantic HTML và CSS responsive, kiểm tra ở nhiều kích thước màn hình cho cổng tra cứu khóa học. |
| `fe-language` | `conflicting` | Dùng JavaScript module hóa logic tương tác và kiểm tra dữ liệu biểu mẫu trong cổng tra cứu khóa học.<br>Không thể tự viết logic phía client cho cổng tra cứu khóa học; chỉ sửa nội dung tĩnh. |
| `fe-framework` | `satisfied` | Thiết kế cây component, route và trạng thái tải/lỗi cho ứng dụng cổng tra cứu khóa học. |
| `fe-api` | `satisfied` | Tích hợp REST API, xử lý loading, empty, error và hủy request cho cổng tra cứu khóa học. |
| `fe-testing-workflow` | `satisfied` | Bổ sung test bằng Testing Library, xử lý góp ý review và cấu hình build cho cổng tra cứu khóa học. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 22/30 | Điểm nháp 22/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `fe-technical-specialization` | 19/25 | Điểm nháp 19/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `fe-role-capability` | 15/20 | Điểm nháp 15/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 12/15 | Điểm nháp 12/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 8/10 | Điểm nháp 8/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-fe-06-01` (education): Chương trình học có bài tổng hợp về cổng tra cứu khóa học; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-fe-06-02` (projects): Dựng giao diện semantic HTML và CSS responsive, kiểm tra ở nhiều kích thước màn hình cho cổng tra cứu khóa học.
- `ev-v2d-fe-06-03` (projects): Dùng JavaScript module hóa logic tương tác và kiểm tra dữ liệu biểu mẫu trong cổng tra cứu khóa học.
- `ev-v2d-fe-06-04` (other): Không thể tự viết logic phía client cho cổng tra cứu khóa học; chỉ sửa nội dung tĩnh.
- `ev-v2d-fe-06-05` (projects): Thiết kế cây component, route và trạng thái tải/lỗi cho ứng dụng cổng tra cứu khóa học.
- `ev-v2d-fe-06-06` (projects): Tích hợp REST API, xử lý loading, empty, error và hủy request cho cổng tra cứu khóa học.
- `ev-v2d-fe-06-07` (projects): Bổ sung test bằng Testing Library, xử lý góp ý review và cấu hình build cho cổng tra cứu khóa học.
- `ev-v2d-fe-06-08` (projects): Chiều sâu kỹ thuật của cổng tra cứu khóa học: Có đầu ra kỹ thuật nhưng trạng thái một năng lực chưa thể kết luận.
- `ev-v2d-fe-06-09` (projects): Lập luận trong cổng tra cứu khóa học: Ghi lại quyết định của dự án nhưng chưa giải thích được mâu thuẫn trong hồ sơ.
- `ev-v2d-fe-06-10` (projects): Bàn giao cổng tra cứu khóa học: Có artifact bàn giao và một cảnh báo cần xác minh.
- `ev-v2d-fe-06-11` (other): Cách trình bày cổng tra cứu khóa học: Thông tin khá rõ ngoài điểm mâu thuẫn cần human review.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-fe-07 — Junior Frontend Developer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `57`
- Nhãn nháp: `reject`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `fe-web-foundations` | `satisfied` | Triển khai layout bằng Grid và Flexbox, xử lý keyboard focus và breakpoint cho giao diện quản lý đơn hàng. |
| `fe-language` | `satisfied` | Bật kiểm tra kiểu nghiêm ngặt, loại bỏ kiểu không xác định và xử lý promise cho giao diện quản lý đơn hàng. |
| `fe-framework` | `unsatisfied` | Không sử dụng React, Vue hoặc framework tương đương trong giao diện quản lý đơn hàng. |
| `fe-api` | `satisfied` | Dùng fetch với token xác thực, ánh xạ lỗi HTTP và đồng bộ dữ liệu màn hình giao diện quản lý đơn hàng. |
| `fe-testing-workflow` | `satisfied` | Thiết lập lint, unit test và quy trình merge có kiểm tra tự động cho giao diện quản lý đơn hàng. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 16/30 | Điểm nháp 16/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `fe-technical-specialization` | 15/25 | Điểm nháp 15/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `fe-role-capability` | 12/20 | Điểm nháp 12/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 8/15 | Điểm nháp 8/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 6/10 | Điểm nháp 6/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-fe-07-01` (education): Chương trình học có bài tổng hợp về giao diện quản lý đơn hàng; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-fe-07-02` (projects): Triển khai layout bằng Grid và Flexbox, xử lý keyboard focus và breakpoint cho giao diện quản lý đơn hàng.
- `ev-v2d-fe-07-03` (projects): Bật kiểm tra kiểu nghiêm ngặt, loại bỏ kiểu không xác định và xử lý promise cho giao diện quản lý đơn hàng.
- `ev-v2d-fe-07-04` (other): Không sử dụng React, Vue hoặc framework tương đương trong giao diện quản lý đơn hàng.
- `ev-v2d-fe-07-05` (projects): Dùng fetch với token xác thực, ánh xạ lỗi HTTP và đồng bộ dữ liệu màn hình giao diện quản lý đơn hàng.
- `ev-v2d-fe-07-06` (projects): Thiết lập lint, unit test và quy trình merge có kiểm tra tự động cho giao diện quản lý đơn hàng.
- `ev-v2d-fe-07-07` (projects): Chiều sâu kỹ thuật của giao diện quản lý đơn hàng: Một phần công việc phụ thuộc vào thành viên khác và không có khả năng thay thế.
- `ev-v2d-fe-07-08` (projects): Lập luận trong giao diện quản lý đơn hàng: Nêu đúng giới hạn hiện tại nhưng chưa có kế hoạch kiểm chứng năng lực thiếu.
- `ev-v2d-fe-07-09` (projects): Bàn giao giao diện quản lý đơn hàng: Chỉ bàn giao được phần việc hẹp.
- `ev-v2d-fe-07-10` (other): Cách trình bày giao diện quản lý đơn hàng: Thông tin phủ định rõ và không bị che bởi danh sách từ khóa.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-fe-08 — Junior Frontend Developer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `24`
- Nhãn nháp: `reject`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `fe-web-foundations` | `unsatisfied` | Chưa thể tự xây giao diện responsive bằng HTML và CSS. |
| `fe-language` | `unsatisfied` | Không thể tự viết logic phía client cho ứng dụng theo dõi thói quen; chỉ sửa nội dung tĩnh. |
| `fe-framework` | `unsatisfied` | Chưa từng xây ứng dụng bằng framework frontend dựa trên component. |
| `fe-api` | `unsatisfied` | Không thể gọi hoặc xử lý response API từ màn hình ứng dụng theo dõi thói quen. |
| `fe-testing-workflow` | `unsatisfied` | Chưa từng dùng Git và chưa từng kiểm thử giao diện. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 5/30 | Điểm nháp 5/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `fe-technical-specialization` | 5/25 | Điểm nháp 5/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `fe-role-capability` | 6/20 | Điểm nháp 6/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 4/15 | Điểm nháp 4/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 4/10 | Điểm nháp 4/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-fe-08-01` (education): Chương trình học có bài tổng hợp về ứng dụng theo dõi thói quen; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-fe-08-02` (other): Chưa thể tự xây giao diện responsive bằng HTML và CSS.
- `ev-v2d-fe-08-03` (other): Không thể tự viết logic phía client cho ứng dụng theo dõi thói quen; chỉ sửa nội dung tĩnh.
- `ev-v2d-fe-08-04` (other): Chưa từng xây ứng dụng bằng framework frontend dựa trên component.
- `ev-v2d-fe-08-05` (other): Không thể gọi hoặc xử lý response API từ màn hình ứng dụng theo dõi thói quen.
- `ev-v2d-fe-08-06` (other): Chưa từng dùng Git và chưa từng kiểm thử giao diện.
- `ev-v2d-fe-08-07` (projects): Chiều sâu kỹ thuật của ứng dụng theo dõi thói quen: Không có artifact hoặc tác vụ chuyên môn do ứng viên tự hoàn thành.
- `ev-v2d-fe-08-08` (projects): Lập luận trong ứng dụng theo dõi thói quen: Chưa có quyết định kỹ thuật để đánh giá.
- `ev-v2d-fe-08-09` (projects): Bàn giao ứng dụng theo dõi thói quen: Không có quy trình bàn giao có thể tái tạo.
- `ev-v2d-fe-08-10` (other): Cách trình bày ứng dụng theo dõi thói quen: Giới hạn được phát biểu rõ, không tạo ấn tượng sai về kinh nghiệm.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-fe-09 — Junior Frontend Developer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `53`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `missing-critical-evidence, low-score-without-explicit-critical-unsatisfied`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `fe-web-foundations` | `missing` | Không có thông tin trực tiếp |
| `fe-language` | `satisfied` | Dùng JavaScript module hóa logic tương tác và kiểm tra dữ liệu biểu mẫu trong trang điều hành câu lạc bộ. |
| `fe-framework` | `missing` | Không có thông tin trực tiếp |
| `fe-api` | `satisfied` | Tích hợp REST API, xử lý loading, empty, error và hủy request cho trang điều hành câu lạc bộ. |
| `fe-testing-workflow` | `missing` | Không có thông tin trực tiếp |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 14/30 | Điểm nháp 14/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `fe-technical-specialization` | 13/25 | Điểm nháp 13/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `fe-role-capability` | 12/20 | Điểm nháp 12/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 8/15 | Điểm nháp 8/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 6/10 | Điểm nháp 6/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-fe-09-01` (education): Chương trình học có bài tổng hợp về trang điều hành câu lạc bộ; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-fe-09-02` (education): Có chỉnh màu trong template; không trình bày cấu trúc semantic hay xử lý responsive.
- `ev-v2d-fe-09-03` (projects): Dùng JavaScript module hóa logic tương tác và kiểm tra dữ liệu biểu mẫu trong trang điều hành câu lạc bộ.
- `ev-v2d-fe-09-04` (education): Theo dõi khóa học framework; không có source hay đầu ra ứng dụng.
- `ev-v2d-fe-09-05` (projects): Tích hợp REST API, xử lý loading, empty, error và hủy request cho trang điều hành câu lạc bộ.
- `ev-v2d-fe-09-06` (education): Đã gửi source cho nhóm qua tệp nén; không có pull request hay kiểm tra trước merge.
- `ev-v2d-fe-09-07` (projects): Chiều sâu kỹ thuật của trang điều hành câu lạc bộ: Có một số thao tác đơn lẻ nhưng chưa thành luồng hoàn chỉnh.
- `ev-v2d-fe-09-08` (projects): Lập luận trong trang điều hành câu lạc bộ: Lý do thực hiện chưa gắn với tiêu chí thành công.
- `ev-v2d-fe-09-09` (projects): Bàn giao trang điều hành câu lạc bộ: Artifact rời rạc và chưa có hướng dẫn tái chạy.
- `ev-v2d-fe-09-10` (other): Cách trình bày trang điều hành câu lạc bộ: Hồ sơ không khẳng định các năng lực chưa được chứng minh.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-fe-10 — Junior Frontend Developer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `68`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `missing-critical-evidence, low-score-without-explicit-critical-unsatisfied, lower-threshold-boundary`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `fe-web-foundations` | `satisfied` | Triển khai layout bằng Grid và Flexbox, xử lý keyboard focus và breakpoint cho website đặt lịch dịch vụ. |
| `fe-language` | `satisfied` | Bật kiểm tra kiểu nghiêm ngặt, loại bỏ kiểu không xác định và xử lý promise cho website đặt lịch dịch vụ. |
| `fe-framework` | `satisfied` | Xây component React tái sử dụng, tách state và tối ưu render cho website đặt lịch dịch vụ. |
| `fe-api` | `satisfied` | Dùng fetch với token xác thực, ánh xạ lỗi HTTP và đồng bộ dữ liệu màn hình website đặt lịch dịch vụ. |
| `fe-testing-workflow` | `missing` | Không có thông tin trực tiếp |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 20/30 | Điểm nháp 20/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `fe-technical-specialization` | 17/25 | Điểm nháp 17/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `fe-role-capability` | 13/20 | Điểm nháp 13/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 10/15 | Điểm nháp 10/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 8/10 | Điểm nháp 8/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-fe-10-01` (education): Chương trình học có bài tổng hợp về website đặt lịch dịch vụ; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-fe-10-02` (projects): Triển khai layout bằng Grid và Flexbox, xử lý keyboard focus và breakpoint cho website đặt lịch dịch vụ.
- `ev-v2d-fe-10-03` (projects): Bật kiểm tra kiểu nghiêm ngặt, loại bỏ kiểu không xác định và xử lý promise cho website đặt lịch dịch vụ.
- `ev-v2d-fe-10-04` (projects): Xây component React tái sử dụng, tách state và tối ưu render cho website đặt lịch dịch vụ.
- `ev-v2d-fe-10-05` (projects): Dùng fetch với token xác thực, ánh xạ lỗi HTTP và đồng bộ dữ liệu màn hình website đặt lịch dịch vụ.
- `ev-v2d-fe-10-06` (education): Biết tên công cụ test frontend nhưng không có test hoặc kết quả chạy tự động.
- `ev-v2d-fe-10-07` (projects): Chiều sâu kỹ thuật của website đặt lịch dịch vụ: Phần lớn năng lực có ví dụ nhưng chiều sâu chưa đồng đều.
- `ev-v2d-fe-10-08` (projects): Lập luận trong website đặt lịch dịch vụ: Có giải thích lựa chọn chính và một giả định chưa kiểm tra.
- `ev-v2d-fe-10-09` (projects): Bàn giao website đặt lịch dịch vụ: Có bản chạy thử và ghi chú vận hành cơ bản.
- `ev-v2d-fe-10-10` (other): Cách trình bày website đặt lịch dịch vụ: Thông tin tương đối rõ nhưng cần xác minh phần còn thiếu.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-fe-11 — Junior Frontend Developer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `85`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `conflicting-critical-evidence, upper-threshold-boundary`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `fe-web-foundations` | `conflicting` | Chuyển thiết kế thành trang web thích ứng, giữ cấu trúc heading và biểu mẫu có nhãn trong cổng tra cứu khóa học.<br>Không nắm nền tảng bố cục web; phần giao diện cổng tra cứu khóa học dùng nguyên mẫu có sẵn. |
| `fe-language` | `satisfied` | Viết TypeScript quản lý state, kiểu dữ liệu API và xử lý lỗi phía client cho cổng tra cứu khóa học. |
| `fe-framework` | `satisfied` | Dùng Vue Composition API tổ chức màn hình và luồng dữ liệu cho cổng tra cứu khóa học. |
| `fe-api` | `satisfied` | Tạo lớp gọi API có validation response và retry có giới hạn cho cổng tra cứu khóa học. |
| `fe-testing-workflow` | `satisfied` | Dùng Git theo pull request và viết component test cho tương tác chính của cổng tra cứu khóa học. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 25/30 | Điểm nháp 25/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `fe-technical-specialization` | 21/25 | Điểm nháp 21/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `fe-role-capability` | 17/20 | Điểm nháp 17/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 13/15 | Điểm nháp 13/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 9/10 | Điểm nháp 9/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-fe-11-01` (education): Chương trình học có bài tổng hợp về cổng tra cứu khóa học; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-fe-11-02` (work_experience): Chuyển thiết kế thành trang web thích ứng, giữ cấu trúc heading và biểu mẫu có nhãn trong cổng tra cứu khóa học.
- `ev-v2d-fe-11-03` (other): Không nắm nền tảng bố cục web; phần giao diện cổng tra cứu khóa học dùng nguyên mẫu có sẵn.
- `ev-v2d-fe-11-04` (projects): Viết TypeScript quản lý state, kiểu dữ liệu API và xử lý lỗi phía client cho cổng tra cứu khóa học.
- `ev-v2d-fe-11-05` (work_experience): Dùng Vue Composition API tổ chức màn hình và luồng dữ liệu cho cổng tra cứu khóa học.
- `ev-v2d-fe-11-06` (projects): Tạo lớp gọi API có validation response và retry có giới hạn cho cổng tra cứu khóa học.
- `ev-v2d-fe-11-07` (work_experience): Dùng Git theo pull request và viết component test cho tương tác chính của cổng tra cứu khóa học.
- `ev-v2d-fe-11-08` (projects): Chiều sâu kỹ thuật của cổng tra cứu khóa học: Artifact kỹ thuật khá hoàn chỉnh ngoài điểm cần xác minh.
- `ev-v2d-fe-11-09` (projects): Lập luận trong cổng tra cứu khóa học: Nêu trade-off và cách kiểm tra kết quả.
- `ev-v2d-fe-11-10` (projects): Bàn giao cổng tra cứu khóa học: Bàn giao có review, test và hướng dẫn sử dụng.
- `ev-v2d-fe-11-11` (other): Cách trình bày cổng tra cứu khóa học: Trình bày tốt nhưng chưa giải quyết được phát biểu mâu thuẫn.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-fe-12 — Junior Frontend Developer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `79`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `critical-unsatisfied-at-or-above-waitlist-threshold`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `fe-web-foundations` | `satisfied` | Dựng giao diện semantic HTML và CSS responsive, kiểm tra ở nhiều kích thước màn hình cho giao diện quản lý đơn hàng. |
| `fe-language` | `satisfied` | Dùng JavaScript module hóa logic tương tác và kiểm tra dữ liệu biểu mẫu trong giao diện quản lý đơn hàng. |
| `fe-framework` | `satisfied` | Thiết kế cây component, route và trạng thái tải/lỗi cho ứng dụng giao diện quản lý đơn hàng. |
| `fe-api` | `satisfied` | Tích hợp REST API, xử lý loading, empty, error và hủy request cho giao diện quản lý đơn hàng. |
| `fe-testing-workflow` | `unsatisfied` | Chưa từng dùng Git và chưa từng kiểm thử giao diện. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 23/30 | Điểm nháp 23/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `fe-technical-specialization` | 20/25 | Điểm nháp 20/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `fe-role-capability` | 16/20 | Điểm nháp 16/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 12/15 | Điểm nháp 12/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 8/10 | Điểm nháp 8/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-fe-12-01` (education): Chương trình học có bài tổng hợp về giao diện quản lý đơn hàng; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-fe-12-02` (projects): Dựng giao diện semantic HTML và CSS responsive, kiểm tra ở nhiều kích thước màn hình cho giao diện quản lý đơn hàng.
- `ev-v2d-fe-12-03` (projects): Dùng JavaScript module hóa logic tương tác và kiểm tra dữ liệu biểu mẫu trong giao diện quản lý đơn hàng.
- `ev-v2d-fe-12-04` (projects): Thiết kế cây component, route và trạng thái tải/lỗi cho ứng dụng giao diện quản lý đơn hàng.
- `ev-v2d-fe-12-05` (projects): Tích hợp REST API, xử lý loading, empty, error và hủy request cho giao diện quản lý đơn hàng.
- `ev-v2d-fe-12-06` (other): Chưa từng dùng Git và chưa từng kiểm thử giao diện.
- `ev-v2d-fe-12-07` (projects): Chiều sâu kỹ thuật của giao diện quản lý đơn hàng: Các năng lực còn lại có thực hành và đầu ra cụ thể.
- `ev-v2d-fe-12-08` (projects): Lập luận trong giao diện quản lý đơn hàng: Nêu cách xử lý trong phạm vi đã biết và giới hạn cần hỗ trợ.
- `ev-v2d-fe-12-09` (projects): Bàn giao giao diện quản lý đơn hàng: Có artifact bàn giao cho phần việc đã hoàn thành.
- `ev-v2d-fe-12-10` (other): Cách trình bày giao diện quản lý đơn hàng: Hồ sơ minh bạch về năng lực chưa đạt.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-fe-13 — Junior Frontend Developer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `45`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `missing-critical-evidence, low-score-without-explicit-critical-unsatisfied`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `fe-web-foundations` | `missing` | Không có thông tin trực tiếp |
| `fe-language` | `missing` | Không có thông tin trực tiếp |
| `fe-framework` | `missing` | Không có thông tin trực tiếp |
| `fe-api` | `missing` | Không có thông tin trực tiếp |
| `fe-testing-workflow` | `missing` | Không có thông tin trực tiếp |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 12/30 | Điểm nháp 12/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `fe-technical-specialization` | 10/25 | Điểm nháp 10/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `fe-role-capability` | 10/20 | Điểm nháp 10/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 7/15 | Điểm nháp 7/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 6/10 | Điểm nháp 6/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-fe-13-01` (education): Chương trình học có bài tổng hợp về ứng dụng theo dõi thói quen; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-fe-13-02` (education): Có chỉnh màu trong template; không trình bày cấu trúc semantic hay xử lý responsive.
- `ev-v2d-fe-13-03` (other): Hoàn thành bài cú pháp JavaScript nhưng không có chức năng web được mô tả.
- `ev-v2d-fe-13-04` (education): Theo dõi khóa học framework; không có source hay đầu ra ứng dụng.
- `ev-v2d-fe-13-05` (other): Biết API cung cấp dữ liệu nhưng không có request hoặc trạng thái giao diện được triển khai.
- `ev-v2d-fe-13-06` (education): Đã gửi source cho nhóm qua tệp nén; không có pull request hay kiểm tra trước merge.
- `ev-v2d-fe-13-07` (projects): Chiều sâu kỹ thuật của ứng dụng theo dõi thói quen: Chỉ có nội dung học tập và quan sát, chưa có sản phẩm áp dụng.
- `ev-v2d-fe-13-08` (projects): Lập luận trong ứng dụng theo dõi thói quen: Không có quyết định kỹ thuật thuộc trách nhiệm ứng viên.
- `ev-v2d-fe-13-09` (projects): Bàn giao ứng dụng theo dõi thói quen: Không có artifact có thể kiểm tra độc lập.
- `ev-v2d-fe-13-10` (other): Cách trình bày ứng dụng theo dõi thói quen: Không suy diễn từ tên khóa học hoặc công cụ được nhắc tới.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-fe-14 — Junior Frontend Developer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `89`
- Nhãn nháp: `pass`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `fe-web-foundations` | `satisfied` | Chuyển thiết kế thành trang web thích ứng, giữ cấu trúc heading và biểu mẫu có nhãn trong trang điều hành câu lạc bộ. |
| `fe-language` | `satisfied` | Viết TypeScript quản lý state, kiểu dữ liệu API và xử lý lỗi phía client cho trang điều hành câu lạc bộ. |
| `fe-framework` | `satisfied` | Dùng Vue Composition API tổ chức màn hình và luồng dữ liệu cho trang điều hành câu lạc bộ. |
| `fe-api` | `satisfied` | Tạo lớp gọi API có validation response và retry có giới hạn cho trang điều hành câu lạc bộ. |
| `fe-testing-workflow` | `satisfied` | Dùng Git theo pull request và viết component test cho tương tác chính của trang điều hành câu lạc bộ. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 27/30 | Điểm nháp 27/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `fe-technical-specialization` | 22/25 | Điểm nháp 22/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `fe-role-capability` | 18/20 | Điểm nháp 18/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 13/15 | Điểm nháp 13/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 9/10 | Điểm nháp 9/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-fe-14-01` (education): Chương trình học có bài tổng hợp về trang điều hành câu lạc bộ; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-fe-14-02` (work_experience): Chuyển thiết kế thành trang web thích ứng, giữ cấu trúc heading và biểu mẫu có nhãn trong trang điều hành câu lạc bộ.
- `ev-v2d-fe-14-03` (projects): Viết TypeScript quản lý state, kiểu dữ liệu API và xử lý lỗi phía client cho trang điều hành câu lạc bộ.
- `ev-v2d-fe-14-04` (work_experience): Dùng Vue Composition API tổ chức màn hình và luồng dữ liệu cho trang điều hành câu lạc bộ.
- `ev-v2d-fe-14-05` (projects): Tạo lớp gọi API có validation response và retry có giới hạn cho trang điều hành câu lạc bộ.
- `ev-v2d-fe-14-06` (work_experience): Dùng Git theo pull request và viết component test cho tương tác chính của trang điều hành câu lạc bộ.
- `ev-v2d-fe-14-07` (projects): Chiều sâu kỹ thuật của trang điều hành câu lạc bộ: Chứng minh năng lực qua nhiệm vụ tương đương thay vì lặp lại từ khóa JD.
- `ev-v2d-fe-14-08` (projects): Lập luận trong trang điều hành câu lạc bộ: Giải thích mục tiêu, cách đo và một giới hạn của giải pháp.
- `ev-v2d-fe-14-09` (projects): Bàn giao trang điều hành câu lạc bộ: Có source, kết quả kiểm tra và hướng dẫn tái tạo.
- `ev-v2d-fe-14-10` (other): Cách trình bày trang điều hành câu lạc bộ: Thông tin có cấu trúc, nhất quán và truy ngược được tới artifact.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-fe-15 — Junior Frontend Developer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `58`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `low-score-without-explicit-critical-unsatisfied`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `fe-web-foundations` | `satisfied` | Trong một bài tập nhỏ có hướng dẫn từng bước, dựng giao diện semantic HTML và CSS responsive, kiểm tra ở nhiều kích thước màn hình cho website đặt lịch dịch vụ. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác. |
| `fe-language` | `satisfied` | Trong một bài tập nhỏ có hướng dẫn từng bước, dùng JavaScript module hóa logic tương tác và kiểm tra dữ liệu biểu mẫu trong website đặt lịch dịch vụ. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác. |
| `fe-framework` | `satisfied` | Trong một bài tập nhỏ có hướng dẫn từng bước, thiết kế cây component, route và trạng thái tải/lỗi cho ứng dụng website đặt lịch dịch vụ. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác. |
| `fe-api` | `satisfied` | Trong một bài tập nhỏ có hướng dẫn từng bước, tích hợp REST API, xử lý loading, empty, error và hủy request cho website đặt lịch dịch vụ. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác. |
| `fe-testing-workflow` | `satisfied` | Trong một bài tập nhỏ có hướng dẫn từng bước, bổ sung test bằng Testing Library, xử lý góp ý review và cấu hình build cho website đặt lịch dịch vụ. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 18/30 | Điểm nháp 18/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `fe-technical-specialization` | 14/25 | Điểm nháp 14/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `fe-role-capability` | 11/20 | Điểm nháp 11/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 9/15 | Điểm nháp 9/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 6/10 | Điểm nháp 6/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-fe-15-01` (education): Chương trình học có bài tổng hợp về website đặt lịch dịch vụ; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-fe-15-02` (projects): Trong một bài tập nhỏ có hướng dẫn từng bước, dựng giao diện semantic HTML và CSS responsive, kiểm tra ở nhiều kích thước màn hình cho website đặt lịch dịch vụ. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác.
- `ev-v2d-fe-15-03` (projects): Trong một bài tập nhỏ có hướng dẫn từng bước, dùng JavaScript module hóa logic tương tác và kiểm tra dữ liệu biểu mẫu trong website đặt lịch dịch vụ. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác.
- `ev-v2d-fe-15-04` (projects): Trong một bài tập nhỏ có hướng dẫn từng bước, thiết kế cây component, route và trạng thái tải/lỗi cho ứng dụng website đặt lịch dịch vụ. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác.
- `ev-v2d-fe-15-05` (projects): Trong một bài tập nhỏ có hướng dẫn từng bước, tích hợp REST API, xử lý loading, empty, error và hủy request cho website đặt lịch dịch vụ. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác.
- `ev-v2d-fe-15-06` (projects): Trong một bài tập nhỏ có hướng dẫn từng bước, bổ sung test bằng Testing Library, xử lý góp ý review và cấu hình build cho website đặt lịch dịch vụ. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác.
- `ev-v2d-fe-15-07` (projects): Chiều sâu kỹ thuật của website đặt lịch dịch vụ: Mỗi năng lực chỉ xuất hiện trong một bài tập nhỏ có hướng dẫn.
- `ev-v2d-fe-15-08` (projects): Lập luận trong website đặt lịch dịch vụ: Quyết định chủ yếu theo mẫu, chưa có so sánh hoặc kiểm chứng độc lập.
- `ev-v2d-fe-15-09` (projects): Bàn giao website đặt lịch dịch vụ: Có tệp kết quả nhưng hướng dẫn bàn giao còn tối thiểu.
- `ev-v2d-fe-15-10` (other): Cách trình bày website đặt lịch dịch vụ: Nêu đúng phạm vi hạn chế, tổng điểm thấp không đồng nghĩa yêu cầu bị phủ định.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-qa-01 — Junior QA Engineer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `93`
- Nhãn nháp: `pass`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `qa-testing-foundations` | `satisfied` | Mô tả các bước STLC, xác định rủi ro và ưu tiên kiểm thử cho kiểm thử cổng đăng ký môn học. |
| `qa-test-cases` | `satisfied` | Duy trì bộ test theo yêu cầu thay đổi và theo dõi vòng đời lỗi của kiểm thử cổng đăng ký môn học. |
| `qa-api-testing` | `satisfied` | Dùng Postman kiểm tra method, status, schema và trường hợp xác thực lỗi cho API của kiểm thử cổng đăng ký môn học. |
| `qa-data-check` | `satisfied` | Kiểm tra ràng buộc và bản ghi bất thường bằng SQL khi xác minh kiểm thử cổng đăng ký môn học. |
| `qa-automation-foundation` | `satisfied` | Tạo test Cypress có setup dữ liệu, assertion và báo cáo kết quả cho kiểm thử cổng đăng ký môn học. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 29/30 | Điểm nháp 29/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `qa-technical-specialization` | 23/25 | Điểm nháp 23/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `qa-role-capability` | 18/20 | Điểm nháp 18/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 14/15 | Điểm nháp 14/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 9/10 | Điểm nháp 9/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-qa-01-01` (education): Chương trình học có bài tổng hợp về kiểm thử cổng đăng ký môn học; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-qa-01-02` (work_experience): Mô tả các bước STLC, xác định rủi ro và ưu tiên kiểm thử cho kiểm thử cổng đăng ký môn học.
- `ev-v2d-qa-01-03` (projects): Duy trì bộ test theo yêu cầu thay đổi và theo dõi vòng đời lỗi của kiểm thử cổng đăng ký môn học.
- `ev-v2d-qa-01-04` (work_experience): Dùng Postman kiểm tra method, status, schema và trường hợp xác thực lỗi cho API của kiểm thử cổng đăng ký môn học.
- `ev-v2d-qa-01-05` (projects): Kiểm tra ràng buộc và bản ghi bất thường bằng SQL khi xác minh kiểm thử cổng đăng ký môn học.
- `ev-v2d-qa-01-06` (work_experience): Tạo test Cypress có setup dữ liệu, assertion và báo cáo kết quả cho kiểm thử cổng đăng ký môn học.
- `ev-v2d-qa-01-07` (projects): Chiều sâu kỹ thuật của kiểm thử cổng đăng ký môn học: Giải pháp bao phủ luồng chính, dữ liệu biên và bước kiểm tra lại.
- `ev-v2d-qa-01-08` (projects): Lập luận trong kiểm thử cổng đăng ký môn học: Nêu rõ lựa chọn kỹ thuật, giả định và một phương án đã loại bỏ.
- `ev-v2d-qa-01-09` (projects): Bàn giao kiểm thử cổng đăng ký môn học: Bàn giao source, hướng dẫn chạy và kết quả kiểm tra cho người dùng nội bộ.
- `ev-v2d-qa-01-10` (other): Cách trình bày kiểm thử cổng đăng ký môn học: Mô tả ngắn gọn phạm vi, kết quả định lượng và giới hạn còn lại.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-qa-02 — Junior QA Engineer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `88`
- Nhãn nháp: `pass`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `qa-testing-foundations` | `satisfied` | Phân tích yêu cầu, lập test condition và giải thích kỹ thuật thiết kế test được chọn trong đánh giá chất lượng ứng dụng thương mại. |
| `qa-test-cases` | `satisfied` | Viết test case có precondition, dữ liệu, expected result và liên kết defect cho đánh giá chất lượng ứng dụng thương mại. |
| `qa-api-testing` | `satisfied` | Tạo collection kiểm thử request/response HTTP và biến môi trường cho đánh giá chất lượng ứng dụng thương mại. |
| `qa-data-check` | `satisfied` | So sánh dữ liệu API với bảng quan hệ và lưu câu truy vấn tái kiểm tra cho đánh giá chất lượng ứng dụng thương mại. |
| `qa-automation-foundation` | `satisfied` | Viết kịch bản Playwright cho luồng chính, dùng locator ổn định và chạy lại trên CI cho đánh giá chất lượng ứng dụng thương mại. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 28/30 | Điểm nháp 28/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `qa-technical-specialization` | 22/25 | Điểm nháp 22/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `qa-role-capability` | 17/20 | Điểm nháp 17/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 13/15 | Điểm nháp 13/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 8/10 | Điểm nháp 8/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-qa-02-01` (education): Chương trình học có bài tổng hợp về đánh giá chất lượng ứng dụng thương mại; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-qa-02-02` (work_experience): Phân tích yêu cầu, lập test condition và giải thích kỹ thuật thiết kế test được chọn trong đánh giá chất lượng ứng dụng thương mại.
- `ev-v2d-qa-02-03` (projects): Viết test case có precondition, dữ liệu, expected result và liên kết defect cho đánh giá chất lượng ứng dụng thương mại.
- `ev-v2d-qa-02-04` (work_experience): Tạo collection kiểm thử request/response HTTP và biến môi trường cho đánh giá chất lượng ứng dụng thương mại.
- `ev-v2d-qa-02-05` (projects): So sánh dữ liệu API với bảng quan hệ và lưu câu truy vấn tái kiểm tra cho đánh giá chất lượng ứng dụng thương mại.
- `ev-v2d-qa-02-06` (work_experience): Viết kịch bản Playwright cho luồng chính, dùng locator ổn định và chạy lại trên CI cho đánh giá chất lượng ứng dụng thương mại.
- `ev-v2d-qa-02-07` (projects): Chiều sâu kỹ thuật của đánh giá chất lượng ứng dụng thương mại: Thực hiện phần cốt lõi và xử lý ít nhất một lỗi phát sinh.
- `ev-v2d-qa-02-08` (projects): Lập luận trong đánh giá chất lượng ứng dụng thương mại: So sánh hai cách triển khai trước khi chọn giải pháp phù hợp phạm vi.
- `ev-v2d-qa-02-09` (projects): Bàn giao đánh giá chất lượng ứng dụng thương mại: Có quy trình review và tài liệu để thành viên khác chạy lại.
- `ev-v2d-qa-02-10` (other): Cách trình bày đánh giá chất lượng ứng dụng thương mại: Thông tin nhất quán, có đầu ra nhưng phần đo lường chưa hoàn toàn độc lập.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-qa-03 — Junior QA Engineer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `82`
- Nhãn nháp: `waitlist`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `qa-testing-foundations` | `satisfied` | Áp dụng phân vùng tương đương, giá trị biên và decision table để thiết kế phạm vi test cho kiểm thử hệ thống quản lý kho. |
| `qa-test-cases` | `satisfied` | Thực hiện regression, ghi bug report có bước tái hiện và mức độ ảnh hưởng trong kiểm thử hệ thống quản lý kho. |
| `qa-api-testing` | `satisfied` | Đối chiếu hợp đồng API, kiểm tra dữ liệu biên và lưu kết quả chạy lại cho kiểm thử hệ thống quản lý kho. |
| `qa-data-check` | `satisfied` | Viết truy vấn SELECT, JOIN và GROUP BY để đối chiếu dữ liệu sau thao tác trong kiểm thử hệ thống quản lý kho. |
| `qa-automation-foundation` | `satisfied` | Dùng Selenium tổ chức page object và tự động hóa regression của kiểm thử hệ thống quản lý kho. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 26/30 | Điểm nháp 26/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `qa-technical-specialization` | 20/25 | Điểm nháp 20/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `qa-role-capability` | 16/20 | Điểm nháp 16/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 12/15 | Điểm nháp 12/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 8/10 | Điểm nháp 8/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-qa-03-01` (education): Chương trình học có bài tổng hợp về kiểm thử hệ thống quản lý kho; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-qa-03-02` (work_experience): Áp dụng phân vùng tương đương, giá trị biên và decision table để thiết kế phạm vi test cho kiểm thử hệ thống quản lý kho.
- `ev-v2d-qa-03-03` (projects): Thực hiện regression, ghi bug report có bước tái hiện và mức độ ảnh hưởng trong kiểm thử hệ thống quản lý kho.
- `ev-v2d-qa-03-04` (work_experience): Đối chiếu hợp đồng API, kiểm tra dữ liệu biên và lưu kết quả chạy lại cho kiểm thử hệ thống quản lý kho.
- `ev-v2d-qa-03-05` (projects): Viết truy vấn SELECT, JOIN và GROUP BY để đối chiếu dữ liệu sau thao tác trong kiểm thử hệ thống quản lý kho.
- `ev-v2d-qa-03-06` (work_experience): Dùng Selenium tổ chức page object và tự động hóa regression của kiểm thử hệ thống quản lý kho.
- `ev-v2d-qa-03-07` (projects): Chiều sâu kỹ thuật của kiểm thử hệ thống quản lý kho: Hoàn thành luồng chính và kiểm tra dữ liệu đầu vào phổ biến.
- `ev-v2d-qa-03-08` (projects): Lập luận trong kiểm thử hệ thống quản lý kho: Giải thích quyết định dựa trên yêu cầu và giới hạn thời gian.
- `ev-v2d-qa-03-09` (projects): Bàn giao kiểm thử hệ thống quản lý kho: Bàn giao qua repository và checklist chạy thử.
- `ev-v2d-qa-03-10` (other): Cách trình bày kiểm thử hệ thống quản lý kho: Nêu vai trò, kết quả và một giới hạn kỹ thuật.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-qa-04 — Junior QA Engineer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `75`
- Nhãn nháp: `waitlist`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `qa-testing-foundations` | `satisfied` | Mô tả các bước STLC, xác định rủi ro và ưu tiên kiểm thử cho xác minh luồng thanh toán thử nghiệm. |
| `qa-test-cases` | `satisfied` | Duy trì bộ test theo yêu cầu thay đổi và theo dõi vòng đời lỗi của xác minh luồng thanh toán thử nghiệm. |
| `qa-api-testing` | `satisfied` | Dùng Postman kiểm tra method, status, schema và trường hợp xác thực lỗi cho API của xác minh luồng thanh toán thử nghiệm. |
| `qa-data-check` | `satisfied` | Kiểm tra ràng buộc và bản ghi bất thường bằng SQL khi xác minh xác minh luồng thanh toán thử nghiệm. |
| `qa-automation-foundation` | `satisfied` | Tạo test Cypress có setup dữ liệu, assertion và báo cáo kết quả cho xác minh luồng thanh toán thử nghiệm. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 24/30 | Điểm nháp 24/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `qa-technical-specialization` | 18/25 | Điểm nháp 18/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `qa-role-capability` | 15/20 | Điểm nháp 15/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 11/15 | Điểm nháp 11/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 7/10 | Điểm nháp 7/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-qa-04-01` (education): Chương trình học có bài tổng hợp về xác minh luồng thanh toán thử nghiệm; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-qa-04-02` (projects): Mô tả các bước STLC, xác định rủi ro và ưu tiên kiểm thử cho xác minh luồng thanh toán thử nghiệm.
- `ev-v2d-qa-04-03` (projects): Duy trì bộ test theo yêu cầu thay đổi và theo dõi vòng đời lỗi của xác minh luồng thanh toán thử nghiệm.
- `ev-v2d-qa-04-04` (projects): Dùng Postman kiểm tra method, status, schema và trường hợp xác thực lỗi cho API của xác minh luồng thanh toán thử nghiệm.
- `ev-v2d-qa-04-05` (projects): Kiểm tra ràng buộc và bản ghi bất thường bằng SQL khi xác minh xác minh luồng thanh toán thử nghiệm.
- `ev-v2d-qa-04-06` (projects): Tạo test Cypress có setup dữ liệu, assertion và báo cáo kết quả cho xác minh luồng thanh toán thử nghiệm.
- `ev-v2d-qa-04-07` (projects): Chiều sâu kỹ thuật của xác minh luồng thanh toán thử nghiệm: Có sản phẩm chạy được trong phạm vi học tập hoặc cá nhân.
- `ev-v2d-qa-04-08` (projects): Lập luận trong xác minh luồng thanh toán thử nghiệm: Nêu lý do lựa chọn chính nhưng chưa phân tích sâu trade-off.
- `ev-v2d-qa-04-09` (projects): Bàn giao xác minh luồng thanh toán thử nghiệm: Có source và hướng dẫn cơ bản để tái chạy.
- `ev-v2d-qa-04-10` (other): Cách trình bày xác minh luồng thanh toán thử nghiệm: Thông tin đủ hiểu nhưng thiếu số đo tác động độc lập.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-qa-05 — Junior QA Engineer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `66`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `missing-critical-evidence, low-score-without-explicit-critical-unsatisfied`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `qa-testing-foundations` | `missing` | Không có thông tin trực tiếp |
| `qa-test-cases` | `satisfied` | Viết test case có precondition, dữ liệu, expected result và liên kết defect cho kiểm thử ứng dụng đặt lịch. |
| `qa-api-testing` | `satisfied` | Tạo collection kiểm thử request/response HTTP và biến môi trường cho kiểm thử ứng dụng đặt lịch. |
| `qa-data-check` | `satisfied` | So sánh dữ liệu API với bảng quan hệ và lưu câu truy vấn tái kiểm tra cho kiểm thử ứng dụng đặt lịch. |
| `qa-automation-foundation` | `satisfied` | Viết kịch bản Playwright cho luồng chính, dùng locator ổn định và chạy lại trên CI cho kiểm thử ứng dụng đặt lịch. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 18/30 | Điểm nháp 18/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `qa-technical-specialization` | 17/25 | Điểm nháp 17/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `qa-role-capability` | 14/20 | Điểm nháp 14/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 10/15 | Điểm nháp 10/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 7/10 | Điểm nháp 7/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-qa-05-01` (education): Chương trình học có bài tổng hợp về kiểm thử ứng dụng đặt lịch; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-qa-05-02` (education): Biết thuật ngữ STLC; hồ sơ không có test condition hay cách phân tích yêu cầu.
- `ev-v2d-qa-05-03` (projects): Viết test case có precondition, dữ liệu, expected result và liên kết defect cho kiểm thử ứng dụng đặt lịch.
- `ev-v2d-qa-05-04` (projects): Tạo collection kiểm thử request/response HTTP và biến môi trường cho kiểm thử ứng dụng đặt lịch.
- `ev-v2d-qa-05-05` (projects): So sánh dữ liệu API với bảng quan hệ và lưu câu truy vấn tái kiểm tra cho kiểm thử ứng dụng đặt lịch.
- `ev-v2d-qa-05-06` (projects): Viết kịch bản Playwright cho luồng chính, dùng locator ổn định và chạy lại trên CI cho kiểm thử ứng dụng đặt lịch.
- `ev-v2d-qa-05-07` (projects): Chiều sâu kỹ thuật của kiểm thử ứng dụng đặt lịch: Các phần được mô tả có thao tác thực hành nhưng độ bao phủ chưa đầy đủ.
- `ev-v2d-qa-05-08` (projects): Lập luận trong kiểm thử ứng dụng đặt lịch: Có giải thích cho phần đã làm, không suy diễn phần còn thiếu.
- `ev-v2d-qa-05-09` (projects): Bàn giao kiểm thử ứng dụng đặt lịch: Bàn giao được phạm vi hiện có và ghi rõ giới hạn.
- `ev-v2d-qa-05-10` (other): Cách trình bày kiểm thử ứng dụng đặt lịch: Hồ sơ phân biệt rõ điều đã làm và điều chưa có thông tin.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-qa-06 — Junior QA Engineer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `76`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `conflicting-critical-evidence`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `qa-testing-foundations` | `satisfied` | Áp dụng phân vùng tương đương, giá trị biên và decision table để thiết kế phạm vi test cho kiểm thử cổng đăng ký môn học. |
| `qa-test-cases` | `conflicting` | Thực hiện regression, ghi bug report có bước tái hiện và mức độ ảnh hưởng trong kiểm thử cổng đăng ký môn học.<br>Không có kinh nghiệm quản lý defect cho kiểm thử cổng đăng ký môn học. |
| `qa-api-testing` | `satisfied` | Đối chiếu hợp đồng API, kiểm tra dữ liệu biên và lưu kết quả chạy lại cho kiểm thử cổng đăng ký môn học. |
| `qa-data-check` | `satisfied` | Viết truy vấn SELECT, JOIN và GROUP BY để đối chiếu dữ liệu sau thao tác trong kiểm thử cổng đăng ký môn học. |
| `qa-automation-foundation` | `satisfied` | Dùng Selenium tổ chức page object và tự động hóa regression của kiểm thử cổng đăng ký môn học. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 22/30 | Điểm nháp 22/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `qa-technical-specialization` | 19/25 | Điểm nháp 19/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `qa-role-capability` | 15/20 | Điểm nháp 15/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 12/15 | Điểm nháp 12/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 8/10 | Điểm nháp 8/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-qa-06-01` (education): Chương trình học có bài tổng hợp về kiểm thử cổng đăng ký môn học; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-qa-06-02` (projects): Áp dụng phân vùng tương đương, giá trị biên và decision table để thiết kế phạm vi test cho kiểm thử cổng đăng ký môn học.
- `ev-v2d-qa-06-03` (projects): Thực hiện regression, ghi bug report có bước tái hiện và mức độ ảnh hưởng trong kiểm thử cổng đăng ký môn học.
- `ev-v2d-qa-06-04` (other): Không có kinh nghiệm quản lý defect cho kiểm thử cổng đăng ký môn học.
- `ev-v2d-qa-06-05` (projects): Đối chiếu hợp đồng API, kiểm tra dữ liệu biên và lưu kết quả chạy lại cho kiểm thử cổng đăng ký môn học.
- `ev-v2d-qa-06-06` (projects): Viết truy vấn SELECT, JOIN và GROUP BY để đối chiếu dữ liệu sau thao tác trong kiểm thử cổng đăng ký môn học.
- `ev-v2d-qa-06-07` (projects): Dùng Selenium tổ chức page object và tự động hóa regression của kiểm thử cổng đăng ký môn học.
- `ev-v2d-qa-06-08` (projects): Chiều sâu kỹ thuật của kiểm thử cổng đăng ký môn học: Có đầu ra kỹ thuật nhưng trạng thái một năng lực chưa thể kết luận.
- `ev-v2d-qa-06-09` (projects): Lập luận trong kiểm thử cổng đăng ký môn học: Ghi lại quyết định của dự án nhưng chưa giải thích được mâu thuẫn trong hồ sơ.
- `ev-v2d-qa-06-10` (projects): Bàn giao kiểm thử cổng đăng ký môn học: Có artifact bàn giao và một cảnh báo cần xác minh.
- `ev-v2d-qa-06-11` (other): Cách trình bày kiểm thử cổng đăng ký môn học: Thông tin khá rõ ngoài điểm mâu thuẫn cần human review.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-qa-07 — Junior QA Engineer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `57`
- Nhãn nháp: `reject`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `qa-testing-foundations` | `satisfied` | Mô tả các bước STLC, xác định rủi ro và ưu tiên kiểm thử cho đánh giá chất lượng ứng dụng thương mại. |
| `qa-test-cases` | `satisfied` | Duy trì bộ test theo yêu cầu thay đổi và theo dõi vòng đời lỗi của đánh giá chất lượng ứng dụng thương mại. |
| `qa-api-testing` | `unsatisfied` | Không thể dùng Postman để xác minh endpoint của đánh giá chất lượng ứng dụng thương mại. |
| `qa-data-check` | `satisfied` | Kiểm tra ràng buộc và bản ghi bất thường bằng SQL khi xác minh đánh giá chất lượng ứng dụng thương mại. |
| `qa-automation-foundation` | `satisfied` | Tạo test Cypress có setup dữ liệu, assertion và báo cáo kết quả cho đánh giá chất lượng ứng dụng thương mại. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 16/30 | Điểm nháp 16/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `qa-technical-specialization` | 15/25 | Điểm nháp 15/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `qa-role-capability` | 12/20 | Điểm nháp 12/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 8/15 | Điểm nháp 8/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 6/10 | Điểm nháp 6/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-qa-07-01` (education): Chương trình học có bài tổng hợp về đánh giá chất lượng ứng dụng thương mại; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-qa-07-02` (projects): Mô tả các bước STLC, xác định rủi ro và ưu tiên kiểm thử cho đánh giá chất lượng ứng dụng thương mại.
- `ev-v2d-qa-07-03` (projects): Duy trì bộ test theo yêu cầu thay đổi và theo dõi vòng đời lỗi của đánh giá chất lượng ứng dụng thương mại.
- `ev-v2d-qa-07-04` (other): Không thể dùng Postman để xác minh endpoint của đánh giá chất lượng ứng dụng thương mại.
- `ev-v2d-qa-07-05` (projects): Kiểm tra ràng buộc và bản ghi bất thường bằng SQL khi xác minh đánh giá chất lượng ứng dụng thương mại.
- `ev-v2d-qa-07-06` (projects): Tạo test Cypress có setup dữ liệu, assertion và báo cáo kết quả cho đánh giá chất lượng ứng dụng thương mại.
- `ev-v2d-qa-07-07` (projects): Chiều sâu kỹ thuật của đánh giá chất lượng ứng dụng thương mại: Một phần công việc phụ thuộc vào thành viên khác và không có khả năng thay thế.
- `ev-v2d-qa-07-08` (projects): Lập luận trong đánh giá chất lượng ứng dụng thương mại: Nêu đúng giới hạn hiện tại nhưng chưa có kế hoạch kiểm chứng năng lực thiếu.
- `ev-v2d-qa-07-09` (projects): Bàn giao đánh giá chất lượng ứng dụng thương mại: Chỉ bàn giao được phần việc hẹp.
- `ev-v2d-qa-07-10` (other): Cách trình bày đánh giá chất lượng ứng dụng thương mại: Thông tin phủ định rõ và không bị che bởi danh sách từ khóa.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-qa-08 — Junior QA Engineer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `24`
- Nhãn nháp: `reject`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `qa-testing-foundations` | `unsatisfied` | Chưa biết quy trình hoặc kỹ thuật thiết kế kiểm thử phần mềm. |
| `qa-test-cases` | `unsatisfied` | Không có kinh nghiệm quản lý defect cho kiểm thử hệ thống quản lý kho. |
| `qa-api-testing` | `unsatisfied` | Chưa từng kiểm thử API hoặc đọc request và response HTTP. |
| `qa-data-check` | `unsatisfied` | Không có kỹ năng truy vấn; phần đối chiếu dữ liệu của kiểm thử hệ thống quản lý kho do người khác thực hiện. |
| `qa-automation-foundation` | `unsatisfied` | Chưa từng viết script hoặc test tự động. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 5/30 | Điểm nháp 5/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `qa-technical-specialization` | 5/25 | Điểm nháp 5/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `qa-role-capability` | 6/20 | Điểm nháp 6/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 4/15 | Điểm nháp 4/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 4/10 | Điểm nháp 4/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-qa-08-01` (education): Chương trình học có bài tổng hợp về kiểm thử hệ thống quản lý kho; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-qa-08-02` (other): Chưa biết quy trình hoặc kỹ thuật thiết kế kiểm thử phần mềm.
- `ev-v2d-qa-08-03` (other): Không có kinh nghiệm quản lý defect cho kiểm thử hệ thống quản lý kho.
- `ev-v2d-qa-08-04` (other): Chưa từng kiểm thử API hoặc đọc request và response HTTP.
- `ev-v2d-qa-08-05` (other): Không có kỹ năng truy vấn; phần đối chiếu dữ liệu của kiểm thử hệ thống quản lý kho do người khác thực hiện.
- `ev-v2d-qa-08-06` (other): Chưa từng viết script hoặc test tự động.
- `ev-v2d-qa-08-07` (projects): Chiều sâu kỹ thuật của kiểm thử hệ thống quản lý kho: Không có artifact hoặc tác vụ chuyên môn do ứng viên tự hoàn thành.
- `ev-v2d-qa-08-08` (projects): Lập luận trong kiểm thử hệ thống quản lý kho: Chưa có quyết định kỹ thuật để đánh giá.
- `ev-v2d-qa-08-09` (projects): Bàn giao kiểm thử hệ thống quản lý kho: Không có quy trình bàn giao có thể tái tạo.
- `ev-v2d-qa-08-10` (other): Cách trình bày kiểm thử hệ thống quản lý kho: Giới hạn được phát biểu rõ, không tạo ấn tượng sai về kinh nghiệm.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-qa-09 — Junior QA Engineer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `53`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `missing-critical-evidence, low-score-without-explicit-critical-unsatisfied`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `qa-testing-foundations` | `missing` | Không có thông tin trực tiếp |
| `qa-test-cases` | `satisfied` | Thực hiện regression, ghi bug report có bước tái hiện và mức độ ảnh hưởng trong xác minh luồng thanh toán thử nghiệm. |
| `qa-api-testing` | `missing` | Không có thông tin trực tiếp |
| `qa-data-check` | `satisfied` | Viết truy vấn SELECT, JOIN và GROUP BY để đối chiếu dữ liệu sau thao tác trong xác minh luồng thanh toán thử nghiệm. |
| `qa-automation-foundation` | `missing` | Không có thông tin trực tiếp |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 14/30 | Điểm nháp 14/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `qa-technical-specialization` | 13/25 | Điểm nháp 13/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `qa-role-capability` | 12/20 | Điểm nháp 12/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 8/15 | Điểm nháp 8/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 6/10 | Điểm nháp 6/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-qa-09-01` (education): Chương trình học có bài tổng hợp về xác minh luồng thanh toán thử nghiệm; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-qa-09-02` (education): Biết thuật ngữ STLC; hồ sơ không có test condition hay cách phân tích yêu cầu.
- `ev-v2d-qa-09-03` (projects): Thực hiện regression, ghi bug report có bước tái hiện và mức độ ảnh hưởng trong xác minh luồng thanh toán thử nghiệm.
- `ev-v2d-qa-09-04` (education): Biết API dùng HTTP; hồ sơ không nêu request hay response đã kiểm tra.
- `ev-v2d-qa-09-05` (projects): Viết truy vấn SELECT, JOIN và GROUP BY để đối chiếu dữ liệu sau thao tác trong xác minh luồng thanh toán thử nghiệm.
- `ev-v2d-qa-09-06` (education): Biết khái niệm automation testing; hồ sơ không nêu framework hay test có thể tái chạy.
- `ev-v2d-qa-09-07` (projects): Chiều sâu kỹ thuật của xác minh luồng thanh toán thử nghiệm: Có một số thao tác đơn lẻ nhưng chưa thành luồng hoàn chỉnh.
- `ev-v2d-qa-09-08` (projects): Lập luận trong xác minh luồng thanh toán thử nghiệm: Lý do thực hiện chưa gắn với tiêu chí thành công.
- `ev-v2d-qa-09-09` (projects): Bàn giao xác minh luồng thanh toán thử nghiệm: Artifact rời rạc và chưa có hướng dẫn tái chạy.
- `ev-v2d-qa-09-10` (other): Cách trình bày xác minh luồng thanh toán thử nghiệm: Hồ sơ không khẳng định các năng lực chưa được chứng minh.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-qa-10 — Junior QA Engineer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `68`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `missing-critical-evidence, low-score-without-explicit-critical-unsatisfied, lower-threshold-boundary`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `qa-testing-foundations` | `satisfied` | Mô tả các bước STLC, xác định rủi ro và ưu tiên kiểm thử cho kiểm thử ứng dụng đặt lịch. |
| `qa-test-cases` | `satisfied` | Duy trì bộ test theo yêu cầu thay đổi và theo dõi vòng đời lỗi của kiểm thử ứng dụng đặt lịch. |
| `qa-api-testing` | `satisfied` | Dùng Postman kiểm tra method, status, schema và trường hợp xác thực lỗi cho API của kiểm thử ứng dụng đặt lịch. |
| `qa-data-check` | `satisfied` | Kiểm tra ràng buộc và bản ghi bất thường bằng SQL khi xác minh kiểm thử ứng dụng đặt lịch. |
| `qa-automation-foundation` | `missing` | Không có thông tin trực tiếp |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 20/30 | Điểm nháp 20/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `qa-technical-specialization` | 17/25 | Điểm nháp 17/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `qa-role-capability` | 13/20 | Điểm nháp 13/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 10/15 | Điểm nháp 10/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 8/10 | Điểm nháp 8/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-qa-10-01` (education): Chương trình học có bài tổng hợp về kiểm thử ứng dụng đặt lịch; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-qa-10-02` (projects): Mô tả các bước STLC, xác định rủi ro và ưu tiên kiểm thử cho kiểm thử ứng dụng đặt lịch.
- `ev-v2d-qa-10-03` (projects): Duy trì bộ test theo yêu cầu thay đổi và theo dõi vòng đời lỗi của kiểm thử ứng dụng đặt lịch.
- `ev-v2d-qa-10-04` (projects): Dùng Postman kiểm tra method, status, schema và trường hợp xác thực lỗi cho API của kiểm thử ứng dụng đặt lịch.
- `ev-v2d-qa-10-05` (projects): Kiểm tra ràng buộc và bản ghi bất thường bằng SQL khi xác minh kiểm thử ứng dụng đặt lịch.
- `ev-v2d-qa-10-06` (education): Đã xem demo Selenium nhưng không có kịch bản tự viết hoặc kết quả chạy.
- `ev-v2d-qa-10-07` (projects): Chiều sâu kỹ thuật của kiểm thử ứng dụng đặt lịch: Phần lớn năng lực có ví dụ nhưng chiều sâu chưa đồng đều.
- `ev-v2d-qa-10-08` (projects): Lập luận trong kiểm thử ứng dụng đặt lịch: Có giải thích lựa chọn chính và một giả định chưa kiểm tra.
- `ev-v2d-qa-10-09` (projects): Bàn giao kiểm thử ứng dụng đặt lịch: Có bản chạy thử và ghi chú vận hành cơ bản.
- `ev-v2d-qa-10-10` (other): Cách trình bày kiểm thử ứng dụng đặt lịch: Thông tin tương đối rõ nhưng cần xác minh phần còn thiếu.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-qa-11 — Junior QA Engineer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `85`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `conflicting-critical-evidence, upper-threshold-boundary`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `qa-testing-foundations` | `conflicting` | Phân tích yêu cầu, lập test condition và giải thích kỹ thuật thiết kế test được chọn trong kiểm thử cổng đăng ký môn học.<br>Không thể giải thích cách chọn dữ liệu test cho kiểm thử cổng đăng ký môn học. |
| `qa-test-cases` | `satisfied` | Viết test case có precondition, dữ liệu, expected result và liên kết defect cho kiểm thử cổng đăng ký môn học. |
| `qa-api-testing` | `satisfied` | Tạo collection kiểm thử request/response HTTP và biến môi trường cho kiểm thử cổng đăng ký môn học. |
| `qa-data-check` | `satisfied` | So sánh dữ liệu API với bảng quan hệ và lưu câu truy vấn tái kiểm tra cho kiểm thử cổng đăng ký môn học. |
| `qa-automation-foundation` | `satisfied` | Viết kịch bản Playwright cho luồng chính, dùng locator ổn định và chạy lại trên CI cho kiểm thử cổng đăng ký môn học. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 25/30 | Điểm nháp 25/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `qa-technical-specialization` | 21/25 | Điểm nháp 21/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `qa-role-capability` | 17/20 | Điểm nháp 17/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 13/15 | Điểm nháp 13/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 9/10 | Điểm nháp 9/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-qa-11-01` (education): Chương trình học có bài tổng hợp về kiểm thử cổng đăng ký môn học; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-qa-11-02` (work_experience): Phân tích yêu cầu, lập test condition và giải thích kỹ thuật thiết kế test được chọn trong kiểm thử cổng đăng ký môn học.
- `ev-v2d-qa-11-03` (other): Không thể giải thích cách chọn dữ liệu test cho kiểm thử cổng đăng ký môn học.
- `ev-v2d-qa-11-04` (projects): Viết test case có precondition, dữ liệu, expected result và liên kết defect cho kiểm thử cổng đăng ký môn học.
- `ev-v2d-qa-11-05` (work_experience): Tạo collection kiểm thử request/response HTTP và biến môi trường cho kiểm thử cổng đăng ký môn học.
- `ev-v2d-qa-11-06` (projects): So sánh dữ liệu API với bảng quan hệ và lưu câu truy vấn tái kiểm tra cho kiểm thử cổng đăng ký môn học.
- `ev-v2d-qa-11-07` (work_experience): Viết kịch bản Playwright cho luồng chính, dùng locator ổn định và chạy lại trên CI cho kiểm thử cổng đăng ký môn học.
- `ev-v2d-qa-11-08` (projects): Chiều sâu kỹ thuật của kiểm thử cổng đăng ký môn học: Artifact kỹ thuật khá hoàn chỉnh ngoài điểm cần xác minh.
- `ev-v2d-qa-11-09` (projects): Lập luận trong kiểm thử cổng đăng ký môn học: Nêu trade-off và cách kiểm tra kết quả.
- `ev-v2d-qa-11-10` (projects): Bàn giao kiểm thử cổng đăng ký môn học: Bàn giao có review, test và hướng dẫn sử dụng.
- `ev-v2d-qa-11-11` (other): Cách trình bày kiểm thử cổng đăng ký môn học: Trình bày tốt nhưng chưa giải quyết được phát biểu mâu thuẫn.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-qa-12 — Junior QA Engineer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `79`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `critical-unsatisfied-at-or-above-waitlist-threshold`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `qa-testing-foundations` | `satisfied` | Áp dụng phân vùng tương đương, giá trị biên và decision table để thiết kế phạm vi test cho đánh giá chất lượng ứng dụng thương mại. |
| `qa-test-cases` | `satisfied` | Thực hiện regression, ghi bug report có bước tái hiện và mức độ ảnh hưởng trong đánh giá chất lượng ứng dụng thương mại. |
| `qa-api-testing` | `satisfied` | Đối chiếu hợp đồng API, kiểm tra dữ liệu biên và lưu kết quả chạy lại cho đánh giá chất lượng ứng dụng thương mại. |
| `qa-data-check` | `satisfied` | Viết truy vấn SELECT, JOIN và GROUP BY để đối chiếu dữ liệu sau thao tác trong đánh giá chất lượng ứng dụng thương mại. |
| `qa-automation-foundation` | `unsatisfied` | Chưa từng viết script hoặc test tự động. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 23/30 | Điểm nháp 23/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `qa-technical-specialization` | 20/25 | Điểm nháp 20/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `qa-role-capability` | 16/20 | Điểm nháp 16/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 12/15 | Điểm nháp 12/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 8/10 | Điểm nháp 8/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-qa-12-01` (education): Chương trình học có bài tổng hợp về đánh giá chất lượng ứng dụng thương mại; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-qa-12-02` (projects): Áp dụng phân vùng tương đương, giá trị biên và decision table để thiết kế phạm vi test cho đánh giá chất lượng ứng dụng thương mại.
- `ev-v2d-qa-12-03` (projects): Thực hiện regression, ghi bug report có bước tái hiện và mức độ ảnh hưởng trong đánh giá chất lượng ứng dụng thương mại.
- `ev-v2d-qa-12-04` (projects): Đối chiếu hợp đồng API, kiểm tra dữ liệu biên và lưu kết quả chạy lại cho đánh giá chất lượng ứng dụng thương mại.
- `ev-v2d-qa-12-05` (projects): Viết truy vấn SELECT, JOIN và GROUP BY để đối chiếu dữ liệu sau thao tác trong đánh giá chất lượng ứng dụng thương mại.
- `ev-v2d-qa-12-06` (other): Chưa từng viết script hoặc test tự động.
- `ev-v2d-qa-12-07` (projects): Chiều sâu kỹ thuật của đánh giá chất lượng ứng dụng thương mại: Các năng lực còn lại có thực hành và đầu ra cụ thể.
- `ev-v2d-qa-12-08` (projects): Lập luận trong đánh giá chất lượng ứng dụng thương mại: Nêu cách xử lý trong phạm vi đã biết và giới hạn cần hỗ trợ.
- `ev-v2d-qa-12-09` (projects): Bàn giao đánh giá chất lượng ứng dụng thương mại: Có artifact bàn giao cho phần việc đã hoàn thành.
- `ev-v2d-qa-12-10` (other): Cách trình bày đánh giá chất lượng ứng dụng thương mại: Hồ sơ minh bạch về năng lực chưa đạt.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-qa-13 — Junior QA Engineer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `45`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `missing-critical-evidence, low-score-without-explicit-critical-unsatisfied`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `qa-testing-foundations` | `missing` | Không có thông tin trực tiếp |
| `qa-test-cases` | `missing` | Không có thông tin trực tiếp |
| `qa-api-testing` | `missing` | Không có thông tin trực tiếp |
| `qa-data-check` | `missing` | Không có thông tin trực tiếp |
| `qa-automation-foundation` | `missing` | Không có thông tin trực tiếp |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 12/30 | Điểm nháp 12/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `qa-technical-specialization` | 10/25 | Điểm nháp 10/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `qa-role-capability` | 10/20 | Điểm nháp 10/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 7/15 | Điểm nháp 7/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 6/10 | Điểm nháp 6/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-qa-13-01` (education): Chương trình học có bài tổng hợp về kiểm thử hệ thống quản lý kho; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-qa-13-02` (education): Biết thuật ngữ STLC; hồ sơ không có test condition hay cách phân tích yêu cầu.
- `ev-v2d-qa-13-03` (other): Đã xem mẫu test case nhưng không có trường hợp tự thiết kế.
- `ev-v2d-qa-13-04` (education): Biết API dùng HTTP; hồ sơ không nêu request hay response đã kiểm tra.
- `ev-v2d-qa-13-05` (other): Đã xem bảng dữ liệu nhưng không có câu truy vấn hoặc phép đối chiếu tự thực hiện.
- `ev-v2d-qa-13-06` (education): Biết khái niệm automation testing; hồ sơ không nêu framework hay test có thể tái chạy.
- `ev-v2d-qa-13-07` (projects): Chiều sâu kỹ thuật của kiểm thử hệ thống quản lý kho: Chỉ có nội dung học tập và quan sát, chưa có sản phẩm áp dụng.
- `ev-v2d-qa-13-08` (projects): Lập luận trong kiểm thử hệ thống quản lý kho: Không có quyết định kỹ thuật thuộc trách nhiệm ứng viên.
- `ev-v2d-qa-13-09` (projects): Bàn giao kiểm thử hệ thống quản lý kho: Không có artifact có thể kiểm tra độc lập.
- `ev-v2d-qa-13-10` (other): Cách trình bày kiểm thử hệ thống quản lý kho: Không suy diễn từ tên khóa học hoặc công cụ được nhắc tới.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-qa-14 — Junior QA Engineer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `89`
- Nhãn nháp: `pass`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `qa-testing-foundations` | `satisfied` | Phân tích yêu cầu, lập test condition và giải thích kỹ thuật thiết kế test được chọn trong xác minh luồng thanh toán thử nghiệm. |
| `qa-test-cases` | `satisfied` | Viết test case có precondition, dữ liệu, expected result và liên kết defect cho xác minh luồng thanh toán thử nghiệm. |
| `qa-api-testing` | `satisfied` | Tạo collection kiểm thử request/response HTTP và biến môi trường cho xác minh luồng thanh toán thử nghiệm. |
| `qa-data-check` | `satisfied` | So sánh dữ liệu API với bảng quan hệ và lưu câu truy vấn tái kiểm tra cho xác minh luồng thanh toán thử nghiệm. |
| `qa-automation-foundation` | `satisfied` | Viết kịch bản Playwright cho luồng chính, dùng locator ổn định và chạy lại trên CI cho xác minh luồng thanh toán thử nghiệm. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 27/30 | Điểm nháp 27/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `qa-technical-specialization` | 22/25 | Điểm nháp 22/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `qa-role-capability` | 18/20 | Điểm nháp 18/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 13/15 | Điểm nháp 13/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 9/10 | Điểm nháp 9/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-qa-14-01` (education): Chương trình học có bài tổng hợp về xác minh luồng thanh toán thử nghiệm; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-qa-14-02` (work_experience): Phân tích yêu cầu, lập test condition và giải thích kỹ thuật thiết kế test được chọn trong xác minh luồng thanh toán thử nghiệm.
- `ev-v2d-qa-14-03` (projects): Viết test case có precondition, dữ liệu, expected result và liên kết defect cho xác minh luồng thanh toán thử nghiệm.
- `ev-v2d-qa-14-04` (work_experience): Tạo collection kiểm thử request/response HTTP và biến môi trường cho xác minh luồng thanh toán thử nghiệm.
- `ev-v2d-qa-14-05` (projects): So sánh dữ liệu API với bảng quan hệ và lưu câu truy vấn tái kiểm tra cho xác minh luồng thanh toán thử nghiệm.
- `ev-v2d-qa-14-06` (work_experience): Viết kịch bản Playwright cho luồng chính, dùng locator ổn định và chạy lại trên CI cho xác minh luồng thanh toán thử nghiệm.
- `ev-v2d-qa-14-07` (projects): Chiều sâu kỹ thuật của xác minh luồng thanh toán thử nghiệm: Chứng minh năng lực qua nhiệm vụ tương đương thay vì lặp lại từ khóa JD.
- `ev-v2d-qa-14-08` (projects): Lập luận trong xác minh luồng thanh toán thử nghiệm: Giải thích mục tiêu, cách đo và một giới hạn của giải pháp.
- `ev-v2d-qa-14-09` (projects): Bàn giao xác minh luồng thanh toán thử nghiệm: Có source, kết quả kiểm tra và hướng dẫn tái tạo.
- `ev-v2d-qa-14-10` (other): Cách trình bày xác minh luồng thanh toán thử nghiệm: Thông tin có cấu trúc, nhất quán và truy ngược được tới artifact.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-qa-15 — Junior QA Engineer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `58`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `low-score-without-explicit-critical-unsatisfied`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `qa-testing-foundations` | `satisfied` | Trong một bài tập nhỏ có hướng dẫn từng bước, áp dụng phân vùng tương đương, giá trị biên và decision table để thiết kế phạm vi test cho kiểm thử ứng dụng đặt lịch. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác. |
| `qa-test-cases` | `satisfied` | Trong một bài tập nhỏ có hướng dẫn từng bước, thực hiện regression, ghi bug report có bước tái hiện và mức độ ảnh hưởng trong kiểm thử ứng dụng đặt lịch. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác. |
| `qa-api-testing` | `satisfied` | Trong một bài tập nhỏ có hướng dẫn từng bước, đối chiếu hợp đồng API, kiểm tra dữ liệu biên và lưu kết quả chạy lại cho kiểm thử ứng dụng đặt lịch. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác. |
| `qa-data-check` | `satisfied` | Trong một bài tập nhỏ có hướng dẫn từng bước, viết truy vấn SELECT, JOIN và GROUP BY để đối chiếu dữ liệu sau thao tác trong kiểm thử ứng dụng đặt lịch. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác. |
| `qa-automation-foundation` | `satisfied` | Trong một bài tập nhỏ có hướng dẫn từng bước, dùng Selenium tổ chức page object và tự động hóa regression của kiểm thử ứng dụng đặt lịch. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 18/30 | Điểm nháp 18/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `qa-technical-specialization` | 14/25 | Điểm nháp 14/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `qa-role-capability` | 11/20 | Điểm nháp 11/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 9/15 | Điểm nháp 9/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 6/10 | Điểm nháp 6/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-qa-15-01` (education): Chương trình học có bài tổng hợp về kiểm thử ứng dụng đặt lịch; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-qa-15-02` (projects): Trong một bài tập nhỏ có hướng dẫn từng bước, áp dụng phân vùng tương đương, giá trị biên và decision table để thiết kế phạm vi test cho kiểm thử ứng dụng đặt lịch. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác.
- `ev-v2d-qa-15-03` (projects): Trong một bài tập nhỏ có hướng dẫn từng bước, thực hiện regression, ghi bug report có bước tái hiện và mức độ ảnh hưởng trong kiểm thử ứng dụng đặt lịch. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác.
- `ev-v2d-qa-15-04` (projects): Trong một bài tập nhỏ có hướng dẫn từng bước, đối chiếu hợp đồng API, kiểm tra dữ liệu biên và lưu kết quả chạy lại cho kiểm thử ứng dụng đặt lịch. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác.
- `ev-v2d-qa-15-05` (projects): Trong một bài tập nhỏ có hướng dẫn từng bước, viết truy vấn SELECT, JOIN và GROUP BY để đối chiếu dữ liệu sau thao tác trong kiểm thử ứng dụng đặt lịch. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác.
- `ev-v2d-qa-15-06` (projects): Trong một bài tập nhỏ có hướng dẫn từng bước, dùng Selenium tổ chức page object và tự động hóa regression của kiểm thử ứng dụng đặt lịch. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác.
- `ev-v2d-qa-15-07` (projects): Chiều sâu kỹ thuật của kiểm thử ứng dụng đặt lịch: Mỗi năng lực chỉ xuất hiện trong một bài tập nhỏ có hướng dẫn.
- `ev-v2d-qa-15-08` (projects): Lập luận trong kiểm thử ứng dụng đặt lịch: Quyết định chủ yếu theo mẫu, chưa có so sánh hoặc kiểm chứng độc lập.
- `ev-v2d-qa-15-09` (projects): Bàn giao kiểm thử ứng dụng đặt lịch: Có tệp kết quả nhưng hướng dẫn bàn giao còn tối thiểu.
- `ev-v2d-qa-15-10` (other): Cách trình bày kiểm thử ứng dụng đặt lịch: Nêu đúng phạm vi hạn chế, tổng điểm thấp không đồng nghĩa yêu cầu bị phủ định.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-de-01 — Junior Data Engineer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `93`
- Nhãn nháp: `pass`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `de-python` | `satisfied` | Dùng pandas xây bước biến đổi có kiểm tra kiểu và test đầu vào cho pipeline tổng hợp giao dịch hằng ngày. |
| `de-sql` | `satisfied` | Xây câu lệnh incremental merge và đối chiếu số lượng bản ghi trong pipeline tổng hợp giao dịch hằng ngày. |
| `de-pipeline` | `satisfied` | Xây pipeline ETL có incremental load, checkpoint và xử lý chạy lại cho pipeline tổng hợp giao dịch hằng ngày. |
| `de-data-model-quality` | `satisfied` | Xây data mart dạng star schema, định nghĩa grain và rule chất lượng dữ liệu cho pipeline tổng hợp giao dịch hằng ngày. |
| `de-delivery-workflow` | `satisfied` | Thiết lập CI chạy test, build container và tài liệu khôi phục khi pipeline pipeline tổng hợp giao dịch hằng ngày lỗi. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 29/30 | Điểm nháp 29/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `de-technical-specialization` | 23/25 | Điểm nháp 23/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `de-role-capability` | 18/20 | Điểm nháp 18/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 14/15 | Điểm nháp 14/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 9/10 | Điểm nháp 9/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-de-01-01` (education): Chương trình học có bài tổng hợp về pipeline tổng hợp giao dịch hằng ngày; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-de-01-02` (work_experience): Dùng pandas xây bước biến đổi có kiểm tra kiểu và test đầu vào cho pipeline tổng hợp giao dịch hằng ngày.
- `ev-v2d-de-01-03` (projects): Xây câu lệnh incremental merge và đối chiếu số lượng bản ghi trong pipeline tổng hợp giao dịch hằng ngày.
- `ev-v2d-de-01-04` (work_experience): Xây pipeline ETL có incremental load, checkpoint và xử lý chạy lại cho pipeline tổng hợp giao dịch hằng ngày.
- `ev-v2d-de-01-05` (projects): Xây data mart dạng star schema, định nghĩa grain và rule chất lượng dữ liệu cho pipeline tổng hợp giao dịch hằng ngày.
- `ev-v2d-de-01-06` (work_experience): Thiết lập CI chạy test, build container và tài liệu khôi phục khi pipeline pipeline tổng hợp giao dịch hằng ngày lỗi.
- `ev-v2d-de-01-07` (projects): Chiều sâu kỹ thuật của pipeline tổng hợp giao dịch hằng ngày: Giải pháp bao phủ luồng chính, dữ liệu biên và bước kiểm tra lại.
- `ev-v2d-de-01-08` (projects): Lập luận trong pipeline tổng hợp giao dịch hằng ngày: Nêu rõ lựa chọn kỹ thuật, giả định và một phương án đã loại bỏ.
- `ev-v2d-de-01-09` (projects): Bàn giao pipeline tổng hợp giao dịch hằng ngày: Bàn giao source, hướng dẫn chạy và kết quả kiểm tra cho người dùng nội bộ.
- `ev-v2d-de-01-10` (other): Cách trình bày pipeline tổng hợp giao dịch hằng ngày: Mô tả ngắn gọn phạm vi, kết quả định lượng và giới hạn còn lại.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-de-02 — Junior Data Engineer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `88`
- Nhãn nháp: `pass`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `de-python` | `satisfied` | Tổ chức package Python xử lý dữ liệu, cấu hình tham số và retry có giới hạn trong luồng dữ liệu sự kiện ứng dụng. |
| `de-sql` | `satisfied` | Viết CTE và window function để chuẩn hóa, khử trùng và kiểm tra dữ liệu cho luồng dữ liệu sự kiện ứng dụng. |
| `de-pipeline` | `satisfied` | Thiết kế luồng ELT theo lịch, theo dõi trạng thái và cảnh báo bước thất bại trong luồng dữ liệu sự kiện ứng dụng. |
| `de-data-model-quality` | `satisfied` | Theo dõi data quality, phân loại lỗi nguồn và lập quy trình đối soát trong luồng dữ liệu sự kiện ứng dụng. |
| `de-delivery-workflow` | `satisfied` | Quản lý source bằng Git, chạy pipeline trên Linux, đọc log và đóng gói môi trường bằng Docker cho luồng dữ liệu sự kiện ứng dụng. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 28/30 | Điểm nháp 28/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `de-technical-specialization` | 22/25 | Điểm nháp 22/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `de-role-capability` | 17/20 | Điểm nháp 17/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 13/15 | Điểm nháp 13/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 8/10 | Điểm nháp 8/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-de-02-01` (education): Chương trình học có bài tổng hợp về luồng dữ liệu sự kiện ứng dụng; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-de-02-02` (work_experience): Tổ chức package Python xử lý dữ liệu, cấu hình tham số và retry có giới hạn trong luồng dữ liệu sự kiện ứng dụng.
- `ev-v2d-de-02-03` (projects): Viết CTE và window function để chuẩn hóa, khử trùng và kiểm tra dữ liệu cho luồng dữ liệu sự kiện ứng dụng.
- `ev-v2d-de-02-04` (work_experience): Thiết kế luồng ELT theo lịch, theo dõi trạng thái và cảnh báo bước thất bại trong luồng dữ liệu sự kiện ứng dụng.
- `ev-v2d-de-02-05` (projects): Theo dõi data quality, phân loại lỗi nguồn và lập quy trình đối soát trong luồng dữ liệu sự kiện ứng dụng.
- `ev-v2d-de-02-06` (work_experience): Quản lý source bằng Git, chạy pipeline trên Linux, đọc log và đóng gói môi trường bằng Docker cho luồng dữ liệu sự kiện ứng dụng.
- `ev-v2d-de-02-07` (projects): Chiều sâu kỹ thuật của luồng dữ liệu sự kiện ứng dụng: Thực hiện phần cốt lõi và xử lý ít nhất một lỗi phát sinh.
- `ev-v2d-de-02-08` (projects): Lập luận trong luồng dữ liệu sự kiện ứng dụng: So sánh hai cách triển khai trước khi chọn giải pháp phù hợp phạm vi.
- `ev-v2d-de-02-09` (projects): Bàn giao luồng dữ liệu sự kiện ứng dụng: Có quy trình review và tài liệu để thành viên khác chạy lại.
- `ev-v2d-de-02-10` (other): Cách trình bày luồng dữ liệu sự kiện ứng dụng: Thông tin nhất quán, có đầu ra nhưng phần đo lường chưa hoàn toàn độc lập.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-de-03 — Junior Data Engineer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `82`
- Nhãn nháp: `waitlist`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `de-python` | `satisfied` | Viết Python đọc dữ liệu theo lô, chuẩn hóa schema và ghi log lỗi cho data mart theo dõi vận hành. |
| `de-sql` | `satisfied` | Tối ưu truy vấn sau khi đọc execution plan và bổ sung index cho bảng trung gian của data mart theo dõi vận hành. |
| `de-pipeline` | `satisfied` | Tách extract, transform và load thành các task có dependency rõ ràng cho data mart theo dõi vận hành. |
| `de-data-model-quality` | `satisfied` | Thiết kế fact, dimension và kiểm tra uniqueness, null, referential integrity cho data mart theo dõi vận hành. |
| `de-delivery-workflow` | `satisfied` | Mở pull request, xử lý review và viết hướng dẫn vận hành cùng lệnh kiểm tra cho data mart theo dõi vận hành. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 26/30 | Điểm nháp 26/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `de-technical-specialization` | 20/25 | Điểm nháp 20/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `de-role-capability` | 16/20 | Điểm nháp 16/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 12/15 | Điểm nháp 12/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 8/10 | Điểm nháp 8/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-de-03-01` (education): Chương trình học có bài tổng hợp về data mart theo dõi vận hành; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-de-03-02` (work_experience): Viết Python đọc dữ liệu theo lô, chuẩn hóa schema và ghi log lỗi cho data mart theo dõi vận hành.
- `ev-v2d-de-03-03` (projects): Tối ưu truy vấn sau khi đọc execution plan và bổ sung index cho bảng trung gian của data mart theo dõi vận hành.
- `ev-v2d-de-03-04` (work_experience): Tách extract, transform và load thành các task có dependency rõ ràng cho data mart theo dõi vận hành.
- `ev-v2d-de-03-05` (projects): Thiết kế fact, dimension và kiểm tra uniqueness, null, referential integrity cho data mart theo dõi vận hành.
- `ev-v2d-de-03-06` (work_experience): Mở pull request, xử lý review và viết hướng dẫn vận hành cùng lệnh kiểm tra cho data mart theo dõi vận hành.
- `ev-v2d-de-03-07` (projects): Chiều sâu kỹ thuật của data mart theo dõi vận hành: Hoàn thành luồng chính và kiểm tra dữ liệu đầu vào phổ biến.
- `ev-v2d-de-03-08` (projects): Lập luận trong data mart theo dõi vận hành: Giải thích quyết định dựa trên yêu cầu và giới hạn thời gian.
- `ev-v2d-de-03-09` (projects): Bàn giao data mart theo dõi vận hành: Bàn giao qua repository và checklist chạy thử.
- `ev-v2d-de-03-10` (other): Cách trình bày data mart theo dõi vận hành: Nêu vai trò, kết quả và một giới hạn kỹ thuật.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-de-04 — Junior Data Engineer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `75`
- Nhãn nháp: `waitlist`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `de-python` | `satisfied` | Dùng pandas xây bước biến đổi có kiểm tra kiểu và test đầu vào cho pipeline đồng bộ dữ liệu bán hàng. |
| `de-sql` | `satisfied` | Xây câu lệnh incremental merge và đối chiếu số lượng bản ghi trong pipeline đồng bộ dữ liệu bán hàng. |
| `de-pipeline` | `satisfied` | Xây pipeline ETL có incremental load, checkpoint và xử lý chạy lại cho pipeline đồng bộ dữ liệu bán hàng. |
| `de-data-model-quality` | `satisfied` | Xây data mart dạng star schema, định nghĩa grain và rule chất lượng dữ liệu cho pipeline đồng bộ dữ liệu bán hàng. |
| `de-delivery-workflow` | `satisfied` | Thiết lập CI chạy test, build container và tài liệu khôi phục khi pipeline pipeline đồng bộ dữ liệu bán hàng lỗi. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 24/30 | Điểm nháp 24/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `de-technical-specialization` | 18/25 | Điểm nháp 18/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `de-role-capability` | 15/20 | Điểm nháp 15/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 11/15 | Điểm nháp 11/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 7/10 | Điểm nháp 7/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-de-04-01` (education): Chương trình học có bài tổng hợp về pipeline đồng bộ dữ liệu bán hàng; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-de-04-02` (projects): Dùng pandas xây bước biến đổi có kiểm tra kiểu và test đầu vào cho pipeline đồng bộ dữ liệu bán hàng.
- `ev-v2d-de-04-03` (projects): Xây câu lệnh incremental merge và đối chiếu số lượng bản ghi trong pipeline đồng bộ dữ liệu bán hàng.
- `ev-v2d-de-04-04` (projects): Xây pipeline ETL có incremental load, checkpoint và xử lý chạy lại cho pipeline đồng bộ dữ liệu bán hàng.
- `ev-v2d-de-04-05` (projects): Xây data mart dạng star schema, định nghĩa grain và rule chất lượng dữ liệu cho pipeline đồng bộ dữ liệu bán hàng.
- `ev-v2d-de-04-06` (projects): Thiết lập CI chạy test, build container và tài liệu khôi phục khi pipeline pipeline đồng bộ dữ liệu bán hàng lỗi.
- `ev-v2d-de-04-07` (projects): Chiều sâu kỹ thuật của pipeline đồng bộ dữ liệu bán hàng: Có sản phẩm chạy được trong phạm vi học tập hoặc cá nhân.
- `ev-v2d-de-04-08` (projects): Lập luận trong pipeline đồng bộ dữ liệu bán hàng: Nêu lý do lựa chọn chính nhưng chưa phân tích sâu trade-off.
- `ev-v2d-de-04-09` (projects): Bàn giao pipeline đồng bộ dữ liệu bán hàng: Có source và hướng dẫn cơ bản để tái chạy.
- `ev-v2d-de-04-10` (other): Cách trình bày pipeline đồng bộ dữ liệu bán hàng: Thông tin đủ hiểu nhưng thiếu số đo tác động độc lập.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-de-05 — Junior Data Engineer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `66`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `missing-critical-evidence, low-score-without-explicit-critical-unsatisfied`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `de-python` | `missing` | Không có thông tin trực tiếp |
| `de-sql` | `satisfied` | Viết CTE và window function để chuẩn hóa, khử trùng và kiểm tra dữ liệu cho hệ thống kiểm tra dữ liệu nguồn. |
| `de-pipeline` | `satisfied` | Thiết kế luồng ELT theo lịch, theo dõi trạng thái và cảnh báo bước thất bại trong hệ thống kiểm tra dữ liệu nguồn. |
| `de-data-model-quality` | `satisfied` | Theo dõi data quality, phân loại lỗi nguồn và lập quy trình đối soát trong hệ thống kiểm tra dữ liệu nguồn. |
| `de-delivery-workflow` | `satisfied` | Quản lý source bằng Git, chạy pipeline trên Linux, đọc log và đóng gói môi trường bằng Docker cho hệ thống kiểm tra dữ liệu nguồn. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 18/30 | Điểm nháp 18/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `de-technical-specialization` | 17/25 | Điểm nháp 17/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `de-role-capability` | 14/20 | Điểm nháp 14/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 10/15 | Điểm nháp 10/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 7/10 | Điểm nháp 7/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-de-05-01` (education): Chương trình học có bài tổng hợp về hệ thống kiểm tra dữ liệu nguồn; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-de-05-02` (education): Có chạy notebook mẫu; hồ sơ không xác định mã nguồn do ứng viên viết.
- `ev-v2d-de-05-03` (projects): Viết CTE và window function để chuẩn hóa, khử trùng và kiểm tra dữ liệu cho hệ thống kiểm tra dữ liệu nguồn.
- `ev-v2d-de-05-04` (projects): Thiết kế luồng ELT theo lịch, theo dõi trạng thái và cảnh báo bước thất bại trong hệ thống kiểm tra dữ liệu nguồn.
- `ev-v2d-de-05-05` (projects): Theo dõi data quality, phân loại lỗi nguồn và lập quy trình đối soát trong hệ thống kiểm tra dữ liệu nguồn.
- `ev-v2d-de-05-06` (projects): Quản lý source bằng Git, chạy pipeline trên Linux, đọc log và đóng gói môi trường bằng Docker cho hệ thống kiểm tra dữ liệu nguồn.
- `ev-v2d-de-05-07` (projects): Chiều sâu kỹ thuật của hệ thống kiểm tra dữ liệu nguồn: Các phần được mô tả có thao tác thực hành nhưng độ bao phủ chưa đầy đủ.
- `ev-v2d-de-05-08` (projects): Lập luận trong hệ thống kiểm tra dữ liệu nguồn: Có giải thích cho phần đã làm, không suy diễn phần còn thiếu.
- `ev-v2d-de-05-09` (projects): Bàn giao hệ thống kiểm tra dữ liệu nguồn: Bàn giao được phạm vi hiện có và ghi rõ giới hạn.
- `ev-v2d-de-05-10` (other): Cách trình bày hệ thống kiểm tra dữ liệu nguồn: Hồ sơ phân biệt rõ điều đã làm và điều chưa có thông tin.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-de-06 — Junior Data Engineer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `76`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `conflicting-critical-evidence`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `de-python` | `satisfied` | Viết Python đọc dữ liệu theo lô, chuẩn hóa schema và ghi log lỗi cho pipeline tổng hợp giao dịch hằng ngày. |
| `de-sql` | `conflicting` | Tối ưu truy vấn sau khi đọc execution plan và bổ sung index cho bảng trung gian của pipeline tổng hợp giao dịch hằng ngày.<br>Không thể tự viết truy vấn phục vụ pipeline tổng hợp giao dịch hằng ngày. |
| `de-pipeline` | `satisfied` | Tách extract, transform và load thành các task có dependency rõ ràng cho pipeline tổng hợp giao dịch hằng ngày. |
| `de-data-model-quality` | `satisfied` | Thiết kế fact, dimension và kiểm tra uniqueness, null, referential integrity cho pipeline tổng hợp giao dịch hằng ngày. |
| `de-delivery-workflow` | `satisfied` | Mở pull request, xử lý review và viết hướng dẫn vận hành cùng lệnh kiểm tra cho pipeline tổng hợp giao dịch hằng ngày. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 22/30 | Điểm nháp 22/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `de-technical-specialization` | 19/25 | Điểm nháp 19/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `de-role-capability` | 15/20 | Điểm nháp 15/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 12/15 | Điểm nháp 12/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 8/10 | Điểm nháp 8/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-de-06-01` (education): Chương trình học có bài tổng hợp về pipeline tổng hợp giao dịch hằng ngày; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-de-06-02` (projects): Viết Python đọc dữ liệu theo lô, chuẩn hóa schema và ghi log lỗi cho pipeline tổng hợp giao dịch hằng ngày.
- `ev-v2d-de-06-03` (projects): Tối ưu truy vấn sau khi đọc execution plan và bổ sung index cho bảng trung gian của pipeline tổng hợp giao dịch hằng ngày.
- `ev-v2d-de-06-04` (other): Không thể tự viết truy vấn phục vụ pipeline tổng hợp giao dịch hằng ngày.
- `ev-v2d-de-06-05` (projects): Tách extract, transform và load thành các task có dependency rõ ràng cho pipeline tổng hợp giao dịch hằng ngày.
- `ev-v2d-de-06-06` (projects): Thiết kế fact, dimension và kiểm tra uniqueness, null, referential integrity cho pipeline tổng hợp giao dịch hằng ngày.
- `ev-v2d-de-06-07` (projects): Mở pull request, xử lý review và viết hướng dẫn vận hành cùng lệnh kiểm tra cho pipeline tổng hợp giao dịch hằng ngày.
- `ev-v2d-de-06-08` (projects): Chiều sâu kỹ thuật của pipeline tổng hợp giao dịch hằng ngày: Có đầu ra kỹ thuật nhưng trạng thái một năng lực chưa thể kết luận.
- `ev-v2d-de-06-09` (projects): Lập luận trong pipeline tổng hợp giao dịch hằng ngày: Ghi lại quyết định của dự án nhưng chưa giải thích được mâu thuẫn trong hồ sơ.
- `ev-v2d-de-06-10` (projects): Bàn giao pipeline tổng hợp giao dịch hằng ngày: Có artifact bàn giao và một cảnh báo cần xác minh.
- `ev-v2d-de-06-11` (other): Cách trình bày pipeline tổng hợp giao dịch hằng ngày: Thông tin khá rõ ngoài điểm mâu thuẫn cần human review.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-de-07 — Junior Data Engineer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `57`
- Nhãn nháp: `reject`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `de-python` | `satisfied` | Dùng pandas xây bước biến đổi có kiểm tra kiểu và test đầu vào cho luồng dữ liệu sự kiện ứng dụng. |
| `de-sql` | `satisfied` | Xây câu lệnh incremental merge và đối chiếu số lượng bản ghi trong luồng dữ liệu sự kiện ứng dụng. |
| `de-pipeline` | `unsatisfied` | Không có kinh nghiệm incremental load trong luồng dữ liệu sự kiện ứng dụng. |
| `de-data-model-quality` | `satisfied` | Xây data mart dạng star schema, định nghĩa grain và rule chất lượng dữ liệu cho luồng dữ liệu sự kiện ứng dụng. |
| `de-delivery-workflow` | `satisfied` | Thiết lập CI chạy test, build container và tài liệu khôi phục khi pipeline luồng dữ liệu sự kiện ứng dụng lỗi. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 16/30 | Điểm nháp 16/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `de-technical-specialization` | 15/25 | Điểm nháp 15/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `de-role-capability` | 12/20 | Điểm nháp 12/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 8/15 | Điểm nháp 8/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 6/10 | Điểm nháp 6/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-de-07-01` (education): Chương trình học có bài tổng hợp về luồng dữ liệu sự kiện ứng dụng; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-de-07-02` (projects): Dùng pandas xây bước biến đổi có kiểm tra kiểu và test đầu vào cho luồng dữ liệu sự kiện ứng dụng.
- `ev-v2d-de-07-03` (projects): Xây câu lệnh incremental merge và đối chiếu số lượng bản ghi trong luồng dữ liệu sự kiện ứng dụng.
- `ev-v2d-de-07-04` (other): Không có kinh nghiệm incremental load trong luồng dữ liệu sự kiện ứng dụng.
- `ev-v2d-de-07-05` (projects): Xây data mart dạng star schema, định nghĩa grain và rule chất lượng dữ liệu cho luồng dữ liệu sự kiện ứng dụng.
- `ev-v2d-de-07-06` (projects): Thiết lập CI chạy test, build container và tài liệu khôi phục khi pipeline luồng dữ liệu sự kiện ứng dụng lỗi.
- `ev-v2d-de-07-07` (projects): Chiều sâu kỹ thuật của luồng dữ liệu sự kiện ứng dụng: Một phần công việc phụ thuộc vào thành viên khác và không có khả năng thay thế.
- `ev-v2d-de-07-08` (projects): Lập luận trong luồng dữ liệu sự kiện ứng dụng: Nêu đúng giới hạn hiện tại nhưng chưa có kế hoạch kiểm chứng năng lực thiếu.
- `ev-v2d-de-07-09` (projects): Bàn giao luồng dữ liệu sự kiện ứng dụng: Chỉ bàn giao được phần việc hẹp.
- `ev-v2d-de-07-10` (other): Cách trình bày luồng dữ liệu sự kiện ứng dụng: Thông tin phủ định rõ và không bị che bởi danh sách từ khóa.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-de-08 — Junior Data Engineer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `24`
- Nhãn nháp: `reject`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `de-python` | `unsatisfied` | Chưa từng dùng Python cho xử lý dữ liệu. |
| `de-sql` | `unsatisfied` | Không thể tự viết truy vấn phục vụ data mart theo dõi vận hành. |
| `de-pipeline` | `unsatisfied` | Chưa từng xây pipeline ETL hoặc ELT. |
| `de-data-model-quality` | `unsatisfied` | Không thể giải thích grain, fact hay dimension của data mart theo dõi vận hành. |
| `de-delivery-workflow` | `unsatisfied` | Chưa dùng Git, Linux và chưa thể bàn giao môi trường pipeline. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 5/30 | Điểm nháp 5/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `de-technical-specialization` | 5/25 | Điểm nháp 5/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `de-role-capability` | 6/20 | Điểm nháp 6/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 4/15 | Điểm nháp 4/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 4/10 | Điểm nháp 4/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-de-08-01` (education): Chương trình học có bài tổng hợp về data mart theo dõi vận hành; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-de-08-02` (other): Chưa từng dùng Python cho xử lý dữ liệu.
- `ev-v2d-de-08-03` (other): Không thể tự viết truy vấn phục vụ data mart theo dõi vận hành.
- `ev-v2d-de-08-04` (other): Chưa từng xây pipeline ETL hoặc ELT.
- `ev-v2d-de-08-05` (other): Không thể giải thích grain, fact hay dimension của data mart theo dõi vận hành.
- `ev-v2d-de-08-06` (other): Chưa dùng Git, Linux và chưa thể bàn giao môi trường pipeline.
- `ev-v2d-de-08-07` (projects): Chiều sâu kỹ thuật của data mart theo dõi vận hành: Không có artifact hoặc tác vụ chuyên môn do ứng viên tự hoàn thành.
- `ev-v2d-de-08-08` (projects): Lập luận trong data mart theo dõi vận hành: Chưa có quyết định kỹ thuật để đánh giá.
- `ev-v2d-de-08-09` (projects): Bàn giao data mart theo dõi vận hành: Không có quy trình bàn giao có thể tái tạo.
- `ev-v2d-de-08-10` (other): Cách trình bày data mart theo dõi vận hành: Giới hạn được phát biểu rõ, không tạo ấn tượng sai về kinh nghiệm.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-de-09 — Junior Data Engineer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `53`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `missing-critical-evidence, low-score-without-explicit-critical-unsatisfied`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `de-python` | `missing` | Không có thông tin trực tiếp |
| `de-sql` | `satisfied` | Tối ưu truy vấn sau khi đọc execution plan và bổ sung index cho bảng trung gian của pipeline đồng bộ dữ liệu bán hàng. |
| `de-pipeline` | `missing` | Không có thông tin trực tiếp |
| `de-data-model-quality` | `satisfied` | Thiết kế fact, dimension và kiểm tra uniqueness, null, referential integrity cho pipeline đồng bộ dữ liệu bán hàng. |
| `de-delivery-workflow` | `missing` | Không có thông tin trực tiếp |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 14/30 | Điểm nháp 14/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `de-technical-specialization` | 13/25 | Điểm nháp 13/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `de-role-capability` | 12/20 | Điểm nháp 12/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 8/15 | Điểm nháp 8/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 6/10 | Điểm nháp 6/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-de-09-01` (education): Chương trình học có bài tổng hợp về pipeline đồng bộ dữ liệu bán hàng; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-de-09-02` (education): Có chạy notebook mẫu; hồ sơ không xác định mã nguồn do ứng viên viết.
- `ev-v2d-de-09-03` (projects): Tối ưu truy vấn sau khi đọc execution plan và bổ sung index cho bảng trung gian của pipeline đồng bộ dữ liệu bán hàng.
- `ev-v2d-de-09-04` (education): Biết thuật ngữ ETL; hồ sơ không có luồng dữ liệu có thể chạy lại.
- `ev-v2d-de-09-05` (projects): Thiết kế fact, dimension và kiểm tra uniqueness, null, referential integrity cho pipeline đồng bộ dữ liệu bán hàng.
- `ev-v2d-de-09-06` (education): Đã nhận source có sẵn; hồ sơ không nêu commit, log hay cách tái tạo môi trường.
- `ev-v2d-de-09-07` (projects): Chiều sâu kỹ thuật của pipeline đồng bộ dữ liệu bán hàng: Có một số thao tác đơn lẻ nhưng chưa thành luồng hoàn chỉnh.
- `ev-v2d-de-09-08` (projects): Lập luận trong pipeline đồng bộ dữ liệu bán hàng: Lý do thực hiện chưa gắn với tiêu chí thành công.
- `ev-v2d-de-09-09` (projects): Bàn giao pipeline đồng bộ dữ liệu bán hàng: Artifact rời rạc và chưa có hướng dẫn tái chạy.
- `ev-v2d-de-09-10` (other): Cách trình bày pipeline đồng bộ dữ liệu bán hàng: Hồ sơ không khẳng định các năng lực chưa được chứng minh.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-de-10 — Junior Data Engineer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `68`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `missing-critical-evidence, low-score-without-explicit-critical-unsatisfied, lower-threshold-boundary`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `de-python` | `satisfied` | Dùng pandas xây bước biến đổi có kiểm tra kiểu và test đầu vào cho hệ thống kiểm tra dữ liệu nguồn. |
| `de-sql` | `satisfied` | Xây câu lệnh incremental merge và đối chiếu số lượng bản ghi trong hệ thống kiểm tra dữ liệu nguồn. |
| `de-pipeline` | `satisfied` | Xây pipeline ETL có incremental load, checkpoint và xử lý chạy lại cho hệ thống kiểm tra dữ liệu nguồn. |
| `de-data-model-quality` | `satisfied` | Xây data mart dạng star schema, định nghĩa grain và rule chất lượng dữ liệu cho hệ thống kiểm tra dữ liệu nguồn. |
| `de-delivery-workflow` | `missing` | Không có thông tin trực tiếp |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 20/30 | Điểm nháp 20/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `de-technical-specialization` | 17/25 | Điểm nháp 17/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `de-role-capability` | 13/20 | Điểm nháp 13/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 10/15 | Điểm nháp 10/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 8/10 | Điểm nháp 8/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-de-10-01` (education): Chương trình học có bài tổng hợp về hệ thống kiểm tra dữ liệu nguồn; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-de-10-02` (projects): Dùng pandas xây bước biến đổi có kiểm tra kiểu và test đầu vào cho hệ thống kiểm tra dữ liệu nguồn.
- `ev-v2d-de-10-03` (projects): Xây câu lệnh incremental merge và đối chiếu số lượng bản ghi trong hệ thống kiểm tra dữ liệu nguồn.
- `ev-v2d-de-10-04` (projects): Xây pipeline ETL có incremental load, checkpoint và xử lý chạy lại cho hệ thống kiểm tra dữ liệu nguồn.
- `ev-v2d-de-10-05` (projects): Xây data mart dạng star schema, định nghĩa grain và rule chất lượng dữ liệu cho hệ thống kiểm tra dữ liệu nguồn.
- `ev-v2d-de-10-06` (education): Biết tên Git, Linux và Docker nhưng không có repository, lệnh chạy hoặc cấu hình bàn giao.
- `ev-v2d-de-10-07` (projects): Chiều sâu kỹ thuật của hệ thống kiểm tra dữ liệu nguồn: Phần lớn năng lực có ví dụ nhưng chiều sâu chưa đồng đều.
- `ev-v2d-de-10-08` (projects): Lập luận trong hệ thống kiểm tra dữ liệu nguồn: Có giải thích lựa chọn chính và một giả định chưa kiểm tra.
- `ev-v2d-de-10-09` (projects): Bàn giao hệ thống kiểm tra dữ liệu nguồn: Có bản chạy thử và ghi chú vận hành cơ bản.
- `ev-v2d-de-10-10` (other): Cách trình bày hệ thống kiểm tra dữ liệu nguồn: Thông tin tương đối rõ nhưng cần xác minh phần còn thiếu.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-de-11 — Junior Data Engineer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `85`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `conflicting-critical-evidence, upper-threshold-boundary`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `de-python` | `conflicting` | Tổ chức package Python xử lý dữ liệu, cấu hình tham số và retry có giới hạn trong pipeline tổng hợp giao dịch hằng ngày.<br>Không thể tự viết bước biến đổi Python trong pipeline tổng hợp giao dịch hằng ngày. |
| `de-sql` | `satisfied` | Viết CTE và window function để chuẩn hóa, khử trùng và kiểm tra dữ liệu cho pipeline tổng hợp giao dịch hằng ngày. |
| `de-pipeline` | `satisfied` | Thiết kế luồng ELT theo lịch, theo dõi trạng thái và cảnh báo bước thất bại trong pipeline tổng hợp giao dịch hằng ngày. |
| `de-data-model-quality` | `satisfied` | Theo dõi data quality, phân loại lỗi nguồn và lập quy trình đối soát trong pipeline tổng hợp giao dịch hằng ngày. |
| `de-delivery-workflow` | `satisfied` | Quản lý source bằng Git, chạy pipeline trên Linux, đọc log và đóng gói môi trường bằng Docker cho pipeline tổng hợp giao dịch hằng ngày. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 25/30 | Điểm nháp 25/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `de-technical-specialization` | 21/25 | Điểm nháp 21/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `de-role-capability` | 17/20 | Điểm nháp 17/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 13/15 | Điểm nháp 13/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 9/10 | Điểm nháp 9/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-de-11-01` (education): Chương trình học có bài tổng hợp về pipeline tổng hợp giao dịch hằng ngày; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-de-11-02` (work_experience): Tổ chức package Python xử lý dữ liệu, cấu hình tham số và retry có giới hạn trong pipeline tổng hợp giao dịch hằng ngày.
- `ev-v2d-de-11-03` (other): Không thể tự viết bước biến đổi Python trong pipeline tổng hợp giao dịch hằng ngày.
- `ev-v2d-de-11-04` (projects): Viết CTE và window function để chuẩn hóa, khử trùng và kiểm tra dữ liệu cho pipeline tổng hợp giao dịch hằng ngày.
- `ev-v2d-de-11-05` (work_experience): Thiết kế luồng ELT theo lịch, theo dõi trạng thái và cảnh báo bước thất bại trong pipeline tổng hợp giao dịch hằng ngày.
- `ev-v2d-de-11-06` (projects): Theo dõi data quality, phân loại lỗi nguồn và lập quy trình đối soát trong pipeline tổng hợp giao dịch hằng ngày.
- `ev-v2d-de-11-07` (work_experience): Quản lý source bằng Git, chạy pipeline trên Linux, đọc log và đóng gói môi trường bằng Docker cho pipeline tổng hợp giao dịch hằng ngày.
- `ev-v2d-de-11-08` (projects): Chiều sâu kỹ thuật của pipeline tổng hợp giao dịch hằng ngày: Artifact kỹ thuật khá hoàn chỉnh ngoài điểm cần xác minh.
- `ev-v2d-de-11-09` (projects): Lập luận trong pipeline tổng hợp giao dịch hằng ngày: Nêu trade-off và cách kiểm tra kết quả.
- `ev-v2d-de-11-10` (projects): Bàn giao pipeline tổng hợp giao dịch hằng ngày: Bàn giao có review, test và hướng dẫn sử dụng.
- `ev-v2d-de-11-11` (other): Cách trình bày pipeline tổng hợp giao dịch hằng ngày: Trình bày tốt nhưng chưa giải quyết được phát biểu mâu thuẫn.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-de-12 — Junior Data Engineer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `79`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `critical-unsatisfied-at-or-above-waitlist-threshold`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `de-python` | `satisfied` | Viết Python đọc dữ liệu theo lô, chuẩn hóa schema và ghi log lỗi cho luồng dữ liệu sự kiện ứng dụng. |
| `de-sql` | `satisfied` | Tối ưu truy vấn sau khi đọc execution plan và bổ sung index cho bảng trung gian của luồng dữ liệu sự kiện ứng dụng. |
| `de-pipeline` | `satisfied` | Tách extract, transform và load thành các task có dependency rõ ràng cho luồng dữ liệu sự kiện ứng dụng. |
| `de-data-model-quality` | `satisfied` | Thiết kế fact, dimension và kiểm tra uniqueness, null, referential integrity cho luồng dữ liệu sự kiện ứng dụng. |
| `de-delivery-workflow` | `unsatisfied` | Chưa dùng Git, Linux và chưa thể bàn giao môi trường pipeline. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 23/30 | Điểm nháp 23/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `de-technical-specialization` | 20/25 | Điểm nháp 20/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `de-role-capability` | 16/20 | Điểm nháp 16/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 12/15 | Điểm nháp 12/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 8/10 | Điểm nháp 8/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-de-12-01` (education): Chương trình học có bài tổng hợp về luồng dữ liệu sự kiện ứng dụng; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-de-12-02` (projects): Viết Python đọc dữ liệu theo lô, chuẩn hóa schema và ghi log lỗi cho luồng dữ liệu sự kiện ứng dụng.
- `ev-v2d-de-12-03` (projects): Tối ưu truy vấn sau khi đọc execution plan và bổ sung index cho bảng trung gian của luồng dữ liệu sự kiện ứng dụng.
- `ev-v2d-de-12-04` (projects): Tách extract, transform và load thành các task có dependency rõ ràng cho luồng dữ liệu sự kiện ứng dụng.
- `ev-v2d-de-12-05` (projects): Thiết kế fact, dimension và kiểm tra uniqueness, null, referential integrity cho luồng dữ liệu sự kiện ứng dụng.
- `ev-v2d-de-12-06` (other): Chưa dùng Git, Linux và chưa thể bàn giao môi trường pipeline.
- `ev-v2d-de-12-07` (projects): Chiều sâu kỹ thuật của luồng dữ liệu sự kiện ứng dụng: Các năng lực còn lại có thực hành và đầu ra cụ thể.
- `ev-v2d-de-12-08` (projects): Lập luận trong luồng dữ liệu sự kiện ứng dụng: Nêu cách xử lý trong phạm vi đã biết và giới hạn cần hỗ trợ.
- `ev-v2d-de-12-09` (projects): Bàn giao luồng dữ liệu sự kiện ứng dụng: Có artifact bàn giao cho phần việc đã hoàn thành.
- `ev-v2d-de-12-10` (other): Cách trình bày luồng dữ liệu sự kiện ứng dụng: Hồ sơ minh bạch về năng lực chưa đạt.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-de-13 — Junior Data Engineer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `45`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `missing-critical-evidence, low-score-without-explicit-critical-unsatisfied`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `de-python` | `missing` | Không có thông tin trực tiếp |
| `de-sql` | `missing` | Không có thông tin trực tiếp |
| `de-pipeline` | `missing` | Không có thông tin trực tiếp |
| `de-data-model-quality` | `missing` | Không có thông tin trực tiếp |
| `de-delivery-workflow` | `missing` | Không có thông tin trực tiếp |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 12/30 | Điểm nháp 12/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `de-technical-specialization` | 10/25 | Điểm nháp 10/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `de-role-capability` | 10/20 | Điểm nháp 10/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 7/15 | Điểm nháp 7/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 6/10 | Điểm nháp 6/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-de-13-01` (education): Chương trình học có bài tổng hợp về data mart theo dõi vận hành; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-de-13-02` (education): Có chạy notebook mẫu; hồ sơ không xác định mã nguồn do ứng viên viết.
- `ev-v2d-de-13-03` (other): Đã xem bảng dữ liệu nhưng không có truy vấn hay phép biến đổi SQL được mô tả.
- `ev-v2d-de-13-04` (education): Biết thuật ngữ ETL; hồ sơ không có luồng dữ liệu có thể chạy lại.
- `ev-v2d-de-13-05` (other): Đã đọc tài liệu data warehouse nhưng không có mô hình hoặc rule chất lượng tự xây.
- `ev-v2d-de-13-06` (education): Đã nhận source có sẵn; hồ sơ không nêu commit, log hay cách tái tạo môi trường.
- `ev-v2d-de-13-07` (projects): Chiều sâu kỹ thuật của data mart theo dõi vận hành: Chỉ có nội dung học tập và quan sát, chưa có sản phẩm áp dụng.
- `ev-v2d-de-13-08` (projects): Lập luận trong data mart theo dõi vận hành: Không có quyết định kỹ thuật thuộc trách nhiệm ứng viên.
- `ev-v2d-de-13-09` (projects): Bàn giao data mart theo dõi vận hành: Không có artifact có thể kiểm tra độc lập.
- `ev-v2d-de-13-10` (other): Cách trình bày data mart theo dõi vận hành: Không suy diễn từ tên khóa học hoặc công cụ được nhắc tới.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-de-14 — Junior Data Engineer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `89`
- Nhãn nháp: `pass`
- Lý do Needs Review: `không có`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `de-python` | `satisfied` | Tổ chức package Python xử lý dữ liệu, cấu hình tham số và retry có giới hạn trong pipeline đồng bộ dữ liệu bán hàng. |
| `de-sql` | `satisfied` | Viết CTE và window function để chuẩn hóa, khử trùng và kiểm tra dữ liệu cho pipeline đồng bộ dữ liệu bán hàng. |
| `de-pipeline` | `satisfied` | Thiết kế luồng ELT theo lịch, theo dõi trạng thái và cảnh báo bước thất bại trong pipeline đồng bộ dữ liệu bán hàng. |
| `de-data-model-quality` | `satisfied` | Theo dõi data quality, phân loại lỗi nguồn và lập quy trình đối soát trong pipeline đồng bộ dữ liệu bán hàng. |
| `de-delivery-workflow` | `satisfied` | Quản lý source bằng Git, chạy pipeline trên Linux, đọc log và đóng gói môi trường bằng Docker cho pipeline đồng bộ dữ liệu bán hàng. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 27/30 | Điểm nháp 27/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `de-technical-specialization` | 22/25 | Điểm nháp 22/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `de-role-capability` | 18/20 | Điểm nháp 18/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 13/15 | Điểm nháp 13/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 9/10 | Điểm nháp 9/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-de-14-01` (education): Chương trình học có bài tổng hợp về pipeline đồng bộ dữ liệu bán hàng; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-de-14-02` (work_experience): Tổ chức package Python xử lý dữ liệu, cấu hình tham số và retry có giới hạn trong pipeline đồng bộ dữ liệu bán hàng.
- `ev-v2d-de-14-03` (projects): Viết CTE và window function để chuẩn hóa, khử trùng và kiểm tra dữ liệu cho pipeline đồng bộ dữ liệu bán hàng.
- `ev-v2d-de-14-04` (work_experience): Thiết kế luồng ELT theo lịch, theo dõi trạng thái và cảnh báo bước thất bại trong pipeline đồng bộ dữ liệu bán hàng.
- `ev-v2d-de-14-05` (projects): Theo dõi data quality, phân loại lỗi nguồn và lập quy trình đối soát trong pipeline đồng bộ dữ liệu bán hàng.
- `ev-v2d-de-14-06` (work_experience): Quản lý source bằng Git, chạy pipeline trên Linux, đọc log và đóng gói môi trường bằng Docker cho pipeline đồng bộ dữ liệu bán hàng.
- `ev-v2d-de-14-07` (projects): Chiều sâu kỹ thuật của pipeline đồng bộ dữ liệu bán hàng: Chứng minh năng lực qua nhiệm vụ tương đương thay vì lặp lại từ khóa JD.
- `ev-v2d-de-14-08` (projects): Lập luận trong pipeline đồng bộ dữ liệu bán hàng: Giải thích mục tiêu, cách đo và một giới hạn của giải pháp.
- `ev-v2d-de-14-09` (projects): Bàn giao pipeline đồng bộ dữ liệu bán hàng: Có source, kết quả kiểm tra và hướng dẫn tái tạo.
- `ev-v2d-de-14-10` (other): Cách trình bày pipeline đồng bộ dữ liệu bán hàng: Thông tin có cấu trúc, nhất quán và truy ngược được tới artifact.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 

### v2d-pair-de-15 — Junior Data Engineer - Yêu cầu tiêu chuẩn

- Tổng điểm nháp: `58`
- Nhãn nháp: `needs_review`
- Lý do Needs Review: `low-score-without-explicit-critical-unsatisfied`

Trạng thái yêu cầu bắt buộc:

| Requirement | Trạng thái | Thông tin được liên kết |
| --- | --- | --- |
| `de-python` | `satisfied` | Trong một bài tập nhỏ có hướng dẫn từng bước, viết Python đọc dữ liệu theo lô, chuẩn hóa schema và ghi log lỗi cho hệ thống kiểm tra dữ liệu nguồn. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác. |
| `de-sql` | `satisfied` | Trong một bài tập nhỏ có hướng dẫn từng bước, tối ưu truy vấn sau khi đọc execution plan và bổ sung index cho bảng trung gian của hệ thống kiểm tra dữ liệu nguồn. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác. |
| `de-pipeline` | `satisfied` | Trong một bài tập nhỏ có hướng dẫn từng bước, tách extract, transform và load thành các task có dependency rõ ràng cho hệ thống kiểm tra dữ liệu nguồn. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác. |
| `de-data-model-quality` | `satisfied` | Trong một bài tập nhỏ có hướng dẫn từng bước, thiết kế fact, dimension và kiểm tra uniqueness, null, referential integrity cho hệ thống kiểm tra dữ liệu nguồn. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác. |
| `de-delivery-workflow` | `satisfied` | Trong một bài tập nhỏ có hướng dẫn từng bước, mở pull request, xử lý review và viết hướng dẫn vận hành cùng lệnh kiểm tra cho hệ thống kiểm tra dữ liệu nguồn. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác. |

Năm nhóm điểm:

| Tiêu chí | Điểm | Lý do nháp |
| --- | ---: | --- |
| `mandatory-requirements` | 18/30 | Điểm nháp 18/30 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `de-technical-specialization` | 14/25 | Điểm nháp 14/25 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `de-role-capability` | 11/20 | Điểm nháp 11/20 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `projects-and-impact` | 9/15 | Điểm nháp 9/15 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |
| `communication-and-evidence-quality` | 6/10 | Điểm nháp 6/10 dựa trên độ sâu, vai trò, đầu ra và giới hạn được mô tả; cần human review xác nhận. |

Toàn bộ thông tin hồ sơ:

- `ev-v2d-de-15-01` (education): Chương trình học có bài tổng hợp về hệ thống kiểm tra dữ liệu nguồn; mức đóng góp phải được xác định từ các mục thực hành bên dưới.
- `ev-v2d-de-15-02` (projects): Trong một bài tập nhỏ có hướng dẫn từng bước, viết Python đọc dữ liệu theo lô, chuẩn hóa schema và ghi log lỗi cho hệ thống kiểm tra dữ liệu nguồn. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác.
- `ev-v2d-de-15-03` (projects): Trong một bài tập nhỏ có hướng dẫn từng bước, tối ưu truy vấn sau khi đọc execution plan và bổ sung index cho bảng trung gian của hệ thống kiểm tra dữ liệu nguồn. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác.
- `ev-v2d-de-15-04` (projects): Trong một bài tập nhỏ có hướng dẫn từng bước, tách extract, transform và load thành các task có dependency rõ ràng cho hệ thống kiểm tra dữ liệu nguồn. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác.
- `ev-v2d-de-15-05` (projects): Trong một bài tập nhỏ có hướng dẫn từng bước, thiết kế fact, dimension và kiểm tra uniqueness, null, referential integrity cho hệ thống kiểm tra dữ liệu nguồn. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác.
- `ev-v2d-de-15-06` (projects): Trong một bài tập nhỏ có hướng dẫn từng bước, mở pull request, xử lý review và viết hướng dẫn vận hành cùng lệnh kiểm tra cho hệ thống kiểm tra dữ liệu nguồn. Hồ sơ không cho thấy ứng viên lặp lại việc này ở phạm vi khác.
- `ev-v2d-de-15-07` (projects): Chiều sâu kỹ thuật của hệ thống kiểm tra dữ liệu nguồn: Mỗi năng lực chỉ xuất hiện trong một bài tập nhỏ có hướng dẫn.
- `ev-v2d-de-15-08` (projects): Lập luận trong hệ thống kiểm tra dữ liệu nguồn: Quyết định chủ yếu theo mẫu, chưa có so sánh hoặc kiểm chứng độc lập.
- `ev-v2d-de-15-09` (projects): Bàn giao hệ thống kiểm tra dữ liệu nguồn: Có tệp kết quả nhưng hướng dẫn bàn giao còn tối thiểu.
- `ev-v2d-de-15-10` (other): Cách trình bày hệ thống kiểm tra dữ liệu nguồn: Nêu đúng phạm vi hạn chế, tổng điểm thấp không đồng nghĩa yêu cầu bị phủ định.

Quyết định của người duyệt: `Đồng ý / Cần sửa`

Ghi chú: 
