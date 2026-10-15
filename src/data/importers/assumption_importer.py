import shutil
from pathlib import Path

import pandas as pd
import yaml


class AssumptionImporter:
    """
    Import an assumption set from an XLSX file
    and convert it into the standard YAML representation.

    Expected Excel structure
    ------------------------
    Sheet: Assumption

        ID | Classification | Assumption | Importance | Description | Selected

    Sheet: Dependency

        Source | Target | Dependency Strength

    Sheet: Model

        One model description item per row in the first column.

    Each row represents one assumption.
    """

    ASSUMPTION_SHEET = "Assumption"
    DEPENDENCY_SHEET = "Dependency"
    CONTEXT_SHEET = "Model"

    REQUIRED_COLUMNS = [
        "ID",
        "Classification",
        "Assumption",
        "Importance",
        "Description",
        "Selected",
    ]

    DEPENDENCY_COLUMNS = [
        "Source",
        "Target",
        "Dependency Strength",
    ]

    def __init__(self, project_root: Path | None = None):
        if project_root is None:
            project_root = Path(__file__).resolve().parents[3]

        self.project_root = project_root

        # Original XLSX files
        self.assumption_source_dir = (
            self.project_root
            / "data"
            / "model"
        )

        # Standard YAML configuration
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
                keep_default_na=False,
            )
        except ValueError as exc:
            raise ValueError(
                f"Required sheet "
                f"'{self.ASSUMPTION_SHEET}' "
                f"was not found in the Excel file."
            ) from exc

        dependency_df = self._read_dependency(file_path)
        context = self._read_context(file_path)

        # --------------------------------------------------
        # Validate columns
        # --------------------------------------------------

        self._validate_columns(
            assumption_df
        )
        self._validate_dependency_columns(dependency_df)

        # --------------------------------------------------
        # Build assumption set
        # --------------------------------------------------

        assumption_set = self._build_assumption_set(
            assumption_df=assumption_df,
            assumption_set_name=model_name,
            context=context,
            dependency_df=dependency_df,
        )

        # --------------------------------------------------
        # Validate assumption set
        # --------------------------------------------------

        self._validate_assumption_set(
            assumption_set
        )

        # --------------------------------------------------
        # Generate YAML filename
        # --------------------------------------------------

        assumption_id = self._make_assumption_id(
            assumption_set["assumption_set_name"]
        )

        output_path = (
            self.assumption_dir
            / f"{assumption_id}.yaml"
        )

        # --------------------------------------------------
        # Save YAML
        # --------------------------------------------------

        with open(
            output_path,
            "w",
            encoding="utf-8",
        ) as f:
            yaml.safe_dump(
                assumption_set,
                f,
                sort_keys=False,
                allow_unicode=True,
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
            {
                path.stem
                for pattern in ("*.yaml", "*.yml", "*.json")
                for path in self.assumption_dir.glob(pattern)
            }
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

    def _validate_dependency_columns(
        self,
        df: pd.DataFrame,
    ) -> None:
        missing_columns = [
            column
            for column in self.DEPENDENCY_COLUMNS
            if column not in df.columns
        ]

        if missing_columns:
            raise ValueError(
                "Missing required columns in "
                f"'{self.DEPENDENCY_SHEET}' sheet: "
                + ", ".join(missing_columns)
            )

    def _build_assumption_set(
        self,
        assumption_df: pd.DataFrame,
        assumption_set_name: str,
        context: list[str],
        dependency_df: pd.DataFrame,
    ) -> dict:
        """
        Convert the DataFrame into the standard
        assumption set YAML structure.
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

            importance = self._clean_weight(
                row["Importance"], "Importance", row_number + 2
            )
            selected = self._clean_selected(
                row["Selected"], row_number + 2
            )

            assumptions.append(
                {
                    "id": assumption_id,
                    "classification": classification,
                    "name": assumption_name,
                    "description": description,
                    "importance": importance,
                    "selected": selected,
                }
            )

        assumption_ids = {assumption["id"] for assumption in assumptions}
        dependencies = []
        for row_number, row in dependency_df.iterrows():
            source = self._clean_required_value(
                row["Source"], "Source", row_number + 2
            )
            target = self._clean_required_value(
                row["Target"], "Target", row_number + 2
            )
            strength = self._clean_weight(
                row["Dependency Strength"],
                "Dependency Strength",
                row_number + 2,
            )
            if source not in assumption_ids or target not in assumption_ids:
                raise ValueError(
                    f"Dependency at Excel row {row_number + 2} references "
                    "an unknown assumption ID."
                )
            dependencies.append(
                {
                    "source": source,
                    "target": target,
                    "dependency_strength": strength,
                }
            )

        return {
            "assumption_set_name": assumption_set_name,
            "version": "1.0",
            "context": context,
            "assumptions": assumptions,
            "dependencies": dependencies,
        }

    def _read_dependency(self, file_path: Path) -> pd.DataFrame:
        try:
            return pd.read_excel(
                file_path,
                sheet_name=self.DEPENDENCY_SHEET,
                keep_default_na=False,
            )
        except ValueError as exc:
            raise ValueError(
                f"Required sheet '{self.DEPENDENCY_SHEET}' "
                "was not found in the Excel file."
            ) from exc

    def _read_context(self, file_path: Path) -> list[str]:
        """Read model context items from the first Context column."""
        try:
            context_df = pd.read_excel(
                file_path,
                sheet_name=self.CONTEXT_SHEET,
                header=None,
                keep_default_na=False,
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

    @staticmethod
    def _clean_weight(value, field: str, row_number: int) -> float:
        if isinstance(value, bool) or pd.isna(value):
            raise ValueError(
                f"'{field}' at Excel row {row_number} must be a number in [0, 1]."
            )
        try:
            value = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"'{field}' at Excel row {row_number} must be a number in [0, 1]."
            ) from exc
        if not 0 <= value <= 1:
            raise ValueError(
                f"'{field}' at Excel row {row_number} must be in [0, 1]."
            )
        return value

    @staticmethod
    def _clean_selected(value, row_number: int):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if not normalized:
                return "N/A"
            if normalized == "true":
                return True
            if normalized == "false":
                return False
            if normalized == "n/a":
                return "N/A"
        raise ValueError(
            f"'Selected' at Excel row {row_number} must be True, False, or N/A."
        )

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
            importance = assumption["importance"]
            selected = assumption["selected"]

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

            self._clean_weight(importance, "Importance", 0)
            if selected not in (True, False, "N/A"):
                raise ValueError(
                    f"Invalid Selected value for assumption '{assumption_id}'."
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
