"""Optimization model for selecting an assumption subset."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import gurobipy as gp
from gurobipy import GRB


def load_yaml(file_path: str | Path) -> dict[str, Any]:
    """Load a YAML mapping from a file."""
    with open(file_path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict):
        raise ValueError(f"Expected a YAML mapping in '{file_path}'.")
    return data


def calculate_importance_scores(
    assumptions: list[dict[str, Any]],
    dependencies: list[dict[str, Any]],
    alpha: float,
) -> dict[str, float]:
    """Combine subjective importance with normalized outgoing influence."""
    if not 0.0 <= alpha <= 1.0:
        raise ValueError("'alpha' must be in [0, 1].")

    assumption_ids = [item["id"] for item in assumptions]
    if len(assumption_ids) != len(set(assumption_ids)):
        raise ValueError("Assumption IDs must be unique.")

    assumption_id_set = set(assumption_ids)
    subjective_importance = {}
    for assumption in assumptions:
        assumption_id = assumption["id"]
        value = assumption.get("importance")
        if isinstance(value, bool) or value is None:
            raise ValueError(f"Invalid importance score for assumption '{assumption_id}'.")
        try:
            value = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Importance score for assumption '{assumption_id}' must be numeric."
            ) from exc
        if not 0.0 <= value <= 1.0:
            raise ValueError(
                f"Importance score for assumption '{assumption_id}' must be in [0, 1]."
            )
        subjective_importance[assumption_id] = value

    influence_scores = {assumption_id: 0.0 for assumption_id in assumption_ids}
    seen_edges: set[tuple[str, str]] = set()
    for dependency in dependencies:
        source = dependency.get("source")
        target = dependency.get("target")
        edge = (source, target)
        if source not in assumption_id_set or target not in assumption_id_set:
            raise ValueError(f"Unknown dependency edge: {edge}.")
        if edge in seen_edges:
            raise ValueError(f"Duplicate dependency edge: {edge}.")
        seen_edges.add(edge)

        strength = dependency.get("dependency_strength")
        if isinstance(strength, bool) or strength is None:
            raise ValueError(f"Invalid dependency strength for edge {edge}.")
        try:
            strength = float(strength)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Dependency strength for edge {edge} must be numeric."
            ) from exc
        if not 0.0 <= strength <= 1.0:
            raise ValueError(f"Dependency strength for edge {edge} must be in [0, 1].")
        influence_scores[source] += strength

    maximum = max(influence_scores.values(), default=0.0)
    normalized = {
        assumption_id: score / maximum if maximum else 0.0
        for assumption_id, score in influence_scores.items()
    }
    return {
        assumption_id: alpha * subjective_importance[assumption_id]
        + (1.0 - alpha) * normalized[assumption_id]
        for assumption_id in assumption_ids
    }


def optimize_assumption_selection(
    model_data: dict[str, Any],
    optimization_config: dict[str, Any],
) -> list[bool]:
    """Return selected flags in the same order as ``model_data`` assumptions."""
    if gp is None or GRB is None:
        raise RuntimeError(
            "Gurobi is required for assumption selection optimization. "
            "Install the 'gurobipy' package and configure a valid license."
        )

    assumptions = model_data.get("assumptions")
    dependencies = model_data.get("dependencies", [])
    if not isinstance(assumptions, list) or not assumptions:
        raise ValueError("'assumptions' must be a non-empty list.")
    if not isinstance(dependencies, list):
        raise ValueError("'dependencies' must be a list.")

    try:
        q_max = float(optimization_config["Q_max"])
        a_value = float(optimization_config["a"])
        alpha = float(optimization_config["alpha"])
    except KeyError as exc:
        raise ValueError(f"Missing optimization parameter: {exc.args[0]}.") from exc
    except (TypeError, ValueError) as exc:
        raise ValueError("'Q_max', 'a', and 'alpha' must be numeric.") from exc
    if q_max < 0:
        raise ValueError("'Q_max' must be non-negative.")
    if not a_value.is_integer() or a_value < 0:
        raise ValueError("'a' must be a non-negative integer.")
    if not 0.0 <= alpha <= 1.0:
        raise ValueError("'alpha' must be in [0, 1].")
    a = int(a_value)

    assumption_ids = [item["id"] for item in assumptions]
    importance_scores = calculate_importance_scores(
        assumptions, dependencies, alpha
    )
    edges = [
        (item["source"], item["target"])
        for item in dependencies
    ]
    parents = {assumption_id: [] for assumption_id in assumption_ids}
    for source, target in edges:
        parents[target].append(source)

    model = gp.Model("assumption_network_selection")
    x = model.addVars(assumption_ids, vtype=GRB.BINARY, name="x")
    y = model.addVars(edges, vtype=GRB.BINARY, name="y")
    z = {
        (assumption_id, count): model.addVar(
            vtype=GRB.BINARY,
            name=f"z_{assumption_id}_{count}",
        )
        for assumption_id in assumption_ids
        for count in range(len(parents[assumption_id]) + 1)
    }

    model.setObjective(
        gp.quicksum(importance_scores[assumption_id] * x[assumption_id]
                    for assumption_id in assumption_ids),
        GRB.MAXIMIZE,
    )
    model.addConstr(
        a * gp.quicksum(x[assumption_id] for assumption_id in assumption_ids)
        + gp.quicksum(
            (3 ** count) * z[assumption_id, count]
            for assumption_id in assumption_ids
            for count in range(len(parents[assumption_id]) + 1)
        )
        <= q_max,
        name="questionnaire_burden",
    )

    for assumption_id in assumption_ids:
        counts = range(len(parents[assumption_id]) + 1)
        model.addConstr(
            gp.quicksum(z[assumption_id, count] for count in counts)
            == x[assumption_id],
            name=f"indegree_state_{assumption_id}",
        )
        model.addConstr(
            gp.quicksum(count * z[assumption_id, count] for count in counts)
            == gp.quicksum(
                y[source, assumption_id]
                for source in parents[assumption_id]
            ),
            name=f"indegree_count_{assumption_id}",
        )

    for source, target in edges:
        model.addConstr(y[source, target] <= x[source])
        model.addConstr(y[source, target] <= x[target])
        model.addConstr(y[source, target] >= x[source] + x[target] - 1)

    model.optimize()
    if model.Status == GRB.INFEASIBLE:
        raise RuntimeError("The assumption selection model is infeasible.")
    if model.Status != GRB.OPTIMAL:
        raise RuntimeError(f"Gurobi did not prove optimality. Solver status: {model.Status}.")
    return [x[assumption_id].X > 0.5 for assumption_id in assumption_ids]


def optimize_from_files(
    model_file: str | Path,
    config_file: str | Path,
) -> list[bool]:
    """Load model and optimization YAML files and run the optimizer."""
    return optimize_assumption_selection(
        load_yaml(model_file),
        load_yaml(config_file),
    )
