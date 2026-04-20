from __future__ import annotations

from dataclasses import dataclass

from .analysis.engine import AnalysisEngine, AnalysisOutput
from .contracts.tasks import TaskSpec
from .planner.classifier import TaskClassifier
from .planner.planner import SimplePlanner
from .planner.priceability import PriceabilityAssessment, PriceabilityChecker
from .reports.builder import ReportSynthesizer
from .reports.markdown import MarkdownReportRenderer


@dataclass(frozen=True)
class OrchestratorResult:
    task: TaskSpec
    priceability: PriceabilityAssessment
    analysis: AnalysisOutput
    markdown_report: str
    synthesized_text: str | None = None


class DigitalAnalysisOrchestrator:
    def __init__(
        self,
        *,
        classifier: TaskClassifier | None = None,
        priceability_checker: PriceabilityChecker | None = None,
        planner: SimplePlanner | None = None,
        analysis_engine: AnalysisEngine | None = None,
        markdown_renderer: MarkdownReportRenderer | None = None,
        synthesizer: ReportSynthesizer | None = None,
    ) -> None:
        self.classifier = classifier or TaskClassifier()
        self.priceability_checker = priceability_checker or PriceabilityChecker()
        self.planner = planner or SimplePlanner()
        self.analysis_engine = analysis_engine or AnalysisEngine()
        self.markdown_renderer = markdown_renderer or MarkdownReportRenderer()
        self.synthesizer = synthesizer

    def run(self, question: str) -> OrchestratorResult:
        task = self.classifier.classify(question)
        priceability = self.priceability_checker.assess(task)
        plan = self.planner.plan(task)
        analysis = self.analysis_engine.analyze(task, plan)
        markdown_report = self.markdown_renderer.render(analysis)
        synthesized_text = None
        if self.synthesizer is not None:
            synthesized_text = self.synthesizer.synthesize(analysis).text
        return OrchestratorResult(
            task=task,
            priceability=priceability,
            analysis=analysis,
            markdown_report=markdown_report,
            synthesized_text=synthesized_text,
        )
