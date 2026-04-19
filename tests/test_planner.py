import unittest

from digital_analysis.contracts.tasks import TaskType
from digital_analysis.planner.classifier import TaskClassifier
from digital_analysis.planner.priceability import PriceabilityChecker


class PlannerTests(unittest.TestCase):
    def test_classifier_macro(self) -> None:
        task = TaskClassifier().classify("What is recession probability next year?")
        self.assertEqual(task.task_type, TaskType.MACRO)

    def test_classifier_geopolitical(self) -> None:
        task = TaskClassifier().classify("What is the chance of war over Taiwan?")
        self.assertEqual(task.task_type, TaskType.GEOPOLITICAL)

    def test_priceability_true_for_macro(self) -> None:
        task = TaskClassifier().classify("Will the Fed cut rates next year?")
        assessment = PriceabilityChecker().assess(task)
        self.assertTrue(assessment.priceable)
        self.assertTrue(assessment.proxy_markets_likely)


if __name__ == "__main__":
    unittest.main()
