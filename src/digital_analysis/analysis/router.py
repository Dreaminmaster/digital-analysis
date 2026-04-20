from __future__ import annotations

from dataclasses import dataclass

from ..contracts.tasks import TaskSpec, TaskType
from .workflows import (
    AssetPricingWorkflow,
    BubbleAssessmentWorkflow,
    GeopoliticalRiskWorkflow,
    RecessionWorkflow,
)


@dataclass(frozen=True)
class WorkflowSelection:
    workflow_name: str
    reason: str


class WorkflowRouter:
    def select(self, task: TaskSpec) -> WorkflowSelection | None:
        if task.task_type == TaskType.MACRO:
            return WorkflowSelection("recession", "Macro task uses recession/macro evidence workflow.")
        if task.task_type == TaskType.GEOPOLITICAL:
            return WorkflowSelection("geopolitical", "Geopolitical task uses conflict-risk workflow.")
        if task.task_type == TaskType.ASSET:
            return WorkflowSelection("asset_pricing", "Asset task uses price and macro anchor workflow.")
        if task.task_type == TaskType.BUBBLE:
            return WorkflowSelection("bubble", "Bubble task uses valuation, options, insider, and risk proxies.")
        return None

    def build(self, task: TaskSpec):
        selection = self.select(task)
        if selection is None:
            return None, None
        if selection.workflow_name == "recession":
            return RecessionWorkflow(), selection
        if selection.workflow_name == "geopolitical":
            return GeopoliticalRiskWorkflow(), selection
        if selection.workflow_name == "asset_pricing":
            return AssetPricingWorkflow(), selection
        if selection.workflow_name == "bubble":
            return BubbleAssessmentWorkflow(), selection
        return None, None
