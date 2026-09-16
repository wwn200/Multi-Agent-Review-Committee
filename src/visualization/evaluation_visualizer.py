from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from src.data.importers.result_importer import EvaluationResultLoader


class EvaluationVisualizer:
    """Create visualizations from multi-agent evaluation results."""

    POTENTIAL_IMPACT_COLUMN = "potential_impact-score"
    FIDELITY_COLUMN = "fidelity-score"
    ASSUMPTION_COLUMN = "assumption_id"
    ASSUMPTION_ASSESSMENT_SCATTER_FILENAME = (
        "potential_impact_vs_fidelity"
    )

    def __init__(
        self,
        loader: EvaluationResultLoader | None = None,
    ) -> None:
        """Initialize a visualizer backed by the result importer."""
        self.loader = loader or EvaluationResultLoader()

    def load_results(self, result_file: str | Path) -> pd.DataFrame:
        """Load evaluation results using ``EvaluationResultLoader``."""
        return self.loader.load(result_file)

    def aggregate_by_assumption(
        self,
        df: pd.DataFrame,
        method: str = "mean",
    ) -> pd.DataFrame:
        """Aggregate evaluator scores into one row per assumption."""
        required_columns = {
            self.ASSUMPTION_COLUMN,
            self.POTENTIAL_IMPACT_COLUMN,
            self.FIDELITY_COLUMN,
        }
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            raise ValueError(
                "Missing required columns: "
                f"{sorted(missing_columns)}"
            )

        if method not in {"mean", "median"}:
            raise ValueError(
                f"Unsupported aggregation method: {method}. "
                "Use 'mean' or 'median'."
            )

        score_columns = [
            self.POTENTIAL_IMPACT_COLUMN,
            self.FIDELITY_COLUMN,
        ]
        return (
            df.groupby(self.ASSUMPTION_COLUMN, as_index=False)[score_columns]
            .agg(method)
        )

    def plot_assumption_assessment_scatter(
        self,
        df: pd.DataFrame,
        aggregation: str = "mean",
        threshold: float = 3.0,
        figsize: tuple[float, float] = (10, 7),
        show: bool = True,
    ) -> Figure:
        """Plot aggregated Potential Impact against Fidelity by assumption."""
        aggregated = self.aggregate_by_assumption(df, method=aggregation)
        fig, ax = plt.subplots(figsize=figsize)

        ax.scatter(
            aggregated[self.FIDELITY_COLUMN],
            aggregated[self.POTENTIAL_IMPACT_COLUMN],
            s=100,
        )

        for _, row in aggregated.iterrows():
            ax.annotate(
                str(row[self.ASSUMPTION_COLUMN]),
                (
                    row[self.FIDELITY_COLUMN],
                    row[self.POTENTIAL_IMPACT_COLUMN],
                ),
                xytext=(8, 5),
                textcoords="offset points",
            )

        ax.axvline(threshold, linestyle="--", linewidth=1.5)
        ax.axhline(threshold, linestyle="--", linewidth=1.5)
        ax.set_xlabel("Fidelity Score")
        ax.set_ylabel("Potential Impact Score")
        ax.set_title(self.ASSUMPTION_ASSESSMENT_SCATTER_FILENAME)
        ax.set_xlim(1, 5)
        ax.set_ylim(1, 5)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()

        if show:
            plt.show()

        return fig

    def plot_result_file(
        self,
        result_file: str | Path,
        aggregation: str = "mean",
        threshold: float = 3.0,
        figsize: tuple[float, float] = (10, 7),
        show: bool = True,
    ) -> Figure:
        """Load, plot, and save a result workbook's visualization."""
        result_path = self.loader.resolve_path(result_file)
        figure = self.plot_assumption_assessment_scatter(
            self.load_results(result_path),
            aggregation=aggregation,
            threshold=threshold,
            figsize=figsize,
            show=show,
        )
        figure.savefig(
            result_path.parent / f"{self.ASSUMPTION_ASSESSMENT_SCATTER_FILENAME}.png",
            dpi=300,
            bbox_inches="tight",
        )
        return figure