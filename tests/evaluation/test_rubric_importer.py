from pathlib import Path
import json

from src.evaluation.rubric_importer import RubricImporter


def test_import_xlsx(tmp_path):
    importer = RubricImporter(
        project_root=tmp_path
    )

    test_file = Path("data/evaluation_rubric/test_rubric.xlsx")

    output_path = importer.import_xlsx(test_file)

    assert output_path.exists()
    assert output_path.name == "test_rubric.json"

    # Load generated JSON
    with open(
        output_path,
        "r",
        encoding="utf-8",
    ) as f:
        rubric = json.load(f)

    # Check basic information
    assert rubric["rubric_name"] == "test_rubric"
    assert rubric["version"] == "1.0"

    # Check scale
    assert rubric["scale"]["min"] == 1
    assert rubric["scale"]["max"] == 5

    # Check criteria
    assert len(rubric["criteria"]) == 6

    criterion = rubric["criteria"][2]

    assert criterion["type"] == "Potential Impact"
    assert criterion["attribute"] == "Usability"
    assert criterion["question"] == (
        "How important is assumption A for usability or simplifying computation?"
    )

    assert criterion["scores"]["1"] == "Not important"
    assert criterion["scores"]["2"] == "Somewhat important"
    assert criterion["scores"]["3"] == "Moderately important"
    assert criterion["scores"]["4"] == "Quite important"
    assert criterion["scores"]["5"] == "Extremely important"

    assert len(rubric["general_guidance"]) == 1

    assert (
        rubric["general_guidance"][0]
        == "a Likert-scale approach is preferred due to its simplicity and ease of interpretation."
    )