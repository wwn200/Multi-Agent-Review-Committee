from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable

import pandas as pd


class EvaluationResultWriter:
    """Store evaluator results as one row per assumption/evaluator pair."""

    def __init__(
        self,
        output_dir: str | Path = "data/outputs",
    ) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        results: Iterable[Any],
        model_name: str,
        rubric_name: str,
        committee_name: str,
    ) -> Path:
        """Write results to a run directory and return the workbook path."""

        rows = [self._result_to_row(result) for result in results]
        dataframe = pd.DataFrame(rows)

        if not rows:
            dataframe = pd.DataFrame(
                columns=[
                    "assumption_id",
                    "evaluator_id",
                    "rationale",
                ]
            )

        result_directory_name = "_".join(
            self._safe_filename_part(value)
            for value in (
                model_name,
                rubric_name,
                committee_name,
            )
        )
        result_directory = self.output_dir / result_directory_name
        result_directory.mkdir(parents=True, exist_ok=True)
        output_path = result_directory / "evaluation_result.xlsx"
        dataframe.to_excel(output_path, index=False)

        return output_path

    def _result_to_row(self, result: Any) -> dict[str, Any]:
        response_data = self._parse_response(result.response)
        row: dict[str, Any] = {
            "assumption_id": result.assumption_id,
            "evaluator_id": result.evaluator_id,
        }

        for evaluation_type, evaluation_data in response_data.items():
            if evaluation_type == "rationale":
                continue

            if not isinstance(evaluation_data, dict):
                raise ValueError(
                    f'Expected "{evaluation_type}" to contain scores.'
                )

            for field, value in evaluation_data.items():
                row[f"{evaluation_type}-{field}"] = value

        row["rationale"] = response_data.get("rationale", "")
        return row

    @staticmethod
    def _parse_response(response: Any) -> dict[str, Any]:
        """Parse a response dictionary or JSON response string."""

        if isinstance(response, dict):
            return response

        if not isinstance(response, str):
            raise ValueError(
                f"Unsupported response type: {type(response).__name__}"
            )

        response = response.strip()
        if response.startswith("```"):
            response = re.sub(r"^```(?:json)?\s*|\s*```$", "", response)

        try:
            parsed = json.loads(response)
        except json.JSONDecodeError as exc:
            raise ValueError("Evaluation response is not valid JSON.") from exc

        if not isinstance(parsed, dict):
            raise ValueError("Evaluation response must be a JSON object.")

        return parsed

    @staticmethod
    def _safe_filename_part(value: str) -> str:
        """Keep generated filenames valid across supported platforms."""

        cleaned = re.sub(r'[<>:"/\\|?*]+', "_", str(value)).strip(" .")
        return cleaned or "evaluation"
