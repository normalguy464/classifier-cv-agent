# Định hướng triển khai và cải thiện sau Runtime v2

Ngày ghi nhận: 2026-08-08

## Mục đích tài liệu

Tài liệu này lưu lại đánh giá về khả năng triển khai Classifier Agent sau kết quả Frozen Test Runtime v2, các nguyên nhân khiến quality gate chưa đạt, hướng xây dựng Runtime v3 và nguyên tắc đánh giá một LLM mới. Đây là tài liệu định hướng cho một chu kỳ cải tiến trong tương lai, không phải bằng chứng rằng Runtime v3 đã được triển khai hoặc đã đạt mục tiêu.

Các kết quả Runtime v1 và Runtime v2 đã công bố phải được giữ nguyên để phục vụ audit. Không được thay đổi runtime rồi chạy lại trên chính Gold test hiện tại để thay thế kết quả đã thất bại.

## 1. Khả năng triển khai thực tế

### Luồng hoạt động dự kiến của bốn agent

```text
CV thực tế
-> Parser Agent chuẩn hóa CV thành CVProfile
-> Classifier Agent đánh giá mức phù hợp và giải thích
-> HR duyệt hoặc điều chỉnh thành ApprovedDecision
-> Communication Agent gửi thông báo đã được phê duyệt
-> Scheduler Agent hỗ trợ đặt lịch khi được phép
```

Classifier Agent không được trực tiếp đọc PDF hoặc DOCX và không được tự động tạo quyết định tuyển dụng không thể đảo ngược. Communication Agent và Scheduler Agent chỉ được nhận quyết định đã qua human review.

### Nếu triển khai Runtime v2 hiện tại

Frozen Test Runtime v2 ghi nhận:

- Accuracy nhãn: `0.48`.
- Macro-F1: `0.1622`.
- Needs Review recall: `0.96`.
- Review rate: `0.98`, tương ứng 49 trong 50 hồ sơ.
- False Reject: `0`.
- Unsafe Pass: `0`.
- L1 requirement-status accuracy: `0.7958`, với 49 sai lệch trên 240 requirement.
- L2 nằm trong khoảng `38.46-56.37`, trung bình `48.53`.

Nếu đưa nguyên trạng vào thực tế, hệ thống vẫn có thể tổng hợp điểm, requirement status, rationale và thông tin hỗ trợ cho HR. Tuy nhiên, gần như mọi hồ sơ sẽ phải chuyển đến người duyệt. Vì vậy, hệ thống hiện phù hợp làm công cụ hỗ trợ ra quyết định và audit hơn là công cụ tự động sàng lọc.

Tập test được chủ động xây dựng với nhiều trường hợp khó và có 25 trong 50 nhãn chuẩn là Needs Review. Review rate ngoài thực tế có thể khác, nhưng tỷ lệ dự đoán 49 trong 50 vẫn cho thấy routing đang quá nhạy.

Chất lượng Parser là một điều kiện đầu vào quan trọng. Nếu Parser bỏ sót SQL, Python, dự án hoặc câu phủ định, Classifier có thể đánh giá sai dù logic phía sau hoạt động đúng. Cần đo riêng:

- Hiệu năng classifier trên `CVProfile` đã được con người chuẩn hóa.
- Hiệu năng end-to-end trên `CVProfile` do Parser sinh từ CV thực tế.

### Có nên tiếp tục dự án không

Nên tiếp tục nếu mục tiêu là:

- Đồ án, luận văn hoặc demo kiến trúc nhiều agent.
- Công cụ hỗ trợ HR có human review và audit.
- Nền tảng để tiếp tục thu thập dữ liệu và cải thiện mô hình.

Chưa nên tuyên bố hệ thống đủ khả năng tự động Pass hoặc Reject ứng viên trong sản xuất. Kết quả hiện tại không chứng minh production readiness hoặc khả năng khái quát trên CV thực tế.

