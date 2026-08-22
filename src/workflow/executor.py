from __future__ import annotations

from ..agents.evaluator import EvaluatorAgent
from ..agents.evaluator import EvaluationResult


class EvaluationExecutor:
    """Execute independent evaluations for a committee of agents."""

    def run(
        self,
        agents: list[EvaluatorAgent],
        rubric: str,
        task: str,
        context: str,
    ) -> list[EvaluationResult]:
        """Run an independent evaluation for each agent.

        Each evaluator receives the same rubric, task, and context,
        but uses its own system prompt and evaluator profile.
        """

        results: list[EvaluationResult] = []

        for agent in agents:
            result = agent.evaluate(
                rubric=rubric,
                task=task,
                context=context,
            )
            results.append(result)

        return results
