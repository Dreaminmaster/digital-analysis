import unittest
from typing import Any, Mapping

from digital_analysis.providers.stooq import StooqProvider
from digital_analysis.providers.worldbank import WorldBankProvider, WorldBankQuery
from digital_analysis.providers.yahoo import YahooPriceProvider


class FakeJsonClient:
    def __init__(self, payload: Any):
        self.payload = payload

    def get_json(self, url: str, *, params: Mapping[str, object] | None = None) -> Any:
        return self.payload

    def post_json(self, url: str, *, body: Mapping[str, object] | None = None, params: Mapping[str, object] | None = None, headers: Mapping[str, str] | None = None) -> Any:
        return self.payload


class FakeTextClient:
    def __init__(self, text: str):
        self.text = text

    def get_text(self, url: str, *, params: Mapping[str, object] | None = None) -> str:
        return self.text


class MarketDataProviderTests(unittest.TestCase):
    def test_worldbank_parse(self) -> None:
        payload = [
            {"page": 1},
            [
                {
                    "country": {"id": "US", "value": "United States"},
                    "indicator": {"id": "NY.GDP.MKTP.CD", "value": "GDP"},
                    "date": "2024",
                    "value": 100,
                }
            ],
        ]
        result = WorldBankProvider(http_client=FakeJsonClient(payload)).get_indicator(
            WorldBankQuery(indicator="NY.GDP.MKTP.CD", countries=("US",))
        )
        self.assertEqual(len(result.rows), 1)
        self.assertEqual(result.rows[0].country, "US")

    def test_stooq_parse(self) -> None:
        csv_text = "Date,Open,High,Low,Close,Volume\n2026-04-18,10,11,9,10.5,1000\n"
        history = StooqProvider(http_client=FakeTextClient(csv_text)).get_history(symbol_query())
        self.assertEqual(len(history.bars), 1)
        self.assertAlmostEqual(history.bars[0].close, 10.5)

    def test_yahoo_parse(self) -> None:
        payload = {
            "chart": {
                "result": [
                    {
                        "timestamp": [1713398400],
                        "indicators": {
                            "quote": [
                                {
                                    "open": [10],
                                    "high": [11],
                                    "low": [9],
                                    "close": [10.5],
                                    "volume": [1000],
                                }
                            ]
                        },
                    }
                ]
            }
        }
        history = YahooPriceProvider(http_client=FakeJsonClient(payload)).get_history(symbol_query())
        self.assertEqual(len(history.bars), 1)
        self.assertAlmostEqual(history.bars[0].close, 10.5)


def symbol_query():
    from digital_analysis.providers.prices import PriceHistoryQuery

    return PriceHistoryQuery(symbol="SPY", interval="d", limit=10)


if __name__ == "__main__":
    unittest.main()
