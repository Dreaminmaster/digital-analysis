import unittest
from typing import Any, Mapping

from digital_analysis.providers.bis import BisCreditGapQuery, BisProvider, BisRateQuery
from digital_analysis.providers.coingecko import CoinGeckoMarketQuery, CoinGeckoPriceQuery, CoinGeckoProvider
from digital_analysis.providers.edgar import EdgarInsiderQuery, EdgarProvider


class FakeJsonClient:
    def __init__(self, payloads: dict[str, Any] | Any):
        self.payloads = payloads

    def get_json(self, url: str, *, params: Mapping[str, object] | None = None) -> Any:
        if isinstance(self.payloads, dict) and url in self.payloads:
            return self.payloads[url]
        return self.payloads

    def post_json(self, url: str, *, body: Mapping[str, object] | None = None, params: Mapping[str, object] | None = None, headers: Mapping[str, str] | None = None) -> Any:
        if isinstance(self.payloads, dict) and url in self.payloads:
            return self.payloads[url]
        return self.payloads


class FakeTextClient:
    def __init__(self, text: str):
        self.text = text
        self.calls: list[tuple[str, Mapping[str, object] | None]] = []

    def get_text(self, url: str, *, params: Mapping[str, object] | None = None) -> str:
        self.calls.append((url, params))
        return self.text


class AdditionalProviderTests(unittest.TestCase):
    def test_edgar_parse(self) -> None:
        ticker_map = {"0": {"ticker": "AAPL", "cik_str": 320193, "title": "Apple Inc."}}
        submissions = {
            "filings": {
                "recent": {
                    "form": ["4", "10-K"],
                    "accessionNumber": ["x1", "x2"],
                    "filingDate": ["2026-01-01", "2026-01-02"],
                    "reportDate": ["2025-12-31", "2025-12-31"],
                    "primaryDocument": ["a.xml", "b.htm"],
                    "primaryDocDescription": ["Form 4", "10-K"],
                }
            }
        }
        client = FakeJsonClient({
            "https://www.sec.gov/files/company_tickers.json": ticker_map,
            "https://data.sec.gov/submissions/CIK0000320193.json": submissions,
        })
        summary = EdgarProvider(http_client=client).get_insider_transactions(EdgarInsiderQuery(ticker="AAPL"))
        self.assertEqual(summary.company_name, "Apple Inc.")
        self.assertEqual(summary.total_form4_count, 1)

    def test_coingecko_prices_parse(self) -> None:
        payload = {
            "bitcoin": {"usd": 70000, "usd_market_cap": 10, "usd_24h_vol": 20},
            "ethereum": {"usd": 3500, "usd_market_cap": 30, "usd_24h_vol": 40},
        }
        rows = CoinGeckoProvider(http_client=FakeJsonClient(payload)).get_prices(
            CoinGeckoPriceQuery(coin_ids=("bitcoin", "ethereum"))
        )
        self.assertEqual(len(rows), 2)
        self.assertAlmostEqual(rows[0].price or 0.0, 70000)

    def test_coingecko_markets_parse(self) -> None:
        payload = [{"id": "bitcoin", "symbol": "btc", "name": "Bitcoin", "current_price": 70000, "market_cap": 10, "market_cap_rank": 1, "total_volume": 20, "price_change_percentage_24h": 3.2}]
        rows = CoinGeckoProvider(http_client=FakeJsonClient(payload)).list_markets(CoinGeckoMarketQuery())
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].name, "Bitcoin")

    def test_bis_policy_rates_parse(self) -> None:
        csv_text = "FREQ,REF_AREA,TIME_PERIOD,OBS_VALUE\nM,US,2026-01,4.50\n"
        rows = BisProvider(http_client=FakeTextClient(csv_text)).get_policy_rates(BisRateQuery())
        self.assertEqual(len(rows), 1)
        self.assertAlmostEqual(rows[0].rate, 4.50)

    def test_bis_credit_gap_url_shape(self) -> None:
        csv_text = "FREQ,REF_AREA,TIME_PERIOD,OBS_VALUE\nQ,US,2025-Q3,2.1\n"
        client = FakeTextClient(csv_text)
        rows = BisProvider(http_client=client).get_credit_to_gdp(BisCreditGapQuery(countries=("US", "CN"), start_year=2015))
        self.assertEqual(len(rows), 1)
        url, params = client.calls[0]
        self.assertIn("WS_CREDIT_GAP/Q.US+CN.C:G:P", url)
        assert params is not None
        self.assertEqual(params["startPeriod"], 2015)


if __name__ == "__main__":
    unittest.main()
