from __future__ import annotations

from dataclasses import dataclass

from ..orchestrator import DigitalAnalysisOrchestrator, OrchestratorResult


@dataclass
class AnalysisService:
    orchestrator: DigitalAnalysisOrchestrator

    def analyze(self, question: str) -> OrchestratorResult:
        return self.orchestrator.run(question)
