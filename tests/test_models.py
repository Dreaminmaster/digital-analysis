import unittest

from digital_analysis.models.api_openai import OpenAICompatibleModel
from digital_analysis.models.base import ModelMessage, ModelRequest
from digital_analysis.models.local_ollama import OllamaModel
from digital_analysis.models.router import ModelBackend, ModelRouter, ModelTask


class FakeJsonClient:
    def __init__(self, payload):
        self.payload = payload

    def get_json(self, url, *, params=None):
        return self.payload

    def post_json(self, url, *, body=None, params=None, headers=None):
        return self.payload


class ModelTests(unittest.TestCase):
    def test_router_prefers_low_cost_for_parse(self) -> None:
        router = ModelRouter(
            backends=(
                ModelBackend(name="strong", kind="cloud_api", strengths=(ModelTask.PARSE,), cost_tier="high"),
                ModelBackend(name="cheap", kind="cloud_api", strengths=(ModelTask.PARSE,), cost_tier="low"),
            )
        )
        backend = router.route(ModelTask.PARSE)
        self.assertIsNotNone(backend)
        assert backend is not None
        self.assertEqual(backend.name, "cheap")

    def test_router_prefers_high_cost_for_synthesize(self) -> None:
        router = ModelRouter(
            backends=(
                ModelBackend(name="cheap", kind="cloud_api", strengths=(ModelTask.SYNTHESIZE,), cost_tier="low"),
                ModelBackend(name="strong", kind="cloud_api", strengths=(ModelTask.SYNTHESIZE,), cost_tier="high"),
            )
        )
        backend = router.route(ModelTask.SYNTHESIZE)
        self.assertIsNotNone(backend)
        assert backend is not None
        self.assertEqual(backend.name, "strong")

    def test_openai_adapter_extracts_text(self) -> None:
        payload = {"choices": [{"message": {"content": "hello"}}]}
        model = OpenAICompatibleModel(base_url="https://api.example.com/v1", api_key="x", model_name="demo", http_client=FakeJsonClient(payload))
        resp = model.complete(ModelRequest(messages=(ModelMessage(role="user", content="hi"),)))
        self.assertEqual(resp.text, "hello")

    def test_ollama_adapter_extracts_text(self) -> None:
        payload = {"message": {"content": "local hello"}}
        model = OllamaModel(model_name="demo", http_client=FakeJsonClient(payload))
        resp = model.complete(ModelRequest(messages=(ModelMessage(role="user", content="hi"),)))
        self.assertEqual(resp.text, "local hello")


if __name__ == "__main__":
    unittest.main()
