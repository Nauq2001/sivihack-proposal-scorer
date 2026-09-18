# Local Hybrid RAG MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Xây MVP RAG hybrid chạy local bằng `all-MiniLM-L6-v2`, chunk benchmark theo section và cung cấp helper sẵn sàng để team Scoring Agent tích hợp.

**Architecture:** `ingest.py` tạo các chunk ổn định trong `records.jsonl`; `embedding.py` encode và chuẩn hóa vector; `index.py` lưu/nạp `.npz`; `engine.py` kết hợp keyword score với cosine semantic score. `api.py` giữ public response an toàn và thêm helper trả block `BENCHMARK REFERENCES`.

**Tech Stack:** Python 3, NumPy, sentence-transformers, unittest, FastAPI hiện có.

**Spec:** `docs/superpowers/specs/2026-09-18-local-hybrid-rag-design.md`

## Global Constraints

- Model cố định là `sentence-transformers/all-MiniLM-L6-v2`, vector 384 chiều.
- Hybrid score là `0.35 * keyword_score + 0.65 * semantic_score`.
- Unit test phải dùng fake embedder và không truy cập mạng.
- Public match chỉ gồm `text`, `sample_type`, `reasoning`.
- `/api/review`, frontend và prompt chấm điểm cuối cùng nằm ngoài phạm vi.

---

### Task 1: Chunk benchmark theo section

**Files:**
- Modify: `backend/rag/ingest.py`
- Create: `backend/tests/test_rag_ingest.py`

**Interfaces:**
- Produces: `chunk_sections(sections, min_words=120, max_words=180, overlap_words=25) -> list[tuple[str, str]]`
- Produces: record fields `parent_record_id`, `chunk_index`, stable chunk `id`

- [ ] **Step 1: Viết test thất bại cho section ngắn, section dài và ID ổn định**

```python
import unittest
from backend.rag.ingest import chunk_sections


class RagIngestChunkTests(unittest.TestCase):
    def test_short_section_keeps_heading(self):
        chunks = chunk_sections([("Delivery plan", "alpha beta gamma")])
        self.assertEqual(chunks, [("Delivery plan", "## Delivery plan\nalpha beta gamma")])

    def test_long_section_is_split_with_overlap(self):
        body = " ".join(f"word{i}" for i in range(260))
        chunks = chunk_sections([("Timeline", body)])
        self.assertEqual(len(chunks), 2)
        first_words = chunks[0][1].split()
        second_words = chunks[1][1].split()
        self.assertEqual(first_words[-25:], second_words[2:27])
        self.assertTrue(all(text.startswith("## Timeline\n") for _, text in chunks))
```

- [ ] **Step 2: Chạy test để xác nhận thất bại**

Run: `py -3 -m unittest backend.tests.test_rag_ingest -v`

Expected: FAIL vì chưa có `chunk_sections`.

- [ ] **Step 3: Cài đặt chunking tối thiểu**

```python
def chunk_sections(sections, min_words=120, max_words=180, overlap_words=25):
    chunks = []
    step = max_words - overlap_words
    for heading, body in sections:
        words = body.split()
        if len(words) <= max_words:
            chunks.append((heading, f"## {heading}\n{body}"))
            continue
        for start in range(0, len(words), step):
            piece = words[start:start + max_words]
            if not piece:
                break
            chunks.append((heading, f"## {heading}\n{' '.join(piece)}"))
            if start + max_words >= len(words):
                break
    return chunks
```

Sau đó sửa `build_records()` để tạo một record cho mỗi chunk, với `parent_record_id`, `chunk_index` và ID dạng `:chunk:000`.

- [ ] **Step 4: Chạy test ingest và test RAG hiện tại**

Run: `py -3 -m unittest backend.tests.test_rag_ingest backend.tests.test_rag -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/rag/ingest.py backend/tests/test_rag_ingest.py
git commit -m "feat: chunk rag benchmark sections"
```

---

### Task 2: Local embedder và NumPy vector index

**Files:**
- Create: `backend/rag/embedding.py`
- Create: `backend/rag/index.py`
- Create: `backend/tests/test_rag_index.py`
- Modify: `backend/requirements.txt`

**Interfaces:**
- Produces: `SentenceEmbedder.encode(texts: list[str]) -> numpy.ndarray`
- Produces: `build_index(records, embedder, output_path, model_name) -> None`
- Produces: `load_index(path, records) -> VectorIndex`
- Produces: `VectorIndex.vectors`, `VectorIndex.record_ids`, `VectorIndex.model_name`

- [ ] **Step 1: Viết test thất bại bằng fake embedder**

