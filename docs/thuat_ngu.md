# Bảng thuật ngữ của dự án

## Thuật ngữ bổ sung sau Stage 8

| Thuật ngữ gốc | Cách diễn đạt ưu tiên | Nghĩa trong dự án |
| --- | --- | --- |
| L3 self-reported confidence | Mức tự tin do L3 tự khai báo | Giá trị `0-1` do LLM trả về cùng output L3. Giá trị này chỉ được kiểm tra đúng phạm vi, chưa được hiệu chỉnh thành xác suất dự đoán đúng, không phải accuracy và không tham gia routing hiện tại. Ở adapter offline, cùng trường này biểu diễn độ phủ thông tin nên không được so sánh trực tiếp với LLM thật. |
| Locally hosted LLM | LLM được tự vận hành trên hạ tầng cục bộ | Mô hình sinh ngôn ngữ có weights và inference server chạy trên máy hoặc máy chủ do dự án kiểm soát. Classifier hiện chưa có thành phần này; L2 embedding chạy local, còn L3 thật gọi API bên ngoài. |
| Model A/B evaluation | Đánh giá đối chứng hai model | Chạy hai model với cùng dữ liệu development/validation, prompt, schema và metric đã định trước để đo chất lượng, chi phí và độ ổn định. Không được kết luận model mới tốt hơn chỉ từ mô tả sản phẩm hoặc một demo case. |

## Thuật ngữ bổ sung khi khóa Runtime v2 và tạo test set mới

| Thuật ngữ gốc | Cách diễn đạt ưu tiên | Nghĩa trong dự án |
| --- | --- | --- |
| Frozen runtime | Runtime đã khóa | Bộ rule, model, prompt, trọng số và ngưỡng đã được duyệt; không được sửa theo output của test set đang dùng để đánh giá cuối. |
| Post-hoc case removal | Xóa case sau khi xem kết quả | Loại một hồ sơ khỏi test set vì classifier dự đoán sai; thao tác này làm metric tăng giả tạo và bị cấm trong Stage 7. |
| Non-safety mismatch | Sai lệch không trực tiếp gây quyết định nguy hiểm | Một số ít dự đoán khác human label nhưng không tạo false Reject, unsafe Pass hay unsafe requirement mismatch; có thể được chấp nhận như hạn chế nếu toàn bộ quality gate vẫn đạt. |
| Blocking safety error | Lỗi an toàn chặn quality gate | False Reject, unsafe Pass hoặc sai trạng thái requirement theo hướng nguy hiểm; không được bỏ qua chỉ vì accuracy tổng thể trên 70%. |
| API-free preflight | Kiểm tra tiền chạy không dùng API | Xác minh runtime, Gold dataset, protocol, hash, QC và request cap trước final evaluation mà không đọc API key hoặc gửi request tới provider. |
| Immutable Gold copy | Bản Gold bất biến | Bản dữ liệu đã human review và khóa hash; nếu sửa nội dung thì phải tạo version khác, không được ghi đè bản dùng cho final evaluation. |
| Irrecoverable gate failure | Quality gate đã chắc chắn không đạt | Một điều kiện khóa đã thất bại trên toàn bộ frozen test và không thể được provider còn lại sửa, chẳng hạn L1 authoritative requirement accuracy dưới ngưỡng; kết quả phải được báo cáo chứ không được tuning bằng test. |
| Conservative over-routing | Chuyển review quá mức theo hướng bảo thủ | Hệ thống tránh Reject hoặc Pass nguy hiểm nhưng đẩy gần như mọi case sang Needs Review, làm giảm khả năng tự động hóa và accuracy. Runtime v2 có review rate 98% trên frozen test. |

## Thuật ngữ bổ sung cho Runtime v2 candidate 3.0.0

| Thuật ngữ gốc | Cách diễn đạt ưu tiên | Nghĩa trong dự án |
| --- | --- | --- |
| Authoritative requirement status | Trạng thái yêu cầu bắt buộc làm nguồn chuẩn | Kết quả L1 đã kiểm tra được chuyển nguyên trạng vào L3; LLM không được tự đổi `missing`, `unsatisfied`, `conflicting` hoặc `satisfied`. |
| Score mapping version | Phiên bản quy tắc ánh xạ điểm | Phiên bản code chuyển qualitative level và trạng thái thông tin thành điểm; mapping v3 tránh phạt toàn bộ Mandatory quá mạnh khi chỉ một phần requirement không đạt. |
| Double penalty | Phạt trùng | Cùng một thiếu sót vừa kích hoạt tuyến `Needs Review` vừa làm tụt điểm quá mức; mapping v3 loại bỏ phần phạt trùng nhưng vẫn giữ tuyến an toàn. |
| Offline re-score | Chấm lại bằng quy tắc cục bộ | Tính lại điểm từ qualitative output đã lưu khi chỉ mapping deterministic thay đổi; không gửi lại request và không phát sinh token LLM mới. |
| Diagnostic-only validation | Validation chỉ dùng để chẩn đoán | Kết quả đã được xem và có ảnh hưởng đến tuning nên không còn đủ độc lập để xác nhận cấu hình cuối hoặc báo cáo như frozen test. |
| Candidate-protective tie-break | Quy tắc phá hòa ưu tiên bảo vệ ứng viên | Khi nhiều candidate có metric bằng nhau, chọn phương án đưa case sát ngưỡng sang review sớm hơn nếu không tạo false Reject hoặc unsafe Pass. |

## Thuật ngữ bổ sung ở Stage 7

| Từ gốc | Cách hiểu phù hợp trong dự án | Ý nghĩa cụ thể |
| --- | --- | --- |
| Test protocol | Quy trình kiểm thử đã định trước | Tài liệu khóa dữ liệu, metric, ngưỡng, số lần gọi API và điều kiện dừng trước khi xem output test. |
| Label leakage | Rò rỉ nhãn | Nhãn hoặc tên kịch bản xuất hiện trực tiếp hay gián tiếp trong input, khiến classifier đoán đáp án thay vì đánh giá năng lực. |
| Dataset lock | Khóa bộ dữ liệu | Ghi hash và cấm sửa test set sau khi ground truth được duyệt, trừ khi tạo version mới và hủy tư cách so sánh của version cũ. |
| Gold ground truth | Nhãn chuẩn mức Gold | Nhãn đã được ít nhất hai người đánh giá độc lập, xử lý bất đồng và vượt QC; không phải nhãn chỉ do AI tạo. |
| Precondition | Điều kiện tiên quyết | Điều kiện phải đạt trước khi được phép chạy final evaluation, chẳng hạn đủ reviewer, không leakage và classifier chưa nhìn thấy test set. |
| Bootstrap confidence interval | Khoảng bất định bằng lấy mẫu lặp | Cách lấy mẫu lại test set nhiều lần với seed cố định để cho thấy metric có thể dao động bao nhiêu do cỡ mẫu hữu hạn. |
| Ablation | Thử nghiệm loại bỏ thành phần | So sánh L1, L2, L3 riêng lẻ và các tổ hợp để đo đóng góp thực tế của từng tầng. |
| Hard cap | Giới hạn tuyệt đối | Số HTTP request tối đa mà runner không được vượt qua dù có retry hay lỗi provider. |
| Cross-requirement contradiction | Mâu thuẫn giữa các yêu cầu liên quan | Một requirement bị đánh dấu missing hoặc unsatisfied nhưng thông tin của requirement khác lại trực tiếp chứng minh nó, ví dụ FastAPI/pytest chứng minh Python. |
| Two-person consensus panel | Hội đồng đồng thuận hai người | Hai người cùng thảo luận và thống nhất một quyết định review cuối; khác với hai lượt chấm độc lập rồi mới so sánh. Stage 7 v1 dùng hình thức này theo xác nhận của người dùng. |
| Final-performance report | Báo cáo hiệu năng cuối trên test đã khóa | Kết quả chỉ được sinh sau khi runtime và ground truth đã khóa; dù đạt hay không đạt, không được dùng output để chỉnh chính runtime đó. |
| Generalization failure | Khả năng khái quát hóa chưa đạt | Cấu hình hoạt động tốt trên development nhưng không giữ được chất lượng trên cách diễn đạt hoặc case mới trong frozen test. |
| Routing over-trigger | Điều kiện chuyển review bị kích hoạt quá mức | Nhiều rule an toàn cùng đẩy phần lớn hoặc toàn bộ case sang `Needs Review`, làm giảm khả năng tự động hóa dù tránh được quyết định nguy hiểm. |

## Mục đích

Đây là bảng cách hiểu theo ngữ cảnh dự án, không phải bản dịch từng từ. Cột thứ hai ưu tiên cách gọi tự nhiên đối với quy trình tuyển dụng; cột thứ ba giải thích chính xác thuật ngữ được hệ thống dùng để làm gì. Tên lớp, trường JSON, giá trị mã và lệnh vẫn giữ nguyên dạng gốc khi cần đối chiếu với source code.

Trong tài liệu dành cho người dùng, `evidence` nên được gọi là “thông tin làm căn cứ đánh giá” hoặc ngắn hơn là “căn cứ từ CV”. Nó không mặc nhiên là sự thật đã được xác minh; đó có thể chỉ là thông tin ứng viên trình bày trong CV.

