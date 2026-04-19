from __future__ import annotations

from dataclasses import dataclass, field

from ..contracts.evidence import EvidenceBundle, EvidenceItem, EvidenceKind, SourceProvenance
from ..contracts.tasks import TaskSpec
from ..planner.planner import SignalPlan
from .confidence import ConfidenceEngine
from .contradiction import ContradictionEngine
from .horizons import HorizonGroupingEngine
from .scenarios import ScenarioComposer


@dataclass(frozen=True)
class AnalysisOutput:
    task: TaskSpec
    plan: SignalPlan
    summary: str
    confidence: float
    evidence: EvidenceBundle
    gaps: tuple[str, ...] = ()
    contradictions: tuple[str, ...] = ()
    scenarios: tuple[str, ...] = ()
    metadata: dict[str, object] = field(default_factory=dict)


class AnalysisEngine:
    """Baseline autonomous analysis engine.

    Upgraded to emit structured evidence so future synthesis/reporting can rely
    on contracts instead of only free-form summary text.
    """

    def __init__(self) -> None:
        self._contradictions = ContradictionEngine()
        self._horizons = HorizonGroupingEngine()
        self._confidence = ConfidenceEngine()
        self._scenarios = ScenarioComposer()

    def analyze(self, task: TaskSpec, plan: SignalPlan) -> AnalysisOutput:
        signal_notes = tuple(req.category.replace("_", " ") for req in plan.required_signals)
        horizon_bucket = self._horizons.group(signal_notes)
        contradiction_findings = self._contradictions.detect(signal_notes + plan.notes)
        scenarios = self._scenarios.compose(task.question)

        evidence_items = tuple(
            EvidenceItem(
                kind=EvidenceKind.OTHER,
                label=req.category,
                summary=req.reason,
                horizon=task.horizon.value,
                confidence_hint=min(0.3 + req.priority * 0.15, 0.9),
                provenance=SourceProvenance(provider_id="planner", notes=("planned-signal",)),
            )
            for req in plan.required_signals
        )
        evidence = EvidenceBundle(items=evidence_items)

        gaps: list[str] = []
        if not horizon_bucket.short_term:
            gaps.append("Short-term pricing coverage is weak.")
        if not horizon_bucket.medium_term:
            gaps.append("Medium-term pricing coverage is weak.")
        if not plan.required_signals:
            gaps.append("No planned signals available.")

        confidence = self._confidence.score(
            evidence_count=len(plan.required_signals),
            contradiction_count=len(contradiction_findings),
            missing_coverage_count=len(gaps),
        )

        summary = (
            f"Task classified as {task.task_type.value} with {len(plan.required_signals)} planned signal categories. "
            f"Autonomous baseline analysis grouped signals by horizon, checked for contradictions, "
            f"and synthesized scenario scaffolding."
        )

        return AnalysisOutput(
            task=task,
            plan=plan,
            summary=summary,
            confidence=confidence,
            evidence=evidence,
            gaps=tuple(gaps),
            contradictions=tuple(f.explanation for f in contradiction_findings),
            scenarios=scenarios,
            metadata={
                "horizons": {
                    "short": horizon_bucket.short_term,
                    "medium": horizon_bucket.medium_term,
                    "long": horizon_bucket.long_term,
                    "unknown": horizon_bucket.unknown,
                }
            },
        )
