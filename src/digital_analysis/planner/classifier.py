from __future__ import annotations

from ..contracts.tasks import TaskSpec, TaskType, TimeHorizon


class TaskClassifier:
    def classify(self, question: str) -> TaskSpec:
        q = question.lower()

        task_type = TaskType.GENERAL
        horizon = TimeHorizon.UNKNOWN

        if any(word in q for word in ("war", "conflict", "invasion", "taiwan", "ww3", "geopolit")):
            task_type = TaskType.GEOPOLITICAL
        elif any(word in q for word in ("recession", "fed", "inflation", "economy", "yield")):
            task_type = TaskType.MACRO
        elif any(word in q for word in ("bubble", "overvalued", "mania", "hype")):
            task_type = TaskType.BUBBLE
        elif any(word in q for word in ("option", "iv", "volatility", "put", "call", "max pain")):
            task_type = TaskType.OPTIONS
        elif any(word in q for word in ("buy", "gold", "bitcoin", "btc", "stock", "asset")):
            task_type = TaskType.ASSET

        if any(word in q for word in ("this month", "1 month", "3 months", "short term", "next month")):
            horizon = TimeHorizon.SHORT
        elif any(word in q for word in ("12 months", "1 year", "next year", "medium term")):
            horizon = TimeHorizon.MEDIUM
        elif any(word in q for word in ("3 years", "5 years", "long term", "decade")):
            horizon = TimeHorizon.LONG

        return TaskSpec(question=question, task_type=task_type, horizon=horizon)
