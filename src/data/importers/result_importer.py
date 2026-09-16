from __future__ import annotations

from pathlib import Path

import pandas as pd


class EvaluationResultLoader:
    """Import evaluation results."""

    RESULT_FILENAME = "evaluation_result.xlsx"

    def __init__(
        self,
        project_root: str | Path | None = None,
        output_dir: str | Path | None = None,
    ) -> None:
        if output_dir is not None:
            self.output_dir = Path(output_dir)
        else:
            if project_root is None:
                project_root = Path(__file__).resolve().parents[3]
            self.output_dir = Path(project_root) / "data" / "outputs"

    def load(self, result_file: str | Path) -> pd.DataFrame:
        """Load one evaluation result workbook as a DataFrame.

        ``result_file`` may be an explicit workbook path or a run directory
        name relative to the configured ``data/outputs`` directory.
        """

        file_path = self.resolve_path(result_file)
        if not file_path.exists():
            raise FileNotFoundError(
                f"Evaluation result file not found: {file_path}"
            )

        return pd.read_excel(file_path)

    def resolve_path(self, result_file: str | Path) -> Path:
        """Resolve a run name or workbook path to its workbook path."""
        file_path = Path(result_file)
        if not file_path.is_absolute():
            file_path = self.output_dir / file_path
        if file_path.is_dir() or file_path.suffix.lower() != ".xlsx":
            file_path = file_path / self.RESULT_FILENAME
        return file_path

    def list_results(self) -> list[str]:
        """Return the names of all evaluation result directories."""

        if not self.output_dir.exists():
            return []

        return sorted(
            path.name
            for path in self.output_dir.iterdir()
            if path.is_dir()
            and (path / self.RESULT_FILENAME).is_file()
        )
