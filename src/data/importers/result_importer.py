from __future__ import annotations

from pathlib import Path

import pandas as pd


class EvaluationResultLoader:
    """Import evaluation results from Excel files."""

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

        ``result_file`` is a filename relative to
        the configured ``data/outputs`` directory.
        """

        file_path = (
            self.output_dir
            / f"{result_file}.xlsx"
        )
        if not file_path.exists():
            raise FileNotFoundError(
                f"Evaluation result file not found: {file_path}"
            )

        return pd.read_excel(file_path)

    def list_results(self) -> list[str]:
        """Return the names of all Excel result files."""

        if not self.output_dir.exists():
            return []

        return sorted(
            path.name
            for path in self.output_dir.glob("*.xlsx")
            if path.is_file()
        )