Không có giải pháp AI tuyển dụng nào bảo đảm loại bỏ hoàn toàn mọi sai sót. Mục tiêu thực tế hơn cho chu kỳ tiếp theo là:

- Accuracy đạt ít nhất `0.70` trên test độc lập.
- Macro-F1 phản ánh khả năng phân biệt nhiều nhãn, không chỉ dự đoán một nhãn chiếm ưu thế.
- Duy trì không có False Reject và Unsafe Pass trên tập đánh giá.
- Giảm review rate xuống mức có ích trong vận hành.
- Xác nhận lại bằng CV thực tế đã được đồng ý sử dụng hoặc ẩn danh không thể đảo ngược.

## 2. Phân tích nguyên nhân và hướng cải thiện

### 2.1. L1 còn sai requirement

L1 đã cải thiện từ `0.6417` ở Runtime v1 lên `0.7958` ở Runtime v2, nhưng vẫn có 49 trong 240 requirement bị sai. Các hướng sai chính gồm:

- `satisfied` bị nhận thành `missing`: 23.
- `missing` bị nhận thành `satisfied`: 16.
- `conflicting` bị nhận thành `satisfied`: 5.
- `unsatisfied` bị nhận thành `missing`: 5.

Đây là nút thắt quan trọng vì prompt v15 yêu cầu L3 giữ nguyên requirement status do L1 cung cấp. Khi L1 sai, L3 không có cơ chế chính thức để sửa lại.

Hướng cải thiện:

1. Tách bước trích xuất thông tin khỏi bước kết luận requirement status.
2. Xây dựng ontology kỹ năng theo từng vai trò, gồm từ đồng nghĩa, framework, ngôn ngữ, quan hệ phụ thuộc và các khái niệm dễ bị suy diễn nhầm.
3. Mỗi requirement cần có tín hiệu xác nhận, tín hiệu phủ định, tín hiệu chỉ mang tính bối cảnh và quy tắc cho trường hợp không đủ thông tin.
4. Bổ sung test cho từng nhóm lỗi trên development data.
5. Không dùng kết quả chi tiết của Gold test hiện tại để tạo rule đặc thù cho chính các case đó.

### 2.2. L2 chưa tạo được khả năng phân biệt

Điểm L2 bị nén vào một khoảng hẹp. CV mạnh, trung bình và yếu có thể nhận điểm gần nhau, khiến L2 khó đóng góp vào việc phân biệt Pass, Waitlist, Needs Review và Reject.

Hướng cải thiện:

- So khớp semantic ở cấp từng requirement thay vì chỉ dựa vào mức tương đồng tổng quát CV-JD.
- Phân biệt việc CV chỉ nhắc tên kỹ năng với việc ứng viên thực sự sử dụng kỹ năng trong dự án hoặc công việc.
- Bổ sung các đặc trưng như số requirement bắt buộc đạt, độ sâu của thông tin hỗ trợ, kinh nghiệm thực hành, mức sở hữu công việc và kết quả dự án.
- Huấn luyện calibrator trên development data lớn và đa dạng hơn.
- Khi đủ dữ liệu, so sánh embedding calibration hiện tại với một mô hình supervised có validation độc lập.

### 2.3. L3 đang bị ràng buộc bởi L1

Việc buộc L3 sao chép requirement status của L1 giúp output nhất quán, nhưng cũng truyền lỗi của L1 vào L3. Runtime v3 có thể thử tách output L3 thành:

- `independent_assessment`: đánh giá độc lập từ CV, JD và rubric.
- `l1_disagreement`: danh sách requirement mà L3 không đồng ý với L1 cùng thông tin hỗ trợ.

Routing sau đó mới quyết định:

- Các tầng đồng thuận và đủ độ tin cậy có thể tiếp tục.
- Mâu thuẫn liên quan requirement bắt buộc phải chuyển Needs Review.
- L3 không được âm thầm ghi đè L1 và cũng không bị buộc lặp lại một trạng thái có thể sai.

Thiết kế này phải được kiểm chứng bằng development data và test mới; đây chưa phải thay đổi đã được phê duyệt.

