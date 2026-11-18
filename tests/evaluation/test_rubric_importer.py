from pathlib import Path
import yaml

import pandas as pd

from src.data.importers.rubric_importer import RubricImporter


def test_import_xlsx(tmp_path):
    importer = RubricImporter(
        project_root=tmp_path
    )

    test_file = Path("data/evaluation_rubric/test_rubric.xlsx")
    source_criteria = pd.read_excel(
        test_file,
        sheet_name=importer.RUBRIC_SHEET,
    )
    source_guidance = pd.read_excel(
        test_file,
        sheet_name=importer.GENERAL_SHEET,
        header=None,
    ).iloc[:, 0]

    output_path = importer.import_xlsx(test_file)

    assert output_path.exists()
    assert output_path.name == "test_rubric.yaml"

    # Load generated YAML
    with open(
        output_path,
        "r",
        encoding="utf-8",
    ) as f:
        rubric = yaml.safe_load(f)

    # Check basic information
    assert rubric["rubric_name"] == "test_rubric"
    assert rubric["version"] == "1.0"

    # Check scale
    assert rubric["scale"]["min"] == 1
    assert rubric["scale"]["max"] == 5

    # Check criteria
    assert len(rubric["criteria"]) == len(source_criteria)

    criterion = rubric["criteria"][2]
    source_criterion = source_criteria.iloc[2]

    assert criterion["type"] == str(source_criterion["Type"]).strip()
    assert criterion["attribute"] == str(source_criterion["Attribute"]).strip()
    assert criterion["question"] == str(source_criterion["Question"]).strip()

    for score in range(1, 6):
        assert criterion["scores"][str(score)] == str(
            source_criterion[f"Score-{score}"]
        ).strip()

    expected_guidance = [
        str(item).strip()
        for item in source_guidance
        if pd.notna(item) and str(item).strip()
    ]
    assert rubric["general_guidance"] == expected_guidance
