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
            id="m1", slug="recession-main", question="Will there be a recession?", active=True, closed=False,
            volume=None, liquidity=None, best_bid=None, best_ask=None,
            outcomes=(OutcomeQuote(name="Yes", probability=0.42), OutcomeQuote(name="No", probability=0.58)),
        )
        return [PolymarketEvent(id="e1", slug="recession", title="US recession?", active=True, closed=False, volume=None, liquidity=None, markets=(market,))]


class FakePolymarketWar:
    def list_events(self, query):
        market = PolymarketMarket(
            id="m1", slug="war-main", question="Will war escalate?", active=True, closed=False,
            volume=None, liquidity=None, best_bid=None, best_ask=None,
            outcomes=(OutcomeQuote(name="Yes", probability=0.25), OutcomeQuote(name="No", probability=0.75)),
        )
        return [PolymarketEvent(id="e1", slug="war", title="War escalation?", active=True, closed=False, volume=None, liquidity=None, markets=(market,))]


class FakeYahooPrice:
    def get_history(self, query):
        return PriceHistory(
            symbol=query.symbol,
            interval=query.interval,
            bars=(PriceBar("2026-04-01", 100, 101, 99, 100), PriceBar("2026-04-20", 109, 110, 108, 109)),
            provider_id="yahoo_price",
        )


class FakeCftc:
    def list_reports(self, query):
        return [CftcCotReport("GOLD - COMMODITY EXCHANGE INC.", "2026-04-14", 1000, 300, 100, 200, 250)]


class AnalysisEnrichmentTests(unittest.TestCase):
    def test_recession_enrichment_changes_summary_or_confidence(self) -> None:
        task = TaskSpec(question="Will there be a recession?", task_type=TaskType.MACRO, horizon=TimeHorizon.MEDIUM)
        base = AnalysisEngine().analyze(task, SimplePlanner().plan(task))
        enriched = RecessionWorkflow(
            treasury=FakeTreasury(), fedwatch=FakeFedWatch(), fear_greed=FakeFearGreed(), polymarket=FakePolymarketRecession()
        ).enrich(base)
        self.assertNotEqual(enriched.summary, base.summary)
        self.assertIn("evidence_score", enriched.metadata)

    def test_geopolitical_enrichment_changes_summary_or_confidence(self) -> None:
        task = TaskSpec(question="What is war risk?", task_type=TaskType.GEOPOLITICAL, horizon=TimeHorizon.SHORT)
        base = AnalysisEngine().analyze(task, SimplePlanner().plan(task))
        enriched = GeopoliticalRiskWorkflow(
            polymarket=FakePolymarketWar(), fear_greed=FakeFearGreed(), gold_prices=FakeYahooPrice(), cftc=FakeCftc()
        ).enrich(base)
        self.assertNotEqual(enriched.summary, base.summary)
        self.assertGreaterEqual(enriched.confidence, 0.0)

    def test_asset_pricing_enrichment_changes_summary_or_confidence(self) -> None:
        task = TaskSpec(question="Is gold attractive now?", task_type=TaskType.ASSET, horizon=TimeHorizon.MEDIUM)
        base = AnalysisEngine().analyze(task, SimplePlanner().plan(task))
        enriched = AssetPricingWorkflow(prices=FakeYahooPrice(), treasury=FakeTreasury(), fear_greed=FakeFearGreed()).enrich(base, symbol="GLD")
        self.assertNotEqual(enriched.summary, base.summary)
        self.assertIn("evidence_score", enriched.metadata)


if __name__ == "__main__":
    unittest.main()
