from __future__ import annotations

from dataclasses import dataclass

from ..analysis.engine import AnalysisOutput
from ..models.base import ChatModel, ModelResponse
from .synthesis import SynthesisPromptBuilder


@dataclass
class ReportSynthesizer:
    model: ChatModel
    prompt_builder: SynthesisPromptBuilder | None = None

    def synthesize(self, analysis: AnalysisOutput) -> ModelResponse:
        builder = self.prompt_builder or SynthesisPromptBuilder()
        request = builder.build(analysis)
        return self.model.complete(request)
