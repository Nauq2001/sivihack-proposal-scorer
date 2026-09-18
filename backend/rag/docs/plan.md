# Kế hoạch triển khai Scoring RAG

> **Dành cho agent triển khai:** Dùng kỹ năng `superpowers:subagent-driven-development` (khuyến nghị) hoặc `superpowers:executing-plans` để thực hiện lần lượt các nhiệm vụ. Dùng ô đánh dấu (`- [ ]`) để theo dõi.
>
> **Trạng thái tài liệu:** Đây là kế hoạch ban đầu, chưa được cập nhật thành danh sách công việc đã hoàn thành. Các đường dẫn và lệnh kiểm thử bên dưới là dự kiến ở thời điểm lập kế hoạch. Bản hiện tại dùng truy xuất từ khóa trong Python, hỗ trợ custom criteria, chưa dùng SQLite FTS5 hay embedding. Xem [README hướng dẫn tích hợp hiện tại](../README.md).

**Mục tiêu:** Xây RAG từ benchmark Markdown để Scoring Agent tra cứu theo từng tiêu chí khi đánh giá proposal chưa từng thấy.

**Kiến trúc:** Nạp Markdown ngoại tuyến thành các bản ghi theo tiêu chí. Trả ví dụ đã lọc và cân bằng qua `POST /rag/retrieve`; agent dùng để tham khảo cách chấm, còn trích dẫn phải đến từ RFP và proposal hiện tại.

**Công nghệ dự kiến:** Python, FastAPI, SQLite FTS5 để tìm từ khóa dự phòng, thư viện Gemini hiện có khi bật embedding ngữ nghĩa, JSON qua HTTP.

---

## Nhiệm vụ 1: Định nghĩa cấu trúc kho benchmark

**Các file:**

- Tạo: `backend/rag/schema.py`
- Tạo: `backend/rag/README.md`
- Kiểm thử: `backend/tests/test_rag_schema.py`

- [ ] **Bước 1: Viết test thất bại** kiểm tra bản ghi bắt buộc có `criterion_id`, `sample_type`, `score`, `text`, `source_file` và từ chối loại mẫu không hợp lệ.
- [ ] **Bước 2: Chạy** `python -m pytest backend/tests/test_rag_schema.py -v`; kỳ vọng thất bại vì chưa có module schema.
- [ ] **Bước 3: Triển khai** mô hình Pydantic cho `BenchmarkRecord` và mô hình dữ liệu gửi/trả của truy xuất. Chấp nhận `weak`, `medium`, `strong`, `overpromise`.
- [ ] **Bước 4: Chạy lại** test; kỳ vọng đạt.
- [ ] **Bước 5: Commit** `feat: define scoring rag records`.

## Nhiệm vụ 2: Nạp Markdown

**Các file:**

- Tạo: `backend/rag/ingest.py`
- Tạo: `backend/rag/data/records.jsonl`
- Kiểm thử: `backend/tests/test_rag_ingest.py`

- [ ] **Bước 1: Viết test thất bại** với mẫu Markdown nhỏ có tiêu đề, kiểm tra việc nạp giữ được tiêu đề, file nguồn và loại mẫu.
- [ ] **Bước 2: Chạy** `python -m pytest backend/tests/test_rag_ingest.py -v`; kỳ vọng thất bại vì chưa có phần nạp.
- [ ] **Bước 3: Triển khai** bộ tách Markdown bằng thư viện chuẩn, bắt đầu đoạn mới tại `#`, `##` hoặc `###`, giữ tiêu đề cùng nội dung và xuất JSONL. Không tách bảng hay danh sách khỏi tiêu đề của chúng.
- [ ] **Bước 4: Thêm file ánh xạ** cho 100 mẫu dự kiến, gán từng file nguồn vào `weak`, `medium`, `strong` hoặc `overpromise`; không suy nhãn từ nội dung.
- [ ] **Bước 5: Chạy** test rồi nạp thư mục dữ liệu thật; kỳ vọng JSONL hợp lệ và không có bản ghi rỗng.
- [ ] **Bước 6: Commit** `feat: ingest markdown benchmark cases`.

## Nhiệm vụ 3: Triển khai truy xuất

**Các file:**

- Tạo: `backend/rag/store.py`
- Tạo: `backend/rag/retrieve.py`
- Kiểm thử: `backend/tests/test_rag_retrieve.py`

