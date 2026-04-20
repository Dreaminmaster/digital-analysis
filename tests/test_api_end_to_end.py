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

    def test_monitor_run_flow(self) -> None:
        client = TestClient(app)
        monitor = client.post('/monitors', json={'topic': 'Recession risk', 'query': 'Will there be a recession next year?', 'schedule_hint': 'daily'}).json()
        run = client.post(f"/monitors/{monitor['monitor_id']}/run")
        self.assertEqual(run.status_code, 200)
        runs = client.get('/monitor-runs')
        self.assertEqual(runs.status_code, 200)
        self.assertGreaterEqual(len(runs.json()), 1)
        compare = client.get(f"/monitors/{monitor['monitor_id']}/compare")
        self.assertEqual(compare.status_code, 200)

    def test_run_all_monitors(self) -> None:
        client = TestClient(app)
        client.post('/monitors', json={'topic': 'Recession risk', 'query': 'Will there be a recession next year?', 'schedule_hint': 'daily'})
        resp = client.post('/monitors/run-all')
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json(), list)


if __name__ == '__main__':
    unittest.main()
