from __future__ import annotations

from src.evaluation.assumption_loader import AssumptionLoader
from src.workflow.config import WorkflowConfigLoader
from src.workflow.workflow import EvaluationWorkflow


class FakeLLMClient:
    """Capture evaluator requests without making an API call."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        self.calls.append((system_prompt, user_prompt))
        return "evaluation response"


def test_workflow_evaluates_each_assumption_with_each_committee_member():
    client = FakeLLMClient()
    workflow = EvaluationWorkflow(client, seed=42)

    results = workflow.run(
        committee_config="test_committee",
        model_name="cutting_stock_model",
        rubric_name="test_rubric",
    )

    committee_config = WorkflowConfigLoader().load(
        committee_name="test_committee",
        model="cutting_stock_model",
        rubric="test_rubric",
    )
    model = AssumptionLoader().load("cutting_stock_model")
    committee_size = sum(
        member.count for member in committee_config.committee
    )

    expected_evaluations = len(model["assumptions"]) * committee_size
    assert len(results) == expected_evaluations
    assert len(client.calls) == expected_evaluations

    first_system_prompt, first_user_prompt = client.calls[0]
    assert "test_rubric" not in first_system_prompt
    assert model["context"][0] in first_user_prompt
    assert "ID: S1" in first_user_prompt
    assert "Name: Production Time Insensitivity" in first_user_prompt
    assert "Description: Products are assumed" in first_user_prompt

    last_user_prompt = client.calls[-1][1]
    assert "ID: C2" in last_user_prompt
    assert "Name: Restricted Search Space" in last_user_prompt
    assert all(result.response == "evaluation response" for result in results)

    print("\n=== Assumption S1 First Agent Evaluation Result ===")
    print(results[0].response)

    print("\n=== Assumption C2 Last Agent Evaluation Result ===")
    print(results[-1].response)
