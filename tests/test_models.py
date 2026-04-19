import unittest

from digital_analysis.models.router import ModelBackend, ModelRouter, ModelTask


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


if __name__ == "__main__":
    unittest.main()
