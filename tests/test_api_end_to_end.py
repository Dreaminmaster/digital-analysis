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


if __name__ == '__main__':
    unittest.main()
