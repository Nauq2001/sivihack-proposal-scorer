import tempfile
import unittest
from pathlib import Path

import numpy as np

from backend.knowledge.service import KnowledgeService


class FakeEmbedder:
    model_name = "fake"

    def encode(self, texts):
        rows = []
        for text in texts:
            lowered = text.lower()
            rows.append([
                1.0 if "backup" in lowered or "stored" in lowered else 0.0,
                1.0 if "pricing" in lowered else 0.0,
            ])
        vectors = np.asarray(rows, dtype=np.float32)
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        return vectors / np.maximum(norms, 1e-12)


class KnowledgeServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.service = KnowledgeService(Path(self.temp_dir.name), FakeEmbedder())

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_and_search_document(self):
        result = self.service.add_document(
            "policy.md",
            b"# Data residency\nBackups are stored in EU regions.",
        )

        matches = self.service.search("Where are backups stored?", top_k=1)

        self.assertEqual(result["status"], "indexed")
        self.assertEqual(result["chunk_count"], 1)
        self.assertEqual(matches[0]["filename"], "policy.md")
        self.assertEqual(matches[0]["section"], "Data residency")

    def test_duplicate_content_is_rejected(self):
        self.service.add_document("one.txt", b"same content")

        with self.assertRaisesRegex(ValueError, "already exists"):
            self.service.add_document("two.txt", b"same content")

    def test_invalid_extension_is_rejected(self):
        with self.assertRaisesRegex(ValueError, r"\.md and \.txt"):
            self.service.add_document("policy.pdf", b"plain text")

    def test_empty_knowledgebase_returns_no_matches(self):
        self.assertEqual(self.service.search("anything"), [])


if __name__ == "__main__":
    unittest.main()
