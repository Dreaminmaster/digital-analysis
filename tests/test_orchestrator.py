import unittest

from digital_analysis.orchestrator import DigitalAnalysisOrchestrator
from digital_analysis.reports.builder import ReportSynthesizer
from digital_analysis.models.base import ModelResponse


class FakeModel:
    def complete(self, request):
        return ModelResponse(text="synthetic answer", model_name="fake")


class FakeWorkflow:
    def enrich(self, analysis, **kwargs):
        metadata = dict(analysis.metadata)
        metadata['fake_enriched'] = True
        metadata['kwargs'] = kwargs
        return type(analysis)(
            task=analysis.task,
            plan=analysis.plan,
            summary='fake enriched summary',
            confidence=analysis.confidence,
            evidence=analysis.evidence,
            gaps=analysis.gaps,
            contradictions=analysis.contradictions,
            scenarios=analysis.scenarios,
            metadata=metadata,
        )


class FakeWorkflowRouter:
    def build(self, task):
        class Sel:
            workflow_name = 'asset_pricing'
            reason = 'fake route'
        return FakeWorkflow(), Sel()


class OrchestratorTests(unittest.TestCase):
    def test_run_without_synthesis(self) -> None:
        result = DigitalAnalysisOrchestrator(auto_enrich=False).run("Will there be a recession next year?")
        self.assertIn("Analysis Report", result.markdown_report)
        self.assertIsNone(result.synthesized_text)
        self.assertTrue(result.priceability.priceable)

    def test_run_with_synthesis(self) -> None:
        orchestrator = DigitalAnalysisOrchestrator(synthesizer=ReportSynthesizer(model=FakeModel()), auto_enrich=False)
        result = orchestrator.run("Will there be a recession next year?")
        self.assertEqual(result.synthesized_text, "synthetic answer")

    def test_auto_enrich_uses_workflow_router_and_target_asset(self) -> None:
        orchestrator = DigitalAnalysisOrchestrator(workflow_router=FakeWorkflowRouter(), auto_enrich=True)
        result = orchestrator.run("Should I buy gold now?")
        self.assertEqual(result.analysis.summary, 'fake enriched summary')
        self.assertIn('workflow', result.analysis.metadata)
        self.assertEqual(result.analysis.metadata.get('target_asset'), 'GLD')


if __name__ == "__main__":
    unittest.main()
