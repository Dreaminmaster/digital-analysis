from __future__ import annotations

from dataclasses import dataclass

from ..analysis.engine import AnalysisOutput
from ..models.base import ModelMessage, ModelRequest


@dataclass(frozen=True)
class SynthesisPromptBuilder:
    def build(self, analysis: AnalysisOutput) -> ModelRequest:
        evidence_lines = [f"- {item.label}: {item.summary}" for item in analysis.evidence.items]
        contradiction_lines = [f"- {item}" for item in analysis.contradictions] or ["- None"]
        gap_lines = [f"- {item}" for item in analysis.gaps] or ["- None"]
        scenario_lines = [f"- {item}" for item in analysis.scenarios] or ["- None"]

        system = (
            "You are a market-intelligence synthesis model. "
            "Use only the provided evidence and analysis scaffolding. "
            "Be explicit, structured, and avoid inventing missing evidence."
        )
        user = "\n".join([
            f"Question: {analysis.task.question}",
            "",
            f"Baseline summary: {analysis.summary}",
            f"Confidence: {analysis.confidence:.0%}",
            "",
            "Evidence:",
            *evidence_lines,
            "",
            "Contradictions:",
            *contradiction_lines,
            "",
            "Evidence gaps:",
            *gap_lines,
            "",
            "Scenarios:",
            *scenario_lines,
            "",
            "Write a concise structured answer with: conclusion, evidence interpretation, contradictions, uncertainty, and next monitoring points.",
        ])
        return ModelRequest(messages=(ModelMessage(role="system", content=system), ModelMessage(role="user", content=user)))
