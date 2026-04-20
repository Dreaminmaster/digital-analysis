from __future__ import annotations

import uuid
from datetime import datetime, timezone

from ..orchestrator import DigitalAnalysisOrchestrator, OrchestratorResult
from .alerts import AlertEvent, AlertRule
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

    def create_alert_rule(self, *, monitor_id: str, name: str, metric: str = 'confidence_delta', operator: str = '>=', threshold: float = 0.1) -> AlertRule:
        rule = AlertRule(rule_id=str(uuid.uuid4()), monitor_id=monitor_id, name=name, metric=metric, operator=operator, threshold=threshold)
        return self.store.save_alert_rule(rule)

    def list_alert_rules(self) -> list[AlertRule]:
        return self.store.list_alert_rules()

    def list_alert_events(self) -> list[AlertEvent]:
        return self.store.list_alert_events()

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
            "contradiction_count": len(result.analysis.contradictions),
            "evidence_count": len(result.analysis.evidence.items),
        })
        self._evaluate_alerts(monitor.monitor_id)
        return result

    def run_all_monitors(self) -> list[dict[str, object]]:
        outputs: list[dict[str, object]] = []
        for monitor in self.list_monitors():
            result = self.run_monitor(monitor.monitor_id)
            outputs.append({
                "monitor_id": monitor.monitor_id,
                "topic": monitor.topic,
                "confidence": result.analysis.confidence,
                "summary": result.analysis.summary,
            })
        return outputs

    def compare_monitor_runs(self, monitor_id: str) -> dict[str, object]:
        runs = [r for r in self.store.list_monitor_runs() if r.get("monitor_id") == monitor_id]
        runs = sorted(runs, key=lambda r: str(r.get("ran_at", "")))
        if len(runs) < 2:
            return {
                "monitor_id": monitor_id,
                "run_count": len(runs),
                "message": "Not enough history to compare runs.",
            }
        prev = runs[-2]
        latest = runs[-1]
        prev_conf = float(prev.get("confidence", 0.0))
        latest_conf = float(latest.get("confidence", 0.0))
        delta = latest_conf - prev_conf
        trend = "up" if delta > 0 else "down" if delta < 0 else "flat"
        prev_evidence = int(prev.get("evidence_count", 0))
        latest_evidence = int(latest.get("evidence_count", 0))
        prev_contra = int(prev.get("contradiction_count", 0))
        latest_contra = int(latest.get("contradiction_count", 0))
        return {
            "monitor_id": monitor_id,
            "run_count": len(runs),
            "previous_confidence": prev_conf,
            "latest_confidence": latest_conf,
            "confidence_delta": delta,
            "trend": trend,
            "latest_summary": latest.get("summary"),
            "evidence_delta": latest_evidence - prev_evidence,
            "contradiction_delta": latest_contra - prev_contra,
        }

    def _evaluate_alerts(self, monitor_id: str) -> None:
        comparison = self.compare_monitor_runs(monitor_id)
        if comparison.get('run_count', 0) < 2:
            return
        for rule in self.list_alert_rules():
            if rule.monitor_id != monitor_id or not rule.active:
                continue
            actual_value = float(comparison.get(rule.metric, 0.0) or 0.0)
            triggered = False
            if rule.operator == '>=':
                triggered = actual_value >= rule.threshold
            elif rule.operator == '>':
                triggered = actual_value > rule.threshold
            elif rule.operator == '<=':
                triggered = actual_value <= rule.threshold
            elif rule.operator == '<':
                triggered = actual_value < rule.threshold
            if triggered:
                self.store.save_alert_event(
                    AlertEvent(
                        event_id=str(uuid.uuid4()),
                        rule_id=rule.rule_id,
                        monitor_id=monitor_id,
                        metric=rule.metric,
                        actual_value=actual_value,
                        threshold=rule.threshold,
                        message=f"Alert '{rule.name}' triggered for monitor {monitor_id}: {rule.metric}={actual_value}",
                    )
                )
