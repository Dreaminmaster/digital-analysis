from __future__ import annotations

from ..analysis.engine import AnalysisOutput


class MarkdownReportRenderer:
    def render(self, output: AnalysisOutput) -> str:
        lines = [
            "# Analysis Report",
            "",
            "## Question",
            output.task.question,
            "",
            "## Summary",
            output.summary,
            "",
            "## Confidence",
            f"{output.confidence:.0%}",
            "",
            "## Planned Evidence",
        ]
        if output.evidence.items:
            for item in output.evidence.items:
                lines.append(f"- **{item.label}**: {item.summary}")
        else:
            lines.append("- None")

        lines.append("")
        lines.append("## Evidence Gaps")
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
