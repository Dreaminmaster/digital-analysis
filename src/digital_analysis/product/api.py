from __future__ import annotations

from typing import Any

from ..models.base import ChatModel
from ..orchestrator import DigitalAnalysisOrchestrator
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


def create_app(*, model: ChatModel | None = None) -> Any:
    if FastAPI is None:
        raise RuntimeError("fastapi and pydantic are required to create the API app")

    synthesizer = ReportSynthesizer(model=model) if model is not None else None
    service = AnalysisService(orchestrator=DigitalAnalysisOrchestrator(synthesizer=synthesizer))
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

    return app
