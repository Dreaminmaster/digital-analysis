import unittest

from digital_analysis.analysis.engine import AnalysisEngine
from digital_analysis.contracts.tasks import TaskSpec, TaskType, TimeHorizon
from digital_analysis.planner.planner import SimplePlanner
from digital_analysis.reports.markdown import MarkdownReportRenderer


class ScaffoldTests(unittest.TestCase):
    def test_planner_and_report_flow(self) -> None:
        task = TaskSpec(
            question="What is the probability of a recession in the next 12 months?",
            task_type=TaskType.MACRO,
            horizon=TimeHorizon.MEDIUM,
        )
        planner = SimplePlanner()
        plan = planner.plan(task)

        self.assertGreaterEqual(len(plan.required_signals), 3)

        engine = AnalysisEngine()
        output = engine.analyze(task, plan)
        self.assertGreaterEqual(output.confidence, 0.0)

        renderer = MarkdownReportRenderer()
        report = renderer.render(output)
        self.assertIn("Analysis Report", report)
        self.assertIn("Evidence Gaps", report)


if __name__ == "__main__":
    unittest.main()
