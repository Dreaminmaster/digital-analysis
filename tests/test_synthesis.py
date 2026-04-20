import unittest

from digital_analysis.analysis.engine import AnalysisEngine
from digital_analysis.contracts.tasks import TaskSpec, TaskType, TimeHorizon
from digital_analysis.models.base import ModelResponse
from digital_analysis.planner.planner import SimplePlanner
from digital_analysis.reports.builder import ReportSynthesizer
from digital_analysis.reports.synthesis import SynthesisPromptBuilder


class FakeModel:
    def complete(self, request):
        return ModelResponse(text=request.messages[-1].content[:60], model_name="fake")


class SynthesisTests(unittest.TestCase):
    def test_prompt_builder_contains_evidence(self) -> None:
        task = TaskSpec(question="Will there be a recession?", task_type=TaskType.MACRO, horizon=TimeHorizon.MEDIUM)
        analysis = AnalysisEngine().analyze(task, SimplePlanner().plan(task))
        request = SynthesisPromptBuilder().build(analysis)
        self.assertIn("Evidence:", request.messages[-1].content)
        self.assertIn("Question:", request.messages[-1].content)

    def test_report_synthesizer_calls_model(self) -> None:
        task = TaskSpec(question="Will there be a recession?", task_type=TaskType.MACRO, horizon=TimeHorizon.MEDIUM)
        analysis = AnalysisEngine().analyze(task, SimplePlanner().plan(task))
        resp = ReportSynthesizer(model=FakeModel()).synthesize(analysis)
        self.assertEqual(resp.model_name, "fake")


if __name__ == "__main__":
    unittest.main()
