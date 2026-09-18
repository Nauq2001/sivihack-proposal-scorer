# Thiết kế MVP/PoC RAG hybrid chạy local

## 1. Mục tiêu

Xây bản PoC chứng minh RAG có thể tìm benchmark bằng ngữ nghĩa tốt hơn cơ chế trùng từ khóa hiện tại, đặc biệt với từ đồng nghĩa và custom criterion.

MVP sử dụng `sentence-transformers/all-MiniLM-L6-v2` chạy local, kết hợp semantic score với keyword score. Phần tích hợp vào Scoring Agent và endpoint `/api/review` do team khác thực hiện.

Kết quả demo cần chứng minh được một query dùng cách diễn đạt khác với benchmark vẫn đưa ví dụ phù hợp lên đầu.

## 2. Phạm vi MVP

MVP gồm:

- chunk benchmark Markdown thành các đoạn ngắn;
- tạo embedding local bằng `all-MiniLM-L6-v2`;
- lưu vector vào `backend/rag/data/embeddings.npz`;
- kết hợp keyword score và semantic score;
- giữ cách lọc criterion, cân bằng sample type và loại trùng nguồn;
- cung cấp helper để team Scoring Agent lấy block `BENCHMARK REFERENCES`;
- thêm test tối thiểu và hướng dẫn chạy.

Ngoài phạm vi:

- triển khai `/api/review` và prompt chấm điểm cuối cùng;
- FAISS, Chroma hoặc vector database;
- nhiều embedding provider/model;
- evaluation framework đầy đủ như Recall@k hoặc MRR;
- production fallback, monitoring và tối ưu deployment;
- citation validation và thay đổi frontend.

## 3. Luồng xử lý

```text
Benchmark Markdown
    -> chunk theo section
    -> records.jsonl
    -> all-MiniLM-L6-v2
    -> embeddings.npz

Query
    -> keyword score + cosine semantic score
    -> hybrid score
    -> threshold
    -> cân bằng weak/medium/strong/overpromise
    -> BENCHMARK REFERENCES
```

Các file chính:

- `backend/rag/ingest.py`: tạo chunk và `records.jsonl`.
- `backend/rag/embedding.py`: load model và encode text/query.
- `backend/rag/index.py`: tạo và nạp `embeddings.npz`.
- `backend/rag/engine.py`: tính điểm và chọn kết quả.
- `backend/rag/api.py`: giữ public response và format reference.

## 4. Chunking

Chunking giữ ranh giới heading Markdown:

- section tối đa 180 từ trở thành một chunk;
- section dài hơn được chia thành chunk 120–180 từ;
- overlap mục tiêu khoảng 25 từ;
- heading được thêm vào đầu mỗi chunk;
- không ghép các section không liền nhau.

Mỗi record giữ các trường cần thiết:

```json
{
  "id": "case:response:criterion:chunk:000",
  "parent_record_id": "case:response:criterion",
  "chunk_index": 0,
  "criterion_id": "timeline_clarity",
  "sample_type": "strong",
  "section": "Delivery plan",
  "text": "## Delivery plan\n...",
  "score_range": [4, 5],
  "reasoning": "...",
  "source_file": "cases/example/response.md"
}
```

Chạy ingest nhiều lần với cùng input phải tạo cùng ID và thứ tự.

## 5. Embedding và vector index

Model cố định:

```text
sentence-transformers/all-MiniLM-L6-v2
```

`embeddings.npz` chỉ cần chứa:

- `vectors`: mảng `float32` có shape `(record_count, 384)`;
- `record_ids`: ID theo đúng thứ tự vector;
- `model_name`: tên model dùng để tạo index.

Vector document và query đều được L2-normalize. Semantic score được tính bằng dot product, tương đương cosine similarity.

Khi khởi động, store nạp `records.jsonl`, `embeddings.npz` và model một lần. Nếu thiếu index hoặc số vector không khớp số record, hệ thống báo lỗi yêu cầu tạo lại index. MVP không cần hệ thống version/digest phức tạp.

## 6. Hybrid retrieval

Query được ghép từ:

- `criterion.name`;
- `criterion.description`;
- `criterion.evaluation_question`;
- `proposal_context`;
- `requirement_context`.

Điểm được tính như sau:

```text
keyword_score = số query term khác nhau khớp / số query term hợp lệ
semantic_score = (cosine_similarity + 1) / 2
hybrid_score = 0.35 * keyword_score + 0.65 * semantic_score
```

Base criterion chỉ tìm trong record cùng criterion ID. Custom criterion tìm trên toàn corpus. Kết quả dưới `min_hybrid_score` bị loại.

Trong mỗi loại `weak`, `medium`, `strong`, `overpromise`, hệ thống lấy tối đa `top_k_per_type` kết quả và không lấy hai chunk từ cùng `source_file`.

Các score chỉ dùng nội bộ. Public match vẫn chỉ trả:

```json
{
  "text": "...",
  "sample_type": "strong",
  "reasoning": "..."
}
```

## 7. Public API cho team tích hợp

Payload:

```json
{
  "criterion": {
    "id": "custom_data_residency",
    "name": "EU data residency",
    "description": "Production records and backups must stay in EU regions"
  },
  "proposal_context": "Production records remain in Frankfurt.",
  "requirement_context": "All records must remain in the EU.",
  "top_k_per_type": 1,
  "min_hybrid_score": 0.45
}
```

Quy tắc:

- `top_k_per_type`: số nguyên từ 1 đến 3, mặc định `1`;
- `min_hybrid_score`: số từ 0 đến 1, mặc định `0.45`;
- bỏ trường `relevance_threshold` cũ để contract dễ hiểu.

`retrieve_payload()` giữ nguyên outer response hiện tại. Thêm helper:

```python
def retrieve_benchmark_references(store, payload) -> str:
    result = retrieve_payload(store, payload)
    return format_benchmark_references(result["matches"])
```

Team Scoring Agent gọi helper một lần cho mỗi criterion phù hợp và chèn kết quả vào prompt. Benchmark chỉ là dữ liệu hiệu chỉnh, không phải bằng chứng; citation vẫn phải đến từ RFP và proposal hiện tại.

## 8. Test và tiêu chí hoàn thành

Unit test sử dụng fake embedder để không tải model hoặc truy cập mạng. Các test tối thiểu:

- chunk giữ heading và không vượt giới hạn chính;
- vector index tạo/nạp đúng thứ tự record;
- công thức hybrid score đúng;
- lọc criterion, threshold, cân bằng sample type và loại trùng nguồn;
- public match chỉ có ba trường an toàn;
- helper trả block có nhãn `BENCHMARK REFERENCES`.

Smoke test model thật xác nhận một query dùng từ đồng nghĩa xếp đúng benchmark cao hơn text không liên quan.

MVP hoàn thành khi:

1. Có thể tạo lại `records.jsonl` và `embeddings.npz` bằng lệnh được ghi trong README.
2. Unit test pass mà không cần mạng.
3. Smoke test với `all-MiniLM-L6-v2` pass sau khi model đã được tải.
4. Demo được ít nhất một trường hợp hybrid search tìm tốt hơn keyword-only.
5. Team khác có thể gọi `retrieve_benchmark_references()` mà không cần biết chi tiết vector search.

## 9. Tài liệu bàn giao

`backend/rag/README.md` cần bổ sung:

- cách cài `sentence-transformers` và NumPy;
- cách tạo records và vector index;
- ví dụ gọi `retrieve_payload()` và `retrieve_benchmark_references()`;
- cách chạy unit test và smoke test;
- lưu ý model được tải về máy ở lần chạy đầu tiên.
