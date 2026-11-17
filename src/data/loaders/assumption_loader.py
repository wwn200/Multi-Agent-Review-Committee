import json
from pathlib import Path

import yaml

from ...construction.optimization import load_yaml, optimize_assumption_selection


class AssumptionLoader:
    """
    Load a standardized assumption set from YAML files.
    """

    def __init__(
        self,
        project_root: Path | None = None,
        optimization_config_path: Path | None = None,
    ):
        if project_root is None:
            project_root = Path(__file__).resolve().parents[3]

        self.project_root = project_root

        self.assumption_dir = (
            self.project_root
            / "config"
            / "models"
        )
        self.optimization_config_path = optimization_config_path or (
            self.project_root / "config" / "optimization.yaml"
        )

        self.assumption_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def load(
        self,
        model_name: str,
        *,
        force_optimization: bool = False,
    ) -> dict:
        """
        Load an assumption set by name.

        Example
        -------
        load("test_model")

        loads:

            config/models/test_model.yaml
        """

        assumption_path = self._find_model_path(model_name)

        if assumption_path is None:
            raise FileNotFoundError(
                f"Assumption set not found: "
                f"{model_name}"
            )

        with open(
            assumption_path,
            "r",
            encoding="utf-8",
        ) as f:
            if assumption_path.suffix.lower() in {".yaml", ".yml"}:
                assumption_set = yaml.safe_load(f)
            else:
                assumption_set = json.load(f)

        self._validate_assumption_set(
            assumption_set,
            model_name,
        )

        if force_optimization or any(
            assumption["selected"] == "N/A"
            for assumption in assumption_set["assumptions"]
        ):
            self._resolve_selection(
                assumption_set=assumption_set,
                assumption_path=assumption_path,
                model_name=model_name,
            )
            self._validate_assumption_set(
                assumption_set,
                model_name,
            )

        return assumption_set

    def _resolve_selection(
        self,
        assumption_set: dict,
        assumption_path: Path,
        model_name: str,
    ) -> None:
        """Optimize unresolved selections and persist the selected flags."""
        if assumption_path.suffix.lower() not in {".yaml", ".yml"}:
            raise ValueError(
                f"Cannot persist optimized selections for non-YAML model "
                f"'{model_name}'."
            )
        if not self.optimization_config_path.exists():
            raise FileNotFoundError(
                f"Optimization config not found: {self.optimization_config_path}"
            )

        optimization_config = load_yaml(self.optimization_config_path)
        selections = optimize_assumption_selection(
            model_data=assumption_set,
            optimization_config=optimization_config,
        )

        for assumption, selected in zip(
            assumption_set["assumptions"], selections
        ):
            assumption["selected"] = selected

        with open(assumption_path, "w", encoding="utf-8") as file:
            yaml.safe_dump(
                assumption_set,
                file,
                sort_keys=False,
                allow_unicode=True,
            )

    def list_assumptions(self) -> list[str]:
        """
        Return the names of all available
        assumption sets.
        """

        return sorted(
            {path.stem for path in self.assumption_dir.glob("*.json")}
            | {path.stem for path in self.assumption_dir.glob("*.yaml")}
            | {path.stem for path in self.assumption_dir.glob("*.yml")}
        )

    def _find_model_path(self, model_name: str) -> Path | None:
        """Find a model configuration in the supported config formats."""
        for suffix in (".yaml", ".yml", ".json"):
            path = self.assumption_dir / f"{model_name}{suffix}"
            if path.exists():
                return path

        return None

    def _validate_assumption_set(
        self,
        assumption_set: dict,
        assumption_name: str,
    ) -> None:
        """
        Validate the structure of a loaded
        assumption set.
        """

        if not isinstance(
            assumption_set,
            dict,
        ):
            raise ValueError(
                f"Invalid assumption set "
                f"'{assumption_name}': "
                f"root must be a configuration object."
            )

        required_fields = [
            "assumption_set_name",
            "version",
            "assumptions",
        ]

        for field in required_fields:
            if field not in assumption_set:
                raise ValueError(
                    f"Invalid assumption set "
                    f"'{assumption_name}': "
                    f"missing field '{field}'."
                )

        assumptions = assumption_set[
            "assumptions"
        ]

        context = assumption_set.get("context", [])
        if not isinstance(context, list) or any(
            not isinstance(item, str) or not item.strip()
            for item in context
        ):
            raise ValueError(
                f"Invalid assumption set '{assumption_name}': "
                "'context' must be a list of non-empty strings."
            )

        if not isinstance(
            assumptions,
            list,
        ):
            raise ValueError(
                f"Invalid assumption set "
                f"'{assumption_name}': "
                "'assumptions' must be a list."
            )

        if not assumptions:
            raise ValueError(
                f"Assumption set "
                f"'{assumption_name}' "
                "contains no assumptions."
            )

        required_assumption_fields = [
            "id",
            "classification",
            "name",
            "importance",
            "description",
            "selected"
        ]

        assumption_ids = set()

        for assumption in assumptions:

            if not isinstance(
                assumption,
                dict,
            ):
                raise ValueError(
                    f"Invalid assumption entry "
                    f"in '{assumption_name}'."
                )

            for field in required_assumption_fields:
                if field not in assumption:
                    raise ValueError(
                        f"Invalid assumption in "
                        f"'{assumption_name}': "
                        f"missing field '{field}'."
                    )

            assumption_id = assumption["id"]

            if not assumption_id:
                raise ValueError(
                    "Assumption ID cannot be empty."
                )

            if assumption_id in assumption_ids:
                raise ValueError(
                    f"Duplicate assumption ID: "
                    f"{assumption_id}"
                )

            assumption_ids.add(
                assumption_id
            )

            importance = assumption["importance"]
            if (
                isinstance(importance, bool)
                or not isinstance(importance, (int, float))
                or not 0 <= importance <= 1
            ):
                raise ValueError(
                    f"Invalid importance for assumption '{assumption_id}': "
                    "must be a number in [0, 1]."
                )

            if assumption["selected"] not in (True, False, "N/A"):
                raise ValueError(
                    f"Invalid selected value for assumption '{assumption_id}'."
                )

        dependencies = assumption_set.get("dependencies", [])
        if not isinstance(dependencies, list):
            raise ValueError(
                f"Invalid assumption set '{assumption_name}': "
                "'dependencies' must be a list."
            )

        for dependency in dependencies:
            if not isinstance(dependency, dict):
                raise ValueError(
                    f"Invalid dependency entry in '{assumption_name}'."
                )
            for field in ("source", "target", "dependency_strength"):
                if field not in dependency:
                    raise ValueError(
                        f"Invalid dependency in '{assumption_name}': "
                        f"missing field '{field}'."
                    )
            if (
                dependency["source"] not in assumption_ids
                or dependency["target"] not in assumption_ids
            ):
                raise ValueError(
                    f"Invalid dependency in '{assumption_name}': "
                    "source and target must reference assumption IDs."
                )
            strength = dependency["dependency_strength"]
            if (
                isinstance(strength, bool)
                or not isinstance(strength, (int, float))
                or not 0 <= strength <= 1
            ):
                raise ValueError(
                    f"Invalid dependency strength in '{assumption_name}': "
                    "must be a number in [0, 1]."
                )
