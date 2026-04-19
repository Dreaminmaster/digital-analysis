from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ContradictionFinding:
    left: str
    right: str
    explanation: str
    severity: float = 0.5


class ContradictionEngine:
    """Baseline contradiction detector.

    For now this works on simple signal labels/notes. Later versions should use
    normalized evidence objects with direction, horizon, and confidence.
    """

    def detect(self, signal_notes: tuple[str, ...]) -> tuple[ContradictionFinding, ...]:
        findings: list[ContradictionFinding] = []
        lowered = [note.lower() for note in signal_notes]

        has_risk_off = any("risk-off" in note or "fear" in note for note in lowered)
        has_risk_on = any("risk-on" in note or "greed" in note for note in lowered)
        has_cut = any("rate cuts" in note or "cuts" in note for note in lowered)
        has_growth = any("growth strong" in note or "equities strong" in note for note in lowered)

        if has_risk_off and has_risk_on:
            findings.append(
                ContradictionFinding(
                    left="risk-off signals",
                    right="risk-on signals",
                    explanation="Different markets may be pricing different horizons or tail vs base-case outcomes.",
                    severity=0.7,
                )
            )
        if has_cut and has_growth:
            findings.append(
                ContradictionFinding(
                    left="rate-cut expectations",
                    right="strong growth pricing",
                    explanation="Policy easing expectations can coexist with late-cycle strength or forward-looking risk hedging.",
                    severity=0.6,
                )
            )
        return tuple(findings)
