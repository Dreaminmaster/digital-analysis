from __future__ import annotations

from dataclasses import dataclass

from ..contracts.tasks import TaskType


@dataclass(frozen=True)
class SignalDefinition:
    name: str
    categories: tuple[TaskType, ...]
    description: str


DEFAULT_SIGNAL_REGISTRY: tuple[SignalDefinition, ...] = (
    SignalDefinition("prediction_market", (TaskType.GEOPOLITICAL, TaskType.MACRO, TaskType.OPTIONS), "Direct event/range pricing"),
    SignalDefinition("yield_curve", (TaskType.MACRO,), "Rates curve macro pricing"),
    SignalDefinition("fed_path", (TaskType.MACRO,), "Implied policy path"),
    SignalDefinition("safe_haven_assets", (TaskType.GEOPOLITICAL, TaskType.ASSET), "Risk-off pricing"),
    SignalDefinition("options_chain", (TaskType.OPTIONS, TaskType.ASSET), "Implied move and skew"),
    SignalDefinition("insiders", (TaskType.BUBBLE, TaskType.ASSET), "Management buy/sell activity"),
    SignalDefinition("volatility_credit", (TaskType.GEOPOLITICAL, TaskType.MACRO, TaskType.OPTIONS), "Stress confirmation"),
)
