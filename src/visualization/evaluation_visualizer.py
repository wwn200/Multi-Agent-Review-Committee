from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.figure import Figure

from src.data.importers.result_importer import EvaluationResultLoader


class EvaluationVisualizer:
    """Create visualizations from multi-agent evaluation results."""

    POTENTIAL_IMPACT_COLUMN = "potential_impact-score"
    FIDELITY_COLUMN = "fidelity-score"
    ASSUMPTION_COLUMN = "assumption_id"
    IMPORTANCE_COLUMN = "potential_impact-importance"
    RISK_COLUMN = "potential_impact-risk"
    USABILITY_COLUMN = "potential_impact-usability"
    CONFIDENCE_COLUMN = "fidelity-confidence"
    EVIDENCE_COLUMN = "fidelity-evidence"
    ROBUSTNESS_COLUMN = "fidelity-robustness"

    ASSESSMENT_DIMENSIONS = {
        "Potential Impact": POTENTIAL_IMPACT_COLUMN,
        "Fidelity": FIDELITY_COLUMN,
    }
    ASSESSMENT_ATTRIBUTES = {
        "Importance": IMPORTANCE_COLUMN,
        "Risk": RISK_COLUMN,
        "Usability": USABILITY_COLUMN,
        "Confidence": CONFIDENCE_COLUMN,
        "Evidence": EVIDENCE_COLUMN,
        "Robustness": ROBUSTNESS_COLUMN,
    }

    ASSUMPTION_ASSESSMENT_SCATTER_FILENAME = (
        "potential_impact_vs_fidelity"
    )
    ASSUMPTION_ASSESSMENT_HEATMAP_FILENAME = (
    "assumption_assessment_heatmap"
)
    AGENT_ROLE_SCORE_FILENAME = "agent_role_score_comparison"

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
        threshold: float = 3.0,
        figsize: tuple[float, float] = (10, 7),
        show: bool = True,
    ) -> Figure:
        """Plot aggregated Potential Impact against Fidelity by assumption."""

        fig, ax = plt.subplots(figsize=figsize)

        ax.scatter(
            df[self.FIDELITY_COLUMN],
            df[self.POTENTIAL_IMPACT_COLUMN],
            s=100,
        )

        for _, row in df.iterrows():
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

    def plot_assumption_assessment_heatmap(
        self,
        df: pd.DataFrame,
        figsize: tuple[float, float] = (8, 6),
        show: bool = True,
    ) -> Figure:
        """Plot aggregated Potential Impact and Fidelity scores as a heatmap."""
        
        heatmap_data = (
            df.set_index(self.ASSUMPTION_COLUMN)[
                [
                    self.POTENTIAL_IMPACT_COLUMN,
                    self.FIDELITY_COLUMN,
                ]
            ]
            .rename(
                columns={
                    self.POTENTIAL_IMPACT_COLUMN: "Potential Impact",
                    self.FIDELITY_COLUMN: "Fidelity",
                }
            )
        )

        fig, ax = plt.subplots(figsize=figsize)

        image = ax.imshow(
            heatmap_data.values,
            aspect="auto",
            vmin=1,
            vmax=5,
        )

        ax.set_xticks(range(len(heatmap_data.columns)))
        ax.set_xticklabels(heatmap_data.columns)

        ax.set_yticks(range(len(heatmap_data.index)))
        ax.set_yticklabels(heatmap_data.index)

        # Add score values to each cell
        for i in range(len(heatmap_data.index)):
            for j in range(len(heatmap_data.columns)):
                ax.text(
                    j,
                    i,
                    f"{heatmap_data.iloc[i, j]:.2f}",
                    ha="center",
                    va="center",
                )

        ax.set_xlabel("Assessment Dimension")
        ax.set_ylabel("Assumption")
        ax.set_title(self.ASSUMPTION_ASSESSMENT_HEATMAP_FILENAME)

        fig.colorbar(
            image,
            ax=ax,
            label="Score",
        )

        fig.tight_layout()

        if show:
            plt.show()

        return fig

    def plot_agent_score_distribution(
        self,
        df: pd.DataFrame,
        score_column: str,
        dimension_name: str,
        figsize: tuple[float, float] = (10, 7),
        show: bool = True,
    ) -> Figure:
        """Plot the distribution of agent scores for each assumption."""

        required_columns = {
            self.ASSUMPTION_COLUMN,
            score_column,
        }
        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            raise ValueError(
                "Missing required columns: "
                f"{sorted(missing_columns)}"
            )

        grouped_scores = (
            df.groupby(self.ASSUMPTION_COLUMN)[score_column]
            .apply(list)
        )

        assumptions = grouped_scores.index.tolist()
        scores = grouped_scores.tolist()

        fig, ax = plt.subplots(figsize=figsize)

        positions = np.arange(1, len(assumptions) + 1)

        ax.boxplot(
            scores,
            positions=positions,
            widths=0.55,
            patch_artist=True,
        )

        # Add individual agent scores as jittered points
        rng = np.random.default_rng(42)

        for position, assumption_scores in zip(positions, scores):
            jitter = rng.uniform(
                -0.08,
                0.08,
                size=len(assumption_scores),
            )

            ax.scatter(
                position + jitter,
                assumption_scores,
                alpha=0.7,
                s=35,
            )

        ax.set_xticks(positions)
        ax.set_xticklabels(assumptions)

        ax.set_xlabel("Assumption")
        ax.set_ylabel(f"{dimension_name} Score")
        ax.set_title(
            f"{dimension_name} Score Distribution by Assumption"
        )

        ax.set_ylim(1, 5)
        ax.set_yticks(range(1, 6))

        ax.grid(
            True,
            axis="y",
            alpha=0.3,
            linestyle="--",
        )

        fig.tight_layout()

        if show:
            plt.show()

        return fig

    def plot_agent_score_frequency(
        self,
        df: pd.DataFrame,
        score_column: str,
        attribute_name: str,
        figsize: tuple[float, float] = (10, 7),
        show: bool = True,
    ) -> Figure:
        """Plot the frequency of each possible agent score for an attribute."""

        required_columns = {
            self.ASSUMPTION_COLUMN,
            score_column,
        }
        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            raise ValueError(
                "Missing required columns: "
                f"{sorted(missing_columns)}"
            )

        possible_scores = pd.Index(range(1, 6), name=score_column)
        frequencies = df[score_column].value_counts().reindex(
            possible_scores,
            fill_value=0,
        )

        fig, ax = plt.subplots(figsize=figsize)
        ax.bar(possible_scores, frequencies)

        ax.set_xlabel("Score")
        ax.set_ylabel("Frequency")
        ax.set_title(f"{attribute_name} Score Frequency")
        ax.set_xticks(possible_scores)
        ax.set_xlim(0.5, 5.5)
        ax.grid(
            True,
            axis="y",
            alpha=0.3,
            linestyle="--",
        )

        fig.tight_layout()

        if show:
            plt.show()

        return fig

    def plot_agent_score_by_role(
        self,
        df: pd.DataFrame,
        figsize: tuple[float, float] = (10, 7),
        show: bool = True,
    ) -> Figure:
        """Plot mean assessment dimension scores grouped by evaluator role."""

        required_columns = {
            "evaluator_id",
            *self.ASSESSMENT_DIMENSIONS.values(),
        }
        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            raise ValueError(
                "Missing required columns: "
                f"{sorted(missing_columns)}"
            )

        role_scores = df.copy()
        role_scores["evaluator_role"] = role_scores["evaluator_id"].astype(str).str.replace(
            r"_\d+$",
            "",
            regex=True,
        )
        grouped_scores = role_scores.groupby("evaluator_role", sort=False)[
            list(self.ASSESSMENT_DIMENSIONS.values())
        ].mean()

        roles = grouped_scores.index.tolist()
        dimensions = list(self.ASSESSMENT_DIMENSIONS.items())
        dimension_names = [dimension_name for dimension_name, _ in dimensions]
        positions = np.arange(len(dimensions))
        width = 0.8 / len(roles)

        fig, ax = plt.subplots(figsize=figsize)

        for index, role in enumerate(roles):
            offset = (index - (len(roles) - 1) / 2) * width
            bars = ax.bar(
                positions + offset,
                [grouped_scores.loc[role, score_column] for _, score_column in dimensions],
                width=width,
                label=role,
            )

            ax.bar_label(bars, fmt="%.2f", padding=3)

        ax.set_xlabel("Assessment Dimension")
        ax.set_ylabel("Mean Score")
        ax.set_title("Assessment Scores by Evaluator Role")
        ax.set_xticks(positions)
        ax.set_xticklabels(dimension_names)
        ax.set_ylim(1, 5)
        ax.set_yticks(range(1, 6))
        ax.legend(title="Evaluator Role")
        ax.grid(
            True,
            axis="y",
            alpha=0.3,
            linestyle="--",
        )

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
        df = self.load_results(result_path)
        aggregated = self.aggregate_by_assumption(
            df,
            method=aggregation,
        )

        output_paths = {}

        # Scatter plot
        scatter_path = result_path.parent / f"{self.ASSUMPTION_ASSESSMENT_SCATTER_FILENAME}.png"
        output_paths["potential_impact_vs_fidelity"] = scatter_path

        figure1 = self.plot_assumption_assessment_scatter(
            aggregated,
            threshold=threshold,
            figsize=figsize,
            show=show,
        )
        figure1.savefig(
            scatter_path,
            dpi=300,
            bbox_inches="tight",
        )

        # Heatmap plot
        heatmap_path = result_path.parent / f"{self.ASSUMPTION_ASSESSMENT_HEATMAP_FILENAME}.png"
        output_paths["assumption_assessment_heatmap"] = heatmap_path

        figure2 = self.plot_assumption_assessment_heatmap(
                    aggregated,
                    figsize=figsize,
                    show=show,
                )
        figure2.savefig(
            heatmap_path,
            dpi=300,
            bbox_inches="tight",
        )

        # Agent score distributions for assessment dimensions
        for dimension_name, score_column in self.ASSESSMENT_DIMENSIONS.items():

            filename = (
                dimension_name.lower()
                .replace(" ", "_")
                + "_score_distribution.png"
            )

            distribution_path = result_path.parent / filename

            figure = self.plot_agent_score_distribution(
                df,
                score_column=score_column,
                dimension_name=dimension_name,
                figsize=figsize,
                show=show,
            )

            figure.savefig(
                distribution_path,
                dpi=300,
                bbox_inches="tight",
            )

            output_paths[
                f"{dimension_name.lower().replace(' ', '_')}_score_distribution"
            ] = distribution_path

        # Agent score frequencies for assessment attributes
        for attribute_name, score_column in self.ASSESSMENT_ATTRIBUTES.items():
            filename = (
                attribute_name.lower()
                .replace(" ", "_")
                + "_score_distribution.png"
            )

            distribution_path = result_path.parent / filename

            figure = self.plot_agent_score_frequency(
                df,
                score_column=score_column,
                attribute_name=attribute_name,
                figsize=figsize,
                show=show,
            )

            figure.savefig(
                distribution_path,
                dpi=300,
                bbox_inches="tight",
            )

            output_paths[
                f"{attribute_name.lower().replace(' ', '_')}_score_distribution"
            ] = distribution_path

        # Assessment scores grouped by evaluator role
        role_score_path = (
            result_path.parent / f"{self.AGENT_ROLE_SCORE_FILENAME}.png"
        )
        role_score_figure = self.plot_agent_score_by_role(
            df,
            figsize=figsize,
            show=show,
        )
        role_score_figure.savefig(
            role_score_path,
            dpi=300,
            bbox_inches="tight",
        )
        output_paths[self.AGENT_ROLE_SCORE_FILENAME] = role_score_path

        return output_paths
