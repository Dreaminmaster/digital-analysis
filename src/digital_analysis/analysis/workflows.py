from __future__ import annotations

from dataclasses import replace

from ..analysis.engine import AnalysisOutput
from ..contracts.evidence import EvidenceBundle
from ..providers import (
    CftcCotProvider,
    CftcCotQuery,
    CMEFedWatchProvider,
    FearGreedProvider,
    PolymarketEventQuery,
    PolymarketProvider,
    StooqProvider,
    USTreasuryProvider,
    YahooPriceProvider,
)
from .evidence_builder import EvidenceBuilder


class RecessionWorkflow:
    """Example workflow that fetches a small but real macro evidence set."""

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


class GeopoliticalRiskWorkflow:
    def __init__(
        self,
        *,
        polymarket: PolymarketProvider | None = None,
        fear_greed: FearGreedProvider | None = None,
        gold_prices: YahooPriceProvider | None = None,
        cftc: CftcCotProvider | None = None,
        evidence_builder: EvidenceBuilder | None = None,
    ) -> None:
        self.polymarket = polymarket or PolymarketProvider()
        self.fear_greed = fear_greed or FearGreedProvider()
        self.gold_prices = gold_prices or YahooPriceProvider()
        self.cftc = cftc or CftcCotProvider()
        self.evidence_builder = evidence_builder or EvidenceBuilder()

    def enrich(self, analysis: AnalysisOutput) -> AnalysisOutput:
        groups = []
        pm_events = self.polymarket.list_events(PolymarketEventQuery(slug_contains="war", limit=3))
        if pm_events:
            groups.append(self.evidence_builder.from_polymarket_events(pm_events))

        fg = self.fear_greed.get_index()
        groups.append(self.evidence_builder.from_fear_greed(fg))

        gold = self.gold_prices.get_history(__import__("digital_analysis.providers.prices", fromlist=["PriceHistoryQuery"]).PriceHistoryQuery(symbol="GC=F", limit=20))
        groups.append(self.evidence_builder.from_price_history(gold, label="gold"))

        gold_cot = self.cftc.list_reports(CftcCotQuery(commodity_name="GOLD", limit=1))
        if gold_cot:
            groups.append(self.evidence_builder.from_cftc_reports(gold_cot, label="gold_cot"))

        extra = self.evidence_builder.combine(*groups)
        merged = EvidenceBundle(items=analysis.evidence.items + extra.items)
        return replace(analysis, evidence=merged)


class AssetPricingWorkflow:
    def __init__(
        self,
        *,
        prices: YahooPriceProvider | None = None,
        treasury: USTreasuryProvider | None = None,
        fear_greed: FearGreedProvider | None = None,
        evidence_builder: EvidenceBuilder | None = None,
    ) -> None:
        self.prices = prices or YahooPriceProvider()
        self.treasury = treasury or USTreasuryProvider()
        self.fear_greed = fear_greed or FearGreedProvider()
        self.evidence_builder = evidence_builder or EvidenceBuilder()

    def enrich(self, analysis: AnalysisOutput, *, symbol: str = "GLD") -> AnalysisOutput:
        groups = []
        history = self.prices.get_history(__import__("digital_analysis.providers.prices", fromlist=["PriceHistoryQuery"]).PriceHistoryQuery(symbol=symbol, limit=30))
        groups.append(self.evidence_builder.from_price_history(history, label=symbol))

        curve = self.treasury.latest_yield_curve()
        if curve is not None:
            groups.append(self.evidence_builder.from_treasury_curve(curve))

        fg = self.fear_greed.get_index()
        groups.append(self.evidence_builder.from_fear_greed(fg))

        extra = self.evidence_builder.combine(*groups)
        merged = EvidenceBundle(items=analysis.evidence.items + extra.items)
        return replace(analysis, evidence=merged)
