# src/agents/profile/modifiers.py

from __future__ import annotations

from copy import deepcopy

from .schema import (
    BackgroundSpec,
    EvaluatorPopulationSpec,
    RoleSpec,
    TraitModifier,
    TraitSpec,
)


class ProfileModifier:
    """
    Combine a role specification with a background specification.

    This class applies background-specific modifications to the
    characteristics of an evaluator population.

    It does not perform individual-level random sampling.
    """

    def apply(
        self,
        role: RoleSpec,
        background: BackgroundSpec | None = None,
        *,
        name: str | None = None,
        size: int = 1,
    ) -> EvaluatorPopulationSpec:
        """
        Create an evaluator population specification from a role
        and an optional background.
        """

        if background is None:
            return EvaluatorPopulationSpec(
                name=name or role.name,
                role=role,
                background=None,
                traits=deepcopy(role.base_traits),
                attention_weights=deepcopy(
                    role.default_attention_weights
                ),
                concerns=list(role.default_concerns),
                evidence_preference=role.evidence_preference,
                size=size,
            )

        traits = self._merge_traits(
            role.base_traits,
            background.traits,
        )

        attention_weights = self._merge_attention_weights(
            role.default_attention_weights,
            background.attention_weights,
        )

        concerns = self._merge_concerns(
            role.default_concerns,
            background.concerns,
        )

        evidence_preference = (
            role.evidence_preference
        )

        population_name = (
            name
            or f"{background.name} {role.name}"
        )

        return EvaluatorPopulationSpec(
            name=population_name,
            role=role,
            background=background,
            traits=traits,
            attention_weights=attention_weights,
            concerns=concerns,
            evidence_preference=evidence_preference,
            size=size,
        )

    @staticmethod
    def _merge_traits(
        base_traits: dict[str, TraitSpec],
        modifiers: dict[str, TraitModifier],
    ) -> dict[str, TraitSpec]:
        """
        Apply background modifiers to role-level trait distributions.
        """

        traits = deepcopy(base_traits)

        for trait_name, modifier in modifiers.items():
            if trait_name not in traits:
                continue

            trait = traits[trait_name]

            distribution = trait.distribution

            if distribution.mean is not None:
                distribution.mean += modifier.mean_shift

            if distribution.std is not None:
                distribution.std *= modifier.std_multiplier

        return traits

    @staticmethod
    def _merge_attention_weights(
        base_weights: dict[str, float],
        background_weights: dict[str, float],
    ) -> dict[str, float]:
        """
        Combine role-level and background-level attention weights.

        Background values currently act as additive adjustments.
        Final normalization is deferred to the sampling stage.
        """

        weights = dict(base_weights)

        for dimension, value in background_weights.items():
            weights[dimension] = (
                weights.get(dimension, 0.0)
                + value
            )

        return weights

    @staticmethod
    def _merge_concerns(
        base_concerns: list[str],
        background_concerns: list[str],
    ) -> list[str]:
        """
        Combine role-level and background-level concerns
        while preserving order and removing duplicates.
        """

        concerns: list[str] = []

        for concern in (
            base_concerns + background_concerns
        ):
            if concern not in concerns:
                concerns.append(concern)

        return concerns