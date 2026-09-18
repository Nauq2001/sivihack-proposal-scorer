import unittest

from backend.rag.ingest import chunk_sections, rechunk_records


class RagIngestChunkTests(unittest.TestCase):
    def test_existing_records_can_be_rechunked_idempotently(self):
        record = {
            "id": "case:response:timeline_clarity",
            "criterion_id": "timeline_clarity",
            "sample_type": "strong",
            "source_file": "case/response.md",
            "text": "## Plan\nalpha beta\n\n## Dates\ngamma delta",
        }

        chunks = rechunk_records([record])

        self.assertEqual(
            [chunk["id"] for chunk in chunks],
            [
                "case:response:timeline_clarity:chunk:000",
                "case:response:timeline_clarity:chunk:001",
            ],
        )
        self.assertEqual(rechunk_records(chunks), chunks)

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
