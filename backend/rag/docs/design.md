# Thiết kế Scoring RAG hybrid — MVP

Tài liệu đầy đủ của quyết định MVP nằm tại [`docs/superpowers/specs/2026-09-18-local-hybrid-rag-design.md`](../../../docs/superpowers/specs/2026-09-18-local-hybrid-rag-design.md). Hướng dẫn chạy và contract tích hợp nằm trong [`backend/rag/README.md`](../README.md).

## Trách nhiệm

Scoring RAG truy xuất ví dụ benchmark theo từng criterion. Nó không tạo criterion, không chấm điểm cuối cùng và không cung cấp citation cho proposal hiện tại.

```text
Markdown benchmark
    -> ingest và chunk theo section
    -> records.jsonl
    -> all-MiniLM-L6-v2
    -> embeddings.npz

criterion + proposal/RFP context
    -> keyword score + cosine semantic score
    -> weighted hybrid score
    -> threshold và cân bằng sample type
    -> prompt-safe matches
```

## Thành phần

| File | Trách nhiệm |
|---|---|
| `ingest.py` | Tách Markdown theo heading và tạo chunk ổn định |
| `embedding.py` | Load `all-MiniLM-L6-v2` và tạo vector chuẩn hóa |
| `index.py` | Ghi/nạp NumPy `.npz` và kiểm tra thứ tự record |
| `engine.py` | Lọc criterion, tính hybrid score, threshold và deduplicate |
| `api.py` | Kiểm tra payload, public projection và format prompt block |
| `build_index.py` | CLI tạo `embeddings.npz` từ `records.jsonl` |

## Retrieval

Base criterion chỉ tìm trong record cùng canonical ID; custom criterion tìm toàn corpus. Mỗi candidate nhận:

```text
hybrid_score = 0.35 * keyword_score + 0.65 * semantic_score
```

Kết quả dưới `min_hybrid_score` bị loại. Trong mỗi nhóm `weak`, `medium`, `strong`, `overpromise`, chỉ lấy tối đa `top_k_per_type` và không lặp `source_file`.

Public adapter chỉ trả `text`, `sample_type`, `reasoning`. Metadata và retrieval score không đi vào contract của team tích hợp.

## Chunking

Chunking giữ ranh giới section. Section dài hơn 180 từ được chia với overlap 25 từ; heading được lặp lại ở mỗi chunk. ID chunk được tạo ổn định từ parent record và chỉ số chunk.

## Giới hạn MVP

MVP dùng linear NumPy search, một model local cố định và baseline threshold. Chưa có vector database, provider abstraction, evaluation framework đầy đủ, monitoring hoặc production fallback.
