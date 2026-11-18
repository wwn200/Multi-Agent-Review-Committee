from types import SimpleNamespace

from src.data.importers.result_importer import EvaluationResultLoader
from src.data.writers.excel_writer import EvaluationResultWriter


def test_save_creates_run_directory_and_standard_filename(tmp_path):
    result = SimpleNamespace(
        assumption_id="A1",
        evaluator_id="evaluator-1",
        response={
            "system_quality": {"score": 4, "reliability": 3},
            "traceability": {"score": 3, "auditability": 5},
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
    result_data = EvaluationResultLoader(output_dir=tmp_path).load(output_path)
    assert {
        "system_quality-score",
        "system_quality-reliability",
        "traceability-score",
        "traceability-auditability",
    }.issubset(result_data.columns)


def test_loader_resolves_run_name_and_lists_runs(tmp_path):
    result = SimpleNamespace(
        assumption_id="A1",
        evaluator_id="evaluator-1",
        response={"service_resilience": {"score": 4}},
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
