from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from ..execution.http import JsonHttpClient, UrllibHttpClient
from .base import ProviderParseError, SignalProvider

KALSHI_API_URL = "https://api.elections.kalshi.com/trade-api/v2"


def _coerce_float(value: object) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _cent_probability(value: object) -> float | None:
    raw = _coerce_float(value)
    if raw is None:
        return None
    return raw / 100.0


@dataclass(frozen=True)
class KalshiMarketQuery:
    limit: int = 20
    status: str | None = "open"
    event_ticker: str | None = None
    series_ticker: str | None = None


@dataclass
class KalshiMarket:
    ticker: str
    event_ticker: str
    status: str
    title: str
    yes_bid: float | None
    yes_ask: float | None
    no_bid: float | None
    no_ask: float | None
    last_price: float | None
    volume: float | None
    open_interest: float | None
    raw: Mapping[str, Any] = field(default_factory=dict, repr=False)

    @property
    def midpoint(self) -> float | None:
        if self.yes_bid is None or self.yes_ask is None:
            return None
        return (self.yes_bid + self.yes_ask) / 2.0

    @property
    def yes_probability(self) -> float | None:
        return self.midpoint if self.midpoint is not None else self.last_price


class KalshiProvider(SignalProvider):
    provider_id = "kalshi"
    display_name = "Kalshi"
    capabilities = ("event_markets",)

    def __init__(self, http_client: JsonHttpClient | None = None):
        self.http_client = http_client or UrllibHttpClient()

    def list_markets(self, query: KalshiMarketQuery | None = None) -> list[KalshiMarket]:
        query = query or KalshiMarketQuery()
        payload = self.http_client.get_json(
            f"{KALSHI_API_URL}/markets",
            params={
                "limit": query.limit,
                "status": query.status,
                "event_ticker": query.event_ticker,
                "series_ticker": query.series_ticker,
                "mve_filter": "exclude",
            },
        )
        if not isinstance(payload, Mapping):
            raise ProviderParseError("expected Kalshi payload to be an object")
        rows = payload.get("markets")
        if not isinstance(rows, list):
            raise ProviderParseError("expected Kalshi payload.markets to be a list")
        markets: list[KalshiMarket] = []
        for row in rows:
            if isinstance(row, Mapping):
                markets.append(self._parse_market(row))
        return markets

    def _parse_market(self, row: Mapping[str, Any]) -> KalshiMarket:
        return KalshiMarket(
            ticker=str(row.get("ticker", "")),
            event_ticker=str(row.get("event_ticker", "")),
            status=str(row.get("status", "")),
            title=str(row.get("title", "")),
            yes_bid=_cent_probability(row.get("yes_bid")),
            yes_ask=_cent_probability(row.get("yes_ask")),
            no_bid=_cent_probability(row.get("no_bid")),
            no_ask=_cent_probability(row.get("no_ask")),
            last_price=_cent_probability(row.get("last_price")),
            volume=_coerce_float(row.get("volume")),
            open_interest=_coerce_float(row.get("open_interest")),
            raw=row,
        )
