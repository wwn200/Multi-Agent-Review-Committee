from types import SimpleNamespace

from src.data.importers.result_importer import EvaluationResultLoader
from src.data.writers.excel_writer import EvaluationResultWriter


def test_save_creates_run_directory_and_standard_filename(tmp_path):
    result = SimpleNamespace(
        assumption_id="A1",
        evaluator_id="evaluator-1",
        response={
            "potential_impact": {"score": 4},
            "fidelity": {"score": 3},
            "rationale": "rationale",
        },
    )
    writer = EvaluationResultWriter(output_dir=tmp_path)

    output_path = writer.save(
        [result],
        model_name="model",
        rubric_name="rubric",
        committee_name="committee",
    )

    expected_path = (
        tmp_path
        / "model_rubric_committee"
        / "evaluation_result.xlsx"
    )
    assert output_path == expected_path
    assert output_path.exists()


def test_loader_resolves_run_name_and_lists_runs(tmp_path):
    result = SimpleNamespace(
        assumption_id="A1",
        evaluator_id="evaluator-1",
        response={"potential_impact": {"score": 4}},
    )
    EvaluationResultWriter(output_dir=tmp_path).save(
        [result],
        model_name="model",
        rubric_name="rubric",
        committee_name="committee",
    )
    loader = EvaluationResultLoader(output_dir=tmp_path)

    loaded = loader.load("model_rubric_committee")

    assert len(loaded) == 1
    assert loader.list_results() == ["model_rubric_committee"]
