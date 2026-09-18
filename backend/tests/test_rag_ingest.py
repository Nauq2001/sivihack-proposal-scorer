import unittest

from backend.rag.ingest import chunk_sections


class RagIngestChunkTests(unittest.TestCase):
    def test_short_section_keeps_heading(self):
        chunks = chunk_sections([("Delivery plan", "alpha beta gamma")])

        self.assertEqual(
            chunks,
            [("Delivery plan", "## Delivery plan\nalpha beta gamma")],
        )

    def test_long_section_is_split_with_overlap(self):
        body = " ".join(f"word{i}" for i in range(260))

        chunks = chunk_sections([("Timeline", body)])

        self.assertEqual(len(chunks), 2)
        first_words = chunks[0][1].split()
        second_words = chunks[1][1].split()
        self.assertEqual(first_words[-25:], second_words[2:27])
        self.assertTrue(text.startswith("## Timeline\n") for _, text in chunks)


if __name__ == "__main__":
    unittest.main()
