import unittest

from digital_analysis.providers.yfinance_provider import (
    OptionsChainQuery,
    YFinanceProvider,
    black_scholes_greeks,
)


class FakeOptionsFetcher:
    def __init__(self):
        self.expirations = ("2099-04-17",)
        self.underlying_price = 150.0
        self.calls = [
            {
                "contractSymbol": "AAPL990417C00150000",
                "strike": 150.0,
                "lastPrice": 5.20,
                "bid": 5.00,
                "ask": 5.40,
                "volume": 3000,
                "openInterest": 8000,
                "impliedVolatility": 0.25,
                "inTheMoney": False,
            }
        ]
        self.puts = [
            {
                "contractSymbol": "AAPL990417P00150000",
                "strike": 150.0,
                "lastPrice": 3.40,
                "bid": 3.20,
                "ask": 3.60,
                "volume": 2500,
                "openInterest": 7000,
                "impliedVolatility": 0.26,
                "inTheMoney": True,
            }
        ]

    def fetch_expirations(self, ticker: str):
        return self.expirations

    def fetch_chain(self, ticker: str, expiration: str):
        from digital_analysis.providers.yfinance_provider import _ChainRows

        return _ChainRows(calls=self.calls, puts=self.puts)

    def fetch_underlying_price(self, ticker: str):
        return self.underlying_price


class YFinanceTests(unittest.TestCase):
    def test_black_scholes(self) -> None:
        g = black_scholes_greeks(100, 100, 1.0, 0.05, 0.2, "call")
        self.assertIsNotNone(g)
        assert g is not None
        self.assertGreater(g.delta, 0)

    def test_get_chain(self) -> None:
        provider = YFinanceProvider(fetcher=FakeOptionsFetcher())
        chain = provider.get_chain(OptionsChainQuery(ticker="AAPL"))
        self.assertEqual(chain.ticker, "AAPL")
        self.assertEqual(len(chain.calls), 1)
        self.assertEqual(len(chain.puts), 1)
        self.assertIsNotNone(chain.atm_iv)
        self.assertIsNotNone(chain.implied_move())
        self.assertIsNotNone(chain.calls[0].greeks)


if __name__ == "__main__":
    unittest.main()
