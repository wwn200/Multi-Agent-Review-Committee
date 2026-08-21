from pathlib import Path

import pytest

from src.agents.committee import EvaluatorAgentCommittee
from src.llm.client import LLMClient

from src.evaluation.rubric_loader import RubricLoader
from src.evaluation.rubric_validator import RubricValidator
from src.evaluation.rubric_prompt import build_rubric_prompt


@pytest.mark.api
def test_manufacturing_product_manager_evaluation():
    project_root = Path(__file__).resolve().parents[2]

    role_pm_path = (
        project_root
        / "config"
        / "agents"
        / "roles"
        / "product_manager.yaml"
    )

    role_dm_path = (
            project_root
            / "config"
            / "agents"
            / "roles"
            / "decision_maker.yaml"
        )

    role_rm_path = (
            project_root
            / "config"
            / "agents"
            / "roles"
            / "risk_manager.yaml"
        )

    background_path = (
        project_root
        / "config"
        / "agents"
        / "backgrounds"
        / "manufacturing.yaml"
    )

    # Create the real LLM client
    llm_client = LLMClient()

    # Create the evaluator agent
    committee = EvaluatorAgentCommittee(
        llm_client=llm_client,
        seed=42,
    )

    agent_pm = committee.create_agent(
        role_path=role_pm_path,
        background_path=background_path,
        evaluator_id="product_manager_001",
    )

    agent_dm = committee.create_agent(
            role_path=role_dm_path,
            background_path=background_path,
            evaluator_id="decision_maker_001",
        )

    agent_rm = committee.create_agent(
                role_path=role_rm_path,
                background_path=background_path,
                evaluator_id="risk_manager_001",
            )

    # Load rubric
    rubric_loader = RubricLoader()
    rubric = rubric_loader.load("test_rubric")

    # Validate rubric
    rubric_validator = RubricValidator()
    rubric_validator.validate(rubric)

    # Build rubric prompt
    rubric_prompt = build_rubric_prompt(rubric)

    context = """
The model represents a manufacturing production planning system.
It is used to determine production schedules and allocate products
to production lines.

The model assumes that the production line can be used interchangeably
for all product types. In other words, all product types can be
processed on the same production line without requiring
product-specific equipment, major setup changes, or significant
reconfiguration.

The purpose of the model is to support production planning and
scheduling decisions in a manufacturing environment.
"""

    task = """
Evaluate the following model assumption:

"The equipment failure rate remains stable over the planning horizon."

Assess both the potential impact and fidelity of this assumption.
Consider the assumption from the perspective of a product manager
working in a manufacturing environment.

Provide the scores for Potential Impact and Fidelity, as well as the scores for their respective attributes.

Provide a concise rationale explaining your scores.
"""

    result_pm = agent_pm.evaluate(
        rubric=rubric_prompt,
        context=context,
        task=task,
    )

    result_dm = agent_dm.evaluate(
            rubric=rubric_prompt,
            context=context,
            task=task,
        )

    result_rm = agent_rm.evaluate(
            rubric=rubric_prompt,
            context=context,
            task=task,
        )

    print("\n=== Evaluation Result (Product Manager) ===")
    print(result_pm.response)

    assert result_pm.evaluator_id == "product_manager_001"
    assert result_pm.response

    print("\n=== Evaluation Result (Decision Maker) ===")
    print(result_dm.response)
    
    assert result_dm.evaluator_id == "decision_maker_001"
    assert result_dm.response

    print("\n=== Evaluation Result (Risk Manager) ===")
    print(result_rm.response)
    
    assert result_rm.evaluator_id == "risk_manager_001"
    assert result_rm.response