| Thuật ngữ gốc | Cách gọi phù hợp trong dự án | Nghĩa trong dự án |
| --- | --- | --- |
| Agent | Thành phần xử lý tự động | Một phần của hệ thống đảm nhiệm một công việc và quy trình riêng. Tên như Classifier Agent vẫn được giữ nguyên khi nói về kiến trúc. |
| CV | Hồ sơ ứng tuyển | Tài liệu mô tả kỹ năng, kinh nghiệm, học vấn và dự án của ứng viên. |
| HR | Người phụ trách tuyển dụng | Người dùng kiểm tra, chấp thuận hoặc điều chỉnh kết quả do hệ thống đề xuất. |
| API | Giao diện lập trình ứng dụng | Cách các ứng dụng trao đổi yêu cầu và dữ liệu có cấu trúc. |
| REST API | API theo phong cách REST | API dùng tài nguyên, phương thức HTTP và mã trạng thái theo quy ước REST. |
| Backend | Phần xử lý phía máy chủ | Mã xử lý nghiệp vụ, API, quy trình phân loại và lưu trữ dữ liệu. |
| Frontend | Giao diện sử dụng | Phần màn hình mà người phụ trách tuyển dụng dùng để xem và duyệt kết quả. |
| L1/L2/L3 | Ba tầng đánh giá | L1 dùng quy tắc xác định, L2 đối sánh mức độ liên quan và L3 dùng LLM đánh giá dựa trên thông tin trong hồ sơ. |
| LLM | Mô hình ngôn ngữ lớn | Mô hình dùng ở L3 để lập luận theo bộ tiêu chí và trả đầu ra có cấu trúc. |
| OCR | Nhận dạng ký tự quang học | Kỹ thuật đọc chữ từ ảnh hoặc CV quét; thuộc Parser Agent, không thuộc Classifier Agent. |
| JSON | Định dạng dữ liệu JSON | Định dạng trao đổi các cấu trúc dữ liệu chuẩn qua API hoặc tệp mẫu. |
| YAML | Định dạng cấu hình YAML | Định dạng lưu hồ sơ vị trí, bộ tiêu chí và cấu hình version hóa. |
| Classifier Agent | Thành phần đánh giá độ phù hợp | Phần hệ thống so sánh hồ sơ ứng viên với yêu cầu vị trí và đề xuất kết quả sàng lọc. |
| Parser Agent | Thành phần đọc và chuẩn hóa CV | Phần hệ thống đọc PDF, DOCX hoặc ảnh rồi chuyển nội dung thành `CVProfile`. |
| Contract | Chuẩn dữ liệu trao đổi | Cấu trúc dữ liệu có phiên bản mà các thành phần phải cùng tuân theo khi gửi và nhận dữ liệu. Tên kỹ thuật “data contract” vẫn được giữ trong code. |
| Schema | Khuôn dữ liệu bắt buộc | Định nghĩa trường nào được phép có, kiểu dữ liệu và điều kiện hợp lệ của dữ liệu trao đổi. |
| `CVProfile` | Hồ sơ ứng viên đã chuẩn hóa | Thông tin nghề nghiệp trong CV đã được Parser Agent hoặc nguồn thượng nguồn đưa về cấu trúc mà Classifier Agent hiểu được. |
| `JobProfile` | Hồ sơ vị trí tuyển dụng | Mô tả trách nhiệm, yêu cầu bắt buộc và yêu cầu ưu tiên của một vị trí. |
| `ScoringRubric` | Khung tiêu chí và phân bổ điểm | Quy định hệ thống đánh giá những nhóm năng lực nào, mỗi nhóm tối đa bao nhiêu điểm và căn cứ nào được chấp nhận. |
| `ClassificationConfig` | Cấu hình phân loại | Trọng số L1/L2/L3, ngưỡng quyết định, chính sách xem xét và metadata mô hình. |
| `Evidence` | Thông tin làm căn cứ đánh giá | Một đoạn thông tin cụ thể lấy từ kỹ năng, dự án, kinh nghiệm, học vấn hoặc phần khác của CV, có nguồn và vị trí để người duyệt kiểm tra lại. Nó chưa chắc đã được xác minh độc lập. |
| `ClassificationResult` | Kết quả đánh giá sơ bộ | Kết quả do Classifier Agent đề xuất, gồm điểm, kết quả phân loại, căn cứ từ CV và cảnh báo; chưa được dùng cho bước sau khi người phụ trách chưa xác nhận. |
| `ApprovedDecision` | Kết quả đã được người phụ trách xác nhận | Kết quả cuối của bước phân loại sau khi người phụ trách chấp thuận hoặc điều chỉnh đề xuất. |
| Evidence status | Kết quả đối chiếu yêu cầu | Cho biết thông tin trong CV đủ để xác nhận yêu cầu là đáp ứng, không đáp ứng, chưa xác định được hay đang mâu thuẫn. |
| `satisfied` | Đã xác nhận đáp ứng | Thông tin trong CV đủ cụ thể để xác nhận yêu cầu tuyển dụng được đáp ứng. |
| `unsatisfied` | Đã xác nhận chưa đáp ứng | CV có thông tin rõ cho thấy yêu cầu tuyển dụng chưa được đáp ứng; không được suy ra chỉ vì CV không nhắc tới. |
| `missing` | Chưa đủ thông tin để xác định | CV không cung cấp đủ thông tin để kết luận đáp ứng hay chưa đáp ứng. |
| `conflicting` | Thông tin không nhất quán | Hai hoặc nhiều phần trong CV dẫn tới kết luận trái nhau về cùng một yêu cầu. |
| `Pass` | Đề xuất qua vòng đánh giá hồ sơ | Điểm đủ cao, không có điều kiện bắt buộc kiểm tra thủ công và chưa phải quyết định tuyển dụng cuối cùng. |
| `Waitlist` | Đề xuất giữ lại để cân nhắc | Thông tin đủ rõ để đánh giá, không có điều kiện bắt buộc kiểm tra thủ công, nhưng mức phù hợp thấp hơn nhóm `Pass`. |
| `Reject` | Đề xuất không qua vòng đánh giá hồ sơ | Chỉ được đề xuất khi điểm thấp và có thông tin rõ cho thấy ít nhất một yêu cầu bắt buộc chưa đáp ứng; đây không phải kết luận về giá trị của ứng viên. |
| `Needs Review` | Chưa thể kết luận, cần kiểm tra thủ công | Hệ thống chưa được phép tự chốt vì thông tin thiếu hoặc mâu thuẫn, hệ thống chấm lỗi hoặc bất đồng, hay điểm nằm sát ngưỡng. Sau khi kiểm tra có thể chuyển thành `Pass`, `Waitlist` hoặc `Reject`. |
| Override | Điều chỉnh kết quả đề xuất | Người phụ trách thay đổi kết quả do hệ thống đề xuất và phải ghi lý do. |
| Downstream agent | Thành phần xử lý ở bước sau | Thành phần nhận kết quả đã được duyệt để thực hiện công việc tiếp theo, chẳng hạn gửi thông báo. |
| Upstream | Nguồn cung cấp dữ liệu đầu vào | Thành phần tạo dữ liệu cho một bước, chẳng hạn Parser Agent cung cấp `CVProfile`. |
| Validation | Kiểm tra dữ liệu theo quy tắc | Kiểm tra dữ liệu có đúng kiểu, phạm vi và quy tắc nghiệp vụ hay không. |
| Field | Mục dữ liệu | Một thuộc tính được khai báo trong chuẩn dữ liệu hoặc cấu hình. |
| Quality gate | Điều kiện bắt buộc kiểm tra thủ công | Quy tắc tạm dừng việc tự phân loại và chuyển case sang `Needs Review`. |
| Final score | Điểm cuối sau khi tổng hợp | Điểm sau khi kết hợp L1, L2 và L3 theo trọng số cấu hình. |
| Provider | Dịch vụ mô hình bên ngoài | Dịch vụ cung cấp LLM hoặc khả năng bên ngoài cho hệ thống. |
| Prompt | Nội dung hướng dẫn mô hình | Nội dung có phiên bản hướng dẫn LLM đánh giá theo rubric và chỉ dùng thông tin được cung cấp từ hồ sơ. |
| Structured output | Kết quả đúng khuôn dữ liệu | Kết quả tuân theo schema để Pydantic có thể kiểm tra tự động. |
| Embedding | Véc-tơ biểu diễn ý nghĩa văn bản | Dạng số hóa của văn bản dùng để so sánh mức độ liên quan về ý nghĩa. |
| Semantic matching | So khớp theo ý nghĩa | So sánh nội dung có liên quan về nghĩa hay không, thay vì chỉ tìm từ giống nhau. |
| Deterministic | Cho kết quả lặp lại | Cùng đầu vào và cấu hình luôn tạo cùng kết quả. |
| Fake | Bộ mô phỏng dùng khi kiểm thử | Thành phần thay thế provider thật, cho kết quả ổn định khi test hoặc demo offline. |
| Dependency | Thư viện hoặc phần mềm dự án cần | Thành phần phải có để project chạy hoặc kiểm thử. |
| Package | Gói phần mềm | Đơn vị thư viện được trình quản lý dependency cài vào môi trường dự án. |
| Manifest | Tệp khai báo | Tệp như `pyproject.toml` hoặc `package.json` mô tả dự án và dependency. |
| Lockfile | Tệp khóa phiên bản | Tệp như `uv.lock` hoặc `pnpm-lock.yaml` cố định chính xác các dependency đã được giải quyết. |
| Runtime | Môi trường thực thi | Môi trường chạy ứng dụng cùng interpreter và dependency tương ứng. |
| Scaffold | Khởi tạo bộ khung dự án | Tạo các tệp, thư mục, điểm khởi chạy và cấu hình tối thiểu để một phần hệ thống có thể phát triển hoặc chạy. |
| Workflow | Quy trình xử lý | Chuỗi bước và trạng thái phối hợp hoạt động của hệ thống. |
| Unit test | Kiểm thử đơn vị | Kiểm tra một hàm hoặc module nhỏ trong điều kiện cô lập. |
| Contract test | Kiểm thử chuẩn dữ liệu trao đổi | Kiểm tra schema, field, version, giới hạn và tính tương thích của dữ liệu giữa các thành phần. |
| Integration test | Kiểm thử tích hợp | Kiểm tra nhiều thành phần hoạt động cùng nhau, chẳng hạn API và repository. |
| Regression test | Kiểm thử hồi quy | Bảo đảm hành vi đã đúng trước đó không bị hỏng sau thay đổi mới. |
| Migration | Cập nhật có kiểm soát | Thay đổi có phiên bản để đưa cấu trúc dữ liệu hoặc cơ sở dữ liệu từ phiên bản cũ sang phiên bản mới. |
| Baseline | Mốc so sánh | Cách tiếp cận đơn giản dùng làm chuẩn để biết phương pháp đề xuất có thực sự tốt hơn hay không. |
| Ablation | Thử nghiệm đo đóng góp từng thành phần | Lần lượt bỏ từng phần của phương pháp để xem phần đó đóng góp bao nhiêu. |
| Pilot dataset | Bộ hồ sơ thử nghiệm ban đầu | Tập CV tổng hợp nhỏ dùng để kiểm tra cấu trúc dữ liệu, rubric và quy trình xác nhận kết quả trước khi phát triển quy mô lớn hơn. |
| Frozen test set | Bộ dữ liệu kiểm thử được cố định trước | Dữ liệu cuối chỉ dùng để báo cáo kết quả, không được dùng để tiếp tục điều chỉnh hệ thống. |
| Metadata | Dữ liệu mô tả | Thông tin về phiên bản, mô hình, prompt hoặc nguồn của một lần chạy. |
| Entry point | Điểm bắt đầu chạy ứng dụng | Module hoặc lệnh dùng để khởi động ứng dụng. |
| Secret | Thông tin bí mật | API key, mật khẩu, token hoặc thông tin xác thực không được đưa vào kho mã nguồn. |

