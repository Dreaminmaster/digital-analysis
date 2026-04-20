from __future__ import annotations

import csv
from dataclasses import dataclass
from io import StringIO

from ..execution.http import TextHttpClient, UrllibHttpClient
from ._coerce import _coerce_float
from .base import ProviderParseError, SignalProvider
from .prices import PriceBar, PriceHistory, PriceHistoryQuery

BASE_URL = "https://stooq.com/q/d/l/"
_INTERVAL_MAP = {"d": "d", "w": "w", "m": "m"}


class StooqProvider(SignalProvider):
    provider_id = "stooq"
    display_name = "Stooq"
    capabilities = ("price_history",)

    def __init__(self, http_client: TextHttpClient | None = None):
        self.http_client = http_client or UrllibHttpClient()

    def get_history(self, query: PriceHistoryQuery) -> PriceHistory:
        interval = _INTERVAL_MAP.get(query.interval, "d")
        symbol = query.symbol.lower()
        payload = self.http_client.get_text(
            BASE_URL,
            params={"s": symbol, "i": interval},
        )
        reader = csv.DictReader(StringIO(payload))
        if not reader.fieldnames or "Date" not in reader.fieldnames:
            raise ProviderParseError("expected Stooq CSV with Date column")
        bars: list[PriceBar] = []
        for row in reader:
            if not row:
                continue
            open_ = _coerce_float(row.get("Open"))
            high = _coerce_float(row.get("High"))
            low = _coerce_float(row.get("Low"))
            close = _coerce_float(row.get("Close"))
            if open_ is None or high is None or low is None or close is None:
                continue
            bars.append(
                PriceBar(
                    date=str(row.get("Date", "")),
                    open=open_,
                    high=high,
                    low=low,
                    close=close,
                    volume=_coerce_float(row.get("Volume")),
                )
            )
        if query.limit is not None:
            bars = bars[-query.limit :]
        return PriceHistory(symbol=query.symbol.upper(), interval=query.interval, bars=tuple(bars), provider_id=self.provider_id, raw_symbol=symbol)
