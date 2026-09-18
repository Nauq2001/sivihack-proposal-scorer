"""Integration check; requires FastAPI and httpx in the backend environment."""
import unittest

from fastapi.testclient import TestClient
from backend.main import app


class RagHttpTests(unittest.TestCase):
    def test_custom_query_threshold_and_validation(self):
        with TestClient(app) as client:
            payload = {'criterion': {'id': 'custom_residency', 'description': 'production backups EU regions'}}
            response = client.post('/rag/retrieve', json=payload)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['criterion_id'], 'custom_residency')
            self.assertTrue(response.json()['matches'])
            payload['relevance_threshold'] = 100
            self.assertEqual(client.post('/rag/retrieve', json=payload).json()['matches'], [])
            payload['relevance_threshold'] = 0
            self.assertEqual(client.post('/rag/retrieve', json=payload).status_code, 400)

    def test_disallowed_requirement_criterion_is_rejected(self):
        with TestClient(app) as client:
            response = client.post('/rag/retrieve', json={
                'criterion': {'id': 'completeness_vs_rfp'},
                'top_k': 1,
            })
            self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
