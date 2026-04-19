from __future__ import annotations

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
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "digital-analysis/0.1",
        })
        payload = {
            "model": self.model_name,
            "messages": [{"role": m.role, "content": m.content} for m in request.messages],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }
        data = client.post_json(f"{self.base_url.rstrip('/')}/chat/completions", body=payload)
        text = ""
        if isinstance(data, dict):
            choices = data.get("choices")
            if isinstance(choices, list) and choices:
                first = choices[0]
                if isinstance(first, dict):
                    message = first.get("message")
                    if isinstance(message, dict):
                        content = message.get("content")
                        if isinstance(content, str):
                            text = content
        return ModelResponse(text=text, model_name=self.model_name, raw=data)
