from __future__ import annotations

from ..analysis.engine import AnalysisEngine, AnalysisOutput
from ..contracts.evidence import EvidenceBundle
from ..providers import (
    CftcCotProvider,
    CftcCotQuery,
    CMEFedWatchProvider,
    CoinGeckoPriceQuery,
    CoinGeckoProvider,
    DeribitFuturesCurveQuery,
    DeribitOptionChainQuery,
    DeribitProvider,
    EdgarInsiderQuery,
    EdgarProvider,
    FearGreedProvider,
    PolymarketEventQuery,
    PolymarketProvider,
    USTreasuryProvider,
    YahooPriceProvider,
    YFinanceProvider,
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
        analysis_engine: AnalysisEngine | None = None,
    ) -> None:
        self.treasury = treasury or USTreasuryProvider()
        self.fedwatch = fedwatch or CMEFedWatchProvider()
        self.fear_greed = fear_greed or FearGreedProvider()
        self.polymarket = polymarket or PolymarketProvider()
        self.evidence_builder = evidence_builder or EvidenceBuilder()
        self.analysis_engine = analysis_engine or AnalysisEngine()

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
        return self.analysis_engine.reanalyze_with_evidence(analysis, merged)


class GeopoliticalRiskWorkflow:
    def __init__(
        self,
        *,
        polymarket: PolymarketProvider | None = None,
        fear_greed: FearGreedProvider | None = None,
        gold_prices: YahooPriceProvider | None = None,
        cftc: CftcCotProvider | None = None,
        evidence_builder: EvidenceBuilder | None = None,
        analysis_engine: AnalysisEngine | None = None,
    ) -> None:
        self.polymarket = polymarket or PolymarketProvider()
        self.fear_greed = fear_greed or FearGreedProvider()
        self.gold_prices = gold_prices or YahooPriceProvider()
        self.cftc = cftc or CftcCotProvider()
        self.evidence_builder = evidence_builder or EvidenceBuilder()
        self.analysis_engine = analysis_engine or AnalysisEngine()

    def enrich(self, analysis: AnalysisOutput) -> AnalysisOutput:
        from ..providers.prices import PriceHistoryQuery

        groups = []
        pm_events = self.polymarket.list_events(PolymarketEventQuery(slug_contains="war", limit=3))
        if pm_events:
            groups.append(self.evidence_builder.from_polymarket_events(pm_events))
        fg = self.fear_greed.get_index()
        groups.append(self.evidence_builder.from_fear_greed(fg))
        gold = self.gold_prices.get_history(PriceHistoryQuery(symbol="GC=F", limit=20))
        groups.append(self.evidence_builder.from_price_history(gold, label="gold"))
        gold_cot = self.cftc.list_reports(CftcCotQuery(commodity_name="GOLD", limit=1))
        if gold_cot:
            groups.append(self.evidence_builder.from_cftc_reports(gold_cot, label="gold_cot"))
        extra = self.evidence_builder.combine(*groups)
        merged = EvidenceBundle(items=analysis.evidence.items + extra.items)
        return self.analysis_engine.reanalyze_with_evidence(analysis, merged)


class AssetPricingWorkflow:
    def __init__(
        self,
        *,
        prices: YahooPriceProvider | None = None,
        treasury: USTreasuryProvider | None = None,
        fear_greed: FearGreedProvider | None = None,
        evidence_builder: EvidenceBuilder | None = None,
        analysis_engine: AnalysisEngine | None = None,
    ) -> None:
        self.prices = prices or YahooPriceProvider()
        self.treasury = treasury or USTreasuryProvider()
        self.fear_greed = fear_greed or FearGreedProvider()
        self.evidence_builder = evidence_builder or EvidenceBuilder()
        self.analysis_engine = analysis_engine or AnalysisEngine()

    def enrich(self, analysis: AnalysisOutput, *, symbol: str = "GLD") -> AnalysisOutput:
        from ..providers.prices import PriceHistoryQuery

        groups = []
        history = self.prices.get_history(PriceHistoryQuery(symbol=symbol, limit=30))
        groups.append(self.evidence_builder.from_price_history(history, label=symbol))
        curve = self.treasury.latest_yield_curve()
        if curve is not None:
            groups.append(self.evidence_builder.from_treasury_curve(curve))
        fg = self.fear_greed.get_index()
        groups.append(self.evidence_builder.from_fear_greed(fg))
        extra = self.evidence_builder.combine(*groups)
        merged = EvidenceBundle(items=analysis.evidence.items + extra.items)
        return self.analysis_engine.reanalyze_with_evidence(analysis, merged)