```python
import tempfile
import unittest
from pathlib import Path
import numpy as np

from backend.rag.index import build_index, load_index


class FakeEmbedder:
    def encode(self, texts):
        rows = np.array([[len(text), text.count("risk")] for text in texts], dtype=np.float32)
        norms = np.linalg.norm(rows, axis=1, keepdims=True)
        return rows / np.maximum(norms, 1e-12)


class RagIndexTests(unittest.TestCase):
    def test_index_round_trip_preserves_record_order(self):
        records = [{"id": "a", "text": "risk plan"}, {"id": "b", "text": "timeline"}]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "embeddings.npz"
            build_index(records, FakeEmbedder(), path, "fake")
            index = load_index(path, records)
        self.assertEqual(index.record_ids, ["a", "b"])
        self.assertEqual(index.vectors.shape, (2, 2))
        self.assertEqual(index.model_name, "fake")

    def test_index_rejects_record_count_mismatch(self):
        records = [{"id": "a", "text": "risk"}]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "embeddings.npz"
            build_index(records, FakeEmbedder(), path, "fake")
            with self.assertRaises(ValueError):
                load_index(path, records + [{"id": "b", "text": "timeline"}])
```

- [ ] **Step 2: Chạy test để xác nhận thất bại**

Run: `py -3 -m unittest backend.tests.test_rag_index -v`

Expected: FAIL vì chưa có module `backend.rag.index`.

- [ ] **Step 3: Cài đặt embedder và index tối thiểu**

`embedding.py`:

```python
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class SentenceEmbedder:
    def __init__(self, model_name=MODEL_NAME):
        from sentence_transformers import SentenceTransformer
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def encode(self, texts):
        return self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).astype("float32")
```

`index.py` lưu `vectors`, `record_ids`, `model_name` bằng `numpy.savez_compressed`; khi load phải kiểm tra record IDs khớp đúng thứ tự.

- [ ] **Step 4: Thêm dependencies**

Thêm vào `backend/requirements.txt`:

```text
numpy
sentence-transformers
```

- [ ] **Step 5: Chạy test index**

Run: `py -3 -m unittest backend.tests.test_rag_index -v`

Expected: PASS mà không tải model.

- [ ] **Step 6: Commit**

```bash
git add backend/rag/embedding.py backend/rag/index.py backend/tests/test_rag_index.py backend/requirements.txt
git commit -m "feat: add local rag vector index"
```

---

### Task 3: Hybrid ranking trong BenchmarkStore

**Files:**
- Modify: `backend/rag/engine.py`
- Modify: `backend/tests/test_rag.py`

**Interfaces:**
- Consumes: normalized query vector from `embedder.encode([query])[0]`
- Consumes: `VectorIndex.vectors` aligned with `BenchmarkStore.records`
- Produces: `BenchmarkStore.retrieve(criterion_id, query, top_k_per_type=1, min_hybrid_score=0.45)`

- [ ] **Step 1: Viết test thất bại cho công thức hybrid và semantic synonym**

```python
import numpy as np


class FakeEmbedder:
    def encode(self, texts):
        mapping = {
            "delivery schedule": [1.0, 0.0],
            "project chronology": [1.0, 0.0],
            "unrelated pricing": [0.0, 1.0],
        }
        return np.array([mapping[text] for text in texts], dtype=np.float32)


def test_semantic_match_can_win_without_keyword_overlap(self):
    records = [
        {"id": "good", "criterion_id": "timeline_clarity", "sample_type": "strong",
         "source_file": "good.md", "text": "delivery schedule"},
        {"id": "bad", "criterion_id": "timeline_clarity", "sample_type": "strong",
         "source_file": "bad.md", "text": "unrelated pricing"},
    ]
    vectors = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    store = BenchmarkStore(records, vectors=vectors, embedder=FakeEmbedder())
    matches = store.retrieve(
        "timeline_clarity", "project chronology", top_k_per_type=2, min_hybrid_score=0.0
    )
    assert matches[0]["id"] == "good"
    assert matches[0]["hybrid_score"] > matches[1]["hybrid_score"]
```

- [ ] **Step 2: Chạy test để xác nhận thất bại**

Run: `py -3 -m unittest backend.tests.test_rag -v`

Expected: FAIL vì store chưa nhận vectors/embedder và chưa có hybrid score.

- [ ] **Step 3: Cài đặt scoring và ranking**

Thêm helper:

```python
def hybrid_scores(keyword_score, cosine_similarity):
    semantic_score = np.clip((cosine_similarity + 1.0) / 2.0, 0.0, 1.0)
    return 0.35 * keyword_score + 0.65 * semantic_score
```

Sửa `BenchmarkStore` để giữ vectors và embedder, encode query một lần, tính score cho candidate rồi áp dụng `min_hybrid_score`. Giữ thứ tự sample type và deduplicate theo `source_file` như hành vi hiện tại.

