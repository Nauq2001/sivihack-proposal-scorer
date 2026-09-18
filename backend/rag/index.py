"""Persistence helpers for the local NumPy vector index."""

from dataclasses import dataclass
from pathlib import Path

import numpy as np


DEFAULT_VECTOR_INDEX = Path(__file__).parent / "data" / "embeddings.npz"


@dataclass(frozen=True)
class VectorIndex:
    vectors: np.ndarray
    record_ids: list[str]
    model_name: str


def build_index(records, embedder, output_path=DEFAULT_VECTOR_INDEX, model_name=None):
    records = list(records)
    vectors = np.asarray(embedder.encode([record["text"] for record in records]), dtype=np.float32)
    if vectors.ndim != 2 or vectors.shape[0] != len(records):
        raise ValueError("embedder must return one vector per record")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output_path,
        vectors=vectors,
        record_ids=np.asarray([record["id"] for record in records]),
        model_name=np.asarray(model_name or getattr(embedder, "model_name", "unknown")),
    )


def load_index(path, records):
    path = Path(path)
    try:
        with np.load(path, allow_pickle=False) as data:
            vectors = np.asarray(data["vectors"], dtype=np.float32)
            record_ids = data["record_ids"].astype(str).tolist()
            model_name = str(data["model_name"].item())
    except (OSError, KeyError, ValueError) as exc:
        raise ValueError(f"cannot load RAG vector index {path}: {exc}") from exc

    expected_ids = [record["id"] for record in records]
    if record_ids != expected_ids:
        raise ValueError("vector index record IDs do not match records.jsonl; rebuild the index")
    if vectors.ndim != 2 or vectors.shape[0] != len(expected_ids):
        raise ValueError("vector index shape does not match records.jsonl; rebuild the index")
    return VectorIndex(vectors=vectors, record_ids=record_ids, model_name=model_name)
