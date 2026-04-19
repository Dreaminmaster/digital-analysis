from __future__ import annotations

from dataclasses import dataclass

from .base import ModelRequest, ModelResponse


@dataclass
class OllamaModel:
    model_name: str
    endpoint: str = "http://localhost:11434"

    def complete(self, request: ModelRequest) -> ModelResponse:
        return ModelResponse(
            text="[Ollama adapter scaffold: transport not wired yet]",
            model_name=self.model_name,
            raw={
                "endpoint": self.endpoint,
                "messages": [{"role": m.role, "content": m.content} for m in request.messages],
            },
        )
