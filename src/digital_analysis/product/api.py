from __future__ import annotations

from typing import Any

from ..models.base import ChatModel
from ..orchestrator import DigitalAnalysisOrchestrator
from ..product.monitoring import MonitoringService
from ..product.service import AnalysisService
from ..reports.builder import ReportSynthesizer

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
except ImportError:  # pragma: no cover
    FastAPI = None  # type: ignore[assignment]
    HTTPException = RuntimeError  # type: ignore[assignment]
    BaseModel = object  # type: ignore[assignment]


class AnalyzeRequest(BaseModel):  # type: ignore[misc,valid-type]
    question: str
    synthesize: bool = False


class EvidenceResponse(BaseModel):  # type: ignore[misc,valid-type]
    label: str
    summary: str
    value_text: str | None = None


class AnalyzeResponse(BaseModel):  # type: ignore[misc,valid-type]
    question: str
    task_type: str
    horizon: str
    priceable: bool
    conclusion: str
    confidence: float
    key_evidence: list[EvidenceResponse]
    contradictory_evidence: list[str]
    scenarios: list[str]
    uncertainty: list[str]
    suggested_next_checks: list[str]
    markdown_report: str
    metadata: dict[str, Any]
    synthesized_text: str | None = None


class HealthResponse(BaseModel):  # type: ignore[misc,valid-type]
    ok: bool
    service: str


class WatchlistCreateRequest(BaseModel):  # type: ignore[misc,valid-type]
    name: str
    query: str
    tags: list[str] = []


class WatchlistItemResponse(BaseModel):  # type: ignore[misc,valid-type]
    item_id: str
    name: str
    query: str
    tags: list[str]


class MonitorCreateRequest(BaseModel):  # type: ignore[misc,valid-type]
    topic: str
    query: str
    schedule_hint: str = "manual"


class MonitorResponse(BaseModel):  # type: ignore[misc,valid-type]
    monitor_id: str
    topic: str
    query: str
    schedule_hint: str
    active: bool


class MonitorRunResponse(BaseModel):  # type: ignore[misc,valid-type]
    run_id: str
    monitor_id: str
    topic: str
    query: str
    ran_at: str
    task_type: str
    confidence: float
    summary: str


class MonitorRunTriggerResponse(BaseModel):  # type: ignore[misc,valid-type]
    monitor_id: str
    confidence: float
    summary: str


class MonitorComparisonResponse(BaseModel):  # type: ignore[misc,valid-type]
    monitor_id: str
    run_count: int
    message: str | None = None
    previous_confidence: float | None = None
    latest_confidence: float | None = None
    confidence_delta: float | None = None
    trend: str | None = None
    latest_summary: str | None = None
    evidence_delta: int | None = None
    contradiction_delta: int | None = None


class AlertRuleCreateRequest(BaseModel):  # type: ignore[misc,valid-type]
    monitor_id: str
    name: str
    metric: str = 'confidence_delta'
    operator: str = '>='
    threshold: float = 0.1


class AlertRuleResponse(BaseModel):  # type: ignore[misc,valid-type]
    rule_id: str
    monitor_id: str
    name: str
    metric: str
    operator: str
    threshold: float
    active: bool


class AlertEventResponse(BaseModel):  # type: ignore[misc,valid-type]
    event_id: str
    rule_id: str
    monitor_id: str
    triggered_at: str
    metric: str
    actual_value: float
    threshold: float
    message: str


