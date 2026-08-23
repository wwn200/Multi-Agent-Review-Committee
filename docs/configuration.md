# Configuration Reference

## Model Workbook

The source workbook is expected at:

```text
data/model/<model_name>/assumption_set.xlsx
```

It contains:

- `Assumption`: columns `ID`, `Classification`, `Assumption`, and
  `Description`.
- `Model`: one model context item per row in the first column.

The importer writes the result to:

```text
config/models/<model_name>.yaml
```

The generated structure contains `assumption_set_name`, `version`, `context`,
and `assumptions`. Each assumption preserves its ID, classification, name, and
description.

## Rubric Workbook

The source workbook is expected at:

```text
data/evaluation_rubric/<rubric_name>.xlsx
```

It contains:

- `Rubric`: criterion type, attribute, question, and score descriptions.
- `General`: optional guidance items in the first column.

The importer writes:

```text
config/rubrics/<rubric_name>.yaml
```

## Committee Configuration

Committee files are stored in `config/committee/`:

```yaml
committee_name: test_committee
committee:
  - role: product_manager
    background: manufacturing
    count: 2
  - role: risk_manager
    background: manufacturing
    count: 2
```

The `count` value must be a positive integer. Each counted member becomes a
separate evaluator agent.

## Task Template

`config/task_template.yaml` stores the fixed task text. It must contain the
`{evaluation_target}` placeholder. The workflow replaces that placeholder for
each assumption with:

```text
ID: <id>
Name: <name>
Description: <description>
```

## LLM Settings

LLM settings are stored in `config/setting.yaml`. The client currently reads
`llm.default_model`. The API key is supplied through `OPENAI_API_KEY`.

## Import Commands

Run these commands from the project root:

```bash
python main.py import-rubric <rubric_name>
python main.py import-model <model_name>
```

After import, use:

```bash
python main.py evaluate-model <committee_name> <model_name> <rubric_name>
```

The CLI attempts automatic model and rubric import only when their YAML
configuration is missing. Committee configurations are never imported
automatically.