## Thuật ngữ bổ sung tại Stage 3

| Thuật ngữ gốc | Cách diễn đạt ưu tiên | Nghĩa trong dự án |
| --- | --- | --- |
| Annotation | Phiếu đánh giá tham chiếu | Bản ghi kết quả đối chiếu yêu cầu, điểm theo nhóm, kết quả đề xuất và lý do mà người phụ trách cần xác nhận cho một CV. |
| Annotator | Người lập phiếu đánh giá | Người đọc thông tin trong hồ sơ và đề xuất hoặc xác nhận phiếu đánh giá. Kết quả do AI tự tạo không thay thế được người duyệt. |
| Human review | Người phụ trách kiểm tra và xác nhận | Bước một người có trách nhiệm đọc đề xuất, kiểm tra căn cứ, chấp thuận hoặc sửa và ghi lại quyết định. |
| Ground truth | Kết quả chuẩn đã được người duyệt xác nhận | Kết quả được dùng làm đáp án tham chiếu khi evaluation; draft label do AI tạo chưa phải ground truth. |
| Criterion | Nhóm tiêu chí đánh giá | Một nhóm năng lực trong rubric, chẳng hạn yêu cầu bắt buộc hoặc năng lực kỹ thuật. |
| Criterion score | Điểm theo nhóm tiêu chí | Số điểm được cấp cho một nhóm dựa trên thông tin trong hồ sơ và lý do chấm. |
| Weighted points | Điểm theo trọng số | Điểm đóng góp đã bị giới hạn bởi trọng số của tiêu chí; tại Stage 3 năm mức tối đa là 30, 25, 20, 15 và 10. |
| Label | Kết quả phân loại | Giá trị mã `pass`, `waitlist`, `reject` hoặc `needs_review` của một case. |
| Draft label | Kết quả do hệ thống đề xuất | Kết quả ban đầu để người phụ trách xem xét; không phải kết quả cuối hoặc ground truth. |
| Final label | Kết quả đã được xác nhận | Kết quả do người phụ trách chốt sau khi xem thông tin trong hồ sơ, điểm và lý do chấm. |
| Rationale | Lý do và căn cứ chấm | Giải thích ngắn nêu thông tin nào trong hồ sơ dẫn tới trạng thái, điểm hoặc kết quả nào. |
| Evidence ID | Mã đoạn thông tin làm căn cứ | Định danh nối một đánh giá với đoạn thông tin cụ thể trong cùng `CVProfile`. |
| Review status | Trạng thái xử lý phiếu đánh giá | Trạng thái như `pending`, `approved` hoặc `changes_requested` cho biết người phụ trách đã xử lý đến đâu. |
| Reviewer reference | Mã người xác nhận | Định danh giả danh phục vụ truy vết mà không cần lưu thông tin nhận dạng cá nhân. |
| Audit trail | Lịch sử truy vết quyết định | Lịch sử cho biết đề xuất ban đầu, người xác nhận, thay đổi, lý do và thời điểm quyết định. |
| Ambiguous case | Trường hợp chưa thể kết luận thống nhất | Case có thể dẫn tới nhiều cách hiểu hợp lý và cần người phụ trách giải quyết hoặc làm rõ rubric. |
| Boundary score | Điểm sát ngưỡng | Điểm nằm trong vùng cấu hình cần review, hiện là 58–62 hoặc 73–77 tính cả hai đầu. |
| Label leakage | Rò rỉ nhãn | Tình trạng nhãn hoặc rationale lọt vào input của classifier, khiến evaluation không còn phản ánh khả năng thực tế. |
| Synthetic data | Dữ liệu tổng hợp | Dữ liệu giả lập có chủ đích để thử nghiệm mà không sử dụng CV thật hoặc PII. |
| Strong fit | Mức độ phù hợp cao | Case có thông tin cụ thể và nhất quán cho yêu cầu bắt buộc cùng nhiều tiêu chí quan trọng; không phải tên một kết quả trong contract. |
| Schema version | Phiên bản khuôn dữ liệu | Thay đổi khi cấu trúc field hoặc quy tắc hợp lệ của dữ liệu thay đổi. |
| Configuration version | Phiên bản bộ quy tắc vận hành | Thay đổi khi trọng số, ngưỡng hoặc hành vi quyết định thay đổi dù khuôn dữ liệu có thể giữ nguyên. |

## Thuật ngữ bổ sung tại Stage 4

