import unittest

from digital_analysis.analysis.confidence import ConfidenceEngine
from digital_analysis.analysis.contradiction import ContradictionEngine
from digital_analysis.analysis.engine import AnalysisEngine
from digital_analysis.analysis.scorer import EvidenceScoringEngine
from digital_analysis.contracts.evidence import EvidenceBundle, EvidenceItem, EvidenceKind
from digital_analysis.contracts.tasks import TaskSpec, TaskType, TimeHorizon
from digital_analysis.planner.planner import SimplePlanner


class AnalysisTests(unittest.TestCase):
    def test_contradiction_engine(self) -> None:
        findings = ContradictionEngine().detect(("risk-off", "risk-on"))
        self.assertGreaterEqual(len(findings), 1)

    def test_contradiction_from_evidence(self) -> None:
        evidence = EvidenceBundle(items=(
            EvidenceItem(kind=EvidenceKind.PRICE, label="fg", summary="", direction="risk_on"),
            EvidenceItem(kind=EvidenceKind.CURVE, label="curve", summary="", direction="inverted"),
        ))
        findings = ContradictionEngine().detect_from_evidence(evidence)
        self.assertGreaterEqual(len(findings), 1)

    def test_confidence_engine(self) -> None:
        score = ConfidenceEngine().score(evidence_count=4, contradiction_count=1, missing_coverage_count=1)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 0.95)

    def test_scoring_engine(self) -> None:
        evidence = EvidenceBundle(items=(
            EvidenceItem(kind=EvidenceKind.PRICE, label="a", summary="", direction="up", confidence_hint=0.8),
            EvidenceItem(kind=EvidenceKind.PRICE, label="b", summary="", direction="down", confidence_hint=0.6),
        ))
        score = EvidenceScoringEngine().score(evidence)
        self.assertEqual(score.item_count, 2)
        self.assertAlmostEqual(score.average_confidence_hint, 0.7, places=2)

    def test_analysis_engine(self) -> None:
        task = TaskSpec(
            question="Will the Fed cut rates next year?",
            task_type=TaskType.MACRO,
            horizon=TimeHorizon.MEDIUM,
        )
        plan = SimplePlanner().plan(task)
        output = AnalysisEngine().analyze(task, plan)
        self.assertIn("Autonomous baseline analysis", output.summary)
        self.assertGreaterEqual(output.confidence, 0.0)
        self.assertGreaterEqual(len(output.scenarios), 1)


if __name__ == "__main__":
    unittest.main()
