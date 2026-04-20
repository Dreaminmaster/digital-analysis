from __future__ import annotations

from dataclasses import dataclass, field

from ..contracts.tasks import TaskSpec, TaskType


@dataclass(frozen=True)
class SignalRequirement:
    category: str
    reason: str
    priority: int = 1


@dataclass(frozen=True)
class SignalPlan:
    task: TaskSpec
    required_signals: tuple[SignalRequirement, ...]
    rejected_signals: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    suggested_symbols: tuple[str, ...] = ()
    suggested_providers: tuple[str, ...] = ()


class SimplePlanner:
    """A deliberately simple but increasingly useful baseline planner."""

    def plan(self, task: TaskSpec) -> SignalPlan:
        requirements: list[SignalRequirement] = []
        notes: list[str] = []
        symbols: list[str] = []
        providers: list[str] = []
        q = task.question.lower()

        if task.task_type == TaskType.GEOPOLITICAL:
            requirements.extend([
                SignalRequirement("prediction_market", "Direct event pricing", 3),
                SignalRequirement("safe_haven_assets", "Tail-risk pricing", 2),
                SignalRequirement("energy_commodities", "Conflict proxy", 2),
                SignalRequirement("volatility_credit", "Risk stress confirmation", 2),
            ])
            symbols.extend(["GC=F", "CL=F", "ITA"])
            providers.extend(["polymarket", "yahoo_price", "cftc_cot", "fear_greed"])
        elif task.task_type == TaskType.MACRO:
            requirements.extend([
                SignalRequirement("yield_curve", "Direct macro pricing", 3),
                SignalRequirement("fed_path", "Policy expectation", 3),
                SignalRequirement("risk_assets", "Growth/risk appetite", 2),
                SignalRequirement("credit_stress", "Macro stress confirmation", 2),
            ])
            symbols.extend(["SPY", "HG=F", "CL=F"])
            providers.extend(["us_treasury", "cme_fedwatch", "fear_greed", "polymarket"])
        elif task.task_type == TaskType.BUBBLE:
            requirements.extend([
                SignalRequirement("leader_assets", "Bubble expression in leaders", 3),
                SignalRequirement("options_iv", "Speculation and convexity", 2),
                SignalRequirement("insiders", "Management behavior", 2),
            ])
            symbols.extend([task.target_asset or "NVDA", "BTC-USD", "SMH"])
            providers.extend(["yahoo_price", "yfinance", "sec_edgar", "coingecko", "deribit"])
        elif task.task_type == TaskType.OPTIONS:
            requirements.extend([
                SignalRequirement("options_chain", "Direct implied expectations", 3),
                SignalRequirement("realized_vs_implied", "Premium sanity check", 2),
                SignalRequirement("prediction_market", "Event cross-check", 1),
            ])
            symbols.extend([task.target_asset or "SPY"])
            providers.extend(["yfinance", "yahoo_price", "kalshi", "fear_greed"])
        elif task.task_type == TaskType.ASSET:
            requirements.extend([
                SignalRequirement("target_asset_price", "Primary asset trend", 3),
                SignalRequirement("macro_anchor", "Rates and risk context", 2),
                SignalRequirement("sentiment_proxy", "Risk appetite context", 1),
            ])
            if "gold" in q:
                symbols.extend(["GLD", "GC=F"])
            elif "bitcoin" in q or "btc" in q:
                symbols.extend(["BTC-USD"])
            else:
                symbols.extend([task.target_asset or "SPY"])
            providers.extend(["yahoo_price", "us_treasury", "fear_greed"])
        else:
            requirements.extend([
                SignalRequirement("prediction_market", "Try direct pricing first", 2),
                SignalRequirement("macro_proxy", "Fallback market signals", 1),
            ])
            notes.append("General task type uses conservative baseline routing.")
            providers.extend(["polymarket", "fear_greed"])

        return SignalPlan(
            task=task,
            required_signals=tuple(requirements),
            notes=tuple(notes),
            suggested_symbols=tuple(dict.fromkeys(symbols)),
            suggested_providers=tuple(dict.fromkeys(providers)),
        )