- [ ] **Bước 1: Viết test thất bại** truy vấn `timeline`, chỉ trả bản ghi lịch trình và tối đa một kết quả mỗi loại khi `top_k_per_type=1`.
- [ ] **Bước 2: Chạy** `python -m pytest backend/tests/test_rag_retrieve.py -v`; kỳ vọng thất bại.
- [ ] **Bước 3: Triển khai** index SQLite FTS5 cho `text`, `section`, `reasoning`, kèm cột metadata cho tiêu chí và loại mẫu.
- [ ] **Bước 4: Triển khai** lọc rồi xếp hạng theo từng loại. Trả ít hơn bốn kết quả khi một loại không có bản ghi liên quan.
- [ ] **Bước 5: Thêm xếp hạng ngữ nghĩa** bằng dịch vụ embedding Gemini hiện có khi đã cấu hình API key; giữ FTS5 làm phương án dự phòng có kết quả xác định.
- [ ] **Bước 6: Chạy** test truy xuất và bốn truy vấn kiểm tra nhanh về lịch trình, giá, độ đầy đủ, mâu thuẫn; kỳ vọng đạt.
- [ ] **Bước 7: Commit** `feat: add benchmark retrieval`.

## Nhiệm vụ 4: Cung cấp endpoint tích hợp

**Các file:**

- Sửa: `backend/main.py`
- Tạo: `backend/rag/api.py`
- Kiểm thử: `backend/tests/test_rag_api.py`
- Sửa: `docs/api/review-contract.md`

- [ ] **Bước 1: Viết test API thất bại** cho `POST /rag/retrieve` với dữ liệu gửi trong thiết kế; kiểm tra JSON trả về có `matches`.
- [ ] **Bước 2: Chạy** `python -m pytest backend/tests/test_rag_api.py -v`; kỳ vọng thất bại vì chưa có route.
- [ ] **Bước 3: Triển khai** route dùng mô hình Pydantic và kho cục bộ. Trả `400` nếu thiếu ID tiêu chí hoặc ngữ cảnh proposal; trả `200` cùng danh sách rỗng khi không có kết quả.
- [ ] **Bước 4: Bổ sung** cấu trúc dữ liệu gửi/trả vào tài liệu API và hướng dẫn team AI gọi `http://<backend-host>:8000/rag/retrieve` một lần mỗi tiêu chí.
- [ ] **Bước 5: Chạy** test API và `python -m py_compile backend/main.py backend/rag/*.py`; kỳ vọng đạt. Lệnh wildcard này cần shell hỗ trợ mở rộng tên file.
- [ ] **Bước 6: Commit** `feat: expose scoring rag api`.

## Nhiệm vụ 5: Nối Scoring Agent và kiểm tra toàn luồng

**Các file:**

- Sửa: module prompt/client trong repo Scoring Agent.
- Tài liệu tích hợp hiện được đặt tại `backend/rag/README.md`.

- [ ] **Bước 1: Thêm lời gọi** gửi `criterion`, `proposal_context`, `requirement_context` đến `/rag/retrieve`.
- [ ] **Bước 2: Đưa ví dụ trả về** vào phần prompt có nhãn rõ `BENCHMARK REFERENCES`.
- [ ] **Bước 3: Thêm quy tắc prompt:** `final_criteria` là căn cứ chính thức, benchmark không phải bằng chứng trích dẫn, nội dung thiếu bằng chứng vẫn phải đánh dấu thiếu.
- [ ] **Bước 4: Chạy agent** trên bốn proposal mẫu hiện có, ghi lại thứ tự điểm và các mâu thuẫn trong mẫu hứa quá mức.
- [ ] **Bước 5: Chạy agent** trên một cặp RFP/proposal chưa thấy, kiểm tra từng câu trích có trong đầu vào hiện tại.
- [ ] **Bước 6: Commit** phần gọi tích hợp và tài liệu trong repo của team AI.

## Hợp đồng bàn giao dự kiến

Theo kế hoạch ban đầu, team AI gọi:

```text
POST http://<rag-host>:8000/rag/retrieve
Content-Type: application/json
```

Kết quả là ngữ cảnh tham chiếu, không phải điểm cuối cùng. Kế hoạch ban đầu giữ cấu trúc trả về của `POST /api/review`. Quyết định mới dùng hàm Python nội bộ và giao schema scoring cho team AI; xem tài liệu tích hợp hiện tại ở đầu trang.
