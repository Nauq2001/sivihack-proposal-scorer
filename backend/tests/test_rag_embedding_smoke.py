import os
import unittest

from backend.rag.embedding import SentenceEmbedder


@unittest.skipUnless(
    os.getenv("RUN_RAG_MODEL_TEST") == "1",
    "set RUN_RAG_MODEL_TEST=1 to run the local model smoke test",
)
class RagEmbeddingSmokeTests(unittest.TestCase):
    def test_synonym_similarity_beats_unrelated_text(self):
        embedder = SentenceEmbedder()

        vectors = embedder.encode([
            "delivery schedule",
            "unrelated pricing",
            "project chronology",
        ])

        self.assertGreater(
            float(vectors[2] @ vectors[0]),
            float(vectors[2] @ vectors[1]),
        )


if __name__ == "__main__":
    unittest.main()
