# Hướng dẫn review synthetic-cv-jd-expansion-v1

## Kết quả tạo dữ liệu

Dataset mở rộng đã được tạo theo quy trình chín bước với phạm vi sau:

| Thành phần | Số lượng |
| --- | ---: |
| Vị trí | 5 |
| CVProfile synthetic | 50 |
| Job Profile/JD | 25 |
| Rubric | 25 |
| Cặp CV-JD | 250 |
| Cặp mỗi vị trí | 50 |

Mỗi vị trí có 10 CV persona và 5 biến thể JD. Tích Descartes `10 × 5` tạo 50 cặp cho mỗi vị trí, tổng cộng 250 cặp.

## Phân bố draft label

| Draft label | Số lượng |
| --- | ---: |
| `Pass` | 50 |
| `Waitlist` | 25 |
| `Needs Review` | 155 |
| `Reject` | 20 |

Tỷ lệ `Needs Review` cao vì dataset chủ động tập trung vào case khó: thiếu thông tin, mâu thuẫn, hai vùng điểm biên, JD mơ hồ, chuyển ngành và hard negative. Phân bố này dùng để kiểm tra routing và failure paths, không phải ước lượng tỷ lệ review trong tuyển dụng thực tế.

## Trạng thái xác thực

- Tất cả 250 cặp là synthetic.
- Tất cả 250 cặp thuộc tầng Bronze.
- `human_review_count` của mọi cặp bằng 0.
- Mọi `review.status` là `pending`.
- Không draft label nào được coi là ground truth.
- Dataset chưa có partition và chưa tạo frozen test.
- Dataset không thay đổi split Stage 6 hiện tại.

## Những điểm từ bộ Claude được giữ lại

- Persona theo loại case thay vì sinh CV hoàn toàn ngẫu nhiên.
- Kiểm tra tổng điểm, giới hạn tiêu chí, PII, liên kết nguồn và leakage.
- Phân tầng dữ liệu theo mức độ được con người xác nhận.
- Không đưa case chưa chốt vào Gold.

## Những điểm đã thay đổi để phù hợp repository

- Dùng trực tiếp `CVProfile`, `JobProfile` và `ScoringRubric` Pydantic contract hiện tại.
- Giữ trọng số chính thức `30/25/20/15/10`, không dùng trọng số riêng theo vị trí trong bộ Claude.
- Dùng bốn nhãn `pass`, `waitlist`, `needs_review`, `reject`.
- Thiếu hoặc mâu thuẫn thông tin bắt buộc luôn đi `Needs Review`.
- Điểm dưới 60 chỉ `Reject` khi có `unsatisfied` rõ ràng.
- Không sử dụng override để biến `missing` thành Reject.
- Mọi label do generator tạo đều là draft và chưa finalized.
- Source và test tuân theo type checking, lint và quy tắc không có comment trong code.

## Cách review đề xuất

Không cần đọc 250 cặp theo thứ tự file. Review theo ma trận role–scenario để phát hiện sai hệ thống trước:

1. Với mỗi vị trí, review 10 cặp dùng JD `standard` để xác nhận nội dung persona và rubric.
2. Với mỗi vị trí, chọn một CV `strong`, `moderate`, `explicit_failure` và `hard_negative`, sau đó so sánh trên cả 5 JD.
3. Kiểm tra toàn bộ 25 cặp `ambiguous` có thực sự cần `Needs Review`.
4. Kiểm tra toàn bộ 25 cặp `hard_negative` không được chấm cao chỉ vì từ khóa.
5. Sau khi logic ổn định, thực hiện human review toàn bộ nếu muốn nâng dữ liệu lên Silver hoặc Gold.

Bạn cần duyệt riêng ba vị trí mới trước khi dùng chúng để đánh giá classifier:

- Junior Frontend Developer.
- Junior QA Engineer, hiện lấy Manual QA và kiểm tra dữ liệu làm nền tảng bắt buộc; automation là ưu tiên.
- Junior Data Engineer.

## Các kiểm tra tự động đã thiết kế

- Đủ 50 CV, 25 JD, 25 rubric và 250 cặp.
- Mỗi vị trí có đúng 10 CV, 5 JD và đủ 50 tổ hợp.
- ID và cặp CV-JD duy nhất.
- Contract và evidence reference hợp lệ.
- Rubric và criterion score đúng giới hạn.
- Tổng điểm chính xác.
- Nhãn tuân theo chính sách bảo vệ ứng viên.
- Không có PII, protected field hoặc outcome leakage trong CV.
- Mọi cặp vẫn là Bronze, pending và unassigned.
- Hash và record count trong manifest khớp file.
- QC phải thất bại khi một score hoặc file hash bị sửa.

## Giới hạn còn lại

- 250 cặp chỉ dựa trên 50 CV độc lập; mỗi CV được ghép với 5 JD cùng vai trò.
- Văn phong vẫn là synthetic và sạch hơn CV thực tế.
- Nội dung kỹ thuật và draft score chưa được chuyên gia của ba vị trí mới xác nhận.
- Tập này không thể thay thế real-data validation.
- Không được dùng 250 draft label để tuyên bố accuracy hoặc Macro-F1 thực tế.
- Không nên fine-tune rồi đánh giá trên chính các biến thể cùng candidate nếu chưa có group split chống leakage.

## Lệnh sử dụng

Sinh lại dataset:

```powershell
uv run python -m scripts.generate_synthetic_expansion
```

Chạy test dataset:

```powershell
uv run pytest -q tests/evaluation/test_synthetic_expansion.py
```

Đọc kết quả QC đã sinh:

```powershell
Get-Content -Raw -Encoding utf8 data/synthetic_expansion/v1/quality_report.json
```

