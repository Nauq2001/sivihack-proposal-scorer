# Internal Knowledgebase MVP

Kho kiến thức nội bộ chạy local, tách biệt với benchmark RAG. MVP nhận file UTF-8 `.md` hoặc `.txt` tối đa 2 MB, lưu file gốc, chunk nội dung và tạo embedding bằng `all-MiniLM-L6-v2`.

## Chạy backend

```powershell
backend/.venv/Scripts/python.exe -m uvicorn backend.main:app --port 8000
```

## Thêm tài liệu

```powershell
curl.exe -X POST http://localhost:8000/knowledge/files `
  -F "file=@company-policy.md"
```

## Tìm kiếm

```powershell
curl.exe -X POST http://localhost:8000/knowledge/search `
  -H "Content-Type: application/json" `
  -d '{"query":"Where may backups be stored?","top_k":3}'
```

Kết quả gồm `document_id`, `filename`, `section`, `text` và cosine `score`.

## Lưu trữ

Runtime data nằm trong `backend/knowledge/data/`:

- `files/`: file gốc;
- `records.jsonl`: metadata và chunks;
- `embeddings.npz`: vector index.

Thư mục này bị Git ignore vì chứa dữ liệu nội bộ. Nội dung trùng SHA-256 bị từ chối, kể cả khi tên file khác nhau.

## Python API

```python
from pathlib import Path
from backend.knowledge import KnowledgeService
from backend.rag.embedding import SentenceEmbedder

service = KnowledgeService(
    Path("backend/knowledge/data"),
    SentenceEmbedder(),
)
service.add_document("policy.md", Path("policy.md").read_bytes())
matches = service.search("backup location", top_k=3)
```
