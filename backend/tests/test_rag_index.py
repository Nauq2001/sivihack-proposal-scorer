import tempfile
import unittest
from pathlib import Path

import numpy as np

from backend.rag.index import build_index, load_index


class FakeEmbedder:
    def encode(self, texts):
        rows = np.array(
            [[len(text), text.count("risk")] for text in texts],
            dtype=np.float32,
        )
        norms = np.linalg.norm(rows, axis=1, keepdims=True)
        return rows / np.maximum(norms, 1e-12)


class RagIndexTests(unittest.TestCase):
    def test_index_round_trip_preserves_record_order(self):
        records = [
            {"id": "a", "text": "risk plan"},
            {"id": "b", "text": "timeline"},
        ]

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "embeddings.npz"
            build_index(records, FakeEmbedder(), path, "fake")
            index = load_index(path, records)

        self.assertEqual(index.record_ids, ["a", "b"])
        self.assertEqual(index.vectors.shape, (2, 2))
        self.assertEqual(index.model_name, "fake")

    def test_index_rejects_record_order_mismatch(self):
        records = [
            {"id": "a", "text": "risk"},
            {"id": "b", "text": "timeline"},
        ]

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "embeddings.npz"
            build_index(records, FakeEmbedder(), path, "fake")
            with self.assertRaisesRegex(ValueError, "record IDs"):
                load_index(path, list(reversed(records)))


if __name__ == "__main__":
    unittest.main()
