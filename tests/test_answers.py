import unittest

from digital_analysis.answers.builder import OneShotAnswerBuilder
from digital_analysis.analysis.engine import AnalysisEngine
from digital_analysis.contracts.evidence import EvidenceBundle, EvidenceItem, EvidenceKind
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

    def test_key_evidence_sorted_by_confidence(self) -> None:
        task = TaskSpec(question='Is AI in a bubble?', task_type=TaskType.BUBBLE, horizon=TimeHorizon.MEDIUM)
        analysis = AnalysisEngine().analyze(task, SimplePlanner().plan(task))
        evidence = EvidenceBundle(items=(
            EvidenceItem(kind=EvidenceKind.OTHER, label='low', summary='low', confidence_hint=0.2),
            EvidenceItem(kind=EvidenceKind.OTHER, label='high', summary='high', confidence_hint=0.9),
            EvidenceItem(kind=EvidenceKind.OTHER, label='mid', summary='mid', confidence_hint=0.5),
        ))
        analysis = type(analysis)(
            task=analysis.task,
            plan=analysis.plan,
            summary=analysis.summary,
            confidence=analysis.confidence,
            evidence=evidence,
            gaps=analysis.gaps,
            contradictions=analysis.contradictions,
            scenarios=analysis.scenarios,
            metadata=analysis.metadata,
        )
        answer = OneShotAnswerBuilder().build(analysis)
        labels = [x.label for x in answer.key_evidence]
        self.assertEqual(labels[0], 'high')


if __name__ == '__main__':
    unittest.main()
