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
    direction: str | None = None
    horizon: str | None = None
    confidence_hint: float | None = None


class AnalyzeResponse(BaseModel):  # type: ignore[misc,valid-type]
    task_type: str
    horizon: str
    priceable: bool
    summary: str
    confidence: float
    markdown_report: str
    suggested_symbols: list[str]
    suggested_providers: list[str]
    evidence: list[EvidenceResponse]
    contradictions: list[str]
    scenarios: list[str]
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
        evidence = [
            EvidenceResponse(
                label=item.label,
                summary=item.summary,
                value_text=item.value_text,
                direction=item.direction,
                horizon=item.horizon,
                confidence_hint=item.confidence_hint,
            )
            for item in result.analysis.evidence.items
        ]
        return AnalyzeResponse(
            task_type=result.task.task_type.value,
            horizon=result.task.horizon.value,
            priceable=result.priceability.priceable,
            summary=result.analysis.summary,
            confidence=result.analysis.confidence,
            markdown_report=result.markdown_report,
            suggested_symbols=list(result.analysis.plan.suggested_symbols),
            suggested_providers=list(result.analysis.plan.suggested_providers),
            evidence=evidence,
            contradictions=list(result.analysis.contradictions),
            scenarios=list(result.analysis.scenarios),
            metadata=result.analysis.metadata,
            synthesized_text=synthesized_text,
        )

    @app.post('/watchlist', response_model=WatchlistItemResponse)
    def create_watchlist_item(req: WatchlistCreateRequest) -> WatchlistItemResponse:
        item = monitoring.create_watchlist_item(name=req.name, query=req.query, tags=tuple(req.tags))
        return WatchlistItemResponse(item_id=item.item_id, name=item.name, query=item.query, tags=list(item.tags))

    @app.get('/watchlist', response_model=list[WatchlistItemResponse])
    def list_watchlist_items() -> list[WatchlistItemResponse]:
        return [
            WatchlistItemResponse(item_id=item.item_id, name=item.name, query=item.query, tags=list(item.tags))
            for item in monitoring.list_watchlist_items()
        ]

    @app.post('/monitors', response_model=MonitorResponse)
    def create_monitor(req: MonitorCreateRequest) -> MonitorResponse:
        monitor = monitoring.create_monitor(topic=req.topic, query=req.query, schedule_hint=req.schedule_hint)
        return MonitorResponse(
            monitor_id=monitor.monitor_id,
            topic=monitor.topic,
            query=monitor.query,
            schedule_hint=monitor.schedule_hint,
            active=monitor.active,
        )

    @app.get('/monitors', response_model=list[MonitorResponse])
    def list_monitors() -> list[MonitorResponse]:
        return [
            MonitorResponse(
                monitor_id=item.monitor_id,
                topic=item.topic,
                query=item.query,
                schedule_hint=item.schedule_hint,
                active=item.active,
            )
            for item in monitoring.list_monitors()
        ]

    return app
