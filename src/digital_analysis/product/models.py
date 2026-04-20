from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class AnalysisSession:
    session_id: str
    question: str
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)


@dataclass(frozen=True)
class WatchlistItem:
    item_id: str
    name: str
    query: str
    created_at: str = field(default_factory=_now_iso)
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class TopicMonitor:
    monitor_id: str
    topic: str
    query: str
    schedule_hint: str = "manual"
    created_at: str = field(default_factory=_now_iso)
    active: bool = True
