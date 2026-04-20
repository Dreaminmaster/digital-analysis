import unittest

from digital_analysis.analysis.engine import AnalysisEngine
from digital_analysis.analysis.workflows import RecessionWorkflow
from digital_analysis.contracts.tasks import TaskSpec, TaskType, TimeHorizon
from digital_analysis.planner.planner import SimplePlanner
from digital_analysis.providers.cme_fedwatch import FedMeetingProbability, FedRateProb
from digital_analysis.providers.fear_greed import FearGreedSnapshot
from digital_analysis.providers.polymarket import OutcomeQuote, PolymarketEvent, PolymarketMarket
from digital_analysis.providers.treasury import YieldCurveSnapshot, YieldPoint


class FakeTreasury:
    def latest_yield_curve(self):
        return YieldCurveSnapshot("nominal", "2026-04-20", (YieldPoint("10Y", 4.2), YieldPoint("2Y", 4.5)))


class FakeFedWatch:
    def get_probabilities(self):
        return [FedMeetingProbability("2026-06-17", 0.0425, 0.0450, (FedRateProb(0.04, 0.0425, 0.7),))]


class FakeFearGreed:
    def get_index(self):
        return FearGreedSnapshot(score=60, rating="Greed", timestamp="x", previous_close=55)


class FakePolymarket:
    def list_events(self, query):
        market = PolymarketMarket(
            id="m1",
            slug="recession-main",
            question="Will there be a recession?",
            active=True,
            closed=False,
            volume=None,
            liquidity=None,
            best_bid=None,
            best_ask=None,
            outcomes=(OutcomeQuote(name="Yes", probability=0.42), OutcomeQuote(name="No", probability=0.58)),
        )
        return [PolymarketEvent(id="e1", slug="recession", title="US recession?", active=True, closed=False, volume=None, liquidity=None, markets=(market,))]


class WorkflowTests(unittest.TestCase):
    def test_recession_workflow_enriches_evidence(self) -> None:
        task = TaskSpec(question="Will there be a recession?", task_type=TaskType.MACRO, horizon=TimeHorizon.MEDIUM)
        analysis = AnalysisEngine().analyze(task, SimplePlanner().plan(task))
        workflow = RecessionWorkflow(
            treasury=FakeTreasury(),
            fedwatch=FakeFedWatch(),
            fear_greed=FakeFearGreed(),
            polymarket=FakePolymarket(),
        )
        enriched = workflow.enrich(analysis)
        self.assertGreater(len(enriched.evidence.items), len(analysis.evidence.items))


if __name__ == "__main__":
    unittest.main()
