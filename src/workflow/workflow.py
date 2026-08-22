from __future__ import annotations

from ..agents.committee import EvaluatorAgentCommittee
from ..evaluation.assumption_loader import AssumptionLoader
from ..evaluation.rubric_loader import RubricLoader
from ..evaluation.rubric_prompt import build_rubric_prompt
from ..evaluation.rubric_validator import RubricValidator
from ..llm.client import LLMClient

from .config import TaskTemplateLoader, WorkflowConfig, WorkflowConfigLoader
from .executor import EvaluationExecutor


class EvaluationWorkflow:
    """Orchestrate the complete model evaluation workflow."""

    def __init__(
        self,
        llm_client: LLMClient,
        *,
        seed: int | None = None,
    ) -> None:
        self.llm_client = llm_client
        self.seed = seed

        self.config_loader = WorkflowConfigLoader()
        self.model_loader = AssumptionLoader()
        self.task_template_loader = TaskTemplateLoader(
            self.config_loader.project_root
        )

        self.rubric_loader = RubricLoader()
        self.rubric_validator = RubricValidator()

        self.committee = EvaluatorAgentCommittee(
            llm_client=llm_client,
            seed=seed,
        )

        self.executor = EvaluationExecutor()

    def run(
        self,
        *,
        committee_config: str,
        rubric_name: str,
        model_name: str,
    ):
        """Run the evaluation workflow."""

        # Step 1: Load committee configuration
        config = self.config_loader.load(
            committee_name=committee_config,
            rubric=rubric_name,
            model=model_name,
        )

        # Step 2: Load, validate, and build the rubric prompt
        rubric = self.rubric_loader.load(config.rubric)
        model = self.model_loader.load(config.model)
        task_template = self.task_template_loader.load()

        self.rubric_validator.validate(rubric)

        rubric_prompt = build_rubric_prompt(rubric)

        # Step 3: Build the evaluator committee
        agents = self._build_committee(config)

        context = "\n\n".join(model.get("context", []))
        results = []

        for assumption in model["assumptions"]:
            evaluation_target = (
                f"ID: {assumption['id']}\n"
                f"Name: {assumption['name']}\n"
                f"Description: {assumption['description']}"
            )
            task = task_template.format(
                evaluation_target=evaluation_target,
            )

            results.extend(
                self.executor.run(
                    agents=agents,
                    rubric=rubric_prompt,
                    context=context,
                    task=task,
                )
            )

        # Step 5: Return individual evaluation results
        return results

    def _build_committee(
        self,
        config: WorkflowConfig,
    ):
        """Build evaluator agents according to the workflow configuration."""

        agents = []
        project_root = self.config_loader.project_root

        for member in config.committee:
            role_path = (
                project_root
                / "config"
                / "agents"
                / "roles"
                / f"{member.role}.yaml"
            )

            background_path = None

            if member.background is not None:
                background_path = (
                    project_root
                    / "config"
                    / "agents"
                    / "backgrounds"
                    / f"{member.background}.yaml"
                )

            population = self.committee.create_population(
                role_path=role_path,
                background_path=background_path,
                size=member.count,
                prefix=member.role,
            )

            agents.extend(population)

        return agents
