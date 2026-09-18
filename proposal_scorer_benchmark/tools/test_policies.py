import copy
import json
import subprocess
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT))
from criteria_policy import BASE, normalize_criteria
from repository_policy import admission, quality_bucket, repository_role
from compare_runs import schema_errors


class Policies(unittest.TestCase):
    def test_missing_base_restored(self):
        result = normalize_criteria([], [], 'context')
        self.assertEqual(len(result['criteria']), 7)
        self.assertEqual({r['id'] for r in result['criteria']}, {key for key, _ in BASE})
        self.assertTrue(all(r['source'] == 'base' and r['priority'] == 'minor' for r in result['criteria']))

    def test_base_quote_optional_and_identity_fixed(self):
        rows = [{'source': 'base', 'id': 'tone_persuasiveness', 'name': 'Agent changed this name', 'priority': 'critical'}]
        row = normalize_criteria(rows, [], '')['criteria'][5]
        self.assertEqual(row['name'], 'Tone & Persuasiveness')
        self.assertEqual(row['priority'], 'critical')
        self.assertIsNone(row['rfp_quote'])

    def test_ai_dedup_quote_and_limit(self):
        rows = [{'source': 'ai', 'name': name, 'rfp_quote': quote} for name, quote in
                [('pricing---CLARITY', 'accuracy'), ('Accuracy', 'accuracy'), ('ACCURACY', 'accuracy'),
                 ('Unsupported', 'not in document'), ('Legacy', 'legacy'), ('Continuity', 'continuity'), ('Extra', 'extra')]]
        ai = [r for r in normalize_criteria(rows, [], 'accuracy legacy continuity extra')['criteria'] if r['source'] == 'ai']
        self.assertEqual([r['name'] for r in ai], ['Accuracy', 'Legacy', 'Continuity'])

    def test_custom_not_agent_owned_history_disabled(self):
        result = normalize_criteria([{'name': 'Illegal custom', 'source': 'custom'}, {'name': 'History', 'source': 'history'}],
                                    [{'name': 'User constraint', 'priority': 'major'}], '')
        self.assertEqual(len(result['criteria']), 8)
        self.assertEqual(result['criteria'][-1]['source'], 'custom')
        self.assertTrue(result['requires_user_confirmation'])

    def proposal(self):
        return {'document_type': 'proposal', 'industry': 'Software', 'country': 'DE', 'value_band': '50k-100k',
                'service_type': 'Implementation', 'submitted_date': '2026-08-01', 'outcome': 'won',
                'quality_score': 4.4, 'status': 'submitted', 'quality_provenance': {'method': 'scoring_api',
                'scorer_version': '1', 'rubric_version': '1', 'scored_at': '2026-09-18T10:00:00Z', 'input_sha256': 'a'*64},
                'cross_deal_use': True, 'anonymized_customer_names': True, 'anonymized_amounts': True,
                'sanitized_document': 'sanitized.md'}

    def test_admission_and_rejections(self):
        self.assertTrue(admission(self.proposal(), date(2026, 9, 18))['admitted'])
        mutations = [('status', 'draft'), ('outcome', 'unknown'), ('quality_score', None),
                     ('anonymized_amounts', False), ('anonymized_customer_names', False), ('submitted_date', 'invalid')]
        for key, value in mutations:
            with self.subTest(key=key):
                record = self.proposal()
                record[key] = value
                self.assertFalse(admission(record, date(2026, 9, 18))['admitted'])

    def test_provenance_not_just_a_score(self):
        for key, value in [('rubric_version', None), ('input_sha256', 'short'), ('scored_at', 'bad')]:
            record = self.proposal()
            record['quality_provenance'][key] = value
            self.assertFalse(admission(record, date(2026, 9, 18))['admitted'])

    def test_mock_scores_only_in_explicit_fictional_demo(self):
        record = self.proposal()
        record['quality_provenance']['method'] = 'mock_scoring_api'
        record['fictional'] = True
        self.assertFalse(admission(record, date(2026, 9, 18))['admitted'])
        self.assertTrue(admission(record, date(2026, 9, 18), demo=True)['admitted'])
        record['fictional'] = False
        self.assertFalse(admission(record, date(2026, 9, 18), demo=True)['admitted'])

    def test_old_standard_not_current_assertion(self):
        record = {'document_type': 'rate_card', 'currency': 'EUR', 'effective_from': '2026-03-17'}
        result = admission(record, date(2026, 9, 18))
        self.assertTrue(result['admitted'])
        self.assertFalse(result['may_assert_as_current_standard'])
        self.assertTrue(result['warnings'])
        record['effective_from'] = '2026-03-18'
        self.assertTrue(admission(record, date(2026, 9, 18))['may_assert_as_current_standard'])

    def test_outcomes_independent_of_quality(self):
        record = {'outcome': 'won', 'quality_score': 2.5}
        self.assertEqual(repository_role(record), 'context_only')
        record = {'outcome': 'lost', 'quality_score': 4.5}
        self.assertEqual(repository_role(record), 'context_only')
        self.assertEqual(quality_bucket(3.5), 'intermediate')

    def test_output_schema_rejects_missing_fields_and_bool_score(self):
        schema = json.loads((ROOT / 'evaluation_output.schema.json').read_text(encoding='utf-8'))
        self.assertTrue(schema_errors({}, schema, schema))
        self.assertTrue(schema_errors(True, schema['$defs']['score'], schema))


suite = unittest.defaultTestLoader.loadTestsFromTestCase(Policies)
result = unittest.TextTestRunner(verbosity=1).run(suite)
report = {'tests_run': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
          'passed': result.wasSuccessful(), 'scope': 'Criteria policy, ingestion policy and schema checks; no real scorer calls.'}
(ROOT / 'policy_test_report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
sys.exit(0 if result.wasSuccessful() else 1)
