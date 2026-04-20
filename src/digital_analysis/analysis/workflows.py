from __future__ import annotations

from dataclasses import replace

from ..analysis.engine import AnalysisEngine, AnalysisOutput
from ..contracts.evidence import EvidenceBundle
from ..providers import CMEFedWatchProvider, FearGreedProvider, PolymarketEventQuery, PolymarketProvider, USTreasuryProvider
from .evidence_builder import EvidenceBuilder


class RecessionWorkflow:
    """Example workflow that fetches a small but real macro evidence set.

    This is intentionally narrow and explicit: it demonstrates how real provider
    data gets converted into evidence items and merged into the main analysis.
    """

    def __init__(
        self,
        *,
        treasury: USTreasuryProvider | None = None,
        fedwatch: CMEFedWatchProvider | None = None,
        fear_greed: FearGreedProvider | None = None,
        polymarket: PolymarketProvider | None = None,
        evidence_builder: EvidenceBuilder | None = None,
    ) -> None:
        self.treasury = treasury or USTreasuryProvider()
        self.fedwatch = fedwatch or CMEFedWatchProvider()
        self.fear_greed = fear_greed or FearGreedProvider()
        self.polymarket = polymarket or PolymarketProvider()
        self.evidence_builder = evidence_builder or EvidenceBuilder()

    def enrich(self, analysis: AnalysisOutput) -> AnalysisOutput:
        groups = []

        curve = self.treasury.latest_yield_curve()
        if curve is not None:
            groups.append(self.evidence_builder.from_treasury_curve(curve))

        fed_rows = self.fedwatch.get_probabilities()
        if fed_rows:
            groups.append(self.evidence_builder.from_fedwatch(fed_rows))

        fg = self.fear_greed.get_index()
        groups.append(self.evidence_builder.from_fear_greed(fg))

        pm_events = self.polymarket.list_events(PolymarketEventQuery(slug_contains="recession", limit=3))
        if pm_events:
            groups.append(self.evidence_builder.from_polymarket_events(pm_events))

        extra = self.evidence_builder.combine(*groups)
        merged = EvidenceBundle(items=analysis.evidence.items + extra.items)
        return replace(analysis, evidence=merged)
