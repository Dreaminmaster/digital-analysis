from __future__ import annotations

import json
from dataclasses import dataclass

from ..execution.http import JsonHttpClient, UrllibHttpClient
from .base import ModelRequest, ModelResponse


@dataclass
class OpenAICompatibleModel:
    base_url: str
    api_key: str
    model_name: str
    http_client: JsonHttpClient | None = None

    def complete(self, request: ModelRequest) -> ModelResponse:
        client = self.http_client or UrllibHttpClient(headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "digital-analysis/0.1",
        })
        payload = {
            "model": self.model_name,
            "messages": [{"role": m.role, "content": m.content} for m in request.messages],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }
        # Current HTTP layer is GET-oriented, so this adapter is a placeholder contract.
        # Next step: add POST support in execution/http.py and wire this fully.
        return ModelResponse(
            text="[OpenAI-compatible adapter scaffold: POST transport not wired yet]",
            model_name=self.model_name,
            raw=payload,
        )
