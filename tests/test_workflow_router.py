import unittest

from digital_analysis.analysis.router import WorkflowRouter
from digital_analysis.contracts.tasks import TaskSpec, TaskType, TimeHorizon


class WorkflowRouterTests(unittest.TestCase):
    def test_select_macro(self) -> None:
        task = TaskSpec(question="recession?", task_type=TaskType.MACRO, horizon=TimeHorizon.MEDIUM)
        sel = WorkflowRouter().select(task)
        self.assertIsNotNone(sel)
        assert sel is not None
        self.assertEqual(sel.workflow_name, "recession")

    def test_select_geopolitical(self) -> None:
        task = TaskSpec(question="war?", task_type=TaskType.GEOPOLITICAL, horizon=TimeHorizon.SHORT)
        sel = WorkflowRouter().select(task)
        self.assertIsNotNone(sel)
        assert sel is not None
        self.assertEqual(sel.workflow_name, "geopolitical")

    def test_select_asset(self) -> None:
        task = TaskSpec(question="buy gold?", task_type=TaskType.ASSET, horizon=TimeHorizon.MEDIUM)
        sel = WorkflowRouter().select(task)
        self.assertIsNotNone(sel)
        assert sel is not None
        self.assertEqual(sel.workflow_name, "asset_pricing")

    def test_select_bubble(self) -> None:
        task = TaskSpec(question="bubble?", task_type=TaskType.BUBBLE, horizon=TimeHorizon.MEDIUM)
        sel = WorkflowRouter().select(task)
        self.assertIsNotNone(sel)
        assert sel is not None
        self.assertEqual(sel.workflow_name, "bubble")


if __name__ == "__main__":
    unittest.main()
