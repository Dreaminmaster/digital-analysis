import unittest

from digital_analysis.answers.builder import OneShotAnswerBuilder
from digital_analysis.analysis.engine import AnalysisEngine
from digital_analysis.contracts.tasks import TaskSpec, TaskType, TimeHorizon
from digital_analysis.planner.planner import SimplePlanner


class AnswerTests(unittest.TestCase):
    def test_build_one_shot_answer(self) -> None:
        task = TaskSpec(question='Will there be a recession next year?', task_type=TaskType.MACRO, horizon=TimeHorizon.MEDIUM)
        analysis = AnalysisEngine().analyze(task, SimplePlanner().plan(task))
        answer = OneShotAnswerBuilder().build(analysis)
        self.assertEqual(answer.question, task.question)
        self.assertGreaterEqual(answer.confidence, 0.0)
        self.assertGreaterEqual(len(answer.key_evidence), 1)


if __name__ == '__main__':
    unittest.main()