| Thuật ngữ gốc | Cách diễn đạt ưu tiên | Nghĩa trong dự án |
| --- | --- | --- |
| Classifier core | Phần xử lý cốt lõi của classifier | Các module L1, L2, L3, aggregation và routing hoạt động độc lập với giao diện và database. |
| Orchestration | Điều phối quy trình | Sắp xếp các bước chấm điểm, tổng hợp, định tuyến và tạo kết quả theo đúng thứ tự và trạng thái. |
| LangGraph | Thư viện điều phối workflow theo graph | Công cụ dùng để chạy các node L1, L2, L3, aggregation, routing và result trong Classifier Agent. |
| Node | Bước xử lý trong graph | Một bước nhận state, thực hiện một trách nhiệm cụ thể và trả phần state được cập nhật. |
| State | Trạng thái đang đi qua workflow | Dữ liệu có kiểu chứa request và kết quả trung gian của L1, L2, L3, aggregation, routing. |
| Aggregation | Tổng hợp điểm nhiều tầng | Kết hợp điểm hợp lệ của L1, L2 và L3 theo trọng số cấu hình để tạo final score. |
| Routing | Chọn hướng xử lý kết quả | Áp dụng precedence, threshold và quality gate để đề xuất `Pass`, `Waitlist`, `Reject` hoặc `Needs Review`. |
| Adapter | Lớp kết nối thay thế được | Thành phần chuyển interface nội bộ sang một model, HTTP provider, embedding engine hoặc database implementation cụ thể. |
| Model identifier | Định danh model | Tên xác định model đã được dùng, được ghi cùng version cấu hình để truy lại chính xác chiến lược chấm điểm. |
| Provider identifier | Định danh nhà cung cấp model | Tên logic của dịch vụ cung cấp LLM; cần ghi riêng vì cùng một model identifier có thể được phục vụ qua nhiều provider. |
| Port | Giao diện mà nghiệp vụ phụ thuộc | Interface mô tả khả năng cần dùng mà không buộc application phải biết implementation hạ tầng cụ thể. |
| Dependency injection | Truyền thành phần phụ thuộc từ bên ngoài | Cách đưa repository, model adapter, clock và identifier vào workflow để dễ thay thế và kiểm thử. |
| Repository pattern | Lớp truy cập dữ liệu theo nghiệp vụ | Interface lưu và đọc classification result, decision và audit history mà use case không cần biết câu SQL. |
| Persistence | Lưu trữ có khả năng giữ lại | Cơ chế giữ kết quả và lịch sử sau khi request kết thúc; PostgreSQL giữ qua restart, memory repository thì không. |
| In-memory repository | Kho lưu tạm trong bộ nhớ | Implementation phục vụ test hoặc kiểm tra nhanh, mất dữ liệu khi tiến trình dừng. |
| PostgreSQL | Hệ quản trị cơ sở dữ liệu quan hệ | System of record của project cho classification run, embedding, decision và audit event. |
| pgvector | Phần mở rộng vector cho PostgreSQL | Cho phép lưu embedding có số chiều cố định và hỗ trợ truy vấn vector trong PostgreSQL. |
| SQLAlchemy | Thư viện ánh xạ và truy cập database | Cung cấp model, async engine, session và repository implementation trong backend. |
| Alembic | Công cụ quản lý database migration | Chạy các thay đổi schema có phiên bản và kiểm tra metadata có khớp migration hiện tại không. |
| Append-only | Chỉ được ghi thêm | Dữ liệu audit quan trọng không được update hoặc delete; thay đổi mới phải được ghi thành event hoặc record mới. |
| Database migration | Bản thay đổi schema có phiên bản | File nâng hoặc hạ cấu trúc database theo thứ tự có thể truy vết và kiểm thử. |
| Disposable test database | Database test có thể xóa hoàn toàn | Database tách biệt chỉ phục vụ integration test; migration test được phép downgrade và dựng lại từ đầu. |
| FastAPI | Framework API của backend | Framework tạo health, classification và human-decision endpoints với Pydantic validation. |
| Endpoint | Điểm nhận request của API | Một cặp phương thức HTTP và đường dẫn, ví dụ `POST /v1/classifications`. |
| API key | Khóa xác thực API | Secret cục bộ hoặc được quản lý ngoài source, gửi qua header để truy cập các route được bảo vệ. |
| Health check | Kiểm tra dịch vụ đang sẵn sàng cơ bản | Request nhẹ tới `/health` để xác nhận ứng dụng đã khởi động; không chứng minh toàn bộ model và database path đều hoạt động. |
| Environment variable | Biến cấu hình của môi trường chạy | Giá trị runtime như database URL, adapter, provider, model và secret được đặt ngoài source code. |
| Bootstrap | Bước lắp ghép ứng dụng | Khởi tạo config loader, adapters, repository, use cases và API thành một ứng dụng có thể chạy. |
| Sentence Transformers | Thư viện tạo embedding câu và đoạn văn | Implementation L2 cục bộ dùng model đa ngôn ngữ để mã hóa rubric và từng phần CV. |
| Multilingual embedding | Embedding đa ngôn ngữ | Véc-tơ biểu diễn ý nghĩa có thể so sánh nội dung tiếng Việt và thuật ngữ kỹ thuật tiếng Anh. |
| Cosine similarity | Độ tương đồng cosine | Tín hiệu số đo hướng tương đối giữa hai embedding; trong dự án nó biểu thị mức liên quan, không phải xác suất ứng viên phù hợp. |
| Hashing embedding | Embedding giả lập bằng phép băm | Cách tạo véc-tơ xác định, không cần tải model, chỉ dùng cho test và baseline chứ không đại diện L2 thực. |
| OpenAI-compatible API | API có cấu trúc request tương thích OpenAI | Dạng HTTP interface mà LLM adapter có thể gọi khi provider, model, base URL và API key được cấu hình. |
| Timeout | Giới hạn thời gian chờ | Khoảng thời gian tối đa chờ provider trước khi coi lần gọi không khả dụng và áp dụng fallback an toàn. |
| TF-IDF | Biểu diễn mức quan trọng của từ | Baseline biến văn bản thành trọng số từ để so sánh CV và yêu cầu mà không dùng mô hình ngữ nghĩa sâu. |
| Accuracy | Tỷ lệ dự đoán đúng tổng thể | Số case dự đoán trùng ground truth chia cho tổng case; có thể gây hiểu nhầm khi các nhãn mất cân bằng. |
| Precision | Độ chính xác trong các case được dự đoán là một nhãn | Trong các case model gán một nhãn, tỷ lệ bao nhiêu case thực sự có nhãn đó. |
| Recall | Mức bao phủ một nhãn thật | Trong các case ground truth thuộc một nhãn, tỷ lệ bao nhiêu case được model tìm đúng. |
| F1 score | Điểm cân bằng precision và recall | Trung bình điều hòa của precision và recall cho một nhãn. |
| Macro-F1 | F1 trung bình đều giữa các nhãn | Tính F1 từng nhãn rồi lấy trung bình, để nhãn ít case vẫn có trọng lượng như nhãn nhiều case. |
| Cohen's kappa | Mức đồng thuận đã hiệu chỉnh theo ngẫu nhiên | Đo mức khớp giữa dự đoán và ground truth sau khi trừ phần đồng thuận có thể xảy ra ngẫu nhiên. |
| Confusion matrix | Ma trận đối chiếu nhãn | Bảng đếm ground-truth label theo hàng và predicted label theo cột để thấy model nhầm nhãn nào thành nhãn nào. |
| Diagnostic report | Báo cáo kiểm tra pipeline | Kết quả trên tập nhỏ dùng để phát hiện lỗi hoặc hiểu hành vi ban đầu; không được trình bày như hiệu năng cuối. |
| Version traceability | Khả năng truy ngược phiên bản | Mỗi kết quả ghi đủ rubric, scoring config, model, prompt và bộ quy tắc đã dùng để có thể tái hiện lần chạy. |

## Thuật ngữ bổ sung tại Stage 5

| Thuật ngữ gốc | Cách diễn đạt ưu tiên | Nghĩa trong dự án |
| --- | --- | --- |
| Score breakdown | Bảng tách điểm theo từng tầng | Phần cho biết riêng điểm L1, L2, L3 và final score để thấy tầng nào ảnh hưởng đến kết quả. |
| Level disagreement | Chênh lệch điểm giữa các tầng | Khoảng cách giữa điểm L1, L2 và L3; nếu chênh lệch lớn nhất từ 25 điểm trở lên thì quality gate yêu cầu người phụ trách xem lại. |
| Error case | Trường hợp classifier không khớp kết quả chuẩn | Case có proposed decision khác final label đã được người duyệt xác nhận; chưa được tự động kết luận nguyên nhân. |
| Model error | Sai lệch do model hoặc adapter | Ground truth và rubric vẫn hợp lý nhưng model, embedding, prompt hoặc provider tạo tín hiệu không phù hợp. |
| Label error | Sai lệch trong kết quả chuẩn đã ghi | Human label hoặc điểm tham chiếu được phát hiện chưa phản ánh đúng hồ sơ; chỉ người phụ trách mới được sửa và phải ghi lý do. |
| Rubric ambiguity | Quy tắc đánh giá còn nhiều cách hiểu | Cùng thông tin CV có thể dẫn đến nhiều cách chấm hợp lý vì criterion, threshold hoặc requirement chưa đủ rõ. |
| Review queue | Danh sách case cần người phụ trách xem | Tập ID được ưu tiên từ mismatch, Needs Review, disagreement hoặc boundary để review có trọng tâm. |
| Controlled diagnostic | Lần chạy chẩn đoán có điều kiện kiểm soát | Lần chạy dùng fake hoặc adapter xác định để kiểm tra pipeline và fallback; không đại diện hiệu năng model cuối. |

## Thuật ngữ bổ sung tại Stage 6

