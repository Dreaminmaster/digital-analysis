from __future__ import annotations


class ScenarioComposer:
    def compose(self, task_question: str) -> tuple[str, ...]:
        return (
            f"Base case: market pricing remains the main reference frame for '{task_question}'.",
            "Risk case: direct event or volatility markets diverge sharply from macro proxies.",
            "Extreme case: tail-risk assets and policy expectations reprice at the same time.",
        )
