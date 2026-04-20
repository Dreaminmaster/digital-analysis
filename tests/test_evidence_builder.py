import unittest

from digital_analysis.analysis.evidence_builder import EvidenceBuilder
from digital_analysis.providers.cftc import CftcCotReport
from digital_analysis.providers.cme_fedwatch import FedMeetingProbability, FedRateProb
from digital_analysis.providers.coingecko import CoinGeckoPrice
from digital_analysis.providers.deribit import DeribitFutureTermPoint, DeribitFuturesTermStructure, DeribitOptionChain, DeribitOptionQuote
from digital_analysis.providers.edgar import EdgarInsiderSummary
from digital_analysis.providers.fear_greed import FearGreedSnapshot
from digital_analysis.providers.polymarket import OutcomeQuote, PolymarketEvent, PolymarketMarket
from digital_analysis.providers.treasury import YieldCurveSnapshot, YieldPoint
from digital_analysis.providers.yfinance_provider import OptionContract, OptionsChain


class EvidenceBuilderTests(unittest.TestCase):
    def test_treasury_curve_evidence(self) -> None:
        curve = YieldCurveSnapshot(
            curve_kind="nominal",
            date="2026-04-20",
            points=(YieldPoint("10Y", 4.2), YieldPoint("2Y", 4.5)),
        )
        items = EvidenceBuilder().from_treasury_curve(curve)
        self.assertEqual(len(items), 1)
        self.assertIn("10Y-2Y", items[0].value_text or "")

    def test_fedwatch_evidence(self) -> None:
        rows = [
            FedMeetingProbability(
                meeting_date="2026-06-17",
                current_target_low=0.0425,
                current_target_high=0.0450,
                probabilities=(FedRateProb(0.04, 0.0425, 0.7),),
            )
        ]
        items = EvidenceBuilder().from_fedwatch(rows)
        self.assertEqual(len(items), 1)
        self.assertIn("top band", items[0].value_text or "")

    def test_fear_greed_evidence(self) -> None:
        snap = FearGreedSnapshot(score=60, rating="Greed", timestamp="x", previous_close=55)
        items = EvidenceBuilder().from_fear_greed(snap)
        self.assertEqual(items[0].direction, "risk_on")

    def test_polymarket_evidence(self) -> None:
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
        event = PolymarketEvent(id="e1", slug="recession", title="US recession?", active=True, closed=False, volume=None, liquidity=None, markets=(market,))
        items = EvidenceBuilder().from_polymarket_events([event])
        self.assertEqual(len(items), 1)
        self.assertIn("yes=42.0%", items[0].value_text or "")

    def test_cftc_evidence(self) -> None:
        rows = [CftcCotReport("GOLD", "2026-04-14", 1000, 300, 100, 200, 250)]
        items = EvidenceBuilder().from_cftc_reports(rows)
        self.assertEqual(items[0].direction, "spec_long")

    def test_coingecko_evidence(self) -> None:
        rows = [CoinGeckoPrice("bitcoin", "usd", 70000, 10, 20)]
        items = EvidenceBuilder().from_coingecko_prices(rows)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].label, "coingecko:bitcoin")

    def test_edgar_evidence(self) -> None:
        summary = EdgarInsiderSummary(ticker="NVDA", company_name="NVIDIA", cik="1", recent_form4s=(), total_form4_count=5)
        items = EvidenceBuilder().from_edgar_insiders(summary)
        self.assertEqual(items[0].label, "edgar:NVDA")

    def test_deribit_evidence(self) -> None:
        futures = DeribitFuturesTermStructure(currency="BTC", points=(DeribitFutureTermPoint("BTC-27JUN26", 100000, 99900, 1000),))
        items = EvidenceBuilder().from_deribit_futures(futures)
        self.assertEqual(len(items), 1)
        chain = DeribitOptionChain(currency="BTC", quotes=(DeribitOptionQuote("BTC-27JUN26-100000-C", 55, 100000, 54, 56),))
        items2 = EvidenceBuilder().from_deribit_options(chain)
        self.assertEqual(len(items2), 1)

    def test_yfinance_evidence(self) -> None:
        chain = OptionsChain(
            ticker="NVDA",
            expiration="2099-04-17",
            underlying_price=150.0,
            calls=(OptionContract("c", "call", "2099-04-17", 150, last_price=5.2, bid=5.0, ask=5.4, mid=5.2, implied_volatility=0.25),),
            puts=(OptionContract("p", "put", "2099-04-17", 150, last_price=3.4, bid=3.2, ask=3.6, mid=3.4, implied_volatility=0.26),),
        )
        items = EvidenceBuilder().from_yfinance_chain(chain)
        self.assertEqual(len(items), 1)
        self.assertIn("atm_iv", items[0].value_text or "")


if __name__ == "__main__":
    unittest.main()
