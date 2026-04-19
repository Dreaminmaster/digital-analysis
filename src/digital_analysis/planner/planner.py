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


class SimplePlanner:
    """A deliberately simple baseline planner.

    This is not the final autonomous planner. It exists so the repository has
    a concrete starting point that can later be replaced by a richer planner.
    """

    def plan(self, task: TaskSpec) -> SignalPlan:
        requirements: list[SignalRequirement] = []
        notes: list[str] = []

        if task.task_type == TaskType.GEOPOLITICAL:
            requirements.extend([
                SignalRequirement("prediction_market", "Direct event pricing", 3),
                SignalRequirement("safe_haven_assets", "Tail-risk pricing", 2),
                SignalRequirement("energy_commodities", "Conflict proxy", 2),
                SignalRequirement("volatility_credit", "Risk stress confirmation", 2),
            ])
        elif task.task_type == TaskType.MACRO:
            requirements.extend([
                SignalRequirement("yield_curve", "Direct macro pricing", 3),
                SignalRequirement("fed_path", "Policy expectation", 3),
                SignalRequirement("risk_assets", "Growth/risk appetite", 2),
                SignalRequirement("credit_stress", "Macro stress confirmation", 2),
            ])
        elif task.task_type == TaskType.BUBBLE:
            requirements.extend([
                SignalRequirement("leader_assets", "Bubble expression in leaders", 3),
                SignalRequirement("options_iv", "Speculation and convexity", 2),
                SignalRequirement("insiders", "Management behavior", 2),
            ])
        elif task.task_type == TaskType.OPTIONS:
            requirements.extend([
                SignalRequirement("options_chain", "Direct implied expectations", 3),
                SignalRequirement("realized_vs_implied", "Premium sanity check", 2),
                SignalRequirement("prediction_market", "Event cross-check", 1),
            ])
        else:
            requirements.extend([
                SignalRequirement("prediction_market", "Try direct pricing first", 2),
                SignalRequirement("macro_proxy", "Fallback market signals", 1),
            ])
            notes.append("General task type uses conservative baseline routing.")

        return SignalPlan(task=task, required_signals=tuple(requirements), notes=tuple(notes))
