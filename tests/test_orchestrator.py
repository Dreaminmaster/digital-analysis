import unittest

from digital_analysis.models.base import ModelResponse
from digital_analysis.orchestrator import DigitalAnalysisOrchestrator
from digital_analysis.reports.builder import ReportSynthesizer


class FakeModel:
    def complete(self, request):
        return ModelResponse(text="synthetic answer", model_name="fake")


class OrchestratorTests(unittest.TestCase):
    def test_run_without_synthesis(self) -> None:
        result = DigitalAnalysisOrchestrator().run("Will there be a recession next year?")
        self.assertIn("Analysis Report", result.markdown_report)
        self.assertIsNone(result.synthesized_text)
        self.assertTrue(result.priceability.priceable)

    def test_run_with_synthesis(self) -> None:
        orchestrator = DigitalAnalysisOrchestrator(synthesizer=ReportSynthesizer(model=FakeModel()))
        result = orchestrator.run("Will there be a recession next year?")
        self.assertEqual(result.synthesized_text, "synthetic answer")


if __name__ == "__main__":
    unittest.main()
