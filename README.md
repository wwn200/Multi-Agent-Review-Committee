# Multi-Agent Evaluation Agent

A configurable multi-agent framework for evaluating model assumptions from
multiple stakeholder perspectives.

## Overview

The application provides an end-to-end workflow for evaluating model
assumptions from multiple stakeholder perspectives. It builds a committee
of evaluator agents from configurable role and background definitions and
coordinates rubric loading, model loading, evaluator construction, and
assumption-level evaluation.

## Key Features

- **Multi-agent evaluation** — Evaluate model assumptions from multiple
  evaluator perspectives.
- **Configurable evaluator profiles** — Define evaluator roles,
  backgrounds, traits, and attention preferences.
- **Structured rubric management** — Import, load, validate, and construct
  prompts from evaluation rubrics.
- **Model assumption management** — Import and evaluate structured model
  assumption sets.
- **Integrated evaluation workflow** — Coordinate configuration loading,
  evaluator construction, and assumption-level evaluation through a unified
  workflow.
- **YAML-based configuration** — Store project configuration in a consistent
  YAML format.

## Requirements

- Python 3.10 or newer
- Dependencies listed in `requirements.txt`
- An `OPENAI_API_KEY` environment variable for live evaluations

## Configuration

Configuration is stored under `config/`:

```text
config/
  agents/
    roles/                 Role YAML files
    backgrounds/           Background YAML files
  committee/               Committee YAML files
  models/                  Imported model YAML files
  rubrics/                 Imported rubric YAML files
  setting.yaml             LLM settings
  task_template.yaml       Fixed evaluation task template
```

See `docs/configuration.md` for file formats and import behavior.

## Getting Started

Import a rubric from `data/evaluation_rubric/<name>.xlsx`:

```bash
python main.py import-rubric <rubric_name>
```

Import a model from `data/model/<name>/assumption_set.xlsx`:

```bash
python main.py import-model <model_name>
```

Run an evaluation:

```bash
python main.py evaluate-model <committee_name> <model_name> <rubric_name>
```

For example:

```bash
python main.py evaluate-model test_committee cutting_stock_model test_rubric
```

The evaluation command does not accept context or task input. Context is
loaded from the model workbook, and the task is constructed from
`config/task_template.yaml` and each model assumption.

## Workflow

1. Load the committee configuration. A missing committee is an immediate
   error.
2. Load the model and rubric. If either imported configuration is missing,
   the CLI attempts to import it from its default XLSX location.
3. Load model context from the model workbook's `Model` sheet.
4. Load and validate the rubric.
5. Build the evaluator committee from configured roles, backgrounds, and
   population counts.
6. Build an evaluation target for each model assumption, including its ID,
   name, and description.
7. Execute every target independently for every committee agent.

## Testing

The workflow test uses a fake LLM client and does not make API requests:

```bash
pytest tests/workflow/test_workflow.py
```

API tests are marked with `api` and require a valid API key.

## Project Status

Version 1.0.0 provides a complete workflow for generating individual
evaluator assessments of model assumptions. Aggregation of evaluator
results, disagreement analysis, and higher-level model confidence
assessment are not yet part of the workflow execution path.