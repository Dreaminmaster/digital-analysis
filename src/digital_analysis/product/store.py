from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import json

from .models import AnalysisSession, TopicMonitor, WatchlistItem


class InMemoryStore:
    def __init__(self) -> None:
        self.sessions: dict[str, AnalysisSession] = {}
        self.watchlist_items: dict[str, WatchlistItem] = {}
        self.monitors: dict[str, TopicMonitor] = {}
        self.monitor_runs: list[dict[str, object]] = []

    def save_session(self, session: AnalysisSession) -> AnalysisSession:
        self.sessions[session.session_id] = session
        return session

    def list_sessions(self) -> list[AnalysisSession]:
        return list(self.sessions.values())

    def save_watchlist_item(self, item: WatchlistItem) -> WatchlistItem:
        self.watchlist_items[item.item_id] = item
        return item

    def list_watchlist_items(self) -> list[WatchlistItem]:
        return list(self.watchlist_items.values())

    def save_monitor(self, monitor: TopicMonitor) -> TopicMonitor:
        self.monitors[monitor.monitor_id] = monitor
        return monitor

    def list_monitors(self) -> list[TopicMonitor]:
        return list(self.monitors.values())

    def save_monitor_run(self, run: dict[str, object]) -> dict[str, object]:
        self.monitor_runs.append(run)
        return run

    def list_monitor_runs(self) -> list[dict[str, object]]:
        return list(self.monitor_runs)


class FileStore(InMemoryStore):
    def __init__(self, root_dir: str | Path):
        super().__init__()
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self._load_all()

    def _path(self, name: str) -> Path:
        return self.root_dir / f"{name}.json"

    def _load_all(self) -> None:
        self.sessions = self._load_map("sessions", AnalysisSession)
        self.watchlist_items = self._load_map("watchlist_items", WatchlistItem)
        self.monitors = self._load_map("monitors", TopicMonitor)
        self.monitor_runs = self._load_list("monitor_runs")

    def _load_map(self, name: str, cls):
        path = self._path(name)
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text())
        except json.JSONDecodeError:
            return {}
        if not isinstance(payload, list):
            return {}
        rows = {}
        for item in payload:
            if isinstance(item, dict):
                obj = cls(**item)
                key = getattr(obj, next(iter(obj.__dataclass_fields__.keys())))
                rows[key] = obj
        return rows

    def _load_list(self, name: str) -> list[dict[str, object]]:
        path = self._path(name)
        if not path.exists():
            return []
        try:
            payload = json.loads(path.read_text())
        except json.JSONDecodeError:
            return []
        return payload if isinstance(payload, list) else []

    def _flush(self) -> None:
        self._path("sessions").write_text(json.dumps([asdict(x) for x in self.sessions.values()], ensure_ascii=False, indent=2))
        self._path("watchlist_items").write_text(json.dumps([asdict(x) for x in self.watchlist_items.values()], ensure_ascii=False, indent=2))
        self._path("monitors").write_text(json.dumps([asdict(x) for x in self.monitors.values()], ensure_ascii=False, indent=2))
        self._path("monitor_runs").write_text(json.dumps(self.monitor_runs, ensure_ascii=False, indent=2))

    def save_session(self, session: AnalysisSession) -> AnalysisSession:
        result = super().save_session(session)
        self._flush()
        return result

    def save_watchlist_item(self, item: WatchlistItem) -> WatchlistItem:
        result = super().save_watchlist_item(item)
        self._flush()
        return result

    def save_monitor(self, monitor: TopicMonitor) -> TopicMonitor:
        result = super().save_monitor(monitor)
        self._flush()
        return result

    def save_monitor_run(self, run: dict[str, object]) -> dict[str, object]:
        result = super().save_monitor_run(run)
        self._flush()
        return result
