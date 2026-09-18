import tempfile
import unittest
from pathlib import Path

import numpy as np
from fastapi.testclient import TestClient

import backend.main as backend_main
from backend.knowledge.service import KnowledgeService


class FakeEmbedder:
    def encode(self, texts):
        rows = []
        for text in texts:
            lowered = text.lower()
            rows.append([1.0 if "backup" in lowered else 0.0, 1.0])
        vectors = np.asarray(rows, dtype=np.float32)
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        return vectors / np.maximum(norms, 1e-12)


class KnowledgeHttpTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_service = getattr(backend_main, "KNOWLEDGE_SERVICE", None)
        backend_main.KNOWLEDGE_SERVICE = KnowledgeService(
            Path(self.temp_dir.name), FakeEmbedder()
        )

    def tearDown(self):
        backend_main.KNOWLEDGE_SERVICE = self.original_service
        self.temp_dir.cleanup()

    def test_upload_and_search(self):
        with TestClient(backend_main.app) as client:
            upload = client.post(
                "/knowledge/files",
                files={
                    "file": (
                        "policy.md",
                        b"# Policy\nBackups stay in EU regions.",
                        "text/markdown",
                    )
                },
            )
            self.assertEqual(upload.status_code, 200)
            self.assertEqual(upload.json()["status"], "indexed")

            search = client.post(
                "/knowledge/search",
                json={"query": "backup location", "top_k": 1},
            )
            self.assertEqual(search.status_code, 200)
            self.assertEqual(search.json()["matches"][0]["filename"], "policy.md")


if __name__ == "__main__":
    unittest.main()
