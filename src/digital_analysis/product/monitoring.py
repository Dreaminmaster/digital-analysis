from __future__ import annotations

import uuid
from datetime import datetime, timezone

from ..orchestrator import DigitalAnalysisOrchestrator, OrchestratorResult
from .models import AnalysisSession, TopicMonitor, WatchlistItem
from .store import InMemoryStore


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class MonitoringService:
    def __init__(self, *, orchestrator: DigitalAnalysisOrchestrator, store: InMemoryStore | None = None) -> None:
        self.orchestrator = orchestrator
        self.store = store or InMemoryStore()

    def run_analysis(self, question: str) -> OrchestratorResult:
        result = self.orchestrator.run(question)
        session = AnalysisSession(session_id=str(uuid.uuid4()), question=question)
        self.store.save_session(session)
        return result

    def create_watchlist_item(self, *, name: str, query: str, tags: tuple[str, ...] = ()) -> WatchlistItem:
        item = WatchlistItem(item_id=str(uuid.uuid4()), name=name, query=query, tags=tags)
        return self.store.save_watchlist_item(item)

    def list_watchlist_items(self) -> list[WatchlistItem]:
        return self.store.list_watchlist_items()

    def create_monitor(self, *, topic: str, query: str, schedule_hint: str = "manual") -> TopicMonitor:
        monitor = TopicMonitor(monitor_id=str(uuid.uuid4()), topic=topic, query=query, schedule_hint=schedule_hint)
        return self.store.save_monitor(monitor)

    def list_monitors(self) -> list[TopicMonitor]:
        return self.store.list_monitors()

    def list_monitor_runs(self) -> list[dict[str, object]]:
        return self.store.list_monitor_runs()

    def run_monitor(self, monitor_id: str) -> OrchestratorResult:
        monitor = next(item for item in self.store.list_monitors() if item.monitor_id == monitor_id)
        result = self.run_analysis(monitor.query)
        self.store.save_monitor_run({
            "run_id": str(uuid.uuid4()),
            "monitor_id": monitor.monitor_id,
            "topic": monitor.topic,
            "query": monitor.query,
            "ran_at": _now_iso(),
            "task_type": result.task.task_type.value,
            "confidence": result.analysis.confidence,
            "summary": result.analysis.summary,
        })
        return result
