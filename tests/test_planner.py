import unittest

from digital_analysis.contracts.tasks import TaskType
from digital_analysis.planner.classifier import TaskClassifier
from digital_analysis.planner.planner import SimplePlanner
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

    def test_planner_suggests_macro_symbols(self) -> None:
        from digital_analysis.contracts.tasks import TaskSpec, TimeHorizon

        task = TaskSpec(question="Will there be a recession next year?", task_type=TaskType.MACRO, horizon=TimeHorizon.MEDIUM)
        plan = SimplePlanner().plan(task)
        self.assertIn("SPY", plan.suggested_symbols)
        self.assertIn("us_treasury", plan.suggested_providers)

    def test_planner_suggests_gold_symbols(self) -> None:
        from digital_analysis.contracts.tasks import TaskSpec, TimeHorizon

        task = TaskSpec(question="Is gold attractive now?", task_type=TaskType.ASSET, horizon=TimeHorizon.MEDIUM)
        plan = SimplePlanner().plan(task)
        self.assertIn("GLD", plan.suggested_symbols)

    def test_classifier_extracts_target_asset(self) -> None:
        self.assertEqual(TaskClassifier().classify("Should I buy gold now?").target_asset, "GLD")
        self.assertEqual(TaskClassifier().classify("Is Bitcoin overvalued?").target_asset, "BTC-USD")
        self.assertEqual(TaskClassifier().classify("Is NVDA in a bubble?").target_asset, "NVDA")


if __name__ == "__main__":
    unittest.main()
