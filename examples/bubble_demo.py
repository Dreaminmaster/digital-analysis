from digital_analysis.orchestrator import DigitalAnalysisOrchestrator
from digital_analysis.analysis.workflows import BubbleAssessmentWorkflow


def main() -> int:
    question = "Is AI in a bubble?"
    orchestrator = DigitalAnalysisOrchestrator()
    result = orchestrator.run(question)

    workflow = BubbleAssessmentWorkflow()
    enriched = workflow.enrich(result.analysis, ticker="NVDA")

    print("# Bubble Assessment Demo")
    print()
    print(result.markdown_report)
    print()
    print("## Enriched Evidence")
    for item in enriched.evidence.items:
        print(f"- {item.label}: {item.summary} ({item.value_text or 'n/a'})")
    print()
    print("## Reanalyzed Summary")
    print(enriched.summary)
    print(f"Confidence: {enriched.confidence:.0%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
