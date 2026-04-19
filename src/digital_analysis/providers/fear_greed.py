from __future__ import annotations

from dataclasses import dataclass

from ..execution.http import JsonHttpClient, UrllibHttpClient
from .base import ProviderParseError, SignalProvider

_URL = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"


def _coerce_float(value: object) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


@dataclass(frozen=True)
class FearGreedSnapshot:
    score: float
    rating: str
    timestamp: str | None
    previous_close: float | None


_BROWSER_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://edition.cnn.com/",
}


class FearGreedProvider(SignalProvider):
    provider_id = "fear_greed"
    display_name = "CNN Fear & Greed Index"
    capabilities = ("market_sentiment",)

    def __init__(self, http_client: JsonHttpClient | None = None) -> None:
        self.http_client = http_client or UrllibHttpClient(headers=_BROWSER_HEADERS)

    def get_index(self) -> FearGreedSnapshot:
        data = self.http_client.get_json(_URL)
        if not isinstance(data, dict):
            raise ProviderParseError("unexpected response type from CNN Fear & Greed")
        fg = data.get("fear_and_greed")
        if not isinstance(fg, dict):
            raise ProviderParseError("missing 'fear_and_greed' in response")
        score = _coerce_float(fg.get("score"))
        if score is None:
            raise ProviderParseError("missing or invalid 'score' in fear_and_greed")
        rating = fg.get("rating") if isinstance(fg.get("rating"), str) else "Unknown"
        return FearGreedSnapshot(
            score=score,
            rating=rating,
            timestamp=fg.get("timestamp") if isinstance(fg.get("timestamp"), str) else None,
            previous_close=_coerce_float(fg.get("previous_close")),
        )
