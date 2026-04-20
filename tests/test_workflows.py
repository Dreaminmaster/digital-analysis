import unittest

from digital_analysis.analysis.engine import AnalysisEngine
from digital_analysis.analysis.workflows import AssetPricingWorkflow, BubbleAssessmentWorkflow, GeopoliticalRiskWorkflow, RecessionWorkflow
from digital_analysis.contracts.tasks import TaskSpec, TaskType, TimeHorizon
from digital_analysis.planner.planner import SimplePlanner
from digital_analysis.providers.cftc import CftcCotReport
from digital_analysis.providers.cme_fedwatch import FedMeetingProbability, FedRateProb
from digital_analysis.providers.coingecko import CoinGeckoPrice
from digital_analysis.providers.deribit import DeribitFutureTermPoint, DeribitFuturesTermStructure, DeribitOptionChain, DeribitOptionQuote
from digital_analysis.providers.edgar import EdgarInsiderSummary
from digital_analysis.providers.fear_greed import FearGreedSnapshot
from digital_analysis.providers.polymarket import OutcomeQuote, PolymarketEvent, PolymarketMarket
from digital_analysis.providers.prices import PriceBar, PriceHistory
from digital_analysis.providers.treasury import YieldCurveSnapshot, YieldPoint
from digital_analysis.providers.yfinance_provider import OptionContract, OptionsChain


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


class FakePolymarketAI:
    def list_events(self, query):
        market = PolymarketMarket(
            id="m1", slug="ai-main", question="Is AI overheating?", active=True, closed=False,
            volume=None, liquidity=None, best_bid=None, best_ask=None,
            outcomes=(OutcomeQuote(name="Yes", probability=0.6), OutcomeQuote(name="No", probability=0.4)),
        )
        return [PolymarketEvent(id="e1", slug="ai", title="AI overheating?", active=True, closed=False, volume=None, liquidity=None, markets=(market,))]


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


class FakeYFinance:
    def get_chain(self, query):
        return OptionsChain(
            ticker=query.ticker,
            expiration="2099-04-17",
            underlying_price=150.0,
            calls=(OptionContract("c", "call", "2099-04-17", 150, last_price=5.2, bid=5.0, ask=5.4, mid=5.2, implied_volatility=0.25),),
            puts=(OptionContract("p", "put", "2099-04-17", 150, last_price=3.4, bid=3.2, ask=3.6, mid=3.4, implied_volatility=0.26),),
        )


class FakeEdgar:
    def get_insider_transactions(self, query):
        return EdgarInsiderSummary(ticker=query.ticker.upper(), company_name="NVIDIA", cik="1", recent_form4s=(), total_form4_count=5)


class FakeCoinGecko:
    def get_prices(self, query):
        return [CoinGeckoPrice("bitcoin", "usd", 70000, 10, 20)]


class FakeDeribit:
    def get_futures_term_structure(self, query):
        return DeribitFuturesTermStructure(currency="BTC", points=(DeribitFutureTermPoint("BTC-27JUN26", 100000, 99900, 1000),))

    def get_option_chain(self, query):
        return DeribitOptionChain(currency="BTC", quotes=(DeribitOptionQuote("BTC-27JUN26-100000-C", 55, 100000, 54, 56),))


class WorkflowTests(unittest.TestCase):
    def test_recession_workflow_enriches_evidence(self) -> None:
        task = TaskSpec(question="Will there be a recession?", task_type=TaskType.MACRO, horizon=TimeHorizon.MEDIUM)
        analysis = AnalysisEngine().analyze(task, SimplePlanner().plan(task))
        workflow = RecessionWorkflow(
            treasury=FakeTreasury(), fedwatch=FakeFedWatch(), fear_greed=FakeFearGreed(), polymarket=FakePolymarketRecession()
        )
        enriched = workflow.enrich(analysis)
        self.assertGreater(len(enriched.evidence.items), len(analysis.evidence.items))

    def test_geopolitical_workflow_enriches_evidence(self) -> None:
        task = TaskSpec(question="What is war risk?", task_type=TaskType.GEOPOLITICAL, horizon=TimeHorizon.SHORT)
        analysis = AnalysisEngine().analyze(task, SimplePlanner().plan(task))
        workflow = GeopoliticalRiskWorkflow(
            polymarket=FakePolymarketWar(), fear_greed=FakeFearGreed(), gold_prices=FakeYahooPrice(), cftc=FakeCftc()
        )
        enriched = workflow.enrich(analysis)
        self.assertTrue(any(item.label == "gold" for item in enriched.evidence.items))
        self.assertTrue(any(item.label == "gold_cot" for item in enriched.evidence.items))

    def test_asset_pricing_workflow_enriches_evidence(self) -> None:
        task = TaskSpec(question="Is gold attractive now?", task_type=TaskType.ASSET, horizon=TimeHorizon.MEDIUM)
        analysis = AnalysisEngine().analyze(task, SimplePlanner().plan(task))
        workflow = AssetPricingWorkflow(prices=FakeYahooPrice(), treasury=FakeTreasury(), fear_greed=FakeFearGreed())
        enriched = workflow.enrich(analysis, symbol="GLD")
        self.assertTrue(any(item.label == "GLD" for item in enriched.evidence.items))

    def test_bubble_workflow_enriches_evidence(self) -> None:
        task = TaskSpec(question="Is AI in a bubble?", task_type=TaskType.BUBBLE, horizon=TimeHorizon.MEDIUM)
        analysis = AnalysisEngine().analyze(task, SimplePlanner().plan(task))
        workflow = BubbleAssessmentWorkflow(
            prices=FakeYahooPrice(),
            options=FakeYFinance(),
            insiders=FakeEdgar(),
            coingecko=FakeCoinGecko(),
            deribit=FakeDeribit(),
            fear_greed=FakeFearGreed(),
            polymarket=FakePolymarketAI(),
            cftc=FakeCftc(),
        )
        enriched = workflow.enrich(analysis, ticker="NVDA")
        labels = {item.label for item in enriched.evidence.items}
        self.assertIn("NVDA", labels)
        self.assertIn("yfinance:NVDA:options", labels)
        self.assertIn("edgar:NVDA", labels)


if __name__ == "__main__":
    unittest.main()
