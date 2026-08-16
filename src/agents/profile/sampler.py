# src/agents/profile/sampler.py

from __future__ import annotations

import random

from .schema import (
    DistributionSpec,
    EvaluatorPopulationSpec,
    EvaluatorProfile,
)


class EvaluatorSampler:
    """
    Generate concrete evaluator profiles from a population specification.

    The sampler is responsible for individual-level variation.
    It does not load configuration files or build prompts.
    """

    def __init__(
        self,
        seed: int | None = None,
    ) -> None:
        self._rng = random.Random(seed)
        self._seed = seed

    def sample(
        self,
        population: EvaluatorPopulationSpec,
        evaluator_id: str,
    ) -> EvaluatorProfile:
        """
        Generate one concrete evaluator from a population.
        """

        traits = {
            name: self._sample_trait(trait)
            for name, trait in population.traits.items()
        }

        attention_weights = self._sample_attention_weights(
            population.attention_weights
        )

        return EvaluatorProfile(
            evaluator_id=evaluator_id,
            role=population.role.name,
            expertise=population.role.expertise.copy(),
            background=(
                population.background.name
                if population.background is not None
                else None
            ),
            traits=traits,
            attention_weights=attention_weights,
            concerns=list(population.concerns),
            evidence_preference=population.evidence_preference,
            contextual_information=(
                population.background.contextual_information.copy()
                if population.background is not None
                else {}
            ),
            seed=self._seed,
        )

    def sample_population(
        self,
        population: EvaluatorPopulationSpec,
        *,
        prefix: str = "expert",
    ) -> list[EvaluatorProfile]:
        """
        Generate a complete evaluator population.
        """

        return [
            self.sample(
                population,
                evaluator_id=f"{prefix}_{index:03d}",
            )
            for index in range(1, population.size + 1)
        ]

    def _sample_trait(
        self,
        trait,
    ) -> float:
        """
        Sample a single trait from its probability distribution.
        """

        value = self._sample_distribution(
            trait.distribution
        )

        return self._clip(
            value,
            trait.min_value,
            trait.max_value,
        )

    def _sample_distribution(
        self,
        distribution: DistributionSpec,
    ) -> float:
        """Sample a value from a specified distribution."""

        distribution_type = distribution.distribution

        if distribution_type == "normal":
            assert distribution.mean is not None
            assert distribution.std is not None

            return self._rng.gauss(
                distribution.mean,
                distribution.std,
            )

        if distribution_type == "uniform":
            assert distribution.low is not None
            assert distribution.high is not None

            return self._rng.uniform(
                distribution.low,
                distribution.high,
            )

        if distribution_type == "beta":
            assert distribution.alpha is not None
            assert distribution.beta is not None

            return self._rng.betavariate(
                distribution.alpha,
                distribution.beta,
            )

        if distribution_type == "constant":
            assert distribution.mean is not None

            return distribution.mean

        raise ValueError(
            f"Unsupported distribution: {distribution_type}"
        )

    def _sample_attention_weights(
        self,
        weights: dict[str, float],
    ) -> dict[str, float]:
        """
        Generate individual-level attention weights.

        The current implementation applies small random perturbations
        to population-level attention weights and then normalizes them.
        """

        if not weights:
            return {}

        perturbed: dict[str, float] = {}

        for dimension, weight in weights.items():
            variation = self._rng.gauss(
                0.0,
                0.05,
            )

            perturbed[dimension] = max(
                0.0,
                weight + variation,
            )

        return self._normalize_weights(perturbed)

    @staticmethod
    def _normalize_weights(
        weights: dict[str, float],
    ) -> dict[str, float]:
        """Normalize weights so that they sum to 1."""

        total = sum(weights.values())

        if total <= 0:
            equal_weight = 1.0 / len(weights)

            return {
                dimension: equal_weight
                for dimension in weights
            }

        return {
            dimension: weight / total
            for dimension, weight in weights.items()
        }

    @staticmethod
    def _clip(
        value: float,
        minimum: float,
        maximum: float,
    ) -> float:
        """Restrict a sampled value to a specified range."""

        return max(
            minimum,
            min(value, maximum),
        )