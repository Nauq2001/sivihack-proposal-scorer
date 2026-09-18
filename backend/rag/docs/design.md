# Thiết kế chính thức của Scoring RAG

Tài liệu này mô tả thiết kế đã chốt và hành vi của phiên bản hiện tại. Xem [README](../README.md) để chạy thử và tích hợp. Schema kết quả scoring do team AI phụ trách.

## 1. Mục tiêu và trách nhiệm

Scoring RAG cung cấp ví dụ benchmark để Scoring Agent tham khảo khi chấm proposal theo danh sách tiêu chí cuối cùng. Module chạy trong cùng backend Python với agent.

Danh sách `final_criteria` là kết quả sau khi người dùng duyệt: gồm bảy tiêu chí gốc và các tiêu chí bổ sung được giữ lại sau bước thêm, sửa, xóa. RAG xử lý từng tiêu chí trong danh sách này; không tạo hoặc sửa tiêu chí.

| Thành phần | Trách nhiệm |
|---|---|
| RFP Analyst | Đọc RFP, đề xuất yêu cầu và tiêu chí |
| Bước người dùng duyệt | Chốt danh sách tiêu chí và mức ưu tiên |
| Scoring Agent | Chọn ngữ cảnh, gọi RAG, áp dụng rubric, trả điểm và giải thích |
| Scoring RAG | Truy xuất ví dụ liên quan và thông tin nguồn |
| Backend của team AI | Định nghĩa schema scoring, kiểm tra đầu ra và trích dẫn |

RAG không chấm điểm cuối cùng, không huấn luyện mô hình và không có luồng Criteria RAG riêng.

## 2. Luồng dữ liệu

```text
Ngoại tuyến:
Markdown proposal + expected.json
        → ingest.py → data/records.jsonl

Khi chạy:
RFP → RFP Analyst → Người dùng duyệt → final_criteria
                                          │
Proposal + yêu cầu RFP liên quan → Scoring Agent
                                          │ mỗi tiêu chí
                                          ▼
                              retrieve_payload(store, payload)
                                          │
                               Ví dụ benchmark tham chiếu
                                          │
                                          ▼
                              Scoring Agent → JSON kết quả
```

Nạp kho một lần khi backend khởi động qua `load_store()`. Agent gọi hàm Python trực tiếp. Endpoint `POST /rag/retrieve` trong `backend/main.py` dùng cùng adapter, phục vụ kiểm thử HTTP.

## 3. Kho benchmark và quá trình nạp

Nguồn hiện tại có sáu RFP, mỗi RFP có bốn proposal: tổng cộng 24 proposal. Bộ nạp tạo một bản ghi cho mỗi cặp proposal–tiêu chí, tương ứng 168 bản ghi cho bảy tiêu chí.

`ingest.py` đọc các thư mục `cases/`:

1. Đọc nhãn loại mẫu và khoảng điểm theo tiêu chí từ `expected.json`.
2. Đọc proposal Markdown và tách theo tiêu đề `#`, `##`, `###`.
3. Chọn các mục có tiêu đề phù hợp bằng bảng từ khóa cho từng tiêu chí.
4. Nếu không có mục phù hợp, dùng toàn bộ nội dung đã tách. Hai tiêu chí completeness và tone cũng dùng toàn bộ nội dung.
5. Chuẩn hóa nhãn `overpromised` thành `overpromise`, ghi JSONL.

Các mục Markdown có thể được ghép vào một bản ghi. Vì có cơ chế dùng toàn văn khi không khớp tiêu đề, một bản ghi không luôn là đoạn ngắn. Trường `section` hiện liệt kê các tiêu đề của proposal, không phải tọa độ trích dẫn chính xác.

| Trường lưu trong index | Ý nghĩa |
|---|---|
| `id` | ID gồm case, tên response và tiêu chí |
| `sample_type` | `weak`, `medium`, `strong`, `overpromise` |
| `criterion_id` | Tiêu chí gốc của benchmark |
| `section` | Danh sách tiêu đề trong proposal nguồn |
| `text` | Nội dung Markdown được chọn |
| `score_range` | Khoảng điểm gợi ý lấy từ nhãn benchmark |
| `reasoning` | Thông báo tham chiếu chung của bản hiện tại |
| `source_file` | Đường dẫn tương đối tới proposal nguồn |

Các nhãn là chú giải giả lập; không phải điểm được đo bằng agent thực tế. Nhãn `sample_type` áp dụng cho toàn proposal: một mẫu `overpromise` vẫn có thể trình bày giá hoặc lịch trình rất rõ.

