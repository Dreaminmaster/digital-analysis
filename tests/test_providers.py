import unittest
from typing import Any, Mapping

from digital_analysis.providers.cme_fedwatch import CMEFedWatchProvider
from digital_analysis.providers.fear_greed import FearGreedProvider
from digital_analysis.providers.polymarket import PolymarketEventQuery, PolymarketProvider
from digital_analysis.providers.treasury import USTreasuryProvider


class FakeJsonClient:
    def __init__(self, payload: Any):
        self.payload = payload

    def get_json(self, url: str, *, params: Mapping[str, object] | None = None) -> Any:
        return self.payload


class FakeTextClient:
    def __init__(self, text: str):
        self.text = text

    def get_text(self, url: str, *, params: Mapping[str, object] | None = None) -> str:
        return self.text


class ProviderTests(unittest.TestCase):
    def test_polymarket_parse(self) -> None:
        payload = [
            {
                "id": "1",
                "slug": "us-recession-2026",
                "title": "US recession in 2026?",
                "active": True,
                "closed": False,
                "markets": [
                    {
                        "id": "m1",
                        "slug": "us-recession-2026-main",
                        "question": "Will there be a US recession in 2026?",
                        "active": True,
                        "closed": False,
                        "outcomes": '["Yes","No"]',
                        "outcomePrices": '[0.42,0.58]',
                        "clobTokenIds": '["a","b"]',
                    }
                ],
            }
        ]
        provider = PolymarketProvider(http_client=FakeJsonClient(payload))
        events = provider.list_events(PolymarketEventQuery(slug_contains="recession"))
        self.assertEqual(len(events), 1)
        self.assertAlmostEqual(events[0].markets[0].yes_probability or 0.0, 0.42)

    def test_treasury_parse(self) -> None:
        csv_text = "Date,10 YR,2 YR\n2026-04-18,4.50,4.10\n"
        provider = USTreasuryProvider(http_client=FakeTextClient(csv_text))
        curve = provider.latest_yield_curve()
        self.assertIsNotNone(curve)
        assert curve is not None
        self.assertAlmostEqual(curve.spread("10YR", "2YR") or 0.0, 0.40, places=2)

    def test_fear_greed_parse(self) -> None:
        payload = {"fear_and_greed": {"score": 55, "rating": "Greed", "timestamp": "x", "previous_close": 52}}
        snap = FearGreedProvider(http_client=FakeJsonClient(payload)).get_index()
        self.assertEqual(snap.rating, "Greed")

    def test_fedwatch_parse(self) -> None:
        payload = {"meetings": [{"meetingDate": "2026-06-17", "currentTarget": "425-450", "probabilities": {"400-425": 30, "425-450": 70}}]}
        rows = CMEFedWatchProvider(http_client=FakeJsonClient(payload)).get_probabilities()
        self.assertEqual(len(rows), 1)
        self.assertEqual(len(rows[0].probabilities), 2)


if __name__ == "__main__":
    unittest.main()
