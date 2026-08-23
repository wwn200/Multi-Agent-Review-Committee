# Evaluator Profiles

Evaluator profile definitions are stored in YAML files under
`config/agents/roles/` and `config/agents/backgrounds/`.

## Role Configuration

A role defines the evaluator's general identity and default perspective:

```yaml
name: product_manager
expertise:
  product_strategy: high
base_traits: {}
default_attention_weights: {}
default_concerns: []
```

The actual role files may contain additional trait distributions and
attention-weight definitions.

## Background Configuration

A background adds contextual information and modifies role behavior:

```yaml
name: manufacturing
traits: {}
attention_weights: {}
concerns: []
contextual_information: {}
```

When a background is configured for a committee member, it is merged with the
role before individual profiles are sampled.

## Sampling

`EvaluatorSampler` samples traits and perturbs attention weights using the
workflow seed. Supplying a seed to `EvaluationWorkflow` makes profile
generation reproducible for testing.
