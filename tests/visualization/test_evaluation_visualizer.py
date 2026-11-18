from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")

from src.data.importers.result_importer import EvaluationResultLoader
from src.visualization import EvaluationVisualizer


def _results() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "evaluator_id": [
                "product_manager_001",
                "product_manager_001",
                "decision_maker_001",
            ],
            "assumption_id": ["A", "A", "B"],
            "model_quality-score": [4, 2, 5],
            "traceability-score": [3, 5, 4],
            "cost_efficiency-score": [2, 4, 3],
            "model_quality-reliability": [1, 2, 2],
            "model_quality-recovery_time": [3, 3, 5],
            "traceability-auditability": [4, 4, 5],
            "cost_efficiency-resource_use": [5, 4, 5],
        }
    )


def test_aggregate_by_assumption_supports_mean_and_median():
    visualizer = EvaluationVisualizer()

    mean = visualizer.aggregate_by_assumption(_results())
    median = visualizer.aggregate_by_assumption(_results(), method="median")

    assert list(mean["assumption_id"]) == ["A", "B"]
    assert mean.loc[0, "model_quality-score"] == 3
    assert median.loc[0, "traceability-score"] == 4
    assert mean.loc[0, "cost_efficiency-score"] == 3


def test_plot_agent_score_frequency_includes_all_five_scores():
    visualizer = EvaluationVisualizer()

    figure = visualizer.plot_agent_score_frequency(
        _results(),
        score_column="model_quality-reliability",
        attribute_name="Reliability",
        show=False,
    )

    bars = figure.axes[0].patches
    assert [bar.get_x() + bar.get_width() / 2 for bar in bars] == [1, 2, 3, 4, 5]
    assert [bar.get_height() for bar in bars] == [1, 2, 0, 0, 0]


def test_plot_agent_score_by_role_groups_dimension_scores():
    visualizer = EvaluationVisualizer()

    figure = visualizer.plot_agent_score_by_role(_results(), show=False)

    axis = figure.axes[0]
    assert [label.get_text() for label in axis.get_xticklabels()] == [
        "Model Quality",
        "Traceability",
        "Cost Efficiency",
    ]
    assert len(axis.patches) == 6
    assert [bar.get_height() for bar in axis.patches] == [
        3.0,
        4.0,
        3.0,
        5.0,
        4.0,
        3.0,
    ]


def test_scatter_uses_two_detected_dimensions_as_axes():
    visualizer = EvaluationVisualizer()
    aggregated = visualizer.aggregate_by_assumption(_results())[
        ["assumption_id", "model_quality-score", "traceability-score"]
    ]

    figure = visualizer.plot_assumption_assessment_scatter(
        aggregated,
        show=False,
    )

    axis = figure.axes[0]
    assert axis.get_xlabel() == "Model Quality Score"
    assert axis.get_ylabel() == "Traceability Score"
    assert axis.collections[0].get_offsets().tolist() == [
        [3.0, 4.0],
        [5.0, 4.0],
    ]


def test_plot_result_file_saves_beside_result_workbook(tmp_path: Path):
    result_directory = tmp_path / "model_rubric_committee"
    result_directory.mkdir()
    result_path = result_directory / "evaluation_result.xlsx"
    _results().to_excel(result_path, index=False)
    visualizer = EvaluationVisualizer(
        loader=EvaluationResultLoader(output_dir=tmp_path),
    )

    figure = visualizer.plot_result_file(
        "model_rubric_committee",
        show=False,
    )

    assert figure is not None
    assert (result_directory / "assessment_scores_by_assumption.png").exists()
    assert (result_directory / "assessment_dimension_heatmap.png").exists()
    assert (result_directory / "model_quality_score_distribution.png").exists()
    assert (
        result_directory / "model_quality_reliability_score_distribution.png"
    ).exists()
    assert (
        result_directory / "traceability_auditability_score_distribution.png"
    ).exists()
    assert (result_directory / "agent_role_score_comparison.png").exists()


def test_result_loader_accepts_explicit_xlsx_path(tmp_path: Path):
    result_path = tmp_path / "results.xlsx"
    _results().to_excel(result_path, index=False)

    loaded = EvaluationResultLoader(output_dir=tmp_path).load(result_path)

    assert list(loaded.columns) == list(_results().columns)
