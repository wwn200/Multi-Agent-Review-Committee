from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class CommitteeMemberConfig:
    """Configuration for one type of evaluator in the committee."""

    role: str
    background: str | None
    count: int


@dataclass(frozen=True)
class WorkflowConfig:
    """Configuration for an evaluation workflow."""

    committee_name: str
    rubric: str
    model: str
    committee: list[CommitteeMemberConfig]


class WorkflowConfigLoader:
    """Load evaluation workflow configurations from YAML files."""

    def __init__(self, project_root: Path | None = None):
        if project_root is None:
            project_root = Path(__file__).resolve().parents[2]

        self.project_root = project_root

        self.config_dir = (
            self.project_root / "config" / "committee"
        )

    def load(
        self,
        committee_name: str,
        rubric: str,
        model: str,
    ) -> WorkflowConfig:
        """Load a committee configuration by name."""

        committee_id = self._normalize_name(committee_name)

        config_path = (
            self.config_dir / f"{committee_id}.yaml"
        )

        if not config_path.exists():
            raise FileNotFoundError(
                f"Committee config not found: {committee_name}"
            )

        with open(
            config_path,
            "r",
            encoding="utf-8",
        ) as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError(
                "Workflow config must be a YAML object."
            )

        return self._parse(
            data=data,
            rubric=rubric,
            model=model,
        )

    @staticmethod
    def _parse(
        data: dict,
        rubric: str,
        model: str,
    ) -> WorkflowConfig:
        """Parse raw YAML data into a WorkflowConfig."""

        committee_data = data.get("committee")

        if not isinstance(committee_data, list):
            raise ValueError(
                "Workflow config 'committee' must be a list."
            )

        committee = []

        for index, item in enumerate(committee_data, start=1):
            if not isinstance(item, dict):
                raise ValueError(
                    f"Workflow committee member {index} must be a YAML object."
                )

            role = item.get("role")
            count = item.get("count")

            if not isinstance(role, str) or not role.strip():
                raise ValueError(
                    f"Workflow committee member {index} must define a role."
                )

            if isinstance(count, bool) or not isinstance(count, int) or count < 1:
                raise ValueError(
                    f"Workflow committee member {index} count must be a positive integer."
                )

            background = item.get("background")
            if background is not None and (
                not isinstance(background, str) or not background.strip()
            ):
                raise ValueError(
                    f"Workflow committee member {index} background must be a non-empty string."
                )

            committee.append(
                CommitteeMemberConfig(
                    role=role.strip(),
                    background=background.strip() if background else None,
                    count=count,
                )
            )

        return WorkflowConfig(
            committee_name=data["committee_name"],
            rubric=rubric,
            model=model,
            committee=committee,
        )

    @staticmethod
    def _normalize_name(name: str) -> str:
        """Normalize a workflow config name to the YAML filename format."""

        return (
            name.lower()
            .strip()
            .replace(" ", "_")
            .replace("-", "_")
        )


class TaskTemplateLoader:
    """Load the fixed evaluation task template from YAML."""

    def __init__(self, project_root: Path | None = None):
        if project_root is None:
            project_root = Path(__file__).resolve().parents[2]

        self.template_path = project_root / "config" / "task_template.yaml"

    def load(self) -> str:
        if not self.template_path.exists():
            raise FileNotFoundError(
                f"Task template not found: {self.template_path}"
            )

        with self.template_path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        if not isinstance(data, dict) or not isinstance(data.get("template"), str):
            raise ValueError(
                "Task template configuration must define a 'template' string."
            )

        template = data["template"].strip()
        if "{evaluation_target}" not in template:
            raise ValueError(
                "Task template must contain '{evaluation_target}'."
            )

        return template
