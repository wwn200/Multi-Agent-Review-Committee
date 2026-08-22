import json
import shutil
from pathlib import Path

import pandas as pd


class AssumptionImporter:
    """
    Import an assumption set from an XLSX file
    and convert it into the standard JSON representation.

    Expected Excel structure
    ------------------------
    Sheet: Assumption

        ID | Classification | Assumption | Description

    Sheet: Model

        One model description item per row in the first column.

    Each row represents one assumption.
    """

    ASSUMPTION_SHEET = "Assumption"
    CONTEXT_SHEET = "Model"

    REQUIRED_COLUMNS = [
        "ID",
        "Classification",
        "Assumption",
        "Description",
    ]

    def __init__(self, project_root: Path | None = None):
        if project_root is None:
            project_root = Path(__file__).resolve().parents[2]

        self.project_root = project_root

        # Original XLSX files
        self.assumption_source_dir = (
            self.project_root
            / "data"
            / "model"
        )

        # Standard JSON configuration
        self.assumption_dir = (
            self.project_root
            / "config"
            / "models"
        )

        self.assumption_source_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.assumption_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def import_assumption(
        self,
        model_name: str
    ) -> Path:
        """
        Import an assumption set by name.

        The corresponding XLSX file is expected to exist
        in data/model/.

        Example
        -------
        import_assumption("test_model")

        will read:

            data/model/test_model/assumption_set.xlsx
        """

        file_path = (
            self.assumption_source_dir
            / f"{model_name}" / "assumption_set.xlsx"
        )

        return self.import_xlsx(file_path,model_name)

    def import_xlsx(
        self,
        file_path: str, model_name:str | Path,
    ) -> Path:
        """
        Import an XLSX assumption set and save it as JSON.

        Parameters
        ----------
        file_path:
            Path to the source XLSX file.

        Returns
        -------
        Path
            Path to the generated JSON assumption set.
        """

        file_path = Path(file_path)

        # --------------------------------------------------
        # Validate source file
        # --------------------------------------------------

        if not file_path.exists():
            raise FileNotFoundError(
                f"Assumption file not found: {file_path}"
            )

        if file_path.suffix.lower() != ".xlsx":
            raise ValueError(
                "Assumption source file must be an .xlsx file."
            )

        # --------------------------------------------------
        # Read Excel
        # --------------------------------------------------

        try:
            assumption_df = pd.read_excel(
                file_path,
                sheet_name=self.ASSUMPTION_SHEET,
            )
        except ValueError as exc:
            raise ValueError(
                f"Required sheet "
                f"'{self.ASSUMPTION_SHEET}' "
                f"was not found in the Excel file."
            ) from exc

        context = self._read_context(file_path)

        # --------------------------------------------------
        # Validate columns
        # --------------------------------------------------

        self._validate_columns(
            assumption_df
        )

        # --------------------------------------------------
        # Build assumption set
        # --------------------------------------------------

        assumption_set = self._build_assumption_set(
            assumption_df=assumption_df,
            assumption_set_name=model_name,
            context=context,
        )

        # --------------------------------------------------
        # Validate assumption set
        # --------------------------------------------------

        self._validate_assumption_set(
            assumption_set
        )

        # --------------------------------------------------
        # Generate JSON filename
        # --------------------------------------------------

        assumption_id = self._make_assumption_id(
            assumption_set["assumption_set_name"]
        )

        output_path = (
            self.assumption_dir
            / f"{assumption_id}.json"
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
                assumption_set,
                f,
                indent=4,
                ensure_ascii=False,
            )

        print("Assumption set imported successfully:")
        print(f"  Assumption set: {output_path}")

        return output_path

    def list_assumptions(self) -> list[str]:
        """
        List available imported assumption sets.

        Returns
        -------
        list[str]
            Names of available assumption sets.
        """

        return sorted(
            path.stem
            for path in self.assumption_dir.glob("*.json")
        )

    def _validate_columns(
        self,
        df: pd.DataFrame,
    ) -> None:
        """
        Validate required columns in the Assumption sheet.
        """

        missing_columns = [
            column
            for column in self.REQUIRED_COLUMNS
            if column not in df.columns
        ]

        if missing_columns:
            raise ValueError(
                "Missing required columns in "
                f"'{self.ASSUMPTION_SHEET}' sheet: "
                + ", ".join(missing_columns)
            )

    def _build_assumption_set(
        self,
        assumption_df: pd.DataFrame,
        assumption_set_name: str,
        context: list[str],
    ) -> dict:
        """
        Convert the DataFrame into the standard
        assumption set JSON structure.
        """

        assumptions = []

        for row_number, row in assumption_df.iterrows():

            assumption_id = (
                self._clean_required_value(
                    row["ID"],
                    field="ID",
                    row_number=row_number + 2,
                )
            )

            classification = (
                self._clean_required_value(
                    row["Classification"],
                    field="Classification",
                    row_number=row_number + 2,
                )
            )

            assumption_name = (
                self._clean_required_value(
                    row["Assumption"],
                    field="Assumption",
                    row_number=row_number + 2,
                )
            )

            description = (
                self._clean_required_value(
                    row["Description"],
                    field="Description",
                    row_number=row_number + 2,
                )
            )

            assumptions.append(
                {
                    "id": assumption_id,
                    "classification": classification,
                    "name": assumption_name,
                    "description": description,
                }
            )

        return {
            "assumption_set_name": assumption_set_name,
            "version": "1.0",
            "context": context,
            "assumptions": assumptions,
        }

    def _read_context(self, file_path: Path) -> list[str]:
        """Read model context items from the first Context column."""
        try:
            context_df = pd.read_excel(
                file_path,
                sheet_name=self.CONTEXT_SHEET,
                header=None,
            )
        except ValueError:
            return []

        if context_df.empty:
            return []

        context = []
        for value in context_df.iloc[:, 0]:
            if pd.isna(value):
                continue

            text = str(value).strip()
            if text:
                context.append(text)

        return context

    def _validate_assumption_set(
        self,
        assumption_set: dict,
    ) -> None:
        """
        Validate the generated assumption set.
        """

        assumptions = assumption_set["assumptions"]

        if not assumptions:
            raise ValueError(
                "Assumption set must contain "
                "at least one assumption."
            )

        assumption_ids = set()

        for assumption in assumptions:

            assumption_id = assumption["id"]
            classification = assumption["classification"]
            name = assumption["name"]
            description = assumption["description"]

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

            if not classification:
                raise ValueError(
                    f"Classification cannot be empty "
                    f"for assumption '{assumption_id}'."
                )

            if not name:
                raise ValueError(
                    f"Assumption name cannot be empty "
                    f"for ID '{assumption_id}'."
                )

            if not description:
                raise ValueError(
                    f"Description cannot be empty "
                    f"for assumption '{assumption_id}'."
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
    def _make_assumption_id(
        name: str,
    ) -> str:
        """
        Convert an assumption set name into
        a simple file-safe ID.
        """

        return (
            name.lower()
            .strip()
            .replace(" ", "_")
            .replace("-", "_")
        )
