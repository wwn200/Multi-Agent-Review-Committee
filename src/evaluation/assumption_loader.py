import json
from pathlib import Path


class AssumptionLoader:
    """
    Load a standardized assumption set from JSON.
    """

    def __init__(self, project_root: Path | None = None):
        if project_root is None:
            project_root = Path(__file__).resolve().parents[2]

        self.project_root = project_root

        self.assumption_dir = (
            self.project_root
            / "config"
            / "models"
        )

        self.assumption_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def load(
        self,
        model_name: str,
    ) -> dict:
        """
        Load an assumption set by name.

        Example
        -------
        load("test_model")

        loads:

            config/models/test_model.json
        """

        assumption_path = (
            self.assumption_dir
            / f"{model_name}.json"
        )

        if not assumption_path.exists():
            raise FileNotFoundError(
                f"Assumption set not found: "
                f"{model_name}"
            )

        if assumption_path.suffix.lower() != ".json":
            raise ValueError(
                "Assumption file must be a .json file."
            )

        with open(
            assumption_path,
            "r",
            encoding="utf-8",
        ) as f:
            assumption_set = json.load(f)

        self._validate_assumption_set(
            assumption_set,
            model_name,
        )

        return assumption_set

    def list_assumptions(self) -> list[str]:
        """
        Return the names of all available
        assumption sets.
        """

        return sorted(
            path.stem
            for path in self.assumption_dir.glob("*.json")
        )

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
                f"root must be a JSON object."
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
            "description",
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