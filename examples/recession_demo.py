from __future__ import annotations

from digital_analysis.orchestrator import DigitalAnalysisOrchestrator
from digital_analysis.analysis.workflows import RecessionWorkflow


def main() -> int:
    question = "What is the probability of a recession in the next 12 months?"
    orchestrator = DigitalAnalysisOrchestrator()
    result = orchestrator.run(question)

    workflow = RecessionWorkflow()
    enriched = workflow.enrich(result.analysis)

    print("# Recession Demo")
    print()
    print(result.markdown_report)
    print()
    print("## Enriched Evidence")
    for item in enriched.evidence.items:
        print(f"- {item.label}: {item.summary} ({item.value_text or 'n/a'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
