# Thiết kế MVP Internal Knowledgebase

## Mục tiêu

Cho phép backend nhận tài liệu nội bộ dạng Markdown hoặc text, lưu local, tạo embedding và tìm lại các đoạn liên quan bằng semantic search. Knowledgebase này tách biệt với benchmark RAG hiện tại.

## Phạm vi

MVP gồm:

- upload `.md` và `.txt`, tối đa 2 MB;
- lưu file gốc trong `backend/knowledge/data/files/`;
- chunk theo heading và giới hạn độ dài;
- tạo embedding bằng model local `all-MiniLM-L6-v2`;
- lưu metadata trong `records.jsonl` và vector trong `embeddings.npz`;
- chống file trùng bằng SHA-256;
- Python API và hai HTTP endpoint để thêm/tìm tài liệu.

Không gồm auth, multi-user, sửa/xóa file, PDF/DOCX, OCR, cloud storage hoặc vector database.

## Cấu trúc

```text
backend/knowledge/
├── __init__.py
├── service.py
├── data/
│   ├── files/
│   ├── records.jsonl
│   └── embeddings.npz
└── README.md
```

`service.py` tái sử dụng `SentenceEmbedder` từ `backend.rag.embedding`.

## Luồng cập nhật

```text
file
  → validate extension/size/UTF-8
  → SHA-256 và kiểm tra trùng
  → lưu file gốc
  → chunk
  → encode toàn bộ records
  → ghi records.jsonl và embeddings.npz
  → reload store
```

MVP ghi lại toàn bộ vector index khi thêm file. Cách này đủ cho corpus nhỏ và tránh thêm database.

## API

### Python

```python
add_document(filename: str, content: bytes) -> dict
search_knowledge(query: str, top_k: int = 5) -> list[dict]
```

### HTTP

```http
POST /knowledge/files
Content-Type: multipart/form-data
```

Response:

```json
{
  "document_id": "sha256...",
  "filename": "company-policy.md",
  "chunk_count": 3,
  "status": "indexed"
}
```

```http
POST /knowledge/search
Content-Type: application/json
```

Request:

```json
{"query": "Where may backups be stored?", "top_k": 3}
```

Response:

```json
{
  "matches": [
    {
      "document_id": "sha256...",
      "filename": "company-policy.md",
      "section": "Data residency",
      "text": "...",
      "score": 0.81
    }
  ]
}
```

## Quy tắc

- Knowledgebase rỗng trả `matches: []`.
- Query rỗng, extension sai, file quá lớn hoặc nội dung không phải UTF-8 trả lỗi rõ ràng.
- Nội dung trùng bị từ chối, kể cả filename khác.
- Unit test dùng fake embedder, không tải model hoặc gọi mạng.
- Ghi artifact mới xong mới thay artifact cũ để tránh index dở dang.