| Thuật ngữ gốc | Cách diễn đạt ưu tiên | Nghĩa trong dự án |
| --- | --- | --- |
| Validation split | Phần dữ liệu dùng để điều chỉnh cấu hình | Tập đã tách trước, cho phép so sánh model, weight, threshold và prompt mà không xem kết quả frozen test. |
| Split manifest | Bản ghi cách chia dữ liệu | Artifact lưu ID của từng partition, policy chia, timestamp và source hash để phát hiện overlap hoặc thay đổi dữ liệu sau khi chia. |
| Tuning | Điều chỉnh trên validation | So sánh các candidate dựa trên validation metrics và safety constraints; không được dựa vào frozen-test outcome. |
| Hyperparameter | Tham số cấu hình được thử nghiệm | Giá trị không học trực tiếp từ CV như weight, threshold, similarity range, top-k hoặc disagreement gate. |
| Candidate configuration | Cấu hình ứng viên để so sánh | Một bộ hyperparameter có version đang được evaluation; chưa trở thành cấu hình chính thức trước human approval. |
| Calibration | Hiệu chỉnh cách biến tín hiệu model thành điểm | Điều chỉnh similarity floor và ceiling để E5 relevance không bị dồn hết về 0 hoặc 100. |
| Saturation | Tín hiệu bị chạm trần hoặc chạm sàn | Nhiều similarity khác nhau cùng bị chuẩn hóa thành một điểm cực trị, làm mất khả năng phân biệt hồ sơ. |
| Review rate | Tỷ lệ case được chuyển cho người phụ trách | Số prediction `Needs Review` chia cho tổng validation case; quá cao làm hệ thống an toàn nhưng ít giá trị tự động hóa. |
| Needs Review recall | Mức bao phủ case thực sự cần review | Trong các ground-truth `Needs Review`, tỷ lệ classifier cũng đưa đúng vào review. |
| Unsafe Pass | Pass không an toàn | Case ground truth là `Reject` hoặc `Needs Review` nhưng candidate tự động đề xuất `Pass`. |
| False Reject | Reject nhầm | Case ground truth không phải `Reject` nhưng candidate tự động đề xuất `Reject`; đây là lỗi cần đặc biệt hạn chế để bảo vệ ứng viên. |
| Model revision | Mã snapshot cụ thể của model | Commit hash xác định chính xác trọng số model đã tải và chạy, chặt hơn tên model hoặc alias chung. |
| Configuration freeze | Khóa cấu hình đã duyệt | Ghi phiên bản cuối của rubric, model, prompt, weight, threshold và quality gate; sau đó không tuning theo frozen-test outcome. |
| Authentication key / Auth key | Khóa xác thực dịch vụ | Secret chứng minh request được phép dùng provider. API key chỉ được đọc từ `.env`, không được ghi vào source, cache hoặc report. |
| Free tier | Hạn mức sử dụng miễn phí | Mức quota provider cho phép dùng không thu phí trực tiếp trong giới hạn nhất định; quota và chính sách có thể thay đổi. |
| Rate limit | Giới hạn tốc độ gọi dịch vụ | Số request hoặc token provider cho phép trong một khoảng thời gian. Vượt giới hạn có thể làm batch validation phải chờ hoặc thất bại tạm thời. |
| OpenRouter | Cổng API hợp nhất nhiều LLM provider | Dịch vụ cung cấp endpoint tương thích OpenAI để gọi nhiều model bằng một API key; trong dự án chỉ được dùng qua adapter có structured validation và không lưu secret. |
| Free model variant | Biến thể model miễn phí | Model ID có hậu tố `:free`; phù hợp cho thử nghiệm có giới hạn nhưng quota, provider availability và độ ổn định có thể thấp hơn bản trả phí. |
| Request cap | Trần số lần gọi | Giới hạn nội bộ thấp hơn quota provider để kiểm soát retry, thời gian, chi phí và tránh batch chạy ngoài dự kiến. |
| Mixture-of-Experts / MoE | Kiến trúc kích hoạt một phần chuyên gia | Model có nhiều nhóm tham số nhưng chỉ kích hoạt một phần cho mỗi token; con số tổng tham số không thể được diễn giải trực tiếp thành chất lượng classifier. |
| HTTP 429 | Phản hồi vượt hạn mức tạm thời | Mã phản hồi thường xuất hiện khi request vượt rate limit; không được diễn giải thành hồ sơ không đạt mà phải retry hoặc chuyển sang fallback an toàn. |
| Retry | Thử lại có giới hạn | Gọi lại provider khi output không hợp lệ hoặc có lỗi tạm thời, với số lần tối đa được cấu hình để tránh vòng lặp vô hạn và chi phí bất thường. |
| Token usage | Lượng đơn vị văn bản provider đã xử lý | Metadata gồm input, output và tổng token, dùng để theo dõi quy mô lần gọi và ước tính chi phí; không chứa nội dung API key. |
| Latency | Thời gian phản hồi | Khoảng thời gian từ lúc gửi request đến khi nhận kết quả, dùng đánh giá khả năng chạy demo hoặc batch. |
| Structured-output validation | Kiểm tra kết quả đúng khuôn | Xác nhận JSON của LLM có đúng schema, đủ ID, đúng score bounds và evidence reference trước khi cho phép đi vào aggregation. |
| Cache/resume | Lưu kết quả hợp lệ để chạy tiếp | Cơ chế giữ structured result đã validate để batch có thể tiếp tục sau lỗi hoặc rate limit mà không gọi lại các case đã hoàn tất. |
| Scoring anchor | Mốc diễn giải mức điểm | Mô tả định tính cho các mức điểm từ thấp đến cao nhằm giảm xu hướng LLM chấm tối đa; prompt dùng anchor vẫn phải được validation trước khi chọn. |
| Automatic Pass gate | Điều kiện bổ sung trước khi tự động cho qua | Quy tắc chỉ cho phép kết quả `Pass` tự động khi tín hiệu bắt buộc đạt mức tin cậy cấu hình; nếu không thì chuyển `Needs Review`, không tự động `Reject`. |
| Provider quality gate | Điều kiện chấp nhận chất lượng kết nối model | Bộ kiểm tra valid-output rate, stability và consistency trước khi output provider được xem là đủ tin cậy cho một cấu hình đề xuất. |
| Early stopping | Dừng thử nghiệm sớm theo điều kiện đã định | Ngừng gọi provider khi quality target đã không thể đạt dù chạy thêm, nhằm tránh lãng phí quota và không che giấu thất bại bằng retry vô hạn. |
| Request-level valid-output rate | Tỷ lệ request trả output hợp lệ | Số HTTP request có structured output qua contract validation chia cho toàn bộ HTTP request, bao gồm cả retry; phản ánh độ ổn định thực tế của provider. |
| Attempted-case valid-output rate | Tỷ lệ case đã thử có output hợp lệ | Số case có ít nhất một output hợp lệ chia cho số case thực sự đã được gửi; khác với tỷ lệ trên toàn bộ sample kế hoạch khi experiment dừng sớm. |
| Endpoint-score saturation | Điểm L3 bão hòa ở cực trị | Nhiều output hợp lệ chỉ nhận 0 hoặc 100, làm mất khả năng phân biệt hồ sơ trung bình và case sát ngưỡng dù JSON vẫn đúng schema. |
| Validation overfitting | Điều chỉnh quá sát tập validation | Cấu hình có thể đạt tốt trên số case đã dùng để tuning nhưng không khái quát sang dữ liệu mới; frozen test được tách riêng để kiểm tra rủi ro này. |

## Thuật ngữ bổ sung cho quy trình mở rộng dataset tại Stage 6

| Thuật ngữ gốc | Cách diễn đạt ưu tiên | Nghĩa trong dự án |
| --- | --- | --- |
| Data provenance | Nguồn gốc và lịch sử dữ liệu | Thông tin cho biết CV, JD và nhãn đến từ đâu, được tạo hoặc biến đổi thế nào, có quyền sử dụng gì và ai đã review. |
| Occupational taxonomy | Hệ thống phân loại nghề nghiệp | Danh mục có cấu trúc liên kết nghề, nhiệm vụ và kỹ năng; O*NET và ESCO được dùng làm nguồn tham khảo để mở rộng Job Profile. |
| Hard negative | Case giống bề ngoài nhưng thiếu năng lực cốt lõi | CV có nhiều từ khóa trùng JD nhưng không có ngữ cảnh dự án, nhiệm vụ hoặc đầu ra đủ để xác nhận năng lực. |
| Cartesian product | Tích Descartes các tổ hợp | Cách ghép mỗi CV của một vị trí với mọi biến thể JD cùng vị trí; 10 CV × 5 JD tạo 50 cặp. |
| Bronze tier | Tầng dữ liệu chưa được con người xác nhận đầy đủ | Dữ liệu synthetic, nhãn tự động hoặc dữ liệu ngoài chỉ dùng cho phát triển, stress test và thử nghiệm; không phải ground truth. |
| Silver tier | Tầng dữ liệu đã qua một phần human review | Dữ liệu có ít nhất một vòng đánh giá nhưng chưa đạt điều kiện dùng làm chuẩn cuối theo chính sách dự án. |
| Gold tier | Tầng dữ liệu đủ điều kiện làm chuẩn đã duyệt | Dữ liệu có human review và audit trail đầy đủ, được phép dùng cho validation hoặc frozen test sau khi split hợp lệ. |
| Group split | Chia dữ liệu theo nhóm liên quan | Giữ mọi phiên bản hoặc mọi cặp của cùng ứng viên trong một partition để model không nhìn thấy cùng nội dung ở cả train và test. |
| Data integrity hash | Mã băm kiểm tra tính toàn vẹn | SHA-256 của file dữ liệu được ghi trong manifest để phát hiện file bị thay đổi sau khi tạo hoặc phê duyệt. |
| Pseudonymous reviewer | Người duyệt dùng định danh giả danh | Audit record lưu một mã ổn định như `reviewer-user-001` thay cho tên hoặc thông tin cá nhân thật của người duyệt. |
| Human review count | Số vòng/người đánh giá của con người | Số reviewer độc lập đã xác nhận record; bản Silver hiện có giá trị 1 và chưa đạt điều kiện Gold của dự án. |
| Held-out diagnostic | Tập giữ riêng để chẩn đoán sau | Dữ liệu không được dùng để tuning, nhưng cũng chưa phải frozen test hoặc chuẩn báo cáo cuối vì vẫn ở tầng Silver. |
| L2 score saturation | Điểm L2 bị bão hòa | Nhiều hoặc toàn bộ cặp nhận điểm gần mức tối đa, khiến L2 không còn phân biệt hồ sơ mạnh, trung bình và không phù hợp. |
| Query coverage | Độ bao phủ các truy vấn yêu cầu | Mỗi yêu cầu hoặc trách nhiệm được đối sánh riêng với CV; truy vấn không có thông tin phù hợp vẫn được tính vào mẫu số để tránh một đoạn mạnh che lấp các phần còn thiếu. |
| Section-aware weighting | Trọng số theo mục CV | Điều chỉnh mức đóng góp của thông tin theo nơi nó xuất hiện, chẳng hạn dự án hoặc kinh nghiệm thực hành có trọng số cao hơn một kỹ năng chỉ được liệt kê. |
| Similarity calibration | Hiệu chỉnh độ tương đồng | Chuyển cosine similarity thành thang 0–100 bằng floor và ceiling được so sánh trên development, thay vì dùng khoảng quá rộng làm mọi cặp đạt điểm tối đa. |
| Semantic relevance | Mức liên quan về ngữ nghĩa | Cho biết nội dung CV có nói về cùng kỹ năng, yêu cầu hoặc trách nhiệm hay không; không tự xác minh lời khai là đúng và không thay thế logic phát hiện phủ định hoặc mâu thuẫn. |
| Reranker | Mô hình xếp hạng lại | Mô hình đọc đồng thời một yêu cầu và một đoạn CV để xếp hạng mức phù hợp chi tiết hơn embedding; là phương án so sánh tiếp theo, chưa được chọn làm cấu hình chính thức. |