def create_app(*, model: ChatModel | None = None) -> Any:
    if FastAPI is None:
        raise RuntimeError("fastapi and pydantic are required to create the API app")

    synthesizer = ReportSynthesizer(model=model) if model is not None else None
    orchestrator = DigitalAnalysisOrchestrator(synthesizer=synthesizer)
    service = AnalysisService(orchestrator=orchestrator)
    monitoring = MonitoringService(orchestrator=orchestrator)
    app = FastAPI(title="Digital Analysis API", version="0.1.0")

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(ok=True, service="digital-analysis")

    @app.post("/analyze", response_model=AnalyzeResponse)
    def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
        if not req.question.strip():
            raise HTTPException(status_code=400, detail="question must not be empty")
        result = service.analyze(req.question)
        synthesized_text = result.synthesized_text if req.synthesize else None
        key_evidence = [EvidenceResponse(label=item.label, summary=item.summary, value_text=item.value_text) for item in result.answer.key_evidence]
        return AnalyzeResponse(
            question=result.answer.question,
            task_type=result.task.task_type.value,
            horizon=result.task.horizon.value,
            priceable=result.priceability.priceable,
            conclusion=result.answer.conclusion,
            confidence=result.answer.confidence,
            key_evidence=key_evidence,
            contradictory_evidence=list(result.answer.contradictory_evidence),
            scenarios=list(result.answer.scenarios),
            uncertainty=list(result.answer.uncertainty),
            suggested_next_checks=list(result.answer.suggested_next_checks),
            markdown_report=result.markdown_report,
            metadata=result.answer.metadata,
            synthesized_text=synthesized_text,
        )

    @app.post('/watchlist', response_model=WatchlistItemResponse)
    def create_watchlist_item(req: WatchlistCreateRequest) -> WatchlistItemResponse:
        item = monitoring.create_watchlist_item(name=req.name, query=req.query, tags=tuple(req.tags))
        return WatchlistItemResponse(item_id=item.item_id, name=item.name, query=item.query, tags=list(item.tags))

    @app.get('/watchlist', response_model=list[WatchlistItemResponse])
    def list_watchlist_items() -> list[WatchlistItemResponse]:
        return [WatchlistItemResponse(item_id=item.item_id, name=item.name, query=item.query, tags=list(item.tags)) for item in monitoring.list_watchlist_items()]

    @app.post('/monitors', response_model=MonitorResponse)
    def create_monitor(req: MonitorCreateRequest) -> MonitorResponse:
        monitor = monitoring.create_monitor(topic=req.topic, query=req.query, schedule_hint=req.schedule_hint)
        return MonitorResponse(monitor_id=monitor.monitor_id, topic=monitor.topic, query=monitor.query, schedule_hint=monitor.schedule_hint, active=monitor.active)

    @app.get('/monitors', response_model=list[MonitorResponse])
    def list_monitors() -> list[MonitorResponse]:
        return [MonitorResponse(monitor_id=item.monitor_id, topic=item.topic, query=item.query, schedule_hint=item.schedule_hint, active=item.active) for item in monitoring.list_monitors()]

    @app.post('/monitors/{monitor_id}/run', response_model=MonitorRunTriggerResponse)
    def run_monitor(monitor_id: str) -> MonitorRunTriggerResponse:
        result = monitoring.run_monitor(monitor_id)
        monitor = next(item for item in monitoring.list_monitors() if item.monitor_id == monitor_id)
        return MonitorRunTriggerResponse(monitor_id=monitor.monitor_id, confidence=result.analysis.confidence, summary=result.analysis.summary)

    @app.post('/monitors/run-all')
    def run_all_monitors() -> list[MonitorRunTriggerResponse]:
        rows = monitoring.run_all_monitors()
        return [MonitorRunTriggerResponse(monitor_id=str(row['monitor_id']), confidence=float(row['confidence']), summary=str(row['summary'])) for row in rows]

    @app.get('/monitor-runs', response_model=list[MonitorRunResponse])
    def list_monitor_runs() -> list[MonitorRunResponse]:
        return [MonitorRunResponse(**item) for item in monitoring.list_monitor_runs()]

    @app.get('/monitors/{monitor_id}/compare', response_model=MonitorComparisonResponse)
    def compare_monitor(monitor_id: str) -> MonitorComparisonResponse:
        comparison = monitoring.compare_monitor_runs(monitor_id)
        return MonitorComparisonResponse(**comparison)

    @app.post('/alerts', response_model=AlertRuleResponse)
    def create_alert(req: AlertRuleCreateRequest) -> AlertRuleResponse:
        rule = monitoring.create_alert_rule(monitor_id=req.monitor_id, name=req.name, metric=req.metric, operator=req.operator, threshold=req.threshold)
        return AlertRuleResponse(rule_id=rule.rule_id, monitor_id=rule.monitor_id, name=rule.name, metric=rule.metric, operator=rule.operator, threshold=rule.threshold, active=rule.active)

    @app.get('/alerts', response_model=list[AlertRuleResponse])
    def list_alerts() -> list[AlertRuleResponse]:
        return [AlertRuleResponse(rule_id=r.rule_id, monitor_id=r.monitor_id, name=r.name, metric=r.metric, operator=r.operator, threshold=r.threshold, active=r.active) for r in monitoring.list_alert_rules()]

    @app.get('/alert-events', response_model=list[AlertEventResponse])
    def list_alert_events() -> list[AlertEventResponse]:
        return [AlertEventResponse(event_id=e.event_id, rule_id=e.rule_id, monitor_id=e.monitor_id, triggered_at=e.triggered_at, metric=e.metric, actual_value=e.actual_value, threshold=e.threshold, message=e.message) for e in monitoring.list_alert_events()]

    return app
