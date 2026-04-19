from __future__ import annotations

import argparse

from ..analysis.engine import AnalysisEngine
from ..planner.classifier import TaskClassifier
from ..planner.planner import SimplePlanner
from ..planner.priceability import PriceabilityChecker
from ..reports.markdown import MarkdownReportRenderer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Digital Analysis CLI")
    parser.add_argument("question", help="Natural-language market question")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    classifier = TaskClassifier()
    task = classifier.classify(args.question)

    checker = PriceabilityChecker()
    assessment = checker.assess(task)

    planner = SimplePlanner()
    plan = planner.plan(task)

    engine = AnalysisEngine()
    output = engine.analyze(task, plan)
    output.metadata["priceability"] = assessment.reason

    report = MarkdownReportRenderer().render(output)
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
