from __future__ import annotations

from typing import Any

from agents.profile.schema import EvaluatorProfile

from .sections import (
    BackgroundSection,
    ConcernsSection,
    ContextSection,
    EvaluationBehaviorSection,
    EvaluationPerspectiveSection,
    ExpertiseSection,
    IdentitySection,
    OutputRequirementsSection,
    PromptSection,
    RubricSection,
)
from .templates import (
    BACKGROUND_TEMPLATE,
    CONCERNS_TEMPLATE,
    CONTEXT_TEMPLATE,
    EVALUATION_BEHAVIOR_TEMPLATE,
    EVALUATION_PERSPECTIVE_TEMPLATE,
    EVALUATOR_SYSTEM_PROMPT_TEMPLATE,
    EXPERTISE_TEMPLATE,
    IDENTITY_TEMPLATE,
    OUTPUT_REQUIREMENTS_TEMPLATE,
    RUBRIC_TEMPLATE,
)


class PromptBuilder:
    """
    Build prompts for evaluator agents.

    The builder combines an evaluator profile, rubric, and
    evaluation context into a final system prompt.
    """

    def build_evaluator_prompt(
        self,
        profile: EvaluatorProfile,
        rubric: str,
        context: str,
    ) -> str:
        """
        Build the complete system prompt for an evaluator.
        """

        sections = self._build_sections(
            profile=profile,
            rubric=rubric,
            context=context,
        )

        sections.sort(key=lambda section: section.order)

        return self._assemble_prompt(sections)

    def build_system_prompt(
        self,
        profile: EvaluatorProfile,
        rubric: str,
    ) -> str:
        """
        Build the system prompt for an evaluator.

        The system prompt defines who the evaluator is,
        how the evaluator tends to reason, and which
        evaluation rubric should be followed.
        """

        sections = self._build_system_sections(
            profile=profile,
            rubric=rubric,
        )

        sections.sort(
            key=lambda section: section.order
        )

        return self._assemble_system_prompt(
            sections
        )

    def build_user_prompt(
        self,
        context: str,
        task: str,
    ) -> str:
        """
        Build the user prompt for a specific evaluation task.

        The user prompt contains the current evaluation
        context, assumption, and task.
        """

        return CONTEXT_TEMPLATE.format(
            context=context
        ) + "\n\n" + (
            "## Evaluation Task\n\n"
            f"{task}"
        )

    def _build_system_sections(
        self,
        profile: EvaluatorProfile,
        rubric: str,
    ) -> list[PromptSection]:
        """
        Build all sections that belong to the system prompt.
        """

        return [
            self._build_identity_section(profile),
            self._build_background_section(profile),
            self._build_expertise_section(profile),
            self._build_perspective_section(profile),
            self._build_behavior_section(profile),
            self._build_concerns_section(profile),
            self._build_rubric_section(rubric),
            self._build_output_requirements_section(),
        ]

    def _build_sections(
        self,
        profile: EvaluatorProfile,
        rubric: str,
        context: str,
    ) -> list[PromptSection]:
        """Build all prompt sections from the evaluation inputs."""

        return [
            self._build_identity_section(profile),
            self._build_background_section(profile),
            self._build_expertise_section(profile),
            self._build_perspective_section(profile),
            self._build_behavior_section(profile),
            self._build_concerns_section(profile),
            self._build_rubric_section(rubric),
            self._build_context_section(context),
            self._build_output_requirements_section(),
        ]

    @staticmethod
    def _build_identity_section(
        profile: EvaluatorProfile,
    ) -> IdentitySection:
        content = IDENTITY_TEMPLATE.format(
            role=profile.role,
        )

        return IdentitySection(
            name="Identity",
            content=content,
            order=1,
        )

    @staticmethod
    def _build_background_section(
        profile: EvaluatorProfile,
    ) -> BackgroundSection:
        if profile.background:
            background = profile.background
        else:
            background = "No specific organizational or industry background."

        content = BACKGROUND_TEMPLATE.format(
            background=background,
        )

        return BackgroundSection(
            name="Background",
            content=content,
            order=2,
        )

    @staticmethod
    def _build_expertise_section(
        profile: EvaluatorProfile,
    ) -> ExpertiseSection:
        expertise = "\n".join(
            f"- {name}: {level}"
            for name, level in profile.expertise.items()
        )

        if not expertise:
            expertise = "- No specific expertise information provided."

        content = EXPERTISE_TEMPLATE.format(
            expertise=expertise,
        )

        return ExpertiseSection(
            name="Expertise",
            content=content,
            order=3,
        )

    @staticmethod
    def _build_perspective_section(
        profile: EvaluatorProfile,
    ) -> EvaluationPerspectiveSection:
        attention = "\n".join(
            f"- {dimension}: {weight:.3f}"
            for dimension, weight in (
                profile.attention_weights.items()
            )
        )

        if not attention:
            attention = "- No specific evaluation focus provided."

        content = EVALUATION_PERSPECTIVE_TEMPLATE.format(
            attention=attention,
        )

        return EvaluationPerspectiveSection(
            name="Evaluation Perspective",
            content=content,
            order=4,
        )

    @staticmethod
    def _build_behavior_section(
        profile: EvaluatorProfile,
    ) -> EvaluationBehaviorSection:
        behavior = PromptBuilder._format_traits(
            profile.traits
        )

        if profile.evidence_preference:
            behavior += (
                f"\n- Evidence preference: "
                f"{profile.evidence_preference}"
            )

        if not behavior:
            behavior = "- No specific evaluation behavior provided."

        content = EVALUATION_BEHAVIOR_TEMPLATE.format(
            behavior=behavior,
        )

        return EvaluationBehaviorSection(
            name="Evaluation Behavior",
            content=content,
            order=5,
        )

    @staticmethod
    def _build_concerns_section(
        profile: EvaluatorProfile,
    ) -> ConcernsSection:
        concerns = "\n".join(
            f"- {concern}"
            for concern in profile.concerns
        )

        if not concerns:
            concerns = "- No specific concerns provided."

        content = CONCERNS_TEMPLATE.format(
            concerns=concerns,
        )

        return ConcernsSection(
            name="Concerns",
            content=content,
            order=6,
        )

    @staticmethod
    def _build_rubric_section(
        rubric: str,
    ) -> RubricSection:
        content = RUBRIC_TEMPLATE.format(
            rubric=rubric,
        )

        return RubricSection(
            name="Evaluation Rubric",
            content=content,
            order=7,
        )

    @staticmethod
    def _build_context_section(
        context: str,
    ) -> ContextSection:
        content = CONTEXT_TEMPLATE.format(
            context=context,
        )

        return ContextSection(
            name="Evaluation Context",
            content=content,
            order=8,
        )

    @staticmethod
    def _build_output_requirements_section(
    ) -> OutputRequirementsSection:
        content = OUTPUT_REQUIREMENTS_TEMPLATE

        return OutputRequirementsSection(
            name="Output Requirements",
            content=content,
            order=9,
        )

    @staticmethod
    def _assemble_prompt(
        sections: list[PromptSection],
    ) -> str:
        """
        Assemble prompt sections according to their order.
        """

        section_map = {
            "Identity": "",
            "Background": "",
            "Expertise": "",
            "Evaluation Perspective": "",
            "Evaluation Behavior": "",
            "Concerns": "",
            "Evaluation Rubric": "",
            "Evaluation Context": "",
            "Output Requirements": "",
        }

        for section in sections:
            if section.name in section_map:
                section_map[section.name] = section.content

        return EVALUATOR_SYSTEM_PROMPT_TEMPLATE.format(
            identity=section_map["Identity"],
            background=section_map["Background"],
            expertise=section_map["Expertise"],
            evaluation_perspective=section_map[
                "Evaluation Perspective"
            ],
            evaluation_behavior=section_map[
                "Evaluation Behavior"
            ],
            concerns=section_map["Concerns"],
            rubric=section_map["Evaluation Rubric"],
            context=section_map["Evaluation Context"],
            output_requirements=section_map[
                "Output Requirements"
            ],
        ).strip()

    @staticmethod
    def _assemble_system_prompt(
        sections: list[PromptSection],
    ) -> str:
        """
        Assemble system prompt sections in order.
        """

        return "\n\n".join(
            section.content
            for section in sections
        ).strip()

    @staticmethod
    def _format_traits(
        traits: dict[str, float],
    ) -> str:
        """
        Convert numerical evaluator traits into a readable
        representation for the prompt.
        """

        return "\n".join(
            f"- {name}: {value:.3f}"
            for name, value in traits.items()
        )