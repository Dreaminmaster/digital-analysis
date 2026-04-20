from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from ..execution.http import JsonHttpClient, UrllibHttpClient
from ._coerce import _coerce_float, _coerce_int
from .base import ProviderParseError, SignalProvider

CFTC_BASE_URL = "https://publicreporting.cftc.gov/resource/6dca-aqww.json"


@dataclass(frozen=True)
class CftcCotQuery:
    commodity_name: str | None = None
    limit: int = 20


@dataclass
class CftcCotReport:
    market_name: str
    report_date: str
    open_interest_all: int | None
    noncommercial_long: int | None
    noncommercial_short: int | None
    commercial_long: int | None
    commercial_short: int | None
    raw: Mapping[str, Any] = field(default_factory=dict, repr=False)

    @property
    def noncommercial_net(self) -> int | None:
        if self.noncommercial_long is None or self.noncommercial_short is None:
            return None
        return self.noncommercial_long - self.noncommercial_short

    @property
    def commercial_net(self) -> int | None:
        if self.commercial_long is None or self.commercial_short is None:
            return None
        return self.commercial_long - self.commercial_short


class CftcCotProvider(SignalProvider):
    provider_id = "cftc_cot"
    display_name = "CFTC COT"
    capabilities = ("positioning",)

    def __init__(self, http_client: JsonHttpClient | None = None):
        self.http_client = http_client or UrllibHttpClient()

    def list_reports(self, query: CftcCotQuery | None = None) -> list[CftcCotReport]:
        query = query or CftcCotQuery()
        where = None
        if query.commodity_name:
            where = f"market_and_exchange_names like '%{query.commodity_name}%'"
        payload = self.http_client.get_json(
            CFTC_BASE_URL,
            params={
                "$limit": query.limit,
                "$order": "report_date_as_yyyy_mm_dd desc",
                "$where": where,
            },
        )
        if not isinstance(payload, list):
            raise ProviderParseError("expected CFTC payload to be a list")
        rows: list[CftcCotReport] = []
        for item in payload:
            if not isinstance(item, Mapping):
                continue
            rows.append(
                CftcCotReport(
                    market_name=str(item.get("market_and_exchange_names", "")),
                    report_date=str(item.get("report_date_as_yyyy_mm_dd", "")),
                    open_interest_all=_coerce_int(item.get("open_interest_all")),
                    noncommercial_long=_coerce_int(item.get("noncomm_positions_long_all")),
                    noncommercial_short=_coerce_int(item.get("noncomm_positions_short_all")),
                    commercial_long=_coerce_int(item.get("comm_positions_long_all")),
                    commercial_short=_coerce_int(item.get("comm_positions_short_all")),
                    raw=item,
                )
            )
        return rows