## Thuật ngữ bổ sung cho lần hiệu chỉnh yêu cầu Junior

| Thuật ngữ gốc | Cách diễn đạt ưu tiên | Nghĩa trong dự án |
| --- | --- | --- |
| Market calibration | Hiệu chỉnh theo thị trường mục tiêu | Đối chiếu nhiều tin tuyển dụng hiện hành để điều chỉnh độ sâu Job Profile; không sao chép JD và không biến mọi công nghệ xuất hiện thành yêu cầu bắt buộc. |
| End-to-end analysis | Phân tích trọn quy trình | Dự án đi từ câu hỏi nghiệp vụ, thu thập và kiểm tra dữ liệu đến phân tích, đầu ra, khuyến nghị và giới hạn. |
| Window function | Hàm cửa sổ trong SQL | Phép tính trên nhóm hàng mà vẫn giữ từng hàng, thường dùng cho xếp hạng, tổng lũy kế, so sánh kỳ hoặc loại trùng. |
| OpenAPI | Đặc tả có cấu trúc của API | Mô tả endpoint, input, output và lỗi để con người hoặc công cụ có thể đọc, kiểm tra và tích hợp dịch vụ. |
| Container delivery | Bàn giao môi trường chạy bằng container | Đóng gói ứng dụng và dependency để người khác có thể chạy lại nhất quán, thường dùng Docker hoặc Docker Compose. |
| STLC | Vòng đời kiểm thử phần mềm | Chuỗi hoạt động từ phân tích requirement, lập kế hoạch, thiết kế và chạy test đến ghi defect, regression và kết thúc kiểm thử. |
| Risk-based testing | Kiểm thử ưu tiên theo rủi ro | Phân bổ effort kiểm thử theo khả năng xảy ra lỗi và mức ảnh hưởng thay vì coi mọi chức năng quan trọng như nhau. |
| Automation foundation | Nền tảng kiểm thử tự động | Khả năng viết và chạy một test suite nhỏ có assertion, fixture và kết quả lặp lại; chưa đòi hỏi tự thiết kế framework ở mức Senior. |
| Incremental load | Nạp dữ liệu tăng dần | Chỉ xử lý phần dữ liệu mới hoặc thay đổi thay vì nạp lại toàn bộ, đồng thời phải kiểm soát trùng lặp và khôi phục khi lỗi. |
| Idempotency | Khả năng chạy lại không tạo sai lệch | Cùng một tác vụ được thực hiện lại không làm nhân đôi hoặc làm hỏng trạng thái đã đúng, quan trọng với pipeline, webhook và retry. |
| Data quality | Chất lượng dữ liệu | Các kiểm tra như đầy đủ, duy nhất, hợp lệ, nhất quán và toàn vẹn quan hệ trước khi dữ liệu được dùng cho báo cáo hoặc hệ thống sau. |
| Data lineage | Dấu vết luồng dữ liệu | Thông tin cho biết dữ liệu đi từ nguồn nào, qua biến đổi nào và tới bảng hoặc báo cáo nào để điều tra sai lệch và tác động thay đổi. |

## Thuật ngữ bổ sung cho lựa chọn OpenRouter L3 tại Stage 6

| Thuật ngữ gốc | Cách diễn đạt ưu tiên | Nghĩa trong dự án |
| --- | --- | --- |
| Fixed model identifier | Định danh model cố định | Tên model cụ thể được ghi vào config và report để lần chạy sau không tự chuyển sang model khác; cần cho reproducibility và configuration freeze. |
| Model alias | Tên model trỏ gián tiếp | Tên thuận tiện có thể được provider đổi sang snapshot hoặc endpoint khác; nếu alias không route ổn định thì không phù hợp làm định danh frozen. |
| `require_parameters` | Bắt buộc endpoint hỗ trợ tham số đã gửi | Chính sách OpenRouter chỉ chọn endpoint công bố hỗ trợ các tham số như Response Format; bộ lọc quá chặt có thể trả 404 dù model có trang catalog. |
| Response Healing | Sửa lỗi cú pháp phản hồi JSON | Plugin của OpenRouter có thể sửa một số lỗi JSON trước validation; nó không được phép biến nội dung sai schema hoặc sai nghiệp vụ thành kết quả hợp lệ. |
| Provider availability | Mức sẵn sàng của dịch vụ model | Khả năng endpoint nhận và hoàn tất request tại thời điểm chạy; khác với độ chính xác của model và phải được đo riêng. |
| Provider error envelope | Gói phản hồi báo lỗi của provider | HTTP response có thể thành công ở lớp kết nối nhưng phần thân chứa `error`; adapter phân loại an toàn và không coi đó là điểm ứng viên. |
| HTTP 404 | Không tìm thấy model hoặc endpoint phù hợp | Trong các experiment hiện tại, request bị từ chối trước khi sinh output; có thể do model ID, endpoint đã mất hoặc bộ lọc capability không khớp. |
| HTTP 502 | Lỗi upstream provider | OpenRouter nhận request nhưng dịch vụ model phía sau lỗi; phải retry có giới hạn hoặc fallback sang `Needs Review`, không diễn giải thành hồ sơ không đạt. |
| Structured-output error rate | Tỷ lệ phản hồi sai khuôn có cấu trúc | Tỷ lệ provider không tạo được JSON đúng schema. Đây là tiêu chí vận hành tách biệt với MAE, label accuracy hoặc chất lượng chấm điểm. |
| Terminal provider failure | Lỗi provider đã hết quyền retry | Một case đã dùng hết số lần thử nhưng vẫn unavailable; runner dừng sớm vì valid-output target không còn đạt được mà không tiêu thêm quota. |

## Thuật ngữ bổ sung cho lần chạy Gemini L3 năm vị trí

| Thuật ngữ gốc | Cách diễn đạt ưu tiên | Nghĩa trong dự án |
| --- | --- | --- |
| Request pacing | Giãn cách các lần gọi API | Khoảng chờ tối thiểu giữa hai request để giảm nguy cơ vượt RPM; experiment Gemini v16 dùng tối thiểu 6 giây. |
| Hard request cap | Giới hạn cứng số request | Tổng số lần gọi tối đa mà runner được phép thực hiện, tính cả retry; v16 giới hạn 35 để ngăn tiêu quota ngoài kế hoạch. |
| Request timeout | Thời gian chờ tối đa cho một request | Sau thời gian này request được coi là provider unavailable và đi vào cơ chế retry hoặc dừng an toàn; v16 dùng 60 giây. |
| Sampling parameter | Tham số điều khiển cách model sinh output | Các tham số như `temperature`, `top_p` và `top_k`; request `gemini-3.5-flash-lite` hiện không gửi `temperature` để dùng hành vi mặc định của model. |
| Calibration gate | Điều kiện chấp nhận độ sát điểm | So sánh điểm L3 với điểm human review bằng endpoint-score rate, criterion MAE và total-score MAE; JSON hợp lệ không đồng nghĩa calibration đạt. |
| Stability repeat | Lần chấm lặp để đo ổn định | Gọi cùng một case thêm lần nữa và đo khoảng chênh điểm cùng mức thống nhất requirement status; lệch quá ngưỡng khiến cấu hình chưa được freeze. |
| Requirement scoping | Giới hạn phạm vi của thông tin theo yêu cầu | Một câu phủ định hoặc giới hạn chỉ được làm thay đổi requirement mà nó nêu trực tiếp; thông tin chung có thể giảm criterion score nhưng không tự tạo mâu thuẫn cho mọi kỹ năng. |
| Probe run | Lần chạy thăm dò có giới hạn | Gọi một hoặc rất ít request đã chọn trước để phát hiện lỗi cấu hình hay dữ liệu trước khi tiêu toàn bộ request budget. |
| Data remediation | Hiệu chỉnh dữ liệu có truy vết | Sửa lỗi nội dung trong một dataset version mới, giữ bản cũ để audit và chạy lại các bước phụ thuộc vào hash hoặc nội dung đã đổi. |
| Synthetic evidence inconsistency | Mâu thuẫn trong thông tin synthetic | Ý định kịch bản hoặc nhãn nói một năng lực bị thiếu nhưng một evidence khác lại trực tiếp chứng minh năng lực đó; phải review dữ liệu thay vì ép model học theo nhãn. |
| Score consistency | Tính nhất quán của điểm | `overall_score` phải bằng tổng năm criterion score và mỗi điểm phải tuân thủ weight/cap; output vi phạm bị coi là invalid và chỉ được retry có giới hạn. |
| Direct positive | Thông tin trực tiếp xác nhận đúng năng lực | Nội dung mô tả ứng viên đã thực hiện hoặc tạo đầu ra gắn trực tiếp với một requirement; không được tự lan sang requirement khác chỉ vì cùng criterion. |
| Exact negative | Thông tin trực tiếp xác nhận chưa có đúng năng lực | Câu nêu rõ ứng viên chưa biết, chưa làm hoặc đã thất bại ở chính requirement đang đánh giá; khác với câu hạn chế chung không gọi tên năng lực. |
| Context-only evidence | Thông tin chỉ dùng làm bối cảnh | Education, sở thích hoặc mô tả chung có thể hỗ trợ diễn giải nhưng không đủ để tự đánh dấu requirement là `satisfied`, `unsatisfied` hoặc `conflicting`. |
| Request-budget shortfall | Ngân sách request còn lại không đủ | Số request còn được phép gọi nhỏ hơn số output hợp lệ còn thiếu; runner phải dừng vì batch không thể hoàn tất ngay cả khi mọi request còn lại đều thành công. |

