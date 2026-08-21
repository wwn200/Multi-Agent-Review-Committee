from __future__ import annotations


def build_rubric_prompt(rubric: dict) -> str:
    """Build a prompt section from a validated structured rubric."""

    guidance = rubric.get("general_guidance", [])
    criteria = rubric["criteria"]

    sections: list[str] = []

    sections.append(
        "## Evaluation Rubric"
    )

    if guidance:
        sections.append("### General Guidance")
        sections.extend(
            f"- {item}"
            for item in guidance
        )

    current_type = None

    for criterion in criteria:
        criterion_type = criterion["type"]

        if criterion_type != current_type:
            sections.append(
                f"\n### {criterion_type}"
            )
            current_type = criterion_type

        sections.append(
            f"#### {criterion['attribute']}"
        )

        sections.append(
            f"Question: {criterion['question']}"
        )

        sections.append("Score descriptions:")

        for score, description in criterion["scores"].items():
            sections.append(
                f"- {score}: {description}"
            )

    return "\n".join(sections)