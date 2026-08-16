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
Clearly distinguish your judgment from factual information
provided in the evaluation context.
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