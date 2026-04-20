from __future__ import annotations

from dataclasses import dataclass

from ..contracts.evidence import EvidenceBundle


@dataclass(frozen=True)
class ContradictionFinding:
    left: str
    right: str
    explanation: str
    severity: float = 0.5


class ContradictionEngine:
    """Baseline contradiction detector.

    Supports both simple signal notes and structured evidence items.
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

    def detect_from_evidence(self, evidence: EvidenceBundle) -> tuple[ContradictionFinding, ...]:
        findings: list[ContradictionFinding] = []
        directions = [item.direction for item in evidence.items if item.direction]
        has_risk_on = any(d == "risk_on" for d in directions)
        has_risk_off = any(d == "risk_off" for d in directions)
        has_inverted_curve = any(d == "inverted" for d in directions)
        has_up_asset = any(d == "up" for d in directions)
        has_down_asset = any(d == "down" for d in directions)

        if has_risk_on and has_risk_off:
            findings.append(
                ContradictionFinding(
                    left="risk_on evidence",
                    right="risk_off evidence",
                    explanation="Some evidence points to appetite for risk while other evidence signals defensive positioning.",
                    severity=0.75,
                )
            )
        if has_inverted_curve and (has_up_asset or has_risk_on):
            findings.append(
                ContradictionFinding(
                    left="inverted curve",
                    right="risk-on pricing",
                    explanation="Macro stress pricing can coexist with short-term risk appetite or rising asset prices.",
                    severity=0.6,
                )
            )
        if has_up_asset and has_down_asset:
            findings.append(
                ContradictionFinding(
                    left="upward price evidence",
                    right="downward price evidence",
                    explanation="Related assets or horizons may be diverging instead of moving together.",
                    severity=0.5,
                )
            )
        return tuple(findings)
