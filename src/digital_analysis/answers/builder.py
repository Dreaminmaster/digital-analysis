from __future__ import annotations

from ..analysis.engine import AnalysisOutput
from .schema import AnswerEvidence, OneShotAnswer


class OneShotAnswerBuilder:
    def build(self, analysis: AnalysisOutput) -> OneShotAnswer:
        evidence_items = tuple(
            AnswerEvidence(
                label=item.label,
                summary=item.summary,
                value_text=item.value_text,
            )
            for item in analysis.evidence.items[:6]
        )

        if analysis.contradictions:
            conclusion = (
                f"Current evidence for this {analysis.task.task_type.value} question is mixed. "
                f"The system found meaningful contradictions across signals, so the answer should be treated as probabilistic rather than definitive."
            )
        else:
            conclusion = (
                f"Current evidence for this {analysis.task.task_type.value} question is directionally coherent enough to support a one-shot judgment."
            )

        uncertainty = list(analysis.gaps)
        if not uncertainty:
            uncertainty.append("No major gaps flagged by the current baseline pipeline.")

        next_checks = list(analysis.plan.suggested_symbols[:4])
        if not next_checks:
            next_checks = [req.category for req in analysis.plan.required_signals[:4]]

        return OneShotAnswer(
            question=analysis.task.question,
            conclusion=conclusion,
            confidence=analysis.confidence,
            key_evidence=evidence_items,
            contradictory_evidence=tuple(analysis.contradictions),
            scenarios=tuple(analysis.scenarios),
            uncertainty=tuple(uncertainty),
            suggested_next_checks=tuple(next_checks),
            metadata=dict(analysis.metadata),
        )
