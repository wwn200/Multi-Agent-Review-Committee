from __future__ import annotations

from pathlib import Path

from ..llm.client import LLMClient
from ..prompts.builder import PromptBuilder
from .evaluator import EvaluatorAgent
from .profile.loader import ProfileConfigLoader
from .profile.modifiers import ProfileModifier
from .profile.sampler import EvaluatorSampler


class EvaluatorAgentCommittee:
    """
    Committe for creating evaluator agents.

    The Committe coordinates:
        1. Loading role and background configurations
        2. Applying background-specific modifiers
        3. Sampling individual evaluator profiles
        4. Creating EvaluatorAgent instances
    """

    def __init__(
        self,
        llm_client: LLMClient,
        *,
        profile_loader: ProfileConfigLoader | None = None,
        profile_modifier: ProfileModifier | None = None,
        prompt_builder: PromptBuilder | None = None,
        seed: int | None = None,
    ) -> None:
        self.llm_client = llm_client

        self.profile_loader = (
            profile_loader
            if profile_loader is not None
            else ProfileConfigLoader()
        )

        self.profile_modifier = (
            profile_modifier
            if profile_modifier is not None
            else ProfileModifier()
        )

        self.prompt_builder = (
            prompt_builder
            if prompt_builder is not None
            else PromptBuilder()
        )

        self.seed = seed

    def create_agent(
        self,
        role_path: str | Path,
        *,
        background_path: str | Path | None = None,
        evaluator_id: str = "expert_001",
    ) -> EvaluatorAgent:
        """
        Create a single evaluator agent.
        """

        population = self._create_population_spec(
            role_path=role_path,
            background_path=background_path,
            size=1,
        )

        sampler = EvaluatorSampler(
            seed=self.seed,
        )

        profile = sampler.sample(
            population=population,
            evaluator_id=evaluator_id,
        )

        return EvaluatorAgent(
            profile=profile,
            llm_client=self.llm_client,
            prompt_builder=self.prompt_builder,
        )

    def create_population(
        self,
        role_path: str | Path,
        *,
        background_path: str | Path | None = None,
        size: int = 1,
        prefix: str = "expert",
    ) -> list[EvaluatorAgent]:
        """
        Create a population of evaluator agents.
        """

        if size < 1:
            raise ValueError(
                "Population size must be at least 1."
            )

        population = self._create_population_spec(
            role_path=role_path,
            background_path=background_path,
            size=size,
        )

        sampler = EvaluatorSampler(
            seed=self.seed,
        )

        profiles = sampler.sample_population(
            population=population,
            prefix=prefix,
        )

        return [
            EvaluatorAgent(
                profile=profile,
                llm_client=self.llm_client,
                prompt_builder=self.prompt_builder,
            )
            for profile in profiles
        ]

    def _create_population_spec(
        self,
        role_path: str | Path,
        *,
        background_path: str | Path | None,
        size: int,
    ):
        """
        Load role/background configurations and construct
        a population specification.
        """

        role = self.profile_loader.load_role(
            role_path
        )

        background = None

        if background_path is not None:
            background = (
                self.profile_loader.load_background(
                    background_path
                )
            )

        return self.profile_modifier.apply(
            role=role,
            background=background,
            size=size,
        )
