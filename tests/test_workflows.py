import unittest

from digital_analysis.analysis.engine import AnalysisEngine
from digital_analysis.analysis.workflows import AssetPricingWorkflow, GeopoliticalRiskWorkflow, RecessionWorkflow
from digital_analysis.contracts.tasks import TaskSpec, TaskType, TimeHorizon
from digital_analysis.planner.planner import SimplePlanner
from digital_analysis.providers.cftc import CftcCotReport
from digital_analysis.providers.cme_fedwatch import FedMeetingProbability, FedRateProb
from digital_analysis.providers.fear_greed import FearGreedSnapshot
from digital_analysis.providers.polymarket import OutcomeQuote, PolymarketEvent, PolymarketMarket
from digital_analysis.providers.prices import PriceBar, PriceHistory
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


class FakePolymarketRecession:
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


class FakePolymarketWar:
    def list_events(self, query):
        market = PolymarketMarket(
            id="m1",
            slug="war-main",
            question="Will war escalate?",
            active=True,
            closed=False,
            volume=None,
            liquidity=None,
            best_bid=None,
            best_ask=None,
            outcomes=(OutcomeQuote(name="Yes", probability=0.25), OutcomeQuote(name="No", probability=0.75)),
        )
        return [PolymarketEvent(id="e1", slug="war", title="War escalation?", active=True, closed=False, volume=None, liquidity=None, markets=(market,))]


class FakeYahooPrice:
    def get_history(self, query):
        return PriceHistory(
            symbol=query.symbol,
            interval=query.interval,
            bars=(
                PriceBar("2026-04-01", 100, 101, 99, 100),
                PriceBar("2026-04-20", 109, 110, 108, 109),
            ),
            provider_id="yahoo_price",
        )


class FakeCftc:
    def list_reports(self, query):
        return [
            CftcCotReport(
                market_name="GOLD - COMMODITY EXCHANGE INC.",
                report_date="2026-04-14",
                open_interest_all=1000,
                noncommercial_long=300,
                noncommercial_short=100,
                commercial_long=200,
                commercial_short=250,
            )
        ]


class WorkflowTests(unittest.TestCase):
    def test_recession_workflow_enriches_evidence(self) -> None:
        task = TaskSpec(question="Will there be a recession?", task_type=TaskType.MACRO, horizon=TimeHorizon.MEDIUM)
        analysis = AnalysisEngine().analyze(task, SimplePlanner().plan(task))
        workflow = RecessionWorkflow(
            treasury=FakeTreasury(),
            fedwatch=FakeFedWatch(),
            fear_greed=FakeFearGreed(),
            polymarket=FakePolymarketRecession(),
        )
        enriched = workflow.enrich(analysis)
        self.assertGreater(len(enriched.evidence.items), len(analysis.evidence.items))

    def test_geopolitical_workflow_enriches_evidence(self) -> None:
        task = TaskSpec(question="What is war risk?", task_type=TaskType.GEOPOLITICAL, horizon=TimeHorizon.SHORT)
        analysis = AnalysisEngine().analyze(task, SimplePlanner().plan(task))
        workflow = GeopoliticalRiskWorkflow(
            polymarket=FakePolymarketWar(),
            fear_greed=FakeFearGreed(),
            gold_prices=FakeYahooPrice(),
            cftc=FakeCftc(),
        )
        enriched = workflow.enrich(analysis)
        self.assertTrue(any(item.label == "gold" for item in enriched.evidence.items))
        self.assertTrue(any(item.label == "gold_cot" for item in enriched.evidence.items))

    def test_asset_pricing_workflow_enriches_evidence(self) -> None:
        task = TaskSpec(question="Is gold attractive now?", task_type=TaskType.ASSET, horizon=TimeHorizon.MEDIUM)
        analysis = AnalysisEngine().analyze(task, SimplePlanner().plan(task))
        workflow = AssetPricingWorkflow(
            prices=FakeYahooPrice(),
            treasury=FakeTreasury(),
            fear_greed=FakeFearGreed(),
        )
        enriched = workflow.enrich(analysis, symbol="GLD")
        self.assertTrue(any(item.label == "GLD" for item in enriched.evidence.items))


if __name__ == "__main__":
    unittest.main()
