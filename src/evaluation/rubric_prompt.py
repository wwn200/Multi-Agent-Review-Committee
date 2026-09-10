from __future__ import annotations

import re


def _field_name(value: str) -> str:
    """Convert rubric labels into stable JSON field names."""

    return re.sub(
        r"[^a-z0-9]+",
        "_",
        value.strip().lower(),
    ).strip("_")


def build_output_requirements(rubric: dict) -> str:
    """Build the output schema from the rubric's types and attributes."""

    grouped: dict[str, list[str]] = {}
    for criterion in rubric["criteria"]:
        criterion_type = _field_name(criterion["type"])
        attribute = _field_name(criterion["attribute"])
        grouped.setdefault(criterion_type, [])
        if attribute not in grouped[criterion_type]:
            grouped[criterion_type].append(attribute)

    lines = ["{"]
    for criterion_type, attributes in grouped.items():
        lines.append(f'    "{criterion_type}": {{')
        lines.append('        "score": <any number between 1 to 5, rounded to two decimal places>,')
        for attribute_index, attribute in enumerate(attributes):
            comma = "," if attribute_index < len(attributes) - 1 else ""
            lines.append(
                f'        "{attribute}": <integer from 1 to 5>{comma}'
            )
        lines.append("    },")
    lines.append('    "rationale": "<explanation supporting your evaluation>"')
    lines.append("}")

    return "\n".join(lines)

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
