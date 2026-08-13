import json
import shutil
from pathlib import Path

import pandas as pd


class RubricImporter:
    """
    Import an evaluation rubric from an XLSX file
    and convert it into the standard JSON representation.
    """

    REQUIRED_COLUMNS = [
        "Criterion",
        "Description",
        "1",
        "2",
        "3",
        "4",
        "5",
    ]

    def __init__(self, project_root: Path | None = None):
        if project_root is None:
            project_root = Path(__file__).resolve().parents[2]

        self.project_root = project_root

        self.rubric_dir = (
            self.project_root / "config" / "rubrics"
        )

        self.source_dir = (
            self.project_root / "data" / "rubric_sources"
        )

        self.rubric_dir.mkdir(parents=True, exist_ok=True)
        self.source_dir.mkdir(parents=True, exist_ok=True)

    def import_xlsx(self, file_path: str | Path) -> Path:
        """
        Import an XLSX rubric and save it as a JSON rubric.

        Parameters
        ----------
        file_path:
            Path to the source XLSX file.

        Returns
        -------
        Path
            Path to the generated JSON rubric.
        """

        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"Rubric file not found: {file_path}"
            )

        if file_path.suffix.lower() != ".xlsx":
            raise ValueError(
                "Rubric source file must be an .xlsx file."
            )

        # Read Excel
        df = pd.read_excel(file_path)

        # Validate columns
        self._validate_columns(df)

        # Build rubric
        rubric = self._build_rubric(df)

        # Validate rubric content
        self._validate_rubric(rubric)

        # Save original XLSX
        source_path = self.source_dir / file_path.name
        shutil.copy2(file_path, source_path)

        # Generate JSON filename
        rubric_name = rubric["rubric_name"]
        rubric_id = self._make_rubric_id(rubric_name)

        output_path = self.rubric_dir / f"{rubric_id}.json"

        # Save JSON
        with open(
            output_path,
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                rubric,
                f,
                indent=4,
                ensure_ascii=False,
            )

        print(f"Rubric imported successfully:")
        print(f"  Source: {source_path}")
        print(f"  Rubric: {output_path}")

        return output_path

    def _validate_columns(self, df: pd.DataFrame) -> None:
        """Check whether the Excel file contains all required columns."""

        missing_columns = [
            column
            for column in self.REQUIRED_COLUMNS
            if column not in df.columns
        ]

        if missing_columns:
            raise ValueError(
                "Missing required columns: "
                + ", ".join(missing_columns)
            )

    def _build_rubric(self, df: pd.DataFrame) -> dict:
        """Convert the DataFrame into the standard rubric structure."""

        # Use filename as the default rubric name
        rubric_name = "Imported Rubric"

        criteria = []

        for _, row in df.iterrows():

            criterion_name = str(
                row["Criterion"]
            ).strip()

            description = str(
                row["Description"]
            ).strip()

            scores = {}

            for score in range(1, 6):
                value = row[str(score)]

                if pd.isna(value):
                    raise ValueError(
                        f"Missing score description for "
                        f"criterion '{criterion_name}', "
                        f"score {score}."
                    )

                scores[str(score)] = str(value).strip()

            criteria.append(
                {
                    "name": criterion_name,
                    "description": description,
                    "scores": scores,
                }
            )

        return {
            "rubric_name": rubric_name,
            "version": "1.0",
            "scale": {
                "min": 1,
                "max": 5,
            },
            "criteria": criteria,
        }

    def _validate_rubric(self, rubric: dict) -> None:
        """Validate the generated rubric."""

        if not rubric["criteria"]:
            raise ValueError(
                "Rubric must contain at least one criterion."
            )

        criterion_names = set()

        for criterion in rubric["criteria"]:

            name = criterion["name"]

            if not name:
                raise ValueError(
                    "Criterion name cannot be empty."
                )

            if name in criterion_names:
                raise ValueError(
                    f"Duplicate criterion: {name}"
                )

            criterion_names.add(name)

    @staticmethod
    def _make_rubric_id(name: str) -> str:
        """Convert a rubric name into a simple file-safe ID."""

        return (
            name.lower()
            .strip()
            .replace(" ", "_")
            .replace("-", "_")
        )