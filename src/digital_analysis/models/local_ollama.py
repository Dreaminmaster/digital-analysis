from __future__ import annotations

from dataclasses import dataclass

from ..execution.http import JsonHttpClient, UrllibHttpClient
from .base import ModelRequest, ModelResponse


@dataclass
class OllamaModel:
    model_name: str
    endpoint: str = "http://localhost:11434"
    http_client: JsonHttpClient | None = None

    def complete(self, request: ModelRequest) -> ModelResponse:
        client = self.http_client or UrllibHttpClient(headers={
            "Accept": "application/json",
            "User-Agent": "digital-analysis/0.1",
        })
        payload = {
            "model": self.model_name,
            "messages": [{"role": m.role, "content": m.content} for m in request.messages],
            "stream": False,
            "options": {
                "temperature": request.temperature,
            },
        }
        data = client.post_json(f"{self.endpoint.rstrip('/')}/api/chat", body=payload)
        text = ""
        if isinstance(data, dict):
            message = data.get("message")
            if isinstance(message, dict):
                content = message.get("content")
                if isinstance(content, str):
                    text = content
        return ModelResponse(text=text, model_name=self.model_name, raw=data)
