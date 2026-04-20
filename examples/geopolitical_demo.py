from digital_analysis.orchestrator import DigitalAnalysisOrchestrator
from digital_analysis.analysis.workflows import GeopoliticalRiskWorkflow


def main() -> int:
    question = "What is the risk of war escalation in the next 12 months?"
    orchestrator = DigitalAnalysisOrchestrator()
    result = orchestrator.run(question)

    workflow = GeopoliticalRiskWorkflow()
    enriched = workflow.enrich(result.analysis)

    print("# Geopolitical Risk Demo")
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