## Thuật ngữ bổ sung cho GPT-5.4 mini tại Stage 6

| Thuật ngữ gốc | Cách diễn đạt ưu tiên | Nghĩa trong dự án |
| --- | --- | --- |
| Structured Outputs | Phản hồi theo cấu trúc được ràng buộc | Chế độ API yêu cầu model trả JSON theo schema đã khai báo; output vẫn phải qua Pydantic và kiểm tra nhất quán với request. |
| Strict JSON Schema | JSON Schema ở chế độ ràng buộc nghiêm ngặt | Schema gửi OpenAI phải khai báo mọi field là `required`, không cho field ngoài và chỉ dùng tập tính năng được provider hỗ trợ. |
| Derived field | Trường được dẫn xuất | Giá trị được tính chắc chắn từ các trường nguồn; `overall_score` được tính từ năm criterion score thay vì tin vào phép cộng lặp lại của model. |
| Completion token cap | Giới hạn token sinh tối đa | `max_completion_tokens` chặn tổng token model được dùng cho output và reasoning trong một request nhằm kiểm soát chi phí và lỗi sinh quá dài. |
| Reasoning effort | Mức tài nguyên suy luận | Tham số điều khiển lượng reasoning của model; experiment hiện dùng `none` làm baseline chi phí thấp và chỉ đổi khi có thí nghiệm được phê duyệt. |
| Cached input token | Input token được tính giá cache | Phần prompt trùng được provider nhận diện và tính mức giá thấp hơn input mới; report tách riêng để ước tính chi phí. |
| Lower-bound cost estimate | Ước tính chi phí tối thiểu | Chi phí tính được từ các request có usage; chưa bao gồm request lỗi không trả usage nên không thay thế hóa đơn provider. |
| Unpriced request | Request chưa định giá trong report cục bộ | Request đã gửi nhưng failure result không có usage; vẫn được tính vào hard cap và phải đối chiếu OpenAI Usage Dashboard. |
| Evidence cardinality | Số lượng ID thông tin hỗ trợ theo trạng thái | `missing` cần 0 ID, `satisfied` hoặc `unsatisfied` cần ít nhất 1 ID, `conflicting` cần ít nhất 2 ID khác nhau. |
| Dynamic schema | Schema động theo từng request | JSON Schema được tạo từ đúng rubric và danh sách thông tin của cặp CV-JD hiện tại, nhờ đó chỉ cho phép đúng loại ID và số assessment cần có. |
| Cardinality constraint | Ràng buộc số lượng phần tử | Quy định `minItems` và `maxItems` cho danh sách; tại v4 nó khóa số requirement/criterion assessment và số evidence ID hợp lệ theo status. |
| Development panel gate | Cổng chất lượng trên nhóm development nhỏ | Năm case đã chọn trước phải đồng thời đạt output validity, requirement agreement và các ngưỡng điểm trước khi runner được phép gửi batch còn lại. |
| Series request cap | Trần request của cả chuỗi thử nghiệm | Giới hạn cộng dồn request lịch sử và request phiên bản mới; v4 ghi 13 request trước đó và chỉ cho phép toàn chuỗi v1-v4 tối đa 45. |

## Thuật ngữ bổ sung cho OpenAI role-calibrated hybrid v8 tại Stage 6

| Thuật ngữ gốc | Cách diễn đạt ưu tiên | Nghĩa trong dự án |
| --- | --- | --- |
| Qualitative calibration level | Mức hiệu chỉnh định tính | Một trong bảy mức từ `unsupported` đến `exceptional` do LLM chọn dựa trên độ sâu, phạm vi, ownership và outcome của thông tin; đây chưa phải điểm số. |
| Deterministic level mapping | Ánh xạ mức thành điểm bằng quy tắc xác định | Code chuyển calibration level và requirement status thành weighted points theo bảng version hóa; cùng input luôn cho cùng điểm và không phụ thuộc phép tính của LLM. |
| Capability guard | Quy tắc giữ ranh giới năng lực | Ràng buộc ngăn model suy diễn kỹ năng liên quan thành kỹ năng bắt buộc, ví dụ ETL không tự chứng minh Python và phủ định JavaScript không tự phủ định HTML/CSS. |
| Requirement atom | Đơn vị năng lực nhỏ nhất của một yêu cầu | Phần năng lực cụ thể mà thông tin tích cực hoặc phủ định trực tiếp nhắm tới; status không được lan sang atom khác chỉ vì cùng dự án hoặc cùng nhóm kỹ thuật. |
| Conservative mismatch | Sai lệch theo hướng đưa sang người duyệt | Model chọn `missing` hoặc `conflicting` thay vì trạng thái human review, khiến hồ sơ cần human review thay vì tạo quyết định tự động; vẫn là lỗi phải đo, không phải kết quả đúng. |
| Unsafe requirement mismatch | Sai lệch requirement có thể tạo quyết định không an toàn | Model chuyển sang `satisfied` hoặc `unsatisfied` theo hướng có thể tạo automatic Pass hoặc Reject sai; quality gate v8 yêu cầu số lỗi này bằng 0. |
| Requirement-route agreement | Mức thống nhất về tuyến xử lý từ requirement | Hai lần chấm có thể khác một status chi tiết nhưng phải thống nhất việc hồ sơ được tự động xử lý, Reject có căn cứ hay chuyển `Needs Review`; v8 yêu cầu tỷ lệ này bằng 1,00. |
| Evaluation-policy cache migration | Chuyển cache giữa policy đánh giá tương thích | Tái sử dụng output đã trả phí khi model, prompt, dataset, schema và request không đổi; hàm migration từ chối nếu thay đổi bất kỳ thành phần nào có thể làm provider sinh output khác. |
| Hybrid candidate | Phương án kết hợp L1-L2-L3 đang được so sánh | Một bộ version hóa gồm trọng số, thresholds, disagreement và boundary policy; candidate v8 đã đạt development gate và sau phê duyệt ngày 2026-08-07 được khóa trong `five-role-runtime-v1`. |
| Grid-search | Duyệt lưới các tổ hợp cấu hình | Thử có hệ thống nhiều tổ hợp trọng số và thresholds chỉ trên development, sau đó lọc bằng các điều kiện bảo vệ ứng viên; không được dùng held-out hoặc frozen test để chọn tổ hợp. |
| Routing-safe stability | Độ ổn định an toàn theo tuyến xử lý | Đánh giá lần chấm lặp có giữ cùng đường đi tự động/human review hay không, bổ sung cho exact status agreement và score range. |

## Thuật ngữ bổ sung cho bộ runtime năm vai trò tại Stage 6

| Thuật ngữ gốc | Cách diễn đạt ưu tiên | Nghĩa trong dự án |
| --- | --- | --- |
| Runtime configuration set | Bộ cấu hình dùng khi hệ thống chạy | Nhóm Job Profile, rubric, L1 rule, L2/L3 model strategy và scoring configuration đã liên kết để backend nạp như một đơn vị. |
| Runtime manifest | Bản kê cấu hình runtime | Artifact ghi danh sách vai trò, phiên bản, chiến lược đã duyệt, file nguồn và SHA-256 để phát hiện thiếu file hoặc thay đổi ngoài quy trình. |
| Artifact hash / SHA-256 | Mã kiểm tra nội dung artifact | Dấu vân tay được tính từ toàn bộ byte của file; thay một ký tự sẽ làm mã đổi và manifest từ chối cấu hình chưa được cập nhật có chủ đích. |
| Model revision pinning | Khóa đúng bản sửa đổi của model | Ghi cả model identifier và revision cụ thể để lần chạy sau không âm thầm tải nội dung mới dưới cùng một tên model. |
| Configuration freeze candidate | Bộ cấu hình đang chờ khóa | Trạng thái trước phê duyệt của một candidate đã vượt development gate và được đóng gói đầy đủ; `five-role-runtime-v1` không còn ở trạng thái này sau khi Gate 6 đóng ngày 2026-08-07. |
| Configuration freeze | Khóa cấu hình trước đánh giá cuối | Chuyển artifact đã duyệt sang trạng thái không được tuning theo output Stage 7; mọi thay đổi sau đó phải tạo version mới và không được dùng lại test outcome để tối ưu. |
| Holdout contamination | Mất tính độc lập của dữ liệu để dành | Xảy ra khi dữ liệu held-out được xem hoặc kết quả của nó ảnh hưởng đến rule, prompt, threshold hay model trước đánh giá cuối, làm metric sau đó có nguy cơ thiên lệch. |
| Invalidated holdout | Held-out không còn hợp lệ cho kết luận cuối | Partition vẫn được giữ để audit hoặc diagnostics nhưng không được dùng để tuyên bố final performance; dự án cần test set độc lập khác cho kết luận tương ứng. |
| Diagnostic-only data | Dữ liệu chỉ dùng để chẩn đoán | Dữ liệu có thể giúp tìm lỗi và hiểu hành vi nhưng metric trên đó không được trình bày như kết quả khách quan cuối cùng. |
| Handoff | Tài liệu bàn giao ngữ cảnh | Bản tóm tắt giúp AI hoặc contributor mới biết phải đọc file nào, trạng thái hiện tại, quyết định đã khóa và bước tiếp theo; nó không thay thế `progress.md` là nguồn trạng thái chính thức. |

