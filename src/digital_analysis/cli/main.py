from __future__ import annotations

import argparse

from ..orchestrator import DigitalAnalysisOrchestrator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Digital Analysis CLI")
    parser.add_argument("question", help="Natural-language market question")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    result = DigitalAnalysisOrchestrator().run(args.question)
    print(result.markdown_report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
