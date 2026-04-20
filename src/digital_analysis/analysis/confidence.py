from __future__ import annotations

from ..contracts.evidence import EvidenceBundle


class ConfidenceEngine:
    """Baseline confidence model with evidence-aware adjustment."""

    def score(
        self,
        *,
        evidence_count: int,
        contradiction_count: int,
        missing_coverage_count: int,
    ) -> float:
        score = 0.25
        score += min(evidence_count, 6) * 0.08
        score -= contradiction_count * 0.07
        score -= missing_coverage_count * 0.05
        return max(0.0, min(score, 0.95))

    def adjust_with_evidence(self, base_confidence: float, evidence: EvidenceBundle) -> float:
        score = base_confidence
        hinted = [item.confidence_hint for item in evidence.items if item.confidence_hint is not None]
        if hinted:
            avg = sum(hinted) / len(hinted)
            score = (score * 0.6) + (avg * 0.4)
        return max(0.0, min(score, 0.95))
