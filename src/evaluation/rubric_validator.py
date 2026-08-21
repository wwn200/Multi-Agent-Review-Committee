from __future__ import annotations


class RubricValidator:
    """Validate the structure and content of an evaluation rubric."""

    def validate(self, rubric: dict) -> None:
        """Validate a rubric.

        Raises:
            ValueError: If the rubric is invalid.
        """
        self._validate_structure(rubric)
        self._validate_criteria_scores(rubric)

    @staticmethod
    def _validate_structure(rubric: dict) -> None:
        """Validate the basic structure of a rubric."""
        if not isinstance(rubric, dict):
            raise ValueError("Rubric must be a dictionary.")

    @staticmethod
    def _validate_criteria_scores(rubric: dict) -> None:
        """Validate scores defined for each criterion."""

        criteria = rubric.get("criteria")
        scale = rubric.get("scale")

        if not criteria:
            raise ValueError("Rubric must have evaluation criteria.")

        if not scale:
            raise ValueError("Rubric must have scoring scale.")

        min_score = scale.get("min")
        max_score = scale.get("max")

        for criterion in criteria:
            scores = criterion.get("scores")

            if not scores:
                raise ValueError(
                    "Each criterion must contain a non-empty 'scores'."
                )

            for score in scores:
                try:
                    score_value = int(score)
                except (TypeError, ValueError) as exc:
                    raise ValueError(
                        f"Invalid score '{score}'. "
                        "Scores must be integers."
                    ) from exc

                if not min_score <= score_value <= max_score:
                    raise ValueError(
                        f"Score '{score}' is outside the allowed range "
                        f"[{min_score}, {max_score}]."
                    )