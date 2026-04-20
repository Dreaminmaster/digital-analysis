from __future__ import annotations

from dataclasses import dataclass

from ..contracts.evidence import EvidenceBundle, EvidenceItem, EvidenceKind, SourceProvenance
from ..providers.cme_fedwatch import FedMeetingProbability
from ..providers.fear_greed import FearGreedSnapshot
from ..providers.polymarket import PolymarketEvent
from ..providers.treasury import YieldCurveSnapshot
from ..providers.prices import PriceHistory
from ..providers.cftc import CftcCotReport


@dataclass
class EvidenceBuilder:
    def from_treasury_curve(self, curve: YieldCurveSnapshot) -> tuple[EvidenceItem, ...]:
        spread_10y_2y = curve.spread("10Y", "2Y")
        value_text = None if spread_10y_2y is None else f"10Y-2Y spread {spread_10y_2y:.2f}%"
        direction = None
        if spread_10y_2y is not None:
            direction = "inverted" if spread_10y_2y < 0 else "steepening_or_positive"
        return (
            EvidenceItem(
                kind=EvidenceKind.CURVE,
                label="yield_curve",
                summary="U.S. Treasury curve snapshot",
                value_text=value_text,
                direction=direction,
                horizon="medium",
                confidence_hint=0.8,
                provenance=SourceProvenance(provider_id="us_treasury", as_of=curve.date),
                metadata={"date": curve.date},
            ),
        )

    def from_fear_greed(self, snapshot: FearGreedSnapshot) -> tuple[EvidenceItem, ...]:
        direction = "risk_on" if snapshot.score >= 55 else "risk_off" if snapshot.score < 45 else "neutral"
        return (
            EvidenceItem(
                kind=EvidenceKind.PRICE,
                label="fear_greed",
                summary=f"CNN Fear & Greed rating: {snapshot.rating}",
                value_text=f"score={snapshot.score:.1f}",
                direction=direction,
                horizon="short",
                confidence_hint=0.65,
                provenance=SourceProvenance(provider_id="fear_greed", as_of=snapshot.timestamp),
            ),
        )

    def from_fedwatch(self, rows: list[FedMeetingProbability]) -> tuple[EvidenceItem, ...]:
        if not rows:
            return ()
        first = rows[0]
        best = max(first.probabilities, key=lambda p: p.probability, default=None)
        value_text = None
        if best is not None:
            value_text = f"top band {best.target_low:.2%}-{best.target_high:.2%} @ {best.probability:.1%}"
        return (
            EvidenceItem(
                kind=EvidenceKind.PROBABILITY,
                label="fedwatch",
                summary="Market-implied Fed path from futures",
                value_text=value_text,
                direction="policy_expectation",
                horizon="short",
                confidence_hint=0.8,
                provenance=SourceProvenance(provider_id="cme_fedwatch", as_of=first.meeting_date),
            ),
        )

    def from_polymarket_events(self, events: list[PolymarketEvent]) -> tuple[EvidenceItem, ...]:
        items: list[EvidenceItem] = []
        for event in events[:3]:
            market = event.markets[0] if event.markets else None
            yes_probability = market.yes_probability if market is not None else None
            items.append(
                EvidenceItem(
                    kind=EvidenceKind.PROBABILITY,
                    label=f"polymarket:{event.slug}",
                    summary=event.title,
                    value_text=(f"yes={yes_probability:.1%}" if yes_probability is not None else None),
                    direction="event_pricing",
                    horizon="short",
                    confidence_hint=0.75,
                    provenance=SourceProvenance(provider_id="polymarket", as_of=None),
                    metadata={"slug": event.slug},
                )
            )
        return tuple(items)

    def from_price_history(self, history: PriceHistory, *, label: str | None = None) -> tuple[EvidenceItem, ...]:
        latest = history.latest
        earliest = history.earliest
        if latest is None or earliest is None:
            return ()
        pct_change = ((latest.close - earliest.close) / earliest.close) if earliest.close else None
        direction = None
        value_text = None
        if pct_change is not None:
            direction = "up" if pct_change > 0 else "down" if pct_change < 0 else "flat"
            value_text = f"change={pct_change:.1%} latest={latest.close:.2f}"
        return (
            EvidenceItem(
                kind=EvidenceKind.PRICE,
                label=label or history.symbol,
                summary=f"Price history from {history.provider_id or 'price provider'}",
                value_text=value_text,
                direction=direction,
                horizon="short",
                confidence_hint=0.7,
                provenance=SourceProvenance(provider_id=history.provider_id or "price_provider", as_of=latest.date),
                metadata={"symbol": history.symbol, "interval": history.interval},
            ),
        )

    def from_cftc_reports(self, reports: list[CftcCotReport], *, label: str = "cftc_positioning") -> tuple[EvidenceItem, ...]:
        if not reports:
            return ()
        first = reports[0]
        net = first.noncommercial_net
        direction = None if net is None else "spec_long" if net > 0 else "spec_short" if net < 0 else "neutral"
        return (
            EvidenceItem(
                kind=EvidenceKind.POSITIONING,
                label=label,
                summary=first.market_name,
                value_text=(f"noncommercial_net={net}" if net is not None else None),
                direction=direction,
                horizon="medium",
                confidence_hint=0.72,
                provenance=SourceProvenance(provider_id="cftc_cot", as_of=first.report_date),
            ),
        )

    def combine(self, *groups: tuple[EvidenceItem, ...]) -> EvidenceBundle:
        merged: list[EvidenceItem] = []
        for group in groups:
            merged.extend(group)
        return EvidenceBundle(items=tuple(merged))
