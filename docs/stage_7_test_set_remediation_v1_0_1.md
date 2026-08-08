# Remediation test set Stage 7 phiên bản 1.0.1

## Nguyên nhân

Trong lúc hai người đánh giá cùng đọc bản `1.0.0`, họ phát hiện một số trạng thái requirement chỉ đúng khi nhìn riêng từng dòng nhưng mâu thuẫn khi đọc toàn bộ CV. Ví dụ FastAPI và pytest là thông tin thực hành trực tiếp bằng Python, còn TypeScript/React không thể đồng thời đi cùng phát biểu phủ định toàn bộ nền tảng JavaScript.

Manifest nguồn `1.0.0` có SHA-256 `1f420a79f94f0499198b69a3f70bec413f6483ce0552d44013e7c219949c0b24`. Bản đó chưa được human review hoàn tất, chưa khóa, chưa chạy classifier và chưa gọi LLM.

## Các case được sửa

| Case | Trạng thái cũ chưa hợp lý | Trạng thái mới | Lý do |
| --- | --- | --- | --- |
| `s7-pair-be-04` | `be-python=missing` trong khi FastAPI và pytest satisfied | `be-python=satisfied`, `be-delivery-workflow=missing` | FastAPI và pytest trực tiếp chứng minh Python; thiếu Git/Docker độc lập với năng lực API. |
| `s7-pair-be-06` | `be-python=unsatisfied` trong khi FastAPI và pytest satisfied | `be-python=satisfied`, `be-delivery-workflow=unsatisfied` | Giữ kịch bản explicit failure bằng một requirement độc lập, không phủ định thông tin Python hiện có. |
| `s7-pair-fe-06` | `fe-web-foundations=unsatisfied` trong khi TypeScript và React satisfied | `fe-web-foundations=satisfied`, `fe-testing-workflow=unsatisfied` | TypeScript/React không nhất quán với phủ định toàn bộ JavaScript foundation; Git/testing workflow có thể không đạt độc lập. |
| `s7-pair-qa-04` | `qa-testing-foundations=missing` trong khi kỹ thuật test-case satisfied | `qa-testing-foundations=satisfied`, `qa-automation-foundation=missing` | Equivalence partitioning, boundary value và decision table trực tiếp chứng minh nền tảng kiểm thử. Evidence CI cũng được bỏ để automation thực sự là missing. |
| `s7-pair-qa-06` | `qa-testing-foundations=unsatisfied` trong khi kỹ thuật test-case satisfied | `qa-testing-foundations=satisfied`, `qa-automation-foundation=unsatisfied` | Manual testing foundation có thể đạt trong khi ứng viên xác nhận chưa từng viết automated test. |

## Những gì không thay đổi

- Mỗi case vẫn giữ nguyên scenario, năm nhóm điểm, tổng điểm, draft label và rationale tổng hợp.
- Phân bố toàn bộ vẫn là 10 Pass, 10 Waitlist, 5 Reject và 25 Needs Review.
- Không thay Job Profile, rubric, runtime, threshold, prompt, model hoặc human label đã khóa ở Stage trước.
- Không chạy L1, L2, L3, baseline, ablation hay provider trong quá trình sửa.

## Phòng ngừa tái diễn

QC Stage 7 bổ sung kiểm tra quan hệ prerequisite giữa các requirement có liên hệ rõ ràng. Regression test bao phủ năm case đã sửa và một case giả lập cố tình tái tạo mâu thuẫn Python–FastAPI. Generator tiếp tục dùng requirement độc lập cho `missing_critical` và `explicit_failure` khi requirement đầu tiên là nền tảng của các requirement còn lại.

Sau remediation, bộ `1.0.1` vẫn là Bronze và phải được hai người đánh giá lại ở chính phiên bản này trước khi có thể tạo Gold ground truth.
