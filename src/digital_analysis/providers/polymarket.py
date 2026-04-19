from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Mapping

from ..execution.http import JsonHttpClient, UrllibHttpClient
from .base import ProviderParseError, SignalProvider

GAMMA_BASE_URL = "https://gamma-api.polymarket.com"


def _coerce_float(value: object) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _json_list(value: object, *, field_name: str) -> list[object]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        try:
            decoded = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ProviderParseError(f"invalid {field_name}: {text}") from exc
        if isinstance(decoded, list):
            return decoded
    raise ProviderParseError(f"unexpected {field_name} type: {type(value).__name__}")


@dataclass(frozen=True)
class OutcomeQuote:
    name: str
    probability: float | None
    token_id: str | None = None


@dataclass
class PolymarketMarket:
    id: str
    slug: str
    question: str
    active: bool
    closed: bool
    volume: float | None
    liquidity: float | None
    best_bid: float | None
    best_ask: float | None
    outcomes: tuple[OutcomeQuote, ...]
    raw: Mapping[str, Any] = field(default_factory=dict, repr=False)

    @property
    def yes_probability(self) -> float | None:
        for outcome in self.outcomes:
            if outcome.name.strip().lower() == "yes":
                return outcome.probability
        return None


@dataclass
class PolymarketEvent:
    id: str
    slug: str
    title: str
    active: bool
    closed: bool
    volume: float | None
    liquidity: float | None
    markets: tuple[PolymarketMarket, ...]
    raw: Mapping[str, Any] = field(default_factory=dict, repr=False)


@dataclass(frozen=True)
class PolymarketEventQuery:
    limit: int = 20
    offset: int = 0
    active: bool | None = True
    closed: bool | None = False
    slug_contains: str | None = None


class PolymarketProvider(SignalProvider):
    provider_id = "polymarket"
    display_name = "Polymarket"
    capabilities = ("event_markets",)

    def __init__(self, http_client: JsonHttpClient | None = None):
        self.http_client = http_client or UrllibHttpClient()

    def list_events(self, query: PolymarketEventQuery | None = None) -> list[PolymarketEvent]:
        query = query or PolymarketEventQuery()
        payload = self.http_client.get_json(
            f"{GAMMA_BASE_URL}/events",
            params={
                "limit": query.limit,
                "offset": query.offset,
                "active": query.active,
                "closed": query.closed,
            },
        )
        if not isinstance(payload, list):
            raise ProviderParseError("expected events payload to be a list")
        events = [self._parse_event(item) for item in payload if isinstance(item, Mapping)]
        if query.slug_contains:
            needle = query.slug_contains.strip().lower()
            events = [e for e in events if needle in e.title.lower() or needle in e.slug.lower()]
        return events

    def _parse_event(self, raw_event: Mapping[str, Any]) -> PolymarketEvent:
        raw_markets = raw_event.get("markets")
        markets: list[PolymarketMarket] = []
        if isinstance(raw_markets, list):
            for item in raw_markets:
                if isinstance(item, Mapping):
                    markets.append(self._parse_market(item))
        return PolymarketEvent(
            id=str(raw_event.get("id", "")),
            slug=str(raw_event.get("slug", "")),
            title=str(raw_event.get("title", "")),
            active=bool(raw_event.get("active")),
            closed=bool(raw_event.get("closed")),
            volume=_coerce_float(raw_event.get("volume")),
            liquidity=_coerce_float(raw_event.get("liquidity")),
            markets=tuple(markets),
            raw=raw_event,
        )

    def _parse_market(self, raw_market: Mapping[str, Any]) -> PolymarketMarket:
        outcome_names = _json_list(raw_market.get("outcomes"), field_name="outcomes")
        outcome_prices = _json_list(raw_market.get("outcomePrices"), field_name="outcomePrices")
        token_ids = _json_list(raw_market.get("clobTokenIds"), field_name="clobTokenIds")
        outcomes: list[OutcomeQuote] = []
        for idx, name in enumerate(outcome_names):
            price = outcome_prices[idx] if idx < len(outcome_prices) else None
            token_id = token_ids[idx] if idx < len(token_ids) else None
            outcomes.append(OutcomeQuote(name=str(name), probability=_coerce_float(price), token_id=str(token_id) if token_id is not None else None))
        return PolymarketMarket(
            id=str(raw_market.get("id", "")),
            slug=str(raw_market.get("slug", "")),
            question=str(raw_market.get("question", "")),
            active=bool(raw_market.get("active")),
            closed=bool(raw_market.get("closed")),
            volume=_coerce_float(raw_market.get("volume")),
            liquidity=_coerce_float(raw_market.get("liquidity")),
            best_bid=_coerce_float(raw_market.get("bestBid")),
            best_ask=_coerce_float(raw_market.get("bestAsk")),
            outcomes=tuple(outcomes),
            raw=raw_market,
        )
