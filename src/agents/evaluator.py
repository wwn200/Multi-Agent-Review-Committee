from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..llm.client import LLMClient
from ..prompts.builder import PromptBuilder
from .profile.schema import EvaluatorProfile


@dataclass
class EvaluationResult:
    """
    Result returned by an evaluator agent.
    """

    evaluator_id: str
    response: str
    raw_response: Any | None = None


class EvaluatorAgent:
    """
    An evaluator agent with a concrete evaluator profile.

    The agent combines:
        - an EvaluatorProfile: who the evaluator is
        - a PromptBuilder: how prompts are constructed
        - an LLMClient: how the LLM is called
    """

    def __init__(
        self,
        profile: EvaluatorProfile,
        llm_client: LLMClient,
        *,
        prompt_builder: PromptBuilder | None = None,
    ) -> None:
        self.profile = profile
        self.llm_client = llm_client

        self.prompt_builder = (
            prompt_builder
            if prompt_builder is not None
            else PromptBuilder()
        )

        self.system_prompt: str = ""

    def prepare_system_prompt(
        self,
        rubric: str,
    ) -> str:
        """
        Build and store the system prompt for this evaluator.

        The system prompt describes the evaluator's identity,
        expertise, background, evaluation preferences, and
        evaluation rubric.
        """

        self.system_prompt = (
            self.prompt_builder.build_system_prompt(
                profile=self.profile,
                rubric=rubric,
            )
        )

        return self.system_prompt

    def evaluate(
        self,
        rubric: str,
        context: str,
        task: str,
    ) -> EvaluationResult:
        """
        Evaluate a specific assumption within an evaluation context.

        The evaluator's identity and evaluation behavior are provided
        through the system prompt, while the current evaluation
        context and task are provided through the user prompt.
        """

        system_prompt = self.prepare_system_prompt(
            rubric=rubric,
        )

        user_prompt = (
            self.prompt_builder.build_user_prompt(
                context=context,
                task=task,
            )
        )

        response = self.llm_client.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        return EvaluationResult(
            evaluator_id=self.profile.evaluator_id,
            response=response,
            raw_response=response,
        )
