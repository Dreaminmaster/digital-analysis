from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from ..execution.http import JsonHttpClient, UrllibHttpClient
from ._coerce import _coerce_float
from .base import ProviderParseError, SignalProvider

BASE_URL = "https://api.worldbank.org/v2/country"


@dataclass(frozen=True)
class WorldBankQuery:
    indicator: str
    countries: tuple[str, ...] = ("US",)
    format: str = "json"
    per_page: int = 200


@dataclass(frozen=True)
class WorldBankDataPoint:
    country: str
    country_name: str
    indicator: str
    indicator_name: str
    date: str
    value: float | None


@dataclass
class WorldBankResult:
    indicator: str
    rows: tuple[WorldBankDataPoint, ...]
    raw: object | None = field(default=None, repr=False)


class WorldBankProvider(SignalProvider):
    provider_id = "world_bank"
    display_name = "World Bank"
    capabilities = ("macro_data",)

    def __init__(self, http_client: JsonHttpClient | None = None):
        self.http_client = http_client or UrllibHttpClient()

    def get_indicator(self, query: WorldBankQuery) -> WorldBankResult:
        countries = ";".join(query.countries)
        payload = self.http_client.get_json(
            f"{BASE_URL}/{countries}/indicator/{query.indicator}",
            params={"format": query.format, "per_page": query.per_page},
        )
        if not isinstance(payload, list) or len(payload) < 2 or not isinstance(payload[1], list):
            raise ProviderParseError("expected World Bank payload format [meta, rows]")
        rows: list[WorldBankDataPoint] = []
        for item in payload[1]:
            if not isinstance(item, Mapping):
                continue
            country = item.get("country")
            indicator = item.get("indicator")
            rows.append(
                WorldBankDataPoint(
                    country=str(country.get("id", "")) if isinstance(country, Mapping) else "",
                    country_name=str(country.get("value", "")) if isinstance(country, Mapping) else "",
                    indicator=str(indicator.get("id", "")) if isinstance(indicator, Mapping) else query.indicator,
                    indicator_name=str(indicator.get("value", "")) if isinstance(indicator, Mapping) else query.indicator,
                    date=str(item.get("date", "")),
                    value=_coerce_float(item.get("value")),
                )
            )
        return WorldBankResult(indicator=query.indicator, rows=tuple(rows), raw=payload)
