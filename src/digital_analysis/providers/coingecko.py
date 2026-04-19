from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from ..execution.http import JsonHttpClient, UrllibHttpClient
from ._coerce import _coerce_float, _coerce_int
from .base import ProviderParseError, SignalProvider

BASE_URL = "https://api.coingecko.com/api/v3"


@dataclass(frozen=True)
class CoinGeckoPriceQuery:
    coin_ids: tuple[str, ...]
    vs_currency: str = "usd"


@dataclass(frozen=True)
class CoinGeckoPrice:
    coin_id: str
    vs_currency: str
    price: float | None
    market_cap: float | None = None
    volume_24h: float | None = None


@dataclass(frozen=True)
class CoinGeckoMarketQuery:
    vs_currency: str = "usd"
    ids: tuple[str, ...] = ()
    order: str = "market_cap_desc"
    per_page: int = 50
    page: int = 1


@dataclass
class CoinGeckoMarket:
    coin_id: str
    symbol: str
    name: str
    current_price: float | None
    market_cap: float | None
    market_cap_rank: int | None
    total_volume: float | None
    price_change_percentage_24h: float | None
    raw: Mapping[str, Any] = field(default_factory=dict, repr=False)


class CoinGeckoProvider(SignalProvider):
    provider_id = "coingecko"
    display_name = "CoinGecko"
    capabilities = ("crypto_spot", "crypto_market")

    def __init__(self, http_client: JsonHttpClient | None = None):
        self.http_client = http_client or UrllibHttpClient()

    def get_prices(self, query: CoinGeckoPriceQuery) -> list[CoinGeckoPrice]:
        payload = self.http_client.get_json(
            f"{BASE_URL}/simple/price",
            params={
                "ids": ",".join(query.coin_ids),
                "vs_currencies": query.vs_currency,
                "include_market_cap": "true",
                "include_24hr_vol": "true",
            },
        )
        if not isinstance(payload, Mapping):
            raise ProviderParseError("expected CoinGecko simple price response to be an object")
        results: list[CoinGeckoPrice] = []
        for coin_id in query.coin_ids:
            row = payload.get(coin_id)
            if not isinstance(row, Mapping):
                continue
            results.append(
                CoinGeckoPrice(
                    coin_id=coin_id,
                    vs_currency=query.vs_currency,
                    price=_coerce_float(row.get(query.vs_currency)),
                    market_cap=_coerce_float(row.get(f"{query.vs_currency}_market_cap")),
                    volume_24h=_coerce_float(row.get(f"{query.vs_currency}_24h_vol")),
                )
            )
        return results

    def list_markets(self, query: CoinGeckoMarketQuery | None = None) -> list[CoinGeckoMarket]:
        query = query or CoinGeckoMarketQuery()
        payload = self.http_client.get_json(
            f"{BASE_URL}/coins/markets",
            params={
                "vs_currency": query.vs_currency,
                "ids": ",".join(query.ids) if query.ids else None,
                "order": query.order,
                "per_page": query.per_page,
                "page": query.page,
                "sparkline": "false",
            },
        )
        if not isinstance(payload, list):
            raise ProviderParseError("expected CoinGecko markets payload to be a list")
        rows: list[CoinGeckoMarket] = []
        for item in payload:
            if not isinstance(item, Mapping):
                continue
            rows.append(
                CoinGeckoMarket(
                    coin_id=str(item.get("id", "")),
                    symbol=str(item.get("symbol", "")),
                    name=str(item.get("name", "")),
                    current_price=_coerce_float(item.get("current_price")),
                    market_cap=_coerce_float(item.get("market_cap")),
                    market_cap_rank=_coerce_int(item.get("market_cap_rank")),
                    total_volume=_coerce_float(item.get("total_volume")),
                    price_change_percentage_24h=_coerce_float(item.get("price_change_percentage_24h")),
                    raw=item,
                )
            )
        return rows
