from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from ..execution.http import JsonHttpClient, UrllibHttpClient
from ._coerce import _coerce_float
from .base import ProviderParseError, SignalProvider

BASE_URL = "https://www.deribit.com/api/v2"


@dataclass(frozen=True)
class DeribitFuturesCurveQuery:
    currency: str = "BTC"


@dataclass(frozen=True)
class DeribitOptionChainQuery:
    currency: str = "BTC"


@dataclass(frozen=True)
class DeribitFutureTermPoint:
    instrument_name: str
    mark_price: float | None
    last_price: float | None
    open_interest: float | None


@dataclass
class DeribitFuturesTermStructure:
    currency: str
    points: tuple[DeribitFutureTermPoint, ...]


@dataclass(frozen=True)
class DeribitOptionQuote:
    instrument_name: str
    mark_iv: float | None
    underlying_price: float | None
    bid_iv: float | None
    ask_iv: float | None


@dataclass
class DeribitOptionChain:
    currency: str
    quotes: tuple[DeribitOptionQuote, ...]
    raw: Mapping[str, Any] = field(default_factory=dict, repr=False)


class DeribitProvider(SignalProvider):
    provider_id = "deribit"
    display_name = "Deribit"
    capabilities = ("futures_curve", "options_chain")

    def __init__(self, http_client: JsonHttpClient | None = None):
        self.http_client = http_client or UrllibHttpClient()

    def get_futures_term_structure(self, query: DeribitFuturesCurveQuery | None = None) -> DeribitFuturesTermStructure:
        query = query or DeribitFuturesCurveQuery()
        payload = self.http_client.get_json(
            f"{BASE_URL}/public/get_book_summary_by_currency",
            params={"currency": query.currency, "kind": "future"},
        )
        rows = self._extract_result_list(payload)
        points: list[DeribitFutureTermPoint] = []
        for item in rows:
            if not isinstance(item, Mapping):
                continue
            points.append(
                DeribitFutureTermPoint(
                    instrument_name=str(item.get("instrument_name", "")),
                    mark_price=_coerce_float(item.get("mark_price")),
                    last_price=_coerce_float(item.get("last")),
                    open_interest=_coerce_float(item.get("open_interest")),
                )
            )
        return DeribitFuturesTermStructure(currency=query.currency, points=tuple(points))

    def get_option_chain(self, query: DeribitOptionChainQuery | None = None) -> DeribitOptionChain:
        query = query or DeribitOptionChainQuery()
        payload = self.http_client.get_json(
            f"{BASE_URL}/public/get_book_summary_by_currency",
            params={"currency": query.currency, "kind": "option"},
        )
        rows = self._extract_result_list(payload)
        quotes: list[DeribitOptionQuote] = []
        for item in rows:
            if not isinstance(item, Mapping):
                continue
            quotes.append(
                DeribitOptionQuote(
                    instrument_name=str(item.get("instrument_name", "")),
                    mark_iv=_coerce_float(item.get("mark_iv")),
                    underlying_price=_coerce_float(item.get("underlying_price")),
                    bid_iv=_coerce_float(item.get("bid_iv")),
                    ask_iv=_coerce_float(item.get("ask_iv")),
                )
            )
        return DeribitOptionChain(currency=query.currency, quotes=tuple(quotes), raw=payload if isinstance(payload, Mapping) else {})

    def _extract_result_list(self, payload: object) -> list[object]:
        if not isinstance(payload, Mapping):
            raise ProviderParseError("expected Deribit payload to be an object")
        result = payload.get("result")
        if not isinstance(result, list):
            raise ProviderParseError("expected Deribit payload.result to be a list")
        return result
