# Kho doanh nghiệp giả lập

Toàn bộ tài liệu, người duyệt, lịch sử gửi, kết quả CRM và điểm trong thư mục này đều **hư cấu**. Sáu proposal tái sử dụng nội dung từ bộ benchmark; metadata giả lập đủ bốn ô thắng/thua × viết tốt/kém. Một proposal thua có nội dung tốt không được biến thành mẫu xấu, và một proposal thắng có nội dung kém không được dùng làm mẫu vàng.

`records.json` chứa ba thắng/viết tốt, một thắng/viết kém, một thua/viết tốt và một thua/viết kém. Nhãn kết quả là fixture CRM nhập tay. Điểm chất lượng là fixture của **mock scoring API**, có `quality_provenance.method = mock_scoring_api`; chưa có API scorer thật nên không mô tả chúng là điểm hệ thống đã chạy. Chế độ production của `tools/repository_policy.py` từ chối các điểm mock này; chế độ demo chỉ chấp nhận khi tài liệu được đánh dấu fictional. Khi tích hợp, thay điểm fixture bằng kết quả API lúc nạp và lưu scorer_version, rubric_version, scored_at, input hash và người rà soát nếu có.

Các bản dùng giữa các deal nằm trong `sanitized/`: tên khách/nhà cung cấp và số tiền cụ thể được thay bằng placeholder, còn khoảng giá trị phân khúc chỉ nằm trong metadata. `chunks.jsonl` cắt theo heading và vai trò như pricing, timeline, support_sla, risks, solution; không cắt theo số ký tự. Mỗi chunk giữ record_id, section_path và metadata lọc ngành/quốc gia/loại dịch vụ/kết quả/điểm.

`standards.json` có một rate card, một bảng SLA/năng lực delivery, ba điều khoản mẫu với người/ngày duyệt và ngôn ngữ giả lập, cùng một lịch sử review. Các câu điều khoản chỉ là nguồn văn bản demo, không phải văn bản đã được pháp chế thật duyệt. Giá trong rate card là chuẩn công ty hư cấu, không lấy từ proposal khách khác.

Luồng n8n để tích hợp:

1. Nhận bản đã gửi và metadata CRM; không nạp draft.
2. Gọi API chấm trên **nguyên văn RFP + proposal**, không dùng các chunk RAG để thay thế tài liệu đầu vào.
3. Lưu điểm và nguồn gốc phép chấm; giữ nhãn chất lượng độc lập với won/lost/pending. Điểm 3 đến dưới 4 là intermediate, không ép thành tốt/kém.
4. Nếu dùng giữa các deal, tạo bản ẩn danh, kiểm tra tên khách và số tiền, rồi duyệt lại trước khi bật cross_deal_use. Cờ metadata tự khai không chứng minh nội dung đã sạch; production cần bước kiểm tra nội dung thật.
5. Chạy admission gate. Tài liệu thiếu metadata bị từ chối. Rate card/SLA cũ hơn sáu tháng được đánh dấu cần kiểm tra lại và không được dùng để khẳng định chuẩn hiện hành; có thể giữ để tra cứu lịch sử.
6. Cắt theo section và index cả metadata lẫn nội dung. Lọc metadata trước khi tìm đoạn phù hợp. Kho phát triển theo thời gian, và lỗi kho không chặn phần chấm chính.

Truy vấn demo: lọc `outcome = won`, `quality_score >= 4`, `industry = Business services`, `country = DE`, rồi lấy chunk `section_role = pricing`. Chỉ nói “3/3” khi truy vấn thật sự trả về ba bản hợp lệ đáp ứng cùng điều kiện; không suy diễn kết quả từ kích thước fixture.

Để demo ba mẫu vàng trong fixture này, lọc won, quality_score >= 4, country = DE và service_type = Custom software implementation, chưa lọc ngành. Kết quả có ba proposal thuộc ba ngành khác nhau; không gọi chúng là ba bản cùng ngành. Bộ nhỏ này chỉ có một mẫu vàng cho từng ngành, cần thêm dữ liệu nếu muốn demo so sánh ba bản cùng ngành logistics.

`history` là nguồn tiêu chí có thể mở rộng sau này, cần bằng chứng tài liệu công ty và cấu hình bật riêng. Bộ hiện tại giữ ba nguồn base/ai/custom đúng như bạn xác nhận. Bảng Criteria bốn cột hiển thị Criterion, Source, Priority, Evidence và người dùng chốt trước khi chấm có trọng số. Rubric benchmark hiện tại dùng trung bình bảy tiêu chí gốc để việc so sánh ban đầu có cùng chuẩn.
