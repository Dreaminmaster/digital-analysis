from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class ModelMessage:
    role: str
    content: str


@dataclass(frozen=True)
class ModelRequest:
    messages: tuple[ModelMessage, ...]
    temperature: float = 0.2
    max_tokens: int = 1200
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class ModelResponse:
    text: str
    model_name: str
    raw: object | None = None


class ChatModel(Protocol):
    def complete(self, request: ModelRequest) -> ModelResponse: ...
