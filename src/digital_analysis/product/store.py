from __future__ import annotations

from dataclasses import replace

from .models import AnalysisSession, TopicMonitor, WatchlistItem


class InMemoryStore:
    def __init__(self) -> None:
        self.sessions: dict[str, AnalysisSession] = {}
        self.watchlist_items: dict[str, WatchlistItem] = {}
        self.monitors: dict[str, TopicMonitor] = {}

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

    def set_monitor_active(self, monitor_id: str, active: bool) -> TopicMonitor:
        current = self.monitors[monitor_id]
        updated = replace(current, active=active)
        self.monitors[monitor_id] = updated
        return updated
