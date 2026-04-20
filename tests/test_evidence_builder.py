import unittest

from digital_analysis.analysis.evidence_builder import EvidenceBuilder
from digital_analysis.providers.cme_fedwatch import FedMeetingProbability, FedRateProb
from digital_analysis.providers.fear_greed import FearGreedSnapshot
from digital_analysis.providers.polymarket import OutcomeQuote, PolymarketEvent, PolymarketMarket
from digital_analysis.providers.treasury import YieldCurveSnapshot, YieldPoint


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


if __name__ == "__main__":
    unittest.main()
