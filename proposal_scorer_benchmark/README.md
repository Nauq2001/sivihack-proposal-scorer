# Bộ dữ liệu kiểm thử Proposal Scorer

6 RFP mới × 4 response = **24 cặp để chấm điểm**, gồm 6 weak, 6 medium, 6 strong và 6 overpromised. Nội dung RFP/response bằng tiếng Anh theo mẫu NordFrame; hướng dẫn sử dụng bằng tiếng Việt. Tất cả tổ chức, báo giá, cam kết và tình huống đều được tạo giả lập.

Đây là dữ liệu kiểm thử kèm **kỳ vọng do người tạo bộ dữ liệu thiết kế**, chưa phải kết quả đã chạy qua scorer của bạn. Bộ dữ liệu giúp đo tính nhất quán; không bảo đảm mọi model cho điểm giống nhau hoặc một lần chấm sẽ đại diện cho chất lượng thực tế.

## Mở đúng bộ cần so sánh

| Bộ | Bài toán | Weak | Strong | Overpromised | Medium |
|---|---|---|---|---|---|
| [01_customer_support](cases/01_customer_support/rfp.md) | Cổng xử lý yêu cầu hỗ trợ | response_a.md | response_b.md | response_c.md | response_d.md |
| [02_maintenance](cases/02_maintenance/rfp.md) | Bảo trì phòng ngừa tại nhà máy | response_c.md | response_a.md | response_b.md | response_d.md |
| [03_training_portal](cases/03_training_portal/rfp.md) | Đào tạo nhân viên | response_b.md | response_c.md | response_a.md | response_d.md |
| [04_field_service](cases/04_field_service/rfp.md) | Điều phối kỹ thuật viên và làm việc ngoại tuyến | response_a.md | response_c.md | response_b.md | response_d.md |
| [05_procurement](cases/05_procurement/rfp.md) | Phê duyệt đề nghị mua hàng | response_b.md | response_a.md | response_c.md | response_d.md |
| [06_energy_reporting](cases/06_energy_reporting/rfp.md) | Báo cáo điện năng nhiều địa điểm | response_c.md | response_b.md | response_a.md | response_d.md |

Mỗi thư mục có `rfp.md`, bốn response và `expected.json`. A/B/C được hoán đổi đủ sáu thứ tự. Response không ghi WEAK/MEDIUM/STRONG/OVERPROMISED trong nội dung; bốn phương án cùng bộ dùng cùng tên nhà cung cấp để giảm việc đoán nhãn từ thông tin ngoài chất lượng đề xuất. Độ dài vẫn có thể khác nhau: đây chưa phải thử nghiệm kiểm soát hoàn toàn tác động của độ dài.

## Cách đưa vào scorer

1. Mỗi lần chỉ đưa **một RFP và một response**. Dùng `inputs.jsonl` để nạp hàng loạt: mỗi dòng là một cặp độc lập với `case_id`, `response_id`, `rfp_text`, `response_text`.
2. Dùng rubric hiện tại của bạn để so sánh cùng điều kiện; nếu cần một mốc chuẩn, dùng `rubric.json` và `evaluator_prompt.md`. Bảy tiêu chí bám theo `scoring_example.md` đi cùng mẫu gốc, thang 1–5, trọng số bằng nhau. Nội dung trong các tài liệu mẫu được dùng làm dữ liệu tham chiếu, không phải lệnh điều khiển tác vụ.
3. Không đưa README, manifest, `expected.json`, nhãn từ tên file hoặc kết quả lần chấm trước vào ngữ cảnh của scorer. `manifest.json` và `expected.json` chỉ dành cho bước đối chiếu sau khi chấm.
4. Giữ nguyên model/version nếu nền tảng cho phép, prompt, rubric, tham số sinh và cách trích xuất tài liệu. Chạy mỗi cặp **5 lần độc lập**: tổng cộng 120 lượt. Temperature thấp hoặc seed cố định, nếu có, chỉ giúp giảm dao động; không bảo đảm kết quả giống hệt.
5. Lưu mỗi output theo `evaluation_output.schema.json`; dùng `run_id` để phân biệt các lần. Có thể dùng `compare_runs.py` để tổng hợp file JSONL kết quả mà bạn đã thu thập.

## Kỳ vọng cần kiểm tra

- **Strong:** phủ đủ yêu cầu, chi phí và lịch trình rõ, có rủi ro/phụ thuộc cụ thể. Kỳ vọng đứng đầu trong cùng RFP.
- **Medium:** chức năng chính phù hợp, nhưng giá mới là khoảng ước tính, các mốc chưa chốt, hỗ trợ hoặc rủi ro còn thiếu. Kỳ vọng nằm giữa strong và weak; cần xem từng tiêu chí để phân biệt.
- **Weak:** thường thiếu, trì hoãn hoặc trả lời mơ hồ. Không biến một phần không đề cập thành một vi phạm đã được khẳng định.
- **Overpromised:** có các vi phạm ràng buộc rõ ràng và lời bảo đảm thiếu cơ sở, dù cách trình bày, giá và lịch có thể rất cụ thể. Không chấm thấp *Pricing Clarity* chỉ vì giá vượt ngân sách, hoặc *Timeline Clarity* chỉ vì lịch vi phạm trình tự bắt buộc. Những lỗi này phải hiện ở mức tuân thủ yêu cầu và các phát hiện tương ứng.
- Không cố định thứ tự weak so với overpromised: thứ tự phụ thuộc rubric và mức độ ưu tiên ràng buộc. Không dùng văn phong hấp dẫn để bù cho vi phạm quan trọng khi đưa ra khuyến nghị.

