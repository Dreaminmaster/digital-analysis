from __future__ import annotations

from ..analysis.engine import AnalysisOutput
from ..contracts.tasks import TaskType
from .schema import AnswerEvidence, OneShotAnswer, ReasoningTrace


class OneShotAnswerBuilder:
    def build(self, analysis: AnalysisOutput) -> OneShotAnswer:
        ranked_items = sorted(
            analysis.evidence.items,
            key=lambda item: (item.confidence_hint if item.confidence_hint is not None else 0.0),
            reverse=True,
        )

        key_raw = ranked_items[:6]
        evidence_items = tuple(
            AnswerEvidence(
                label=item.label,
                summary=item.summary,
                value_text=item.value_text,
            )
            for item in key_raw
        )

        traces = tuple(
            ReasoningTrace(
                trace_id=f"ev:{i}:{item.label}",
                label=item.label,
                direction=item.direction,
                confidence_hint=item.confidence_hint,
                provider_id=item.provenance.provider_id if item.provenance is not None else None,
            )
            for i, item in enumerate(key_raw, 1)
        )

        if analysis.contradictions:
            contradiction_suffix = (
                "The signal set contains notable contradictions, so this should be treated as a probabilistic judgment."
            )
        else:
            contradiction_suffix = "Signals are relatively coherent for a one-shot judgment."

        if analysis.task.task_type == TaskType.MACRO:
            conclusion = (
                "Macro-pricing evidence currently supports a directional judgment on growth/rate conditions. "
                + contradiction_suffix
            )
        elif analysis.task.task_type == TaskType.GEOPOLITICAL:
            conclusion = (
                "Geopolitical risk pricing across event and proxy markets suggests a bounded risk assessment rather than a binary prediction. "
                + contradiction_suffix
            )
        elif analysis.task.task_type == TaskType.ASSET:
            conclusion = (
                "Asset-pricing evidence currently indicates a tactical valuation signal under present macro/sentiment context. "
                + contradiction_suffix
            )
        elif analysis.task.task_type == TaskType.BUBBLE:
            conclusion = (
                "Bubble-assessment evidence points to a speculative-pressure read, not an absolute overvaluation verdict. "
                + contradiction_suffix
            )
        else:
            conclusion = (
                f"Current evidence for this {analysis.task.task_type.value} question is suitable for a one-shot probabilistic interpretation. "
                + contradiction_suffix
            )

        uncertainty = list(analysis.gaps)
        if not uncertainty:
            uncertainty.append("No major gaps flagged by the current baseline pipeline.")

        next_checks = list(analysis.plan.suggested_symbols[:4])
        if not next_checks:
            next_checks = [req.category for req in analysis.plan.required_signals[:4]]

        metadata = dict(analysis.metadata)
        metadata.setdefault("answer_version", "v1.2")
        metadata.setdefault("reasoning_trace_ids", tuple(trace.trace_id for trace in traces))

        verdict = "mixed"
        if analysis.confidence >= 0.7 and not analysis.contradictions:
            verdict = "positive"
        elif analysis.confidence < 0.45 or len(analysis.contradictions) >= 2:
            verdict = "negative"

        return OneShotAnswer(
            question=analysis.task.question,
            conclusion=conclusion,
            verdict=verdict,
            confidence=analysis.confidence,
            key_evidence=evidence_items,
            contradictory_evidence=tuple(analysis.contradictions),
            scenarios=tuple(analysis.scenarios),
            uncertainty=tuple(uncertainty),
            suggested_next_checks=tuple(next_checks),
            reasoning_traces=traces,
            metadata=metadata,
        )
