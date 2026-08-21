from pathlib import Path
from unittest.mock import MagicMock

from src.agents.committee import EvaluatorAgentCommittee
from src.llm.client import LLMClient


def test_create_manufacturing_product_manager_prompt():
    """Test creating a manufacturing-background product manager
    and generating its system prompt.
    """

    project_root = Path(__file__).resolve().parents[2]

    role_path = project_root / "config" / "agents" / "roles" / "product_manager.yaml"
    background_path = (
        project_root / "config" / "agents" / "backgrounds" / "manufacturing.yaml"
    )

    # We only test agent/profile/prompt generation here.
    # No actual LLM call is needed.
    llm_client = MagicMock(spec=LLMClient)
    #llm_client = LLMClient()

    committee = EvaluatorAgentCommittee(
        llm_client=llm_client,
        seed=42,
    )

    # Create one evaluator agent
    agent = committee.create_agent(
        role_path=role_path,
        background_path=background_path,
        evaluator_id="product_manager_001",
    )

    # A simple rubric for testing prompt generation
    rubric = """
Evaluate the assumption based on:
1. Potential Impact: How important is this assumption to the validity
   of the model?
2. Fidelity: How realistically does the assumption represent the
   real-world system?
"""

    # Generate the system prompt
    system_prompt = agent.prepare_system_prompt(rubric)

    # Basic checks
    assert agent.profile.evaluator_id == "product_manager_001"
    assert agent.profile.role == "product_manager"
    assert agent.profile.background == "manufacturing"

    assert "product_manager" in system_prompt
    assert "manufacturing" in system_prompt

    # Check that role expertise is included
    assert "product_strategy: advanced" in system_prompt
    assert "operational_requirements: advanced" in system_prompt

    # Check that manufacturing-specific information is included
    assert "production planning" in system_prompt
    assert "machine capacity" in system_prompt
    assert "material waste" in system_prompt

    # Check that evaluation rubric is included
    assert "Potential Impact" in system_prompt
    assert "Fidelity" in system_prompt

    print("\n=== Evaluator Profile ===")
    print(agent.profile)

    print("\n=== Generated System Prompt ===")
    print(system_prompt)