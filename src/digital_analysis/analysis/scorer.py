from __future__ import annotations

from dataclasses import dataclass

from ..contracts.evidence import EvidenceBundle


@dataclass(frozen=True)
class EvidenceScore:
    item_count: int
    positive_count: int
    negative_count: int
    neutral_count: int
    average_confidence_hint: float


class EvidenceScoringEngine:
    def score(self, evidence: EvidenceBundle) -> EvidenceScore:
        positive = 0
        negative = 0
        neutral = 0
        conf_sum = 0.0
        conf_n = 0

        for item in evidence.items:
            direction = (item.direction or "").lower()
            if direction in ("up", "risk_on", "spec_long", "steepening_or_positive"):
                positive += 1
            elif direction in ("down", "risk_off", "spec_short", "inverted"):
                negative += 1
            else:
                neutral += 1

            if item.confidence_hint is not None:
                conf_sum += item.confidence_hint
                conf_n += 1

        avg_conf = conf_sum / conf_n if conf_n else 0.0
        return EvidenceScore(
            item_count=len(evidence.items),
            positive_count=positive,
            negative_count=negative,
            neutral_count=neutral,
            average_confidence_hint=avg_conf,
        )
