from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Mapping

from ..execution.http import JsonHttpClient, UrllibHttpClient
from ._coerce import _coerce_float
from .base import ProviderParseError, SignalProvider
from .prices import PriceBar, PriceHistory, PriceHistoryQuery

BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart"
_INTERVAL_MAP = {"d": "1d", "w": "1wk", "m": "1mo"}


class YahooPriceProvider(SignalProvider):
    provider_id = "yahoo_price"
    display_name = "Yahoo Finance Price"
    capabilities = ("price_history",)

    def __init__(self, http_client: JsonHttpClient | None = None):
        self.http_client = http_client or UrllibHttpClient()

    def get_history(self, query: PriceHistoryQuery) -> PriceHistory:
        payload = self.http_client.get_json(
            f"{BASE_URL}/{query.symbol}",
            params={
                "interval": _INTERVAL_MAP.get(query.interval, "1d"),
                "range": "1y" if query.limit is None else "3mo",
                "includeAdjustedClose": "true",
            },
        )
        if not isinstance(payload, Mapping):
            raise ProviderParseError("expected Yahoo chart payload to be an object")
        chart = payload.get("chart")
        if not isinstance(chart, Mapping):
            raise ProviderParseError("expected Yahoo payload.chart to be an object")
        result = chart.get("result")
        if not isinstance(result, list) or not result or not isinstance(result[0], Mapping):
            raise ProviderParseError("expected Yahoo payload.chart.result[0]")
        row = result[0]
        timestamps = row.get("timestamp")
        indicators = row.get("indicators")
        if not isinstance(timestamps, list) or not isinstance(indicators, Mapping):
            raise ProviderParseError("expected Yahoo timestamps and indicators")
        quote_list = indicators.get("quote")
        if not isinstance(quote_list, list) or not quote_list or not isinstance(quote_list[0], Mapping):
            raise ProviderParseError("expected Yahoo indicators.quote[0]")
        quote = quote_list[0]
        opens = quote.get("open") if isinstance(quote.get("open"), list) else []
        highs = quote.get("high") if isinstance(quote.get("high"), list) else []
        lows = quote.get("low") if isinstance(quote.get("low"), list) else []
        closes = quote.get("close") if isinstance(quote.get("close"), list) else []
        volumes = quote.get("volume") if isinstance(quote.get("volume"), list) else []
        bars: list[PriceBar] = []
        for i, ts in enumerate(timestamps):
            open_ = _coerce_float(opens[i] if i < len(opens) else None)
            high = _coerce_float(highs[i] if i < len(highs) else None)
            low = _coerce_float(lows[i] if i < len(lows) else None)
            close = _coerce_float(closes[i] if i < len(closes) else None)
            if open_ is None or high is None or low is None or close is None:
                continue
            dt = datetime.fromtimestamp(int(ts), tz=timezone.utc).date().isoformat()
            bars.append(PriceBar(date=dt, open=open_, high=high, low=low, close=close, volume=_coerce_float(volumes[i] if i < len(volumes) else None)))
        if query.limit is not None:
            bars = bars[-query.limit :]
        return PriceHistory(symbol=query.symbol.upper(), interval=query.interval, bars=tuple(bars), provider_id=self.provider_id, raw_symbol=query.symbol)
