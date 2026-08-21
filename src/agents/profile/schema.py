# src/agents/profile/schema.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, get_args


DistributionType = Literal[
    "normal",
    "uniform",
    "beta",
    "constant",
]


@dataclass
class DistributionSpec:
    """
    Specification of a probability distribution used to generate
    individual evaluator traits.
    """

    distribution: DistributionType
    mean: float | None = None
    std: float | None = None
    low: float | None = None
    high: float | None = None
    alpha: float | None = None
    beta: float | None = None

    def __post_init__(self) -> None:
        if self.distribution is None:
            raise ValueError("Distribution type is required.")

        if self.distribution not in get_args(DistributionType):
            raise ValueError(
                f"Unsupported distribution type: {self.distribution}"
            )

        if self.distribution == "normal":
            if self.mean is None or self.std is None:
                raise ValueError(
                    "Normal distribution requires mean and std."
                )
            if self.std < 0:
                raise ValueError("Standard deviation cannot be negative.")

        elif self.distribution == "uniform":
            if self.low is None or self.high is None:
                raise ValueError(
                    "Uniform distribution requires low and high."
                )
            if self.low > self.high:
                raise ValueError(
                    "Uniform distribution requires low <= high."
                )

        elif self.distribution == "beta":
            if self.alpha is None or self.beta is None:
                raise ValueError(
                    "Beta distribution requires alpha and beta."
                )
            if self.alpha <= 0 or self.beta <= 0:
                raise ValueError(
                    "Beta distribution parameters must be positive."
                )

        elif self.distribution == "constant":
            if self.mean is None:
                raise ValueError(
                    "Constant distribution requires mean."
                )


@dataclass
class TraitSpec:
    """
    Specification of an evaluator trait.

    The distribution describes how individual-level variation is
    generated within an evaluator population.
    """

    distribution: DistributionSpec

    min_value: float = 0.0
    max_value: float = 1.0

    def __post_init__(self) -> None:
        if self.min_value > self.max_value:
            raise ValueError(
                "min_value must be less than or equal to max_value."
            )


@dataclass
class TraitModifier:
    """
    Background-specific modification applied to a trait distribution.

    For example, an automotive background may increase the expected
    risk sensitivity of a Risk Analyst.
    """

    mean_shift: float = 0.0
    std_multiplier: float = 1.0

    def __post_init__(self) -> None:
        if self.std_multiplier < 0:
            raise ValueError(
                "std_multiplier cannot be negative."
            )


@dataclass
class RoleSpec:
    """
    Defines the characteristics associated with an evaluator role.
    """

    name: str
    description: str = ""

    expertise: dict[str, str] = field(default_factory=dict)

    base_traits: dict[str, TraitSpec] = field(
        default_factory=dict
    )

    default_attention_weights: dict[str, float] = field(
        default_factory=dict
    )

    default_concerns: list[str] = field(
        default_factory=list
    )

    evidence_preference: str | None = None


@dataclass
class BackgroundSpec:
    """
    Defines a contextual background that can modify evaluator
    characteristics.

    Examples include automotive, toy manufacturing, healthcare,
    logistics, etc.
    """

    name: str
    description: str = ""

    traits: dict[str, TraitModifier] = field(
        default_factory=dict
    )

    attention_weights: dict[str, float] = field(
        default_factory=dict
    )

    concerns: list[str] = field(
        default_factory=list
    )

    contextual_information: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class EvaluatorPopulationSpec:
    """
    Defines a population of evaluators sharing a common role and
    background.

    This represents a population-level distribution rather than
    a single evaluator.
    """

    name: str

    role: RoleSpec
    background: BackgroundSpec | None = None

    traits: dict[str, TraitSpec] = field(
        default_factory=dict
    )

    attention_weights: dict[str, float] = field(
        default_factory=dict
    )

    concerns: list[str] = field(
        default_factory=list
    )

    evidence_preference: str | None = None

    size: int = 1

    def __post_init__(self) -> None:
        if self.size < 1:
            raise ValueError("Population size must be at least 1.")


@dataclass
class EvaluatorProfile:
    """
    Concrete profile of an individual evaluator generated from
    an evaluator population specification.
    """

    evaluator_id: str

    role: str
    expertise: dict[str, str]

    background: str | None = None

    traits: dict[str, float] = field(
        default_factory=dict
    )

    attention_weights: dict[str, float] = field(
        default_factory=dict
    )

    concerns: list[str] = field(
        default_factory=list
    )

    evidence_preference: str | None = None

    contextual_information: dict[str, Any] = field(
        default_factory=dict
    )

    seed: int | None = None
