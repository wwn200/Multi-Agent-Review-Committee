from src.data.loaders.rubric_loader import RubricLoader
from src.evaluation.rubric_validator import RubricValidator
from src.evaluation.rubric_prompt import build_rubric_prompt


def test_build_rubric_prompt():
    """Test building a prompt from a structured rubric."""

    # Load rubric
    loader = RubricLoader()
    rubric = loader.load("test_rubric")

    # Validate rubric
    validator = RubricValidator()
    validator.validate(rubric)

    # Build rubric prompt
    rubric_prompt = build_rubric_prompt(rubric)

    # Basic checks
    assert rubric_prompt
    assert "## Evaluation Rubric" in rubric_prompt
    assert "### General Guidance" in rubric_prompt

    for criterion in rubric["criteria"]:
        assert f"### {criterion['type']}" in rubric_prompt
        assert f"#### {criterion['attribute']}" in rubric_prompt
        assert f"Question: {criterion['question']}" in rubric_prompt
        for score, description in criterion["scores"].items():
            assert f"- {score}: {description}" in rubric_prompt

    print("\n=== Generated Rubric Prompt ===")
    print(rubric_prompt)
