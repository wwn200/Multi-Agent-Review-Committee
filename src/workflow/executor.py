from __future__ import annotations

from ..agents.evaluator import EvaluatorAgent
from ..agents.evaluator import EvaluationResult


class EvaluationExecutor:
    """Execute independent evaluations for a committee of agents."""

    def run(
        self,
        agents: list[EvaluatorAgent],
        rubric: str | dict,
        task: str,
        context: str,
        assumption_id: str,
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
                assumption_id=assumption_id,
            )
            results.append(result)

        return results
