from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import date
from io import StringIO
from typing import Mapping

from ..execution.http import TextHttpClient, UrllibHttpClient
from .base import ProviderParseError, SignalProvider

TREASURY_RATES_CSV_URL = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv"


def _coerce_float(value: object) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


@dataclass(frozen=True)
class YieldPoint:
    tenor: str
    value: float


@dataclass
class YieldCurveSnapshot:
    curve_kind: str
    date: str
    points: tuple[YieldPoint, ...]
    raw: Mapping[str, str] = field(default_factory=dict, repr=False)

    def yield_for(self, tenor: str) -> float | None:
        target = tenor.strip().upper().replace(" ", "")
        for point in self.points:
            if point.tenor == target:
                return point.value
        return None

    def spread(self, long_tenor: str, short_tenor: str) -> float | None:
        long_rate = self.yield_for(long_tenor)
        short_rate = self.yield_for(short_tenor)
        if long_rate is None or short_rate is None:
            return None
        return long_rate - short_rate


@dataclass(frozen=True)
class YieldCurveQuery:
    year: int = field(default_factory=lambda: date.today().year)
    curve_kind: str = "nominal"


class USTreasuryProvider(SignalProvider):
    provider_id = "us_treasury"
    display_name = "U.S. Treasury"
    capabilities = ("yield_curves",)

    def __init__(self, http_client: TextHttpClient | None = None):
        self.http_client = http_client or UrllibHttpClient()

    def list_yield_curve(self, query: YieldCurveQuery | None = None) -> list[YieldCurveSnapshot]:
        query = query or YieldCurveQuery()
        payload = self.http_client.get_text(
            f"{TREASURY_RATES_CSV_URL}/{query.year}/all",
            params={"type": "daily_treasury_yield_curve"},
        )
        return self._parse_curve_csv(payload, curve_kind=query.curve_kind)

    def latest_yield_curve(self, query: YieldCurveQuery | None = None) -> YieldCurveSnapshot | None:
        observations = self.list_yield_curve(query)
        return observations[0] if observations else None

    def _parse_curve_csv(self, payload: str, *, curve_kind: str) -> list[YieldCurveSnapshot]:
        reader = csv.DictReader(StringIO(payload))
        if not reader.fieldnames or "Date" not in reader.fieldnames:
            raise ProviderParseError("expected Treasury CSV to include a Date column")
        points_columns = [field for field in reader.fieldnames if field != "Date"]
        observations: list[YieldCurveSnapshot] = []
        for row in reader:
            if not row:
                continue
            raw_date = row.get("Date")
            if not raw_date:
                continue
            points: list[YieldPoint] = []
            for column in points_columns:
                value = _coerce_float(row.get(column))
                if value is None:
                    continue
                points.append(YieldPoint(tenor=column.strip().upper().replace(" ", ""), value=value))
            observations.append(YieldCurveSnapshot(curve_kind=curve_kind, date=str(raw_date), points=tuple(points), raw={key: value or "" for key, value in row.items()}))
        return observations
