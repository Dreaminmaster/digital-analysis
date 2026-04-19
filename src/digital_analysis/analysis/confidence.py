from __future__ import annotations


class ConfidenceEngine:
    """Very simple baseline confidence model.

    Future versions should calibrate on source quality, contradiction severity,
    horizon coverage, freshness, and evidence sufficiency.
    """

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
