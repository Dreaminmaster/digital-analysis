from __future__ import annotations

from dataclasses import dataclass

from .analysis.engine import AnalysisEngine, AnalysisOutput
from .analysis.router import WorkflowRouter
from .answers.builder import OneShotAnswerBuilder
from .answers.schema import OneShotAnswer
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
    answer: OneShotAnswer
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
        workflow_router: WorkflowRouter | None = None,
        answer_builder: OneShotAnswerBuilder | None = None,
        auto_enrich: bool = True,
    ) -> None:
        self.classifier = classifier or TaskClassifier()
        self.priceability_checker = priceability_checker or PriceabilityChecker()
        self.planner = planner or SimplePlanner()
        self.analysis_engine = analysis_engine or AnalysisEngine()
        self.markdown_renderer = markdown_renderer or MarkdownReportRenderer()
        self.synthesizer = synthesizer
        self.workflow_router = workflow_router or WorkflowRouter()
        self.answer_builder = answer_builder or OneShotAnswerBuilder()
        self.auto_enrich = auto_enrich

    def run(self, question: str) -> OrchestratorResult:
        task = self.classifier.classify(question)
        priceability = self.priceability_checker.assess(task)
        plan = self.planner.plan(task)
        analysis = self.analysis_engine.analyze(task, plan)

        if self.auto_enrich:
            workflow, selection = self.workflow_router.build(task)
            if workflow is not None and selection is not None:
                try:
                    if selection.workflow_name == "asset_pricing":
                        analysis = workflow.enrich(analysis, symbol=task.target_asset or "GLD")
                    elif selection.workflow_name == "bubble":
                        analysis = workflow.enrich(analysis, ticker=task.target_asset or "NVDA")
                    else:
                        analysis = workflow.enrich(analysis)
                    metadata = dict(analysis.metadata)
                    metadata["workflow"] = {
                        "name": selection.workflow_name,
                        "reason": selection.reason,
                    }
                    metadata["target_asset"] = task.target_asset
                    analysis = AnalysisOutput(
                        task=analysis.task,
                        plan=analysis.plan,
                        summary=analysis.summary,
                        confidence=analysis.confidence,
                        evidence=analysis.evidence,
                        gaps=analysis.gaps,
                        contradictions=analysis.contradictions,
                        scenarios=analysis.scenarios,
                        metadata=metadata,
                    )
                except Exception as exc:
                    metadata = dict(analysis.metadata)
                    metadata["workflow_error"] = str(exc)
                    metadata["target_asset"] = task.target_asset
                    analysis = AnalysisOutput(
                        task=analysis.task,
                        plan=analysis.plan,
                        summary=analysis.summary,
                        confidence=analysis.confidence,
                        evidence=analysis.evidence,
                        gaps=analysis.gaps,
                        contradictions=analysis.contradictions,
                        scenarios=analysis.scenarios,
                        metadata=metadata,
                    )

        answer = self.answer_builder.build(analysis)
        markdown_report = self.markdown_renderer.render(analysis)
        synthesized_text = None
        if self.synthesizer is not None:
            synthesized_text = self.synthesizer.synthesize(analysis).text
        return OrchestratorResult(
            task=task,
            priceability=priceability,
            analysis=analysis,
            answer=answer,
            markdown_report=markdown_report,
            synthesized_text=synthesized_text,
        )