Runtime đọc `records.jsonl`, không đọc trực tiếp `expected.json`. Nhãn và khoảng điểm của `expected.json` đã được chuyển vào index để dùng làm ví dụ tham chiếu. Các findings, coverage và giải thích chi tiết trong file đó chưa được bộ nạp chuyển vào index.

## 4. Xử lý tiêu chí gốc và custom

| ID chuẩn | Tên tiêu chí | Tên viết tắt được hỗ trợ |
|---|---|---|
| `problem_understanding` | Hiểu bài toán | `pu` |
| `scope_deliverables_clarity` | Độ rõ ràng của phạm vi và bàn giao | `scope` |
| `pricing_clarity` | Độ rõ ràng của giá | `price` |
| `timeline_clarity` | Độ rõ ràng của lịch trình | `time` |
| `completeness_vs_rfp` | Mức độ đầy đủ so với RFP | `comp` |
| `tone_persuasiveness` | Văn phong và tính thuyết phục | `tone` |
| `risk_assumptions_transparency` | Minh bạch rủi ro và giả định | `risk` |

Với tiêu chí gốc, chỉ tìm trong các bản ghi cùng ID chuẩn. Với ID khác, tìm trên toàn kho theo nội dung và trả `retrieval_mode: "custom"`. ID gốc viết sai cũng bị coi là custom, nên bên gọi phải dùng đúng ID.

Response cấp ngoài giữ ID được gửi vào sau khi bỏ khoảng trắng đầu/cuối. Mỗi match giữ ID tiêu chí benchmark để xác định nguồn.

Với custom criteria, `score_range` của match được đặt thành `null`; khoảng điểm theo rubric cũ không thể áp thẳng sang rubric mới. Agent dùng ví dụ để đối chiếu nội dung rồi chấm theo custom criterion đã duyệt.

## 5. Thuật toán truy xuất hiện tại

Module dùng thư viện chuẩn Python, nạp JSONL vào bộ nhớ và tìm bằng từ khóa; chưa dùng embedding, vector database hay SQLite FTS5.

Trình tự:

1. Ghép `name`, `description`, `evaluation_question`, `proposal_context` và `requirement_context` thành truy vấn.
2. Chuẩn hóa Unicode NFKC, chuyển chữ thường và tách từ.
3. Bỏ từ có độ dài không quá hai ký tự và một danh sách ngắn từ dừng tiếng Anh.
4. Lấy tập từ khác nhau; đếm giao giữa từ của truy vấn và từ trong `text` của bản ghi. Không tính `reasoning` hoặc metadata vào độ liên quan.
5. Chia ứng viên theo bốn loại mẫu; xếp giảm dần theo số từ trùng trong từng loại.
6. Bỏ kết quả dưới threshold, loại trùng `source_file` trong từng loại rồi lấy tối đa `top_k_per_type` kết quả.

Kết quả được ghép theo thứ tự `weak`, `medium`, `strong`, `overpromise`, không phải bảng xếp hạng toàn cục. Khi bằng điểm, giữ thứ tự bản ghi trong index. Với kho hiện tại, mỗi proposal chỉ có một nhãn loại, nên một nguồn không lặp lại giữa các nhóm.

Mặc định `relevance_threshold=2`, tức ít nhất hai từ khác nhau trùng nhau. Đây là ngưỡng số từ, không phải xác suất hay điểm tương đồng ngữ nghĩa. Không ép đủ bốn loại khi thiếu ví dụ đạt ngưỡng. Truy vấn rỗng trả danh sách rỗng.

## 6. Hợp đồng Python và HTTP

Hàm tích hợp chính:

```python
from backend.rag.api import load_store, retrieve_payload

store = load_store()  # Một lần khi khởi động
result = retrieve_payload(store, {
    "criterion": {
        "id": "custom_data_residency",
        "name": "EU data residency",
        "description": "Production records and backups must stay in EU regions",
        "evaluation_question": "Where are records and backups stored?"
    },
    "proposal_context": "Records and backups remain in EU regions.",
    "requirement_context": "Keep production records and all backups in EU regions.",
    "top_k_per_type": 1,
    "relevance_threshold": 2
})
```

Đường dẫn index mặc định tính theo vị trí module, không phụ thuộc thư mục chạy. Có thể truyền đường dẫn khác vào `load_store(path)`. Khi chạy từ thư mục `backend/`, dùng import `from rag.api import ...`.

