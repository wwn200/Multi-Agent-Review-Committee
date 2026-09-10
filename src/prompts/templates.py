# src/prompts/templates.py

from __future__ import annotations


IDENTITY_TEMPLATE = """\
You are an evaluator participating in a model credibility assessment.
Your role is: {role}.
"""


EXPERTISE_TEMPLATE = """\
Your areas of expertise include:
{expertise}
"""


BACKGROUND_TEMPLATE = """\
Professional background:
{background}

Contextual Information:
{contextual_information}
"""


EVALUATION_PERSPECTIVE_TEMPLATE = """\
When evaluating the model, pay particular attention to the following areas:
{attention}
"""


EVALUATION_BEHAVIOR_TEMPLATE = """\
Your evaluation style is characterized by the following tendencies:
{behavior}
"""


CONCERNS_TEMPLATE = """\
You should be particularly attentive to the following concerns:
{concerns}
"""


RUBRIC_TEMPLATE = """\
## Evaluation Rubric

The evaluation should follow the following criteria:

{rubric}
"""


CONTEXT_TEMPLATE = """\
## Evaluation Context

The following model and assumption information is provided for evaluation:

{context}
"""


OUTPUT_REQUIREMENTS_TEMPLATE = """\
## Output Requirements

Provide your evaluation according to the specified rubric.

Return your evaluation using the following structure:

{score_structure}

Requirements:
- Every attribute score must be an integer from 1 to 5.
- Every type score can be any number between 1 to 5, rounded to two decimal places. 
- The type score is calculated as a weighted aggregation of its attribute scores, with the weights for each attribute determined by the agent based on its concerns and attention weights.
- "rationale" must explain the reasoning behind your evaluation.
- Do not include fields other than those specified above.
"""

EVALUATION_TASK_TEMPLATE = """\
## Evaluation Task

{task}
"""


EVALUATOR_SYSTEM_PROMPT_TEMPLATE = """\
{identity}

{background}

{expertise}

{evaluation_perspective}

{evaluation_behavior}

{concerns}

{rubric}

{context}

{output_requirements}
"""
