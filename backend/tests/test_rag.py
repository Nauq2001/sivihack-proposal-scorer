import unittest

from backend.rag.engine import BenchmarkStore
from backend.rag.api import retrieve_payload


class ScoringRagTests(unittest.TestCase):
    def test_custom_criterion_uses_description_and_keeps_its_id(self):
        store = BenchmarkStore([{
            'id': 'example', 'criterion_id': 'completeness_vs_rfp',
            'source_file': 'example.md', 'sample_type': 'strong',
            'text': 'Production records and backups remain in EU regions.',
            'score_range': [4, 5],
        }])
        result = retrieve_payload(store, {
            'criterion': {'id': 'custom_residency', 'description': 'Production backups EU regions'},
            'proposal_context': '', 'requirement_context': '',
        })
        self.assertEqual(result['criterion_id'], 'custom_residency')
        self.assertEqual(result['retrieval_mode'], 'custom')
        self.assertEqual(len(result['matches']), 1)
        self.assertEqual(result['matches'][0]['criterion_id'], 'completeness_vs_rfp')
        self.assertIsNone(result['matches'][0]['score_range'])

    def test_threshold_is_inclusive_and_custom_results_are_deduplicated(self):
        record = {'id': 'one', 'criterion_id': 'timeline_clarity',
                  'source_file': 'one.md', 'sample_type': 'strong',
                  'text': 'pilot rollout', 'score_range': [4, 5]}
        store = BenchmarkStore([record, {**record, 'id': 'two', 'criterion_id': 'completeness_vs_rfp'}])
        self.assertEqual(len(store.retrieve('custom', 'pilot rollout', 2, 2)), 1)
        self.assertEqual(store.retrieve('custom', 'pilot rollout', 2, 3), [])

    def test_metadata_does_not_satisfy_threshold(self):
        store = BenchmarkStore([{'criterion_id': 'pricing_clarity', 'sample_type': 'weak',
            'text': 'No quote supplied.', 'section': 'pilot rollout', 'reasoning': 'pilot rollout'}])
        self.assertEqual(store.retrieve('pricing_clarity', 'pilot rollout'), [])

    def test_invalid_options_are_rejected(self):
        store = BenchmarkStore([])
        for threshold in (0, -1, True, '2'):
            with self.assertRaises(ValueError):
                store.retrieve('custom', 'pilot rollout', min_overlap=threshold)

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

        self.assertEqual(matches, [])

    def test_unrelated_query_returns_no_matches(self):
        store = BenchmarkStore.from_file("backend/rag/data/records.jsonl")

        matches = store.retrieve("timeline_clarity", "quantum banana asteroid", top_k_per_type=1)

        self.assertEqual(matches, [])

    def test_api_payload_returns_reference_matches(self):
        store = BenchmarkStore.from_file("backend/rag/data/records.jsonl")

        result = retrieve_payload(store, {
            "criterion": {"id": "risk_assumptions_transparency"},
            "proposal_context": "The supplier guarantees zero defects with no assumptions.",
            "requirement_context": "The RFP requires risks, dependencies and mitigations.",
            "top_k_per_type": 1,
        })

        self.assertIn("matches", result)
        self.assertGreater(len(result["matches"]), 0)
        self.assertLessEqual(len(result["matches"]), 4)


if __name__ == "__main__":
    unittest.main()
