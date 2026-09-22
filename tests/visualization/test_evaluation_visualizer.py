from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")

from src.data.importers.result_importer import EvaluationResultLoader
from src.visualization import EvaluationVisualizer


def _results() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "assumption_id": ["A", "A", "B"],
            "potential_impact-score": [4, 2, 5],
            "fidelity-score": [3, 5, 4],
            "potential_impact-importance": [1, 2, 2],
            "potential_impact-risk": [3, 3, 5],
            "potential_impact-usability": [4, 4, 5],
            "fidelity-confidence": [5, 4, 5],
            "fidelity-evidence": [2, 2, 3],
            "fidelity-robustness": [1, 1, 4],
        }
    )


def test_aggregate_by_assumption_supports_mean_and_median():
    visualizer = EvaluationVisualizer()

    mean = visualizer.aggregate_by_assumption(_results())
    median = visualizer.aggregate_by_assumption(_results(), method="median")

    assert list(mean["assumption_id"]) == ["A", "B"]
    assert mean.loc[0, "potential_impact-score"] == 3
    assert median.loc[0, "fidelity-score"] == 4


def test_plot_agent_score_frequency_includes_all_five_scores():
    visualizer = EvaluationVisualizer()

    figure = visualizer.plot_agent_score_frequency(
        _results(),
        score_column="potential_impact-importance",
        attribute_name="Importance",
        show=False,
    )

    bars = figure.axes[0].patches
    assert [bar.get_x() + bar.get_width() / 2 for bar in bars] == [1, 2, 3, 4, 5]
    assert [bar.get_height() for bar in bars] == [1, 2, 0, 0, 0]


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
    assert (
        result_directory / "potential_impact_vs_fidelity.png"
    ).exists()


def test_result_loader_accepts_explicit_xlsx_path(tmp_path: Path):
    result_path = tmp_path / "results.xlsx"
    _results().to_excel(result_path, index=False)

    loaded = EvaluationResultLoader(output_dir=tmp_path).load(result_path)

    assert list(loaded.columns) == list(_results().columns)
