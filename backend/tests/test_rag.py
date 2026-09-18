import unittest

from backend.rag.engine import BenchmarkStore
from backend.rag.api import retrieve_payload


class ScoringRagTests(unittest.TestCase):
    def test_retrieves_balanced_examples_for_a_criterion(self):
        store = BenchmarkStore.from_file("backend/rag/data/records.jsonl")

        matches = store.retrieve(
            criterion_id="timeline_clarity",
            query="clear milestones dates pilot rollout dependencies",
            top_k_per_type=1,
        )

        self.assertEqual({m["sample_type"] for m in matches}, {"weak", "medium", "strong", "overpromise"})
        self.assertTrue(all(m["criterion_id"] == "timeline_clarity" for m in matches))

    def test_empty_query_does_not_return_unrelated_criteria(self):
        store = BenchmarkStore.from_file("backend/rag/data/records.jsonl")

        matches = store.retrieve("pricing_clarity", "", top_k_per_type=1)

        self.assertTrue(all(m["criterion_id"] == "pricing_clarity" for m in matches))

    def test_api_payload_returns_reference_matches(self):
        store = BenchmarkStore.from_file("backend/rag/data/records.jsonl")

        result = retrieve_payload(store, {
            "criterion": {"id": "risk_assumptions_transparency"},
            "proposal_context": "The supplier guarantees zero defects with no assumptions.",
            "requirement_context": "The RFP requires risks, dependencies and mitigations.",
            "top_k_per_type": 1,
        })

        self.assertIn("matches", result)
        self.assertEqual(len(result["matches"]), 4)


if __name__ == "__main__":
    unittest.main()