### 2.4. Routing đang quá nhạy

Trong Runtime v2, routing bị chi phối bởi:

- 34 lần kích hoạt `missing-critical`.
- 32 lần kích hoạt `low-score-without-explicit-unsatisfied`.
- 15 lần kích hoạt large disagreement.

Nhiều điều kiện có thể cùng kích hoạt trên một hồ sơ. Không nên xóa quality gate chỉ để giảm review rate. Cần:

- Phân biệt thiếu thật trong CV với trường hợp Parser hoặc L1 không tìm thấy.
- Gắn độ tin cậy cho từng requirement assessment.
- Chỉ coi disagreement là nghiêm trọng khi liên quan đến requirement quan trọng hoặc có thể làm đổi tuyến xử lý.
- Kiểm tra chính sách theo từng vai trò thay vì giả định một ngưỡng phù hợp cho mọi vai trò.
- Hiệu chỉnh review bands trên development data có phân bố gần với vận hành thực tế.

### 2.5. Dữ liệu chưa đại diện đủ cho thực tế

Tập 50 Gold case phù hợp để kiểm tra có kiểm soát nhưng chưa đủ chứng minh hiệu quả ngoài thị trường. Chu kỳ mới nên hướng tới:

- Khoảng 100-200 development case cho mỗi vai trò nếu nguồn lực cho phép.
- CV được đồng ý sử dụng hoặc ẩn danh không thể đảo ngược.
- JD từ thị trường được chuẩn hóa và có quyền sử dụng phù hợp.
- Phân bố gồm hồ sơ mạnh, trung bình, yếu, thiếu thông tin, mâu thuẫn và trường hợp biên.
- Ít nhất một phần quan trọng được hai người chấm độc lập trước khi thảo luận.
- Đo mức thống nhất giữa những người review.
- Tạo Gold test mới hoàn toàn độc lập sau khi Runtime v3 được khóa.

Tập test khó và tập mô phỏng phân bố vận hành nên được báo cáo riêng. Một tập cân bằng nhiều case khó giúp kiểm tra failure mode nhưng không thể hiện trực tiếp review rate ngoài thực tế.

## 3. Lộ trình Runtime v3 đề xuất

1. Giữ nguyên Runtime v1, Runtime v2 và các final report làm lịch sử thử nghiệm.
2. Xác định lại mục tiêu sản phẩm là decision support có human review.
3. Thu thập và review development data mới, ưu tiên dữ liệu gần thực tế.
4. Tích hợp Parser và đo riêng lỗi parser với lỗi classifier.
5. Sửa L1 theo requirement atom, quan hệ kỹ năng và phạm vi thông tin.
6. Thiết kế lại L2 theo requirement-level matching và kiểm tra khả năng phân biệt điểm.
7. Cho L3 đánh giá độc lập đồng thời báo mâu thuẫn với L1.
8. Hiệu chỉnh aggregate và routing chỉ trên development/validation.
9. Đặt checkpoint offline trước khi gọi API trả phí.
10. Khóa Runtime v3 khi development gate đạt.
11. Tạo một Gold test mới, độc lập và chạy final evaluation đúng một lần.

Không được xóa case khó sau khi xem kết quả chỉ để tăng metric. Những lỗi không ảnh hưởng an toàn có thể được chấp nhận nếu protocol đã quy định trước và tổng thể đạt mục tiêu.

## 4. Đánh giá phương án đổi LLM

### GPT-5.6 Luna có phải bản nâng cấp chắc chắn không

Không. Theo tài liệu OpenAI tại thời điểm 2026-08-08, `gpt-5.6-luna` được tối ưu cho workload nhạy cảm về chi phí và có khối lượng lớn; OpenAI mô tả nó gần với phân hạng nano của các họ GPT-5 trước. Model hỗ trợ Structured Outputs, Chat Completions và Responses API, nhưng vị trí sản phẩm của nó không cho phép kết luận rằng chất lượng sẽ cao hơn `gpt-5.4-mini` trên bài toán tuyển dụng này.