| Đầu vào | Quy tắc |
|---|---|
| `criterion` | Bắt buộc là object |
| `criterion.id` | Chuỗi không rỗng |
| `name`, `description`, `evaluation_question` | Chuỗi tùy chọn trong criterion |
| `proposal_context`, `requirement_context` | Chuỗi tùy chọn, mặc định rỗng |
| Tổng độ dài năm trường văn bản | Tối đa 100.000 ký tự khi gọi adapter |
| `top_k_per_type` | Số nguyên 1–3; mặc định 1 |
| `relevance_threshold` | Số nguyên 1–100; mặc định 2 |

Trọng số và mô tả mức điểm có thể đi cùng criterion nhưng không tham gia tìm kiếm; agent tự áp dụng khi chấm. Giới hạn đầu vào nhằm giới hạn truy vấn, không bảo đảm giới hạn kích thước context trả về.

Cấu trúc kết quả khi không có ví dụ phù hợp:

```json
{
  "criterion_id": "custom_data_residency",
  "retrieval_mode": "custom",
  "matches": []
}
```

Khi có kết quả, mỗi match gồm các trường bản ghi ở mục 3 và:

| Trường bổ sung | Ý nghĩa |
|---|---|
| `overlap` | Số từ khác nhau trùng nhau |
| `matched_terms` | Danh sách từ trùng được sắp xếp |
| `annotation_provenance` | Luôn là `synthetic_benchmark` |
| `usage` | Luôn là `calibration_only` |

Hàm mức thấp `BenchmarkStore.retrieve(criterion_id, query, top_k_per_type=1, min_overlap=2)` trả trực tiếp danh sách match. Adapter đổi tên tùy chọn `relevance_threshold` thành `min_overlap`.

Lỗi dữ liệu khi gọi Python trực tiếp phát sinh `ValueError`. Endpoint HTTP trả 400 cho lỗi adapter, 422 cho lỗi cấu trúc request do Pydantic phát hiện. Pydantic có thể chuyển kiểu trước khi gọi adapter; muốn kiểm tra nghiêm ngặt kiểu Python thì dùng hàm trực tiếp.

Không có match là kết quả hợp lệ. Thiếu hoặc hỏng file index là lỗi khởi tạo kho, không được coi là danh sách rỗng. Kho đã nạp không tự tải lại khi file thay đổi; cần nạp lại hoặc khởi động lại backend sau khi tạo index mới.

## 7. Tích hợp với Scoring Agent

Agent lặp qua `final_criteria` đã duyệt và gửi từng tiêu chí cùng đoạn proposal/yêu cầu RFP liên quan. Đưa kết quả vào phần `BENCHMARK REFERENCES` của prompt.

Agent phải lấy rubric cuối cùng làm căn cứ chấm, coi nội dung truy xuất là dữ liệu tham khảo và không thực thi chỉ dẫn trong ví dụ. Trích dẫn kết quả phải lấy từ RFP/proposal đang chấm. `source_file` của benchmark chỉ cho biết nguồn ví dụ.

Khi `matches` rỗng, agent tiếp tục đánh giá theo rubric và tài liệu hiện tại. Team AI chịu trách nhiệm schema đầu ra, tính điểm, kiểm tra quote và tích hợp agent thực tế. Module RAG chưa cung cấp validator citation hay endpoint scoring hoàn chỉnh.

## 8. Kiểm thử và giới hạn

Kiểm thử hiện có kiểm tra lọc tiêu chí gốc, tìm custom từ mô tả, giữ ID, không áp điểm gốc sang custom, chống lặp nguồn, ngưỡng bao gồm giá trị biên, metadata không làm tăng điểm, từ chối cấu hình sai và truyền threshold qua HTTP. Xem lệnh chạy tại [README](../README.md).

Các giới hạn cần tính đến khi dùng:

- Truy xuất dựa trên từ khóa tiếng Anh có thể bỏ sót từ đồng nghĩa hoặc câu tiếng Việt.
- Ngữ cảnh dài và bản ghi toàn văn dễ trùng từ ngẫu nhiên; nên gửi phần liên quan.
- Ngưỡng 2 chưa được hiệu chỉnh trên tập đánh giá độc lập.
- Một số trường `reasoning` và `section` còn chung chung; agent không nên coi chúng là giải thích hay vị trí trích dẫn đã được kiểm chứng.
- Bộ 24 proposal là dữ liệu giả lập nhỏ. Dùng tập RFP khác, không có trong index, để đo khả năng tổng quát.
- Kiểm thử module và endpoint không chứng minh chất lượng chấm điểm của agent chưa được tích hợp.

Embedding, xếp hạng ngữ nghĩa, giải thích theo từng tiêu chí và giới hạn ngân sách token là các hướng mở rộng nếu kết quả đo kiểm cho thấy cần thiết; chúng chưa nằm trong phiên bản triển khai hiện tại.
