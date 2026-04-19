from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class EvidenceKind(str, Enum):
    PROBABILITY = "probability"
    PRICE = "price"
    VOLATILITY = "volatility"
    CURVE = "curve"
    POSITIONING = "positioning"
    INSIDER = "insider"
    MACRO = "macro"
    SEARCH = "search"
    OTHER = "other"


@dataclass(frozen=True)
class SourceProvenance:
    provider_id: str
    source_url: str | None = None
    fetched_at: str | None = None
    as_of: str | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class EvidenceItem:
    kind: EvidenceKind
    label: str
    summary: str
    value_text: str | None = None
    direction: str | None = None
    horizon: str | None = None
    confidence_hint: float | None = None
    provenance: SourceProvenance | None = None
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class EvidenceBundle:
    items: tuple[EvidenceItem, ...]

    def labels(self) -> tuple[str, ...]:
        return tuple(item.label for item in self.items)
