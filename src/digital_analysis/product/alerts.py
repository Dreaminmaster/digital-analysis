from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class AlertRule:
    rule_id: str
    monitor_id: str
    name: str
    metric: str = "confidence_delta"
    operator: str = ">="
    threshold: float = 0.1
    created_at: str = field(default_factory=_now_iso)
    active: bool = True


@dataclass(frozen=True)
class AlertEvent:
    event_id: str
    rule_id: str
    monitor_id: str
    triggered_at: str = field(default_factory=_now_iso)
    metric: str = "confidence_delta"
    actual_value: float = 0.0
    threshold: float = 0.0
    message: str = ""
