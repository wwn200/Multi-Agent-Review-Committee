import json
from pathlib import Path


class RubricLoader:
    """
    Load standardized evaluation rubrics from JSON files.
    """

    def __init__(self, project_root: Path | None = None):
        if project_root is None:
            project_root = Path(__file__).resolve().parents[2]

        self.project_root = project_root

        self.rubric_dir = (
            self.project_root / "config" / "rubrics"
        )

    def load(self, rubric_name: str) -> dict:
        """
        Load a rubric by its ID/name.

        Example
        -------
        loader.load("project_evaluation")
        """

        rubric_id = self._normalize_name(rubric_name)

        rubric_path = (
            self.rubric_dir / f"{rubric_id}.json"
        )

        if not rubric_path.exists():
            raise FileNotFoundError(
                f"Rubric not found: {rubric_name}"
            )

        with open(
            rubric_path,
            "r",
            encoding="utf-8",
        ) as f:
            rubric = json.load(f)

        self._validate(rubric)

        return rubric

    def list_rubrics(self) -> list[str]:
        """
        Return all available rubric IDs.
        """

        if not self.rubric_dir.exists():
            return []

        return sorted(
            path.stem
            for path in self.rubric_dir.glob("*.json")
        )

    def _validate(self, rubric: dict) -> None:
        """Validate the basic structure of a rubric."""

        required_fields = [
            "rubric_name",
            "version",
            "scale",
            "criteria",
        ]

        for field in required_fields:
            if field not in rubric:
                raise ValueError(
                    f"Invalid rubric: missing '{field}'."
                )

        if not isinstance(
            rubric["criteria"],
            list,
        ):
            raise ValueError(
                "Rubric 'criteria' must be a list."
            )

        if not rubric["criteria"]:
            raise ValueError(
                "Rubric must contain at least one criterion."
            )

    @staticmethod
    def _normalize_name(name: str) -> str:
        """
        Normalize a rubric name to the JSON filename format.
        """

        return (
            name.lower()
            .strip()
            .replace(" ", "_")
            .replace("-", "_")
        )