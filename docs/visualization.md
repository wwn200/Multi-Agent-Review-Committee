# Evaluation Visualization

`EvaluationVisualizer` creates plots from an evaluation result workbook. It is
implemented in `src/visualization/evaluation_visualizer.py` and uses
`EvaluationResultLoader` to resolve result directories and workbook paths.

## Command-Line Usage

Run the visualization command from the project root:

```bash
python main.py visualize-result <model>_<rubric>_<committee> \
  --aggregation mean
```

The positional argument may be either an evaluation result directory name or
an explicit `.xlsx` workbook path. The `--aggregation` option applies to the
assumption-level scatter plot and heatmap and accepts `mean` or `median`.

For example:

```bash
python main.py visualize-result min_model_test_rubric_test_committee \
  --aggregation median
```

All generated PNG files are saved beside `evaluation_result.xlsx` in the
result directory.

## Generated Visualizations

`plot_result_file` generates the following files:

| File | Visualization | Purpose |
| --- | --- | --- |
| `potential_impact_vs_fidelity.png` | Assumption assessment scatter plot | Shows aggregated Potential Impact against Fidelity for each assumption, including the configured threshold lines. |
| `assumption_assessment_heatmap.png` | Assumption assessment heatmap | Shows aggregated Potential Impact and Fidelity scores for every assumption. |
| `potential_impact_score_distribution.png` | Dimension boxplot | Shows evaluator score distributions by assumption for Potential Impact. |
| `fidelity_score_distribution.png` | Dimension boxplot | Shows evaluator score distributions by assumption for Fidelity. |
| `<attribute>_score_distribution.png` | Attribute frequency plot | Shows the frequency of scores 1, 2, 3, 4, and 5 for each assessment attribute. |
| `agent_role_score_comparison.png` | Grouped bar chart | Shows mean Potential Impact and Fidelity scores by evaluator role. |

The attribute plots are generated for these attributes:

- `importance_score_distribution.png`
- `risk_score_distribution.png`
- `usability_score_distribution.png`
- `confidence_score_distribution.png`
- `evidence_score_distribution.png`
- `robustness_score_distribution.png`

## Result Data Requirements

The result workbook must contain the columns used by the visualizer:

| Column | Used by |
| --- | --- |
| `assumption_id` | Assumption-level plots and boxplots |
| `evaluator_id` | Evaluator-role grouped bar chart |
| `potential_impact-score` | Potential Impact plots and role comparison |
| `fidelity-score` | Fidelity plots and role comparison |
| `potential_impact-importance` | Importance frequency plot |
| `potential_impact-risk` | Risk frequency plot |
| `potential_impact-usability` | Usability frequency plot |
| `fidelity-confidence` | Confidence frequency plot |
| `fidelity-evidence` | Evidence frequency plot |
| `fidelity-robustness` | Robustness frequency plot |

Attribute scores are treated as integer scores from 1 through 5. Each
frequency plot includes all five score positions, even when a score has zero
observations.

Evaluator roles are extracted from `evaluator_id` by removing a trailing
numeric identifier after an underscore. For example,
`product_manager_001` becomes `product_manager` and
`risk_manager_002` becomes `risk_manager`. The role comparison chart averages
the dimension scores across all result rows for each extracted role.

## Python API

To generate a single visualization directly:

```python
from src.visualization import EvaluationVisualizer

visualizer = EvaluationVisualizer()
results = visualizer.load_results(
    "data/outputs/min_model_test_rubric_test_committee/evaluation_result.xlsx"
)

role_figure = visualizer.plot_agent_score_by_role(
    results,
    show=False,
)
role_figure.savefig("agent_role_score_comparison.png", dpi=300)
```

To generate the complete visualization set and save it beside the result
workbook:

```python
output_paths = visualizer.plot_result_file(
    "min_model_test_rubric_test_committee",
    aggregation="mean",
    show=False,
)
```

The returned `output_paths` mapping contains the generated file path for each
visualization.
