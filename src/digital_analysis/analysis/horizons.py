from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class HorizonBucket:
    short_term: tuple[str, ...] = field(default_factory=tuple)
    medium_term: tuple[str, ...] = field(default_factory=tuple)
    long_term: tuple[str, ...] = field(default_factory=tuple)
    unknown: tuple[str, ...] = field(default_factory=tuple)


class HorizonGroupingEngine:
    def group(self, signals: tuple[str, ...]) -> HorizonBucket:
        short_term: list[str] = []
        medium_term: list[str] = []
        long_term: list[str] = []
        unknown: list[str] = []

        for signal in signals:
            s = signal.lower()
            if any(word in s for word in ("options", "iv", "fedwatch", "prediction market", "vix")):
                short_term.append(signal)
            elif any(word in s for word in ("yield curve", "positioning", "risk appetite", "fear & greed")):
                medium_term.append(signal)
            elif any(word in s for word in ("credit gap", "world bank", "capex", "structural")):
                long_term.append(signal)
            else:
                unknown.append(signal)

        return HorizonBucket(
            short_term=tuple(short_term),
            medium_term=tuple(medium_term),
            long_term=tuple(long_term),
            unknown=tuple(unknown),
        )
