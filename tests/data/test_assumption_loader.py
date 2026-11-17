from __future__ import annotations

import yaml

from src.data.loaders import assumption_loader
from src.data.loaders.assumption_loader import AssumptionLoader


def _write_model(project_root, selected: bool | str) -> None:
    model_dir = project_root / "config" / "models"
    model_dir.mkdir(parents=True)
    model = {
        "assumption_set_name": "test_model",
        "version": "1.0",
        "assumptions": [
            {
                "id": "A1",
                "classification": "Test",
                "name": "Test assumption",
                "importance": 0.5,
                "description": "A test assumption.",
                "selected": selected,
            }
        ],
    }
    with (model_dir / "test_model.yaml").open("w", encoding="utf-8") as file:
        yaml.safe_dump(model, file)

    config_dir = project_root / "config"
    with (config_dir / "optimization.yaml").open("w", encoding="utf-8") as file:
        yaml.safe_dump({"Q_max": 50, "a": 6, "alpha": 0.75}, file)


def test_load_can_force_optimization_for_resolved_selections(tmp_path, monkeypatch):
    _write_model(tmp_path, selected=True)
    calls = []

    def optimize(model_data, optimization_config):
        calls.append((model_data, optimization_config))
        return [False]

    monkeypatch.setattr(assumption_loader, "optimize_assumption_selection", optimize)

    model = AssumptionLoader(project_root=tmp_path).load(
        "test_model",
        force_optimization=True,
    )

    assert len(calls) == 1
    assert model["assumptions"][0]["selected"] is False


def test_load_keeps_conditional_optimization_by_default(tmp_path, monkeypatch):
    _write_model(tmp_path, selected=True)
    calls = []
    monkeypatch.setattr(
        assumption_loader,
        "optimize_assumption_selection",
        lambda model_data, optimization_config: calls.append(model_data) or [False],
    )

    model = AssumptionLoader(project_root=tmp_path).load("test_model")

    assert calls == []
    assert model["assumptions"][0]["selected"] is True
