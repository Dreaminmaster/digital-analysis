from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AnswerEvidence:
    label: str
    summary: str
    value_text: str | None = None


@dataclass(frozen=True)
class ReasoningTrace:
    trace_id: str
    label: str
    direction: str | None = None
    confidence_hint: float | None = None
    provider_id: str | None = None


@dataclass(frozen=True)
class OneShotAnswer:
    question: str
    conclusion: str
    verdict: str
    confidence: float
    key_evidence: tuple[AnswerEvidence, ...] = ()
    contradictory_evidence: tuple[str, ...] = ()
    scenarios: tuple[str, ...] = ()
    uncertainty: tuple[str, ...] = ()
    suggested_next_checks: tuple[str, ...] = ()
    reasoning_traces: tuple[ReasoningTrace, ...] = ()
    metadata: dict[str, object] = field(default_factory=dict)
