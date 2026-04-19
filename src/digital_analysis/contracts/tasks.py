from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class TaskType(str, Enum):
    GEOPOLITICAL = "geopolitical"
    MACRO = "macro"
    BUBBLE = "bubble"
    ASSET = "asset"
    OPTIONS = "options"
    GENERAL = "general"


class TimeHorizon(str, Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class TaskSpec:
    question: str
    task_type: TaskType = TaskType.GENERAL
    horizon: TimeHorizon = TimeHorizon.UNKNOWN
    geography: tuple[str, ...] = ()
    target_asset: str | None = None
    needs_probability: bool = True
    metadata: dict[str, object] = field(default_factory=dict)
