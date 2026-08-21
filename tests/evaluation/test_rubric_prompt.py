from src.evaluation.rubric_loader import RubricLoader
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

    # Check evaluation types
    assert "### Potential Impact" in rubric_prompt
    assert "### Fidelity" in rubric_prompt

    # Check attributes
    assert "#### Importance" in rubric_prompt
    assert "#### Risk" in rubric_prompt
    assert "#### Usability" in rubric_prompt

    assert "#### Confidence" in rubric_prompt
    assert "#### Evidence" in rubric_prompt
    assert "#### Robustness" in rubric_prompt

    # Check questions
    assert (
        "How important is assumption A for the validity of the model?"
        in rubric_prompt
    )

    assert (
        "How confident are you that assumption A reflects reality?"
        in rubric_prompt
    )

    # Check score descriptions
    assert "1: Not important" in rubric_prompt
    assert "5: Extremely important" in rubric_prompt

    assert "1: Not confident" in rubric_prompt
    assert "5: Extremely confident" in rubric_prompt

    print("\n=== Generated Rubric Prompt ===")
    print(rubric_prompt)