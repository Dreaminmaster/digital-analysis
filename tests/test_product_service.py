import unittest

from digital_analysis.orchestrator import DigitalAnalysisOrchestrator
from digital_analysis.product.service import AnalysisService


class ProductServiceTests(unittest.TestCase):
    def test_service_analyze(self) -> None:
        service = AnalysisService(orchestrator=DigitalAnalysisOrchestrator())
        result = service.analyze("Will there be a recession next year?")
        self.assertTrue(result.priceability.priceable)
        self.assertIn("Analysis Report", result.markdown_report)


if __name__ == "__main__":
    unittest.main()
