import json
import shutil
from pathlib import Path

import pandas as pd


class RubricImporter:
    """
    Import an evaluation rubric from an XLSX file
    and convert it into the standard JSON representation.

    Expected Excel structure
    ------------------------
    Sheet: Rubric

        Type | Attribute | Question | Score-5 | Score-4 | Score-3 | Score-2 | Score-1

    Sheet: General

        General guidance or suggestions, one item per row.
    """

    RUBRIC_SHEET = "Rubric"
    GENERAL_SHEET = "General"

    REQUIRED_COLUMNS = [
        "Type",
        "Attribute",
        "Question",
        "Score-5",
        "Score-4",
        "Score-3",
        "Score-2",
        "Score-1",
    ]

    def __init__(self, project_root: Path | None = None):
        if project_root is None:
            project_root = Path(__file__).resolve().parents[2]

        self.project_root = project_root

        self.evaluation_rubric_dir = (
             self.project_root / "data" / "evaluation_rubric"
        )

        self.rubric_dir = (
            self.project_root / "config" / "rubrics"
        )

        self.source_dir = (
            self.project_root / "data" / "evaluation_rubric"
        )

        self.rubric_dir.mkdir(parents=True, exist_ok=True)
        self.source_dir.mkdir(parents=True, exist_ok=True)

    def import_rubric(self, rubric_name: str) -> Path:
        """
        Import a rubric by name from the default
        evaluation rubric directory.
        """

        file_path = (
            self.evaluation_rubric_dir
            / f"{rubric_name}.xlsx"
        )

        return self.import_xlsx(file_path)

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

        # --------------------------------------------------
        # Validate source file
        # --------------------------------------------------

        if not file_path.exists():
            raise FileNotFoundError(
                f"Rubric file not found: {file_path}"
            )

        if file_path.suffix.lower() != ".xlsx":
            raise ValueError(
                "Rubric source file must be an .xlsx file."
            )

        # --------------------------------------------------
        # Read Excel workbook
        # --------------------------------------------------

        try:
            rubric_df = pd.read_excel(
                file_path,
                sheet_name=self.RUBRIC_SHEET,
            )
        except ValueError as exc:
            raise ValueError(
                f"Required sheet '{self.RUBRIC_SHEET}' "
                f"was not found in the Excel file."
            ) from exc

        # --------------------------------------------------
        # Validate Rubric columns
        # --------------------------------------------------

        self._validate_columns(rubric_df)

        # --------------------------------------------------
        # Read General guidance
        # --------------------------------------------------

        general_guidance = self._read_general_guidance(
            file_path
        )

        # --------------------------------------------------
        # Build rubric
        # --------------------------------------------------

        rubric = self._build_rubric(
            rubric_df=rubric_df,
            general_guidance=general_guidance,
            rubric_name=file_path.stem,
        )

        # --------------------------------------------------
        # Validate rubric content
        # --------------------------------------------------

        self._validate_rubric(rubric)

        # --------------------------------------------------
        # Generate JSON filename
        # --------------------------------------------------

        rubric_id = self._make_rubric_id(
            rubric["rubric_name"]
        )

        output_path = (
            self.rubric_dir
            / f"{rubric_id}.json"
        )

        # --------------------------------------------------
        # Save JSON
        # --------------------------------------------------

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

        print("Rubric imported successfully:")
        print(f"  Rubric: {output_path}")

        return output_path

    def _validate_columns(
        self,
        df: pd.DataFrame,
    ) -> None:
        """
        Validate that the Rubric sheet contains
        all required columns.
        """

        missing_columns = [
            column
            for column in self.REQUIRED_COLUMNS
            if column not in df.columns
        ]

        if missing_columns:
            raise ValueError(
                "Missing required columns in "
                f"'{self.RUBRIC_SHEET}' sheet: "
                + ", ".join(missing_columns)
            )

    def _read_general_guidance(
        self,
        file_path: Path,
    ) -> list[str]:
        """
        Read general guidance from the General sheet.

        Each non-empty cell in the first column is treated
        as one general guidance item.

        The General sheet is optional.
        """

        try:
            general_df = pd.read_excel(
                file_path,
                sheet_name=self.GENERAL_SHEET,
                header=None,
            )
        except ValueError:
            # General sheet does not exist.
            return []

        guidance = []

        for value in general_df.iloc[:, 0]:
            if pd.isna(value):
                continue

            text = str(value).strip()

            if text:
                guidance.append(text)

        return guidance

    def _build_rubric(
        self,
        rubric_df: pd.DataFrame,
        general_guidance: list[str],
        rubric_name: str,
    ) -> dict:
        """
        Convert the Excel workbook into the standard
        rubric JSON structure.
        """

        criteria = []

        for row_number, row in rubric_df.iterrows():

            # --------------------------------------------------
            # Read basic information
            # --------------------------------------------------

            rubric_type = self._clean_required_value(
                row["Type"],
                field="Type",
                row_number=row_number + 2,
            )

            attribute = self._clean_required_value(
                row["Attribute"],
                field="Attribute",
                row_number=row_number + 2,
            )

            question = self._clean_required_value(
                row["Question"],
                field="Question",
                row_number=row_number + 2,
            )

            # --------------------------------------------------
            # Read score descriptions
            # --------------------------------------------------

            scores = {}

            for score in range(1, 6):

                column = f"Score-{score}"

                value = row[column]

                if pd.isna(value):
                    raise ValueError(
                        f"Missing score description for "
                        f"'{rubric_type} - {attribute}', "
                        f"score {score}, "
                        f"at Excel row {row_number + 2}."
                    )

                score_description = str(
                    value
                ).strip()

                if not score_description:
                    raise ValueError(
                        f"Empty score description for "
                        f"'{rubric_type} - {attribute}', "
                        f"score {score}, "
                        f"at Excel row {row_number + 2}."
                    )

                scores[str(score)] = score_description

            # --------------------------------------------------
            # Add criterion
            # --------------------------------------------------

            criteria.append(
                {
                    "type": rubric_type,
                    "attribute": attribute,
                    "question": question,
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
            "general_guidance": general_guidance,
            "criteria": criteria,
        }

    def _validate_rubric(
        self,
        rubric: dict,
    ) -> None:
        """
        Validate the generated rubric.
        """

        criteria = rubric["criteria"]

        if not criteria:
            raise ValueError(
                "Rubric must contain at least one criterion."
            )

        criterion_keys = set()

        for criterion in criteria:

            rubric_type = criterion["type"]
            attribute = criterion["attribute"]
            question = criterion["question"]

            if not rubric_type:
                raise ValueError(
                    "Criterion type cannot be empty."
                )

            if not attribute:
                raise ValueError(
                    "Criterion attribute cannot be empty."
                )

            if not question:
                raise ValueError(
                    f"Question cannot be empty for "
                    f"'{rubric_type} - {attribute}'."
                )

            # Use Type + Attribute as the unique identifier.
            criterion_key = (
                rubric_type,
                attribute,
            )

            if criterion_key in criterion_keys:
                raise ValueError(
                    f"Duplicate criterion: "
                    f"'{rubric_type} - {attribute}'"
                )

            criterion_keys.add(criterion_key)

            # Validate score descriptions
            scores = criterion["scores"]

            for score in range(1, 6):

                score_key = str(score)

                if score_key not in scores:
                    raise ValueError(
                        f"Missing score {score} for "
                        f"'{rubric_type} - {attribute}'."
                    )

                if not scores[score_key]:
                    raise ValueError(
                        f"Empty score description for "
                        f"'{rubric_type} - {attribute}', "
                        f"score {score}."
                    )

    @staticmethod
    def _clean_required_value(
        value,
        field: str,
        row_number: int,
    ) -> str:
        """
        Clean and validate a required Excel cell.
        """

        if pd.isna(value):
            raise ValueError(
                f"Missing '{field}' at Excel row "
                f"{row_number}."
            )

        value = str(value).strip()

        if not value:
            raise ValueError(
                f"Empty '{field}' at Excel row "
                f"{row_number}."
            )

        return value

    @staticmethod
    def _make_rubric_id(
        name: str,
    ) -> str:
        """
        Convert a rubric name into a simple file-safe ID.
        """

        return (
            name.lower()
            .strip()
            .replace(" ", "_")
            .replace("-", "_")
        )