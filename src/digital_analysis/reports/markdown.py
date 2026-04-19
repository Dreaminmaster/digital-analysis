from __future__ import annotations

from ..analysis.engine import AnalysisOutput


class MarkdownReportRenderer:
    def render(self, output: AnalysisOutput) -> str:
        lines = [
            f"# Analysis Report",
            "",
            f"## Question",
            output.task.question,
            "",
            f"## Summary",
            output.summary,
            "",
            f"## Confidence",
            f"{output.confidence:.0%}",
            "",
            "## Evidence Gaps",
        ]
        lines.extend([f"- {gap}" for gap in output.gaps] or ["- None"])
        if output.contradictions:
            lines.append("")
            lines.append("## Contradictions")
            lines.extend([f"- {item}" for item in output.contradictions])
        if output.scenarios:
            lines.append("")
            lines.append("## Scenarios")
            lines.extend([f"- {item}" for item in output.scenarios])
        return "\n".join(lines)
