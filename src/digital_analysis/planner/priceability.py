from __future__ import annotations

from dataclasses import dataclass

from ..contracts.tasks import TaskSpec, TaskType


@dataclass(frozen=True)
class PriceabilityAssessment:
    priceable: bool
    direct_markets_likely: bool
    proxy_markets_likely: bool
    reason: str


class PriceabilityChecker:
    def assess(self, task: TaskSpec) -> PriceabilityAssessment:
        if task.task_type in (TaskType.GEOPOLITICAL, TaskType.MACRO, TaskType.BUBBLE, TaskType.ASSET, TaskType.OPTIONS):
            direct = task.task_type in (TaskType.GEOPOLITICAL, TaskType.MACRO, TaskType.OPTIONS)
            proxy = True
            return PriceabilityAssessment(
                priceable=True,
                direct_markets_likely=direct,
                proxy_markets_likely=proxy,
                reason="Task category is compatible with market-pricing analysis.",
            )
        return PriceabilityAssessment(
            priceable=False,
            direct_markets_likely=False,
            proxy_markets_likely=False,
            reason="Task is not clearly priceable by available market signals.",
        )
