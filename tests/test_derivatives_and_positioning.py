import unittest
from typing import Any, Mapping

from digital_analysis.providers.cftc import CftcCotProvider, CftcCotQuery
from digital_analysis.providers.deribit import DeribitFuturesCurveQuery, DeribitOptionChainQuery, DeribitProvider


class FakeJsonClient:
    def __init__(self, payload: Any):
        self.payload = payload

    def get_json(self, url: str, *, params: Mapping[str, object] | None = None) -> Any:
        return self.payload

    def post_json(self, url: str, *, body: Mapping[str, object] | None = None, params: Mapping[str, object] | None = None, headers: Mapping[str, str] | None = None) -> Any:
        return self.payload


class DerivativesAndPositioningTests(unittest.TestCase):
    def test_cftc_parse(self) -> None:
        payload = [{
            "market_and_exchange_names": "GOLD - COMMODITY EXCHANGE INC.",
            "report_date_as_yyyy_mm_dd": "2026-04-14",
            "open_interest_all": "1000",
            "noncomm_positions_long_all": "300",
            "noncomm_positions_short_all": "100",
            "comm_positions_long_all": "200",
            "comm_positions_short_all": "250",
        }]
        rows = CftcCotProvider(http_client=FakeJsonClient(payload)).list_reports(CftcCotQuery(commodity_name="GOLD"))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].noncommercial_net, 200)

    def test_deribit_futures_parse(self) -> None:
        payload = {"result": [{"instrument_name": "BTC-27JUN26", "mark_price": 102000, "last": 101500, "open_interest": 1234}]}
        curve = DeribitProvider(http_client=FakeJsonClient(payload)).get_futures_term_structure(DeribitFuturesCurveQuery(currency="BTC"))
        self.assertEqual(len(curve.points), 1)
        self.assertAlmostEqual(curve.points[0].mark_price or 0.0, 102000)

    def test_deribit_options_parse(self) -> None:
        payload = {"result": [{"instrument_name": "BTC-27JUN26-100000-C", "mark_iv": 55, "underlying_price": 100000, "bid_iv": 54, "ask_iv": 56}]}
        chain = DeribitProvider(http_client=FakeJsonClient(payload)).get_option_chain(DeribitOptionChainQuery(currency="BTC"))
        self.assertEqual(len(chain.quotes), 1)
        self.assertAlmostEqual(chain.quotes[0].mark_iv or 0.0, 55)


if __name__ == "__main__":
    unittest.main()
