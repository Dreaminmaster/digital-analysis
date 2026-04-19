from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ModelTask(str, Enum):
    PARSE = "parse"
    PLAN = "plan"
    ANALYZE = "analyze"
    SYNTHESIZE = "synthesize"


@dataclass(frozen=True)
class ModelBackend:
    name: str
    kind: str  # cloud_api / local / deterministic
    strengths: tuple[ModelTask, ...] = ()
    privacy_safe: bool = False
    cost_tier: str = "medium"


class ModelRouter:
    """Baseline model router.

    Routing strategy:
    - privacy-sensitive tasks prefer privacy_safe backends
    - parse/plan prefer lower-cost models where possible
    - synthesize/analyze can prefer stronger models if available
    """

    def __init__(self, backends: tuple[ModelBackend, ...] = ()) -> None:
        self.backends = backends

    def route(self, task: ModelTask, *, privacy_sensitive: bool = False) -> ModelBackend | None:
        candidates = [b for b in self.backends if task in b.strengths]
        if privacy_sensitive:
            candidates = [b for b in candidates if b.privacy_safe]
        if not candidates:
            return self.backends[0] if self.backends else None

        if task in (ModelTask.PARSE, ModelTask.PLAN):
            for cost in ("low", "medium", "high"):
                for backend in candidates:
                    if backend.cost_tier == cost:
                        return backend
        else:
            for cost in ("high", "medium", "low"):
                for backend in candidates:
                    if backend.cost_tier == cost:
                        return backend
        return candidates[0]
