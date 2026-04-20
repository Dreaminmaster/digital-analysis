from __future__ import annotations

from ..contracts.evidence import EvidenceBundle
from .scorer import EvidenceScore


class SummaryRegenerator:
    def regenerate(self, *, task_type: str, evidence: EvidenceBundle, score: EvidenceScore) -> str:
        leaning = "mixed"
        if score.positive_count > score.negative_count:
            leaning = "positive-leaning"
        elif score.negative_count > score.positive_count:
            leaning = "negative-leaning"

        return (
            f"Evidence-driven analysis for {task_type} currently looks {leaning}. "
            f"Structured evidence count={score.item_count}, positive={score.positive_count}, "
            f"negative={score.negative_count}, neutral={score.neutral_count}."
        )