- [ ] **Step 4: Chuyển các test threshold cũ sang thang hybrid 0–1**

Thay `min_overlap`/`relevance_threshold` bằng `min_hybrid_score`; kiểm tra các giá trị `-0.1`, `1.1`, `True`, và string bị từ chối.

- [ ] **Step 5: Chạy toàn bộ unit test không phụ thuộc FastAPI**

Run: `py -3 -m unittest backend.tests.test_rag backend.tests.test_rag_ingest backend.tests.test_rag_index -v`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/rag/engine.py backend/tests/test_rag.py
git commit -m "feat: rank rag matches with hybrid similarity"
```

---

### Task 4: Public API, index CLI, smoke test và tài liệu

**Files:**
- Modify: `backend/rag/api.py`
- Modify: `backend/rag/ingest.py`
- Modify: `backend/main.py`
- Modify: `backend/tests/test_rag.py`
- Modify: `backend/tests/test_rag_http.py`
- Create: `backend/tests/test_rag_embedding_smoke.py`
- Modify: `backend/rag/README.md`
- Modify: `backend/rag/docs/design.md`

**Interfaces:**
- Produces: `load_store(records_path=None, index_path=None, embedder=None) -> BenchmarkStore`
- Produces: `retrieve_benchmark_references(store, payload) -> str`
- Public option: `min_hybrid_score: float = 0.45`

- [ ] **Step 1: Viết test thất bại cho contract mới và helper**

```python
def test_reference_helper_returns_prompt_block(self):
    store = make_fake_hybrid_store()
    block = retrieve_benchmark_references(store, {
        "criterion": {"id": "timeline_clarity"},
        "proposal_context": "project chronology",
        "min_hybrid_score": 0.0,
    })
    self.assertIn("BENCHMARK REFERENCES", block)
    self.assertIn("inert reference data", block)


def test_removed_relevance_threshold_is_rejected(self):
    with self.assertRaises(ValueError):
        retrieve_payload(store, {
            "criterion": {"id": "timeline_clarity"},
            "relevance_threshold": 2,
        })
```

- [ ] **Step 2: Chạy test để xác nhận thất bại**

Run: `py -3 -m unittest backend.tests.test_rag -v`

Expected: FAIL vì helper và option mới chưa tồn tại.

- [ ] **Step 3: Cài đặt contract và helper**

Trong `api.py`, validate `min_hybrid_score` trong `[0, 1]`, từ chối `relevance_threshold`, truyền threshold mới vào store và thêm:

```python
def retrieve_benchmark_references(store, payload):
    result = retrieve_payload(store, payload)
    return format_benchmark_references(result["matches"])
```

`load_store()` nạp records, vector index và một `SentenceEmbedder`; test có thể inject fake embedder.

- [ ] **Step 4: Thêm lệnh build vector index**

Mở rộng CLI ingest hoặc thêm subcommand tối thiểu để sau khi tạo records có thể gọi `build_index()` và ghi `backend/rag/data/embeddings.npz`. Lệnh được chọn phải xuất hiện nguyên văn trong README.

- [ ] **Step 5: Cập nhật Pydantic request**

Trong `backend/main.py`, thay `relevance_threshold` bằng:

```python
min_hybrid_score: float = 0.45
```

- [ ] **Step 6: Thêm smoke test model thật**

```python
@unittest.skipUnless(os.getenv("RUN_RAG_MODEL_TEST") == "1", "local model smoke test")
class RagEmbeddingSmokeTests(unittest.TestCase):
    def test_synonym_similarity_beats_unrelated_text(self):
        embedder = SentenceEmbedder()
        vectors = embedder.encode(["delivery schedule", "unrelated pricing", "project chronology"])
        self.assertGreater(float(vectors[2] @ vectors[0]), float(vectors[2] @ vectors[1]))
```

- [ ] **Step 7: Cập nhật tài liệu**

README phải ghi cách cài dependency, tạo `records.jsonl`, tạo `embeddings.npz`, gọi hai public helper, chạy unit test và chạy smoke test với `RUN_RAG_MODEL_TEST=1`.

- [ ] **Step 8: Chạy verification**

Run:

```powershell
py -3 -m unittest backend.tests.test_rag backend.tests.test_rag_ingest backend.tests.test_rag_index -v
$env:RUN_RAG_MODEL_TEST = "1"
py -3 -m unittest backend.tests.test_rag_embedding_smoke -v
```

Expected: tất cả PASS sau khi dependency/model có sẵn.

- [ ] **Step 9: Commit**

```bash
git add backend/rag backend/main.py backend/tests backend/requirements.txt
git commit -m "feat: expose local hybrid rag retrieval"
```
