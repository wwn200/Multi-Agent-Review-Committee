# System Design

## Architecture

```text
Model XLSX --------------------┐
  Assumption sheet             │
  Model sheet (context)        ▼
                         Model importer
                                │
                                ▼
                         config/models/*.yaml

Rubric XLSX ----------------───┐
  Rubric sheet                 │
  General sheet                ▼
                         Rubric importer
                                │
                                ▼
                         config/rubrics/*.yaml

Committee YAML + role/background YAML
                                │
                                ▼
                         Workflow configuration
                                │
                                ▼
                         Evaluator committee
                                │
       ┌────────────────────────┼────────────────────────┐
       ▼                        ▼                        ▼
  Evaluator 001            Evaluator 002            Evaluator N
       │                        │                        │
       └─────────────── same rubric, context, target ───┘
                                │
                                ▼
                    Individual evaluation results
```

## Execution Sequence

`EvaluationWorkflow` performs the following operations:

1. Loads the committee configuration.
2. Loads the YAML rubric and validates its structure and score ranges.
3. Loads the YAML model and its context items.
4. Loads the fixed task template.
5. Creates each configured evaluator population.
6. Builds a target for each assumption using its ID, name, and description.
7. Sends each target to every evaluator independently.

If a model has `A` assumptions and the committee has `C` agents, the workflow
returns `A * C` individual results.

## Responsibility Boundaries

- Importers convert XLSX source files into YAML configuration files.
- Loaders read and validate persisted model and rubric configurations.
- `WorkflowConfigLoader` reads committee membership and population counts.
- `EvaluatorAgentCommittee` loads profiles and samples individual agents.
- `EvaluationExecutor` forwards one target to all committee agents.
- `EvaluationWorkflow` coordinates the complete process.

The current workflow does not aggregate scores or calculate disagreement
statistics.