Nguồn tham khảo:

- [GPT-5.6 Luna model](https://developers.openai.com/api/docs/models/gpt-5.6-luna)
- [OpenAI model guidance](https://developers.openai.com/api/docs/guides/latest-model)
- [GPT-5.4 mini model](https://developers.openai.com/api/docs/models/gpt-5.4-mini)

OpenAI định vị `gpt-5.6-sol` cho năng lực cao nhất, `gpt-5.6-terra` để cân bằng năng lực và chi phí, còn `gpt-5.6-luna` cho hiệu quả chi phí và khối lượng lớn. Nếu mục tiêu chính là tăng chất lượng với ngân sách vừa phải, `gpt-5.6-terra` hợp lý hơn để đưa vào danh sách thử nghiệm; vẫn không được coi đây là bảo đảm kết quả tốt hơn.

### Ước tính chi phí Luna trên lần chạy tương đương Runtime v2

Runtime v2 ghi nhận 368,620 input token, trong đó 32,000 cached input token, và 64,711 output token. Dựa trên mức giá Luna hiển thị trong tài liệu OpenAI ngày 2026-08-08, một lần chạy có lượng token tương đương được ước tính khoảng `0.15 USD`, so với `0.5461 USD` đã ước tính cho lần Runtime v2 dùng GPT-5.4 mini.

Đây không phải báo giá hoặc hóa đơn. Số reasoning token, output token, retry và chính sách giá có thể thay đổi khi đổi model.

### Vì sao thay model một mình khó đạt 70%

Trong Frozen Test Runtime v2:

- L1-only accuracy: `0.42`.
- L2-only accuracy: `0.50`.
- L3-only accuracy: `0.44`.
- Full hybrid accuracy: `0.48`.

Đổi LLM chỉ trực tiếp thay L3. L1, L2, aggregate và routing vẫn giữ nguyên các lỗi hiện tại. Đặc biệt, nếu prompt tiếp tục bắt L3 sao chép requirement status của L1 thì model mạnh hơn cũng không thể tự sửa phần đó.

### Protocol thử model mới

1. Không chạy trên Gold test Runtime v2.
2. Chọn trước một validation panel đại diện đủ năm vai trò và các failure mode.
3. Giữ nguyên prompt và các cấu hình khác trong vòng A/B đầu tiên để chỉ đo tác động của model.
4. So sánh output validity, requirement accuracy, unsafe mismatch, label accuracy, Macro-F1, criterion MAE, total-score MAE, stability, review rate, latency và chi phí.
5. Chỉ thử thay prompt trong một experiment version riêng sau khi đã xác định lỗi thuộc về model hoặc prompt.
6. Chỉ chọn model mới khi có cải thiện đo được và đáp ứng các điều kiện an toàn.
7. Khóa model identifier hoặc snapshot cụ thể nếu provider cung cấp để tránh hành vi thay đổi âm thầm.

## 5. Kết luận lưu cho quyết định tương lai

Runtime v2 an toàn theo hai lỗi quyết định nghiêm trọng đã đo là False Reject và Unsafe Pass, nhưng chưa hiệu quả về tự động hóa vì accuracy thấp và review rate gần tuyệt đối. Dự án vẫn đáng tiếp tục dưới định vị hệ thống hỗ trợ HR có human review.

Giải pháp có khả năng tạo cải thiện bền vững là một chu kỳ Runtime v3 có dữ liệu mới, sửa L1, thiết kế lại L2, cho L3 đánh giá độc lập, hiệu chỉnh routing và dùng Gold test mới. Đổi sang GPT-5.6 Luna có thể giảm chi phí nhưng không phải cách khắc phục tận gốc. Một model cân bằng chất lượng và chi phí như GPT-5.6 Terra có thể được thử bằng A/B trên validation data, nhưng quyết định cuối phải dựa trên kết quả đo của chính dự án.
