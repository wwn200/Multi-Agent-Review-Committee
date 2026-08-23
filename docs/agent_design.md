# Agent Design

## Agent Composition

Each evaluator agent combines:

1. A role, such as product manager or risk manager.
2. A role-specific expertise and evaluation perspective.
3. An optional organizational or industry background.
4. Sampled traits, attention weights, concerns, and evidence preferences.
5. A prompt builder that creates the system and user prompts.
6. An LLM client that generates the evaluation response.

## Prompt Construction

The system prompt contains the evaluator identity, background, expertise,
evaluation behavior, concerns, rubric, and output requirements.

The user prompt contains:

- The model context loaded from the model configuration.
- The fixed evaluation task template.
- The current assumption target, including ID, name, and description.

Every evaluator receives the same context, rubric, and target. Differences in
responses come from the evaluator profiles and the LLM's reasoning.

## Population Sampling

A committee entry defines a role, an optional background, and a count:

```yaml
committee:
  - role: product_manager
    background: manufacturing
    count: 2
```

The committee creates two separate evaluator agents with IDs such as
`product_manager_001` and `product_manager_002`.

## Evaluation Result

Each agent returns an `EvaluationResult` containing:

- `evaluator_id`
- `response`
- `raw_response`

The executor does not combine these results. A later aggregation component can
consume the returned list.
