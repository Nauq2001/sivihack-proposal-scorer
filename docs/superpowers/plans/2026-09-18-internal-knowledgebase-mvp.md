# Internal Knowledgebase MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Thêm knowledgebase local có thể nhận file `.md`/`.txt` và semantic search ngay sau khi index.

**Architecture:** `KnowledgeService` lưu file, metadata JSONL và NumPy vectors; model embedding được inject để unit test không cần mạng. FastAPI chỉ chuyển request sang service dùng chung.

**Tech Stack:** Python, NumPy, Sentence Transformers, FastAPI, unittest.

**Spec:** `docs/superpowers/specs/2026-09-18-internal-knowledgebase-mvp-design.md`

## Global Constraints

- Chỉ `.md` và `.txt`, tối đa 2 MB, UTF-8.
- Không database hoặc vector database.
- Knowledgebase tách biệt khỏi benchmark RAG.
- Unit test dùng fake embedder.

---

### Task 1: KnowledgeService local

**Files:**
- Create: `backend/knowledge/__init__.py`
- Create: `backend/knowledge/service.py`
- Create: `backend/tests/test_knowledge.py`

**Interfaces:**
- Produces: `KnowledgeService.add_document(filename: str, content: bytes) -> dict`
- Produces: `KnowledgeService.search(query: str, top_k: int = 5) -> list[dict]`

- [ ] **Step 1: Viết test thất bại cho add, duplicate và search**

```python
def test_add_and_search_document(self):
    result = service.add_document("policy.md", b"# Data residency\nBackups remain in EU regions.")
    matches = service.search("Where are backups stored?", top_k=1)
    self.assertEqual(result["status"], "indexed")
    self.assertEqual(matches[0]["filename"], "policy.md")

def test_duplicate_content_is_rejected(self):
    service.add_document("one.txt", b"same content")
    with self.assertRaisesRegex(ValueError, "already exists"):
        service.add_document("two.txt", b"same content")
```

- [ ] **Step 2: Chạy test và xác nhận FAIL do module chưa tồn tại**

Run: `py -3 -m unittest backend.tests.test_knowledge -v`

- [ ] **Step 3: Implement service tối thiểu**

Service validate input, SHA-256 nội dung, chunk bằng helper RAG hiện có, lưu file/records/vectors và cosine-search top-k.

- [ ] **Step 4: Chạy test và xác nhận PASS**

Run: `py -3 -m unittest backend.tests.test_knowledge -v`

- [ ] **Step 5: Commit**

```bash
git add backend/knowledge backend/tests/test_knowledge.py
git commit -m "feat: add local internal knowledgebase"
```

---

### Task 2: FastAPI endpoints và tài liệu

**Files:**
- Modify: `backend/main.py`
- Modify: `backend/requirements.txt`
- Create: `backend/tests/test_knowledge_http.py`
- Create: `backend/knowledge/README.md`

**Interfaces:**
- Produces: `POST /knowledge/files`
- Produces: `POST /knowledge/search`

- [ ] **Step 1: Viết HTTP test thất bại**

```python
def test_upload_and_search(self):
    upload = client.post(
        "/knowledge/files",
        files={"file": ("policy.md", b"# Policy\nBackups stay in EU regions.", "text/markdown")},
    )
    self.assertEqual(upload.status_code, 200)
    search = client.post("/knowledge/search", json={"query": "backup location", "top_k": 1})
    self.assertEqual(search.json()["matches"][0]["filename"], "policy.md")
```

- [ ] **Step 2: Chạy test và xác nhận FAIL vì route chưa tồn tại**

Run: `backend/.venv/Scripts/python.exe -m unittest backend.tests.test_knowledge_http -v`

- [ ] **Step 3: Implement endpoints**

Khởi tạo một `KnowledgeService`, thêm `UploadFile` endpoint và Pydantic search request. Thêm `python-multipart` vào requirements.

- [ ] **Step 4: Viết README với curl và Python examples**

README ghi rõ storage paths, giới hạn file và cách gọi hai endpoint.

- [ ] **Step 5: Chạy full test suite**

Run: `backend/.venv/Scripts/python.exe -m unittest discover -s backend/tests -v`

- [ ] **Step 6: Commit**

```bash
git add backend/main.py backend/requirements.txt backend/knowledge backend/tests/test_knowledge_http.py
git commit -m "feat: expose internal knowledgebase API"
```
