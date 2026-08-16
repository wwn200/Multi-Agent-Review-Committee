# src/prompts/sections.py

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PromptSection:
    """
    A single section of an evaluation prompt.
    """

    name: str
    content: str
    order: int


@dataclass
class IdentitySection(PromptSection):
    """
    Describes who the evaluator is.
    """

    pass


@dataclass
class ExpertiseSection(PromptSection):
    """
    Describes the evaluator's areas and levels of expertise.
    """

    pass


@dataclass
class BackgroundSection(PromptSection):
    """
    Describes the evaluator's organizational or industry background.
    """

    pass


@dataclass
class EvaluationPerspectiveSection(PromptSection):
    """
    Describes what the evaluator tends to focus on.
    """

    pass


@dataclass
class EvaluationBehaviorSection(PromptSection):
    """
    Describes how the evaluator tends to reason and make judgments.
    """

    pass


@dataclass
class ConcernsSection(PromptSection):
    """
    Describes issues and risks the evaluator is particularly
    attentive to.
    """

    pass


@dataclass
class RubricSection(PromptSection):
    """
    Contains the evaluation rubric or evaluation criteria.
    """

    pass


@dataclass
class ContextSection(PromptSection):
    """
    Provides the model, assumption, or other evaluation context.
    """

    pass


@dataclass
class OutputRequirementsSection(PromptSection):
    """
    Specifies the required structure and format of the evaluation output.
    """

    pass