class BubbleAssessmentWorkflow:
    def __init__(
        self,
        *,
        prices: YahooPriceProvider | None = None,
        options: YFinanceProvider | None = None,
        insiders: EdgarProvider | None = None,
        coingecko: CoinGeckoProvider | None = None,
        deribit: DeribitProvider | None = None,
        fear_greed: FearGreedProvider | None = None,
        polymarket: PolymarketProvider | None = None,
        cftc: CftcCotProvider | None = None,
        evidence_builder: EvidenceBuilder | None = None,
        analysis_engine: AnalysisEngine | None = None,
    ) -> None:
        self.prices = prices or YahooPriceProvider()
        self.options = options or YFinanceProvider()
        self.insiders = insiders or EdgarProvider()
        self.coingecko = coingecko or CoinGeckoProvider()
        self.deribit = deribit or DeribitProvider()
        self.fear_greed = fear_greed or FearGreedProvider()
        self.polymarket = polymarket or PolymarketProvider()
        self.cftc = cftc or CftcCotProvider()
        self.evidence_builder = evidence_builder or EvidenceBuilder()
        self.analysis_engine = analysis_engine or AnalysisEngine()

    def enrich(self, analysis: AnalysisOutput, *, ticker: str = "NVDA") -> AnalysisOutput:
        from ..providers.prices import PriceHistoryQuery

        groups = []
        history = self.prices.get_history(PriceHistoryQuery(symbol=ticker, limit=30))
        groups.append(self.evidence_builder.from_price_history(history, label=ticker))

        try:
            chain = self.options.get_chain(__import__("digital_analysis.providers.yfinance_provider", fromlist=["OptionsChainQuery"]).OptionsChainQuery(ticker=ticker))
            groups.append(self.evidence_builder.from_yfinance_chain(chain))
        except Exception:
            pass

        try:
            insider = self.insiders.get_insider_transactions(EdgarInsiderQuery(ticker=ticker, limit=10))
            groups.append(self.evidence_builder.from_edgar_insiders(insider))
        except Exception:
            pass

        fg = self.fear_greed.get_index()
        groups.append(self.evidence_builder.from_fear_greed(fg))

        pm_events = self.polymarket.list_events(PolymarketEventQuery(slug_contains="ai", limit=2))
        if pm_events:
            groups.append(self.evidence_builder.from_polymarket_events(pm_events))

        try:
            crypto = self.coingecko.get_prices(CoinGeckoPriceQuery(coin_ids=("bitcoin", "ethereum")))
            groups.append(self.evidence_builder.from_coingecko_prices(crypto))
        except Exception:
            pass

        try:
            futures = self.deribit.get_futures_term_structure(DeribitFuturesCurveQuery(currency="BTC"))
            groups.append(self.evidence_builder.from_deribit_futures(futures))
            options = self.deribit.get_option_chain(DeribitOptionChainQuery(currency="BTC"))
            groups.append(self.evidence_builder.from_deribit_options(options))
        except Exception:
            pass

        try:
            cftc_rows = self.cftc.list_reports(CftcCotQuery(commodity_name="NASDAQ", limit=1))
            if cftc_rows:
                groups.append(self.evidence_builder.from_cftc_reports(cftc_rows, label="nasdaq_cot"))
        except Exception:
            pass

        extra = self.evidence_builder.combine(*groups)
        merged = EvidenceBundle(items=analysis.evidence.items + extra.items)
        return self.analysis_engine.reanalyze_with_evidence(analysis, merged)
