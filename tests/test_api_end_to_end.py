import unittest

from fastapi.testclient import TestClient

from examples.api_app import app


class ApiEndToEndTests(unittest.TestCase):
    def test_health(self) -> None:
        client = TestClient(app)
        resp = client.get('/health')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()['ok'])

    def test_analyze(self) -> None:
        client = TestClient(app)
        resp = client.post('/analyze', json={'question': 'Will there be a recession next year?', 'synthesize': False})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['task_type'], 'macro')
        self.assertIn('markdown_report', data)
        self.assertIn('suggested_symbols', data)
        self.assertIn('suggested_providers', data)
        self.assertIn('evidence', data)
        self.assertIn('contradictions', data)
        self.assertIn('scenarios', data)
        self.assertIn('metadata', data)

    def test_watchlist_and_monitors(self) -> None:
        client = TestClient(app)
        w = client.post('/watchlist', json={'name': 'Macro', 'query': 'Will there be a recession next year?', 'tags': ['macro']})
        self.assertEqual(w.status_code, 200)
        items = client.get('/watchlist')
        self.assertEqual(items.status_code, 200)
        self.assertGreaterEqual(len(items.json()), 1)

        m = client.post('/monitors', json={'topic': 'Recession risk', 'query': 'Will there be a recession next year?', 'schedule_hint': 'daily'})
        self.assertEqual(m.status_code, 200)
        monitors = client.get('/monitors')
        self.assertEqual(monitors.status_code, 200)
        self.assertGreaterEqual(len(monitors.json()), 1)


if __name__ == '__main__':
    unittest.main()