## Thuật ngữ bổ sung cho chu kỳ cải tiến Runtime v2 tại Stage 7

| Thuật ngữ gốc | Cách diễn đạt ưu tiên | Nghĩa trong dự án |
| --- | --- | --- |
| Runtime improvement cycle | Chu kỳ cải tiến runtime | Quy trình tạo development data mới, sửa và validation một cấu hình version mới, rồi dùng một frozen test mới; không sửa runtime v1 và chạy lại trên test cũ để thay thế kết quả đã thất bại. |
| Go/no-go checkpoint | Điểm kiểm tra tiếp tục hoặc dừng | Điều kiện phải đạt trước khi chuyển sang bước tốn thêm chi phí; Runtime v2 chỉ gọi L3 sau khi dữ liệu được human review và kiểm tra L1/L2 offline đạt yêu cầu. |
| Provider pilot | Đợt thử provider quy mô nhỏ | Một số request LLM được chọn trước để kiểm tra prompt, schema, requirement status, MAE và lỗi nguy hiểm trước khi gửi batch lớn. |
| Prior-CV token Jaccard | Mức trùng token với CV trước | Tỷ lệ giao trên hợp của các token giữa CV mới và CV ở dataset cũ; dùng cùng kiểm tra trùng nguyên văn để phát hiện hồ sơ mới quá giống dữ liệu đã dùng. |
| Capability-focused development data | Dữ liệu phát triển tập trung vào năng lực | Các CV–JD synthetic được thiết kế để phân biệt thao tác trực tiếp, thông tin liên quan gián tiếp, phủ định và mâu thuẫn cho từng requirement cụ thể. |
| Bronze review dataset | Dataset Bronze chờ duyệt | Dữ liệu có annotation nháp nhưng chưa được con người xác nhận; không được dùng làm ground truth để tuning hoặc báo cáo hiệu năng. |
| Silver dataset | Dataset đã được người duyệt xác nhận | Dữ liệu có requirement status, điểm, nhãn và rationale đã được human review; được phép dùng cho development/validation nhưng chưa phải kết quả final độc lập như Gold frozen test. |
| Role one-hot | Vector chỉ báo vai trò | Mỗi vai trò được biểu diễn bằng một cột 0/1 để calibrator học sai lệch thang điểm giữa năm vị trí mà không dùng tên ứng viên hoặc thuộc tính nhạy cảm. |
| Extra Trees regressor | Mô hình hồi quy nhiều cây ngẫu nhiên hóa | Model scikit-learn cục bộ học ánh xạ phi tuyến từ năm điểm semantic và role one-hot sang năm criterion score đã hiệu chỉnh. |
| Minimum samples per leaf | Số mẫu tối thiểu tại một lá cây | Tham số regularization; số lớn hơn làm cây ít chia nhỏ hơn và giảm nguy cơ học thuộc development data. Runtime v2 chọn leaf 3 vì đạt toàn bộ gate và ít overfit hơn leaf 2. |
| Model artifact hash | Mã kiểm tra file model | SHA-256 của file model local; runtime từ chối nạp nếu nội dung file khác cấu hình đã version hóa. |
| Supervised calibration | Hiệu chỉnh có nhãn hướng dẫn | Học ánh xạ từ điểm semantic sang điểm human review chỉ trên development; validation dùng để chọn cấu hình chứ không được đưa vào bước fit tại checkpoint này. |

## Thuật ngữ bổ sung cho định hướng sau Runtime v2 tại Stage 7

| Thuật ngữ gốc | Cách diễn đạt ưu tiên | Nghĩa trong dự án |
| --- | --- | --- |
| Skill ontology | Hệ thống quan hệ giữa các kỹ năng | Danh mục có cấu trúc về kỹ năng, từ đồng nghĩa, framework, ngôn ngữ và quan hệ phụ thuộc theo từng vai trò; giúp L1 tránh suy diễn một kỹ năng thành một requirement khác. |
| Independent assessment | Đánh giá độc lập | Phần L3 tự đánh giá requirement từ CV, JD và rubric thay vì bắt buộc sao chép trạng thái L1; mọi bất đồng quan trọng vẫn phải chuyển human review. |
| A/B model evaluation | So sánh hai model trong cùng điều kiện | Chạy các model trên cùng validation panel với prompt và cấu hình còn lại được giữ nguyên để đo riêng tác động của việc đổi model. |
| End-to-end evaluation | Đánh giá toàn bộ chuỗi xử lý | Đo kết quả từ CV nguồn qua Parser đến Classifier, nhờ đó phân biệt được lỗi trích xuất của Parser với lỗi chấm của Classifier. |
| Operational distribution | Phân bố dữ liệu trong vận hành | Tỷ lệ hồ sơ mạnh, yếu, thiếu thông tin và mâu thuẫn thực sự xuất hiện khi sử dụng hệ thống; có thể khác tập test được chủ động cân bằng nhiều case khó. |

## Thuật ngữ bổ sung cho giao diện kỹ thuật Stage 8

| Thuật ngữ gốc | Cách diễn đạt ưu tiên | Nghĩa trong dự án |
| --- | --- | --- |
| Backend for Frontend | Lớp backend dành riêng cho frontend | Các Route Handler của Next.js nhận yêu cầu từ trình duyệt, gọi FastAPI ở phía máy chủ và không đưa API key của backend vào mã chạy trên trình duyệt. |
| Route Handler | Hàm xử lý HTTP của App Router | File `route.ts` triển khai các endpoint trung gian cho health check, phân loại, phê duyệt, override và đọc lịch sử quyết định. |
| Component test | Kiểm thử hành vi của component | Vitest và Testing Library kiểm tra giao diện ở mức component, gồm tải dữ liệu, trạng thái lỗi, hiển thị điểm và thao tác human review. |
| Browser E2E test | Kiểm thử toàn luồng trên trình duyệt | Playwright mô phỏng người dùng chọn hồ sơ, chạy phân loại, xem thông tin hỗ trợ, phê duyệt, override và đọc lịch sử audit trên bản build production. |
| Deterministic demo data | Dữ liệu demo sinh theo quy tắc xác định | Năm request demo được tái tạo từ dữ liệu Silver đã duyệt; cùng phiên bản nguồn luôn sinh cùng nội dung và không chứa human label trong input gửi classifier. |
| Audit history | Lịch sử quyết định có thể truy vết | Danh sách quyết định cuối, người duyệt, thời điểm, lý do và lý do override được đọc lại từ backend sau khi human review. |
| Offline fallback | Chế độ hiển thị dự phòng khi backend không hoạt động | Frontend vẫn cho xem danh mục hồ sơ demo nhưng khóa thao tác phân loại và báo rõ trạng thái kết nối, thay vì làm mất dữ liệu hoặc tạo kết quả giả. |

## Thuật ngữ bổ sung cho hai chế độ demo tại Stage 8

| Thuật ngữ gốc | Cách diễn đạt ưu tiên | Nghĩa trong dự án |
| --- | --- | --- |
| Execution mode | Chế độ thực thi | Lựa chọn `offline` hoặc `llm` quyết định tiến trình FastAPI nào xử lý health check, phân loại và lịch sử quyết định của một lượt demo. |
| Dual-backend demo | Demo dùng hai backend độc lập | Hai tiến trình FastAPI dùng cấu hình L3 khác nhau: một tiến trình mô phỏng offline và một tiến trình gọi provider thật; cách tách này tránh đổi adapter giữa lúc server đang chạy. |
| Cost confirmation | Xác nhận khả năng phát sinh phí | Checkbox bắt buộc trước khi nút gọi LLM thật được bật, giúp mỗi provider request là hành động chủ động của người dùng. |
| No silent fallback | Không tự chuyển chế độ khi có lỗi | Khi backend LLM thiếu cấu hình hoặc provider lỗi, giao diện báo lỗi thay vì âm thầm dùng kết quả offline và khiến người xem hiểu sai nguồn kết quả. |
| Criterion-specific rationale | Giải thích riêng theo từng tiêu chí | Nội dung giải thích nêu tên và mô tả tiêu chí cùng thông tin đã dùng; ở chế độ offline đây vẫn là giải thích phép tính theo quy tắc, không phải suy luận của LLM. |
| Environment allowlist | Danh sách biến môi trường được phép nạp | Frontend server chỉ nạp URL và khóa xác thực backend cần thiết từ `.env` gốc; provider API key không nằm trong danh sách này nên không được đưa vào tiến trình frontend. |
| Provider API key | Khóa truy cập nhà cung cấp LLM | `CLASSIFIER_LLM_API_KEY` cho phép FastAPI gọi provider có thể phát sinh phí; nó khác `CLASSIFIER_API_KEY`, vốn chỉ xác thực request giữa frontend server và FastAPI. |
| Parser-equivalent input | Đầu vào mô phỏng contract của Parser | `CVProfile` được tạo thủ công để có cùng cấu trúc mà Parser Agent phải trả về; nó kiểm tra Classifier nhưng không đo chất lượng trích xuất của Parser. |
| Irreversible anonymization | Ẩn danh không thể khôi phục hợp lý | Loại hoặc khái quát hóa các trường và chi tiết có thể liên kết artifact với một cá nhân cụ thể; chỉ giữ tín hiệu nghề nghiệp cần cho rubric. |