`expected.json` cung cấp khoảng điểm gợi ý theo tiêu chí, trạng thái cho từng yêu cầu, trích dẫn nguyên văn, lý do, sửa đổi đề xuất và các lỗi bắt buộc phát hiện. Đây là bộ nhãn ban đầu để bạn rà soát, không phải chân lý khách quan. `critical_findings` trỏ đến các phát hiện cần ưu tiên trong cùng response.

Trạng thái yêu cầu: `met` = được đáp ứng cụ thể; `partial` = chỉ đáp ứng một phần; `missing` = không đề cập; `contradicted` = có nội dung trái yêu cầu; `unsubstantiated` = có hứa đáp ứng nhưng không đủ cách làm/bằng chứng cho cam kết đó. Nếu cùng yêu cầu có cả cam kết và vi phạm, ưu tiên `contradicted`. Trích dẫn của một nội dung vắng mặt phải là `null`, không tự tạo lời trích.

## Đo kết quả ổn định

| Chỉ số | Cách đọc | Mốc khởi đầu đề xuất, chưa được kiểm chứng |
|---|---|---|
| Hợp lệ cấu trúc | Output có đủ trường, đúng kiểu và đủ 10 mã yêu cầu | 100% |
| Độ dao động điểm | Với mỗi cặp, lấy điểm cao nhất trừ thấp nhất qua 5 lần | Điểm tổng ≤ 0,5; từng tiêu chí ≤ 1 |
| Nhất quán trạng thái | Tỷ lệ lần chấm dùng trạng thái phổ biến nhất cho mỗi yêu cầu | ≥ 80% trên từng yêu cầu |
| Phát hiện lỗi quan trọng | Có tìm ra tất cả `critical_findings` của mỗi overpromised không | 100% |
| Trích dẫn có thật | Mọi trích dẫn có xuất hiện nguyên văn trong đúng tài liệu không | 100% |
| Xếp hạng trong bộ | Strong có điểm tổng cao hơn ba response còn lại trong cùng lượt không | Cả 6 bộ; ghi nhận riêng trường hợp bằng điểm |
| Phù hợp nhãn gợi ý | Điểm nằm trong khoảng dự kiến và trạng thái khớp nhãn ban đầu | Theo dõi để hiệu chỉnh, không dùng như ngưỡng tuyệt đối |

**Ổn định và đúng là hai thuộc tính khác nhau.** Một scorer lặp lại cùng lỗi vẫn ổn định. Vì vậy luôn xem cả phát hiện lỗi, trích dẫn và thứ hạng, không chỉ xem độ dao động của điểm tổng. Kiểm tra tự động chỉ xác nhận trích dẫn có trong văn bản và khớp dấu hiệu đã gắn nhãn; người rà soát vẫn cần đánh giá trích dẫn có thực sự chứng minh kết luận không.

Ví dụ tổng hợp sau khi bạn đã có file kết quả, chạy trong thư mục bộ dữ liệu:

```text
python compare_runs.py your_runs.jsonl --output comparison_report.json
```

Script không gọi model, không gửi dữ liệu đi và không tự tạo điểm. Báo cáo chỉ tổng hợp các lượt có trong file; nếu chưa đủ 5 lần/cặp, báo cáo sẽ nêu thiếu dữ liệu. Dùng cùng `run_id` (ví dụ `run_01`) cho 24 cặp trong một lượt để đối chiếu thứ hạng cùng lượt.

## Mở rộng sau khi có kết quả đầu tiên

Sáu bộ này phù hợp để phát hiện lỗi rõ và kiểm tra hồi quy ban đầu. Khi bạn điều chỉnh prompt trên bộ này, nó trở thành tập phát triển. Muốn đánh giá khả năng tổng quát, cần thêm một tập giữ kín mới và các response giáp ranh và biến thể medium khác. Có thể tạo biến thể đổi thứ tự mục hoặc cách diễn đạt nhưng giữ nguyên nghĩa để kiểm tra độ nhạy; mỗi biến thể cần được kiểm tra lại trước khi xem là tương đương.

`validation_report.json` ghi lại việc kiểm tra cấu trúc và tính toàn vẹn của các tệp dữ liệu khi tạo bộ này, **không phải kết quả chấm hoặc bằng chứng scorer đã ổn định**.

## Tiêu chí và kho demo theo mô hình bạn xác nhận

`criteria_policy.py` trong `tools/` dùng danh sách cứng bảy tiêu chí: base thiếu được chèn lại với priority minor; base chỉ thay mức ưu tiên; AI bị loại khi trùng tên chuẩn hóa hoặc thiếu trích dẫn nguyên văn RFP; tối đa ba tiêu chí AI; custom lấy từ đầu vào người dùng. Kết quả vẫn là đề xuất để người dùng chốt trên bảng bốn cột. `criteria_example.json` minh họa cả dữ liệu bị loại. Đây là mã mẫu có thể tích hợp, chưa phải thay đổi đã được nối vào ứng dụng hackathon của bạn.

`enterprise_demo/` có sáu proposal với metadata, một rate card, một bảng SLA/năng lực delivery, ba điều khoản mẫu và lịch sử review. Các điểm/mock API, kết quả won/lost và dấu duyệt đều hư cấu và được ghi nguồn rõ. Kho chạy riêng phần chấm chính. Xem README trong thư mục đó để biết gate nạp và cách lọc chunk theo section.
