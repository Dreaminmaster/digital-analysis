from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PriceBar:
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float | None = None


@dataclass
class PriceHistory:
    symbol: str
    interval: str
    bars: tuple[PriceBar, ...]
    provider_id: str | None = None
    raw_symbol: str | None = None
    metadata: dict[str, object] = field(default_factory=dict, repr=False)

    @property
    def latest(self) -> PriceBar | None:
        return self.bars[-1] if self.bars else None

    @property
    def earliest(self) -> PriceBar | None:
        return self.bars[0] if self.bars else None


@dataclass(frozen=True)
class PriceHistoryQuery:
    symbol: str
    interval: str = "d"
    start_date: str | None = None
    end_date: str | None = None
    limit: int | None = None
