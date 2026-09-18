"""File-backed internal knowledgebase for the MVP."""

import hashlib
import json
from pathlib import Path

import numpy as np

from backend.rag.ingest import _sections, chunk_sections


MAX_FILE_BYTES = 2 * 1024 * 1024
ALLOWED_SUFFIXES = frozenset({".md", ".txt"})


class KnowledgeService:
    def __init__(self, data_dir, embedder):
        self.data_dir = Path(data_dir)
        self.files_dir = self.data_dir / "files"
        self.records_path = self.data_dir / "records.jsonl"
        self.index_path = self.data_dir / "embeddings.npz"
        self.embedder = embedder
        self.files_dir.mkdir(parents=True, exist_ok=True)
        self.records, self.vectors = self._load()

    def _load(self):
        if not self.records_path.exists():
            return [], np.empty((0, 0), dtype=np.float32)
        with self.records_path.open(encoding="utf-8") as handle:
            records = [json.loads(line) for line in handle if line.strip()]
        if not self.index_path.exists():
            raise ValueError("knowledge embeddings.npz is missing; rebuild the knowledgebase")
        with np.load(self.index_path, allow_pickle=False) as data:
            vectors = np.asarray(data["vectors"], dtype=np.float32)
        if vectors.ndim != 2 or vectors.shape[0] != len(records):
            raise ValueError("knowledge records and embeddings do not match")
        return records, vectors

    def add_document(self, filename, content):
        safe_name = Path(filename).name
        if Path(safe_name).suffix.lower() not in ALLOWED_SUFFIXES:
            raise ValueError("only .md and .txt files are supported")
        if not isinstance(content, bytes):
            raise ValueError("file content must be bytes")
        if not content or len(content) > MAX_FILE_BYTES:
            raise ValueError("file must contain 1 byte to 2 MB")
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("file must use UTF-8 encoding") from exc
        if not text.strip():
            raise ValueError("file must contain non-whitespace text")

        document_id = hashlib.sha256(content).hexdigest()
        if any(record["document_id"] == document_id for record in self.records):
            raise ValueError("document content already exists")

        chunks = chunk_sections(_sections(text))
        new_records = [
            {
                "id": f"{document_id}:chunk:{index:03d}",
                "document_id": document_id,
                "filename": safe_name,
                "section": heading,
                "text": chunk_text,
            }
            for index, (heading, chunk_text) in enumerate(chunks)
        ]
        all_records = self.records + new_records
        vectors = np.asarray(
            self.embedder.encode([record["text"] for record in all_records]),
            dtype=np.float32,
        )
        if vectors.ndim != 2 or vectors.shape[0] != len(all_records):
            raise ValueError("embedder must return one vector per knowledge chunk")

        stored_name = f"{document_id[:12]}-{safe_name}"
        (self.files_dir / stored_name).write_bytes(content)
        self._persist(all_records, vectors)
        self.records, self.vectors = all_records, vectors
        return {
            "document_id": document_id,
            "filename": safe_name,
            "chunk_count": len(new_records),
            "status": "indexed",
        }

    def _persist(self, records, vectors):
        records_next = self.data_dir / "records.next.jsonl"
        index_next = self.data_dir / "embeddings.next.npz"
        with records_next.open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        np.savez_compressed(index_next, vectors=vectors)
        records_next.replace(self.records_path)
        index_next.replace(self.index_path)

    def search(self, query, top_k=5):
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")
        if type(top_k) is not int or not 1 <= top_k <= 20:
            raise ValueError("top_k must be an integer between 1 and 20")
        if not self.records:
            return []
        query_vector = np.asarray(self.embedder.encode([query]), dtype=np.float32)
        if query_vector.shape != (1, self.vectors.shape[1]):
            raise ValueError("embedder returned an invalid query vector")
        scores = self.vectors @ query_vector[0]
        order = np.argsort(-scores, kind="stable")[:top_k]
        return [
            {
                "document_id": self.records[index]["document_id"],
                "filename": self.records[index]["filename"],
                "section": self.records[index]["section"],
                "text": self.records[index]["text"],
                "score": float(scores[index]),
            }
            for index in order
        ]
