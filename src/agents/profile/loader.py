from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .schema import (
    BackgroundSpec,
    DistributionSpec,
    EvaluatorPopulationSpec,
    RoleSpec,
    TraitModifier,
    TraitSpec,
)


class ProfileConfigLoader:
    """
    Load evaluator profile specifications from YAML configuration files.

    This class is responsible only for configuration parsing and
    conversion into schema objects. It does not perform sampling,
    background modification, or agent generation.
    """

    def load_role(self, path: str | Path) -> RoleSpec:
        """Load a RoleSpec from a YAML file."""
        data = self._load_yaml(path)

        return RoleSpec(
            name=self._require(data, "name"),
            description=data.get("description", ""),
            expertise=data.get("expertise", {}),
            base_traits=self._parse_traits(
                data.get("base_traits", {})
            ),
            default_attention_weights=data.get(
                "default_attention_weights", {}
            ),
            default_concerns=data.get(
                "default_concerns", []
            ),
            evidence_preference=data.get(
                "evidence_preference"
            ),
        )

    def load_background(
        self,
        path: str | Path,
    ) -> BackgroundSpec:
        """Load a BackgroundSpec from a YAML file."""
        data = self._load_yaml(path)

        return BackgroundSpec(
            name=self._require(data, "name"),
            description=data.get("description", ""),
            traits=self._parse_modifiers(
                data.get("traits", {})
            ),
            attention_weights=data.get(
                "attention_weights", {}
            ),
            concerns=data.get("concerns", []),
            contextual_information=data.get(
                "contextual_information", {}
            ),
        )

    def load_population(
        self,
        path: str | Path,
        *,
        role_loader: ProfileConfigLoader | None = None,
        background_loader: ProfileConfigLoader | None = None,
    ) -> EvaluatorPopulationSpec:
        """
        Load an EvaluatorPopulationSpec from a YAML file.

        The population configuration references a role and optionally
        a background. Role/background can be specified either as a
        YAML file path or as a name resolved by the corresponding
        loader.
        """
        data = self._load_yaml(path)

        role = self._load_role_reference(
            data.get("role"),
            role_loader,
            Path(path).parent,
        )

        background = self._load_background_reference(
            data.get("background"),
            background_loader,
            Path(path).parent,
        )

        return EvaluatorPopulationSpec(
            name=self._require(data, "name"),
            role=role,
            background=background,
            traits=self._parse_traits(
                data.get("traits", {})
            ),
            attention_weights=data.get(
                "attention_weights", {}
            ),
            concerns=data.get(
                "concerns",
                [],
            ),
            evidence_preference=data.get(
                "evidence_preference"
            ),
            size=data.get("size", 1),
        )

    @staticmethod
    def _load_yaml(path: str | Path) -> dict[str, Any]:
        """Read a YAML file and return its top-level mapping."""
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(
                f"Profile configuration not found: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Profile configuration path is not a file: {path}"
            )

        with path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        if data is None:
            return {}

        if not isinstance(data, dict):
            raise ValueError(
                f"Expected a YAML mapping in {path}, "
                f"got {type(data).__name__}."
            )

        return data

    @staticmethod
    def _require(
        data: dict[str, Any],
        key: str,
    ) -> Any:
        """Return a required configuration field."""
        if key not in data:
            raise ValueError(
                f"Missing required field: '{key}'."
            )

        return data[key]

    @staticmethod
    def _parse_traits(
        traits: dict[str, Any],
    ) -> dict[str, TraitSpec]:
        """Convert YAML trait definitions into TraitSpec objects."""
        parsed: dict[str, TraitSpec] = {}

        for name, config in traits.items():
            if not isinstance(config, dict):
                raise ValueError(
                    f"Trait '{name}' must be a mapping."
                )

            distribution_config = config.get(
                "distribution"
            )

            if not isinstance(distribution_config, dict):
                raise ValueError(
                    f"Trait '{name}' must define a "
                    "'distribution' mapping."
                )

            distribution = DistributionSpec(
                distribution=distribution_config.get(
                    "distribution"
                ),
                mean=distribution_config.get("mean"),
                std=distribution_config.get("std"),
                low=distribution_config.get("low"),
                high=distribution_config.get("high"),
                alpha=distribution_config.get("alpha"),
                beta=distribution_config.get("beta"),
            )

            parsed[name] = TraitSpec(
                distribution=distribution,
                min_value=config.get(
                    "min_value",
                    0.0,
                ),
                max_value=config.get(
                    "max_value",
                    1.0,
                ),
            )

        return parsed

    @staticmethod
    def _parse_modifiers(
        modifiers: dict[str, Any],
    ) -> dict[str, TraitModifier]:
        """Convert YAML trait modifiers into TraitModifier objects."""
        parsed: dict[str, TraitModifier] = {}

        for name, config in modifiers.items():
            if not isinstance(config, dict):
                raise ValueError(
                    f"Trait modifier '{name}' must be a mapping."
                )

            parsed[name] = TraitModifier(
                mean_shift=config.get(
                    "mean_shift",
                    0.0,
                ),
                std_multiplier=config.get(
                    "std_multiplier",
                    1.0,
                ),
            )

        return parsed

    @staticmethod
    def _load_role_reference(
        reference: Any,
        loader: ProfileConfigLoader | None,
        base_dir: Path,
    ) -> RoleSpec:
        """
        Resolve a role reference.

        A role can currently be supplied as:
        1. an inline mapping, or
        2. a YAML file path.
        """
        if isinstance(reference, dict):
            return ProfileConfigLoader._role_from_dict(reference)

        if isinstance(reference, str):
            if loader is None:
                loader = ProfileConfigLoader()

            role_path = Path(reference)

            if not role_path.is_absolute():
                role_path = base_dir / role_path

            return loader.load_role(role_path)

        raise ValueError(
            "Population 'role' must be a mapping or YAML file path."
        )

    @staticmethod
    def _load_background_reference(
        reference: Any,
        loader: ProfileConfigLoader | None,
        base_dir: Path,
    ) -> BackgroundSpec | None:
        """
        Resolve an optional background reference.

        A background can currently be supplied as:
        1. an inline mapping, or
        2. a YAML file path.
        """
        if reference is None:
            return None

        if isinstance(reference, dict):
            return ProfileConfigLoader._background_from_dict(
                reference
            )

        if isinstance(reference, str):
            if loader is None:
                loader = ProfileConfigLoader()

            background_path = Path(reference)

            if not background_path.is_absolute():
                background_path = base_dir / background_path

            return loader.load_background(background_path)

        raise ValueError(
            "Population 'background' must be a mapping, "
            "YAML file path, or null."
        )

    @staticmethod
    def _role_from_dict(
        data: dict[str, Any],
    ) -> RoleSpec:
        """Create a RoleSpec from an inline mapping."""
        return RoleSpec(
            name=ProfileConfigLoader._require(
                data,
                "name",
            ),
            description=data.get(
                "description",
                "",
            ),
            expertise=data.get(
                "expertise",
                {},
            ),
            base_traits=ProfileConfigLoader._parse_traits(
                data.get(
                    "base_traits",
                    {},
                )
            ),
            default_attention_weights=data.get(
                "default_attention_weights",
                {},
            ),
            default_concerns=data.get(
                "default_concerns",
                [],
            ),
            evidence_preference=data.get(
                "evidence_preference"
            ),
        )

    @staticmethod
    def _background_from_dict(
        data: dict[str, Any],
    ) -> BackgroundSpec:
        """Create a BackgroundSpec from an inline mapping."""
        return BackgroundSpec(
            name=ProfileConfigLoader._require(
                data,
                "name",
            ),
            description=data.get(
                "description",
                "",
            ),
            traits=ProfileConfigLoader._parse_modifiers(
                data.get(
                    "traits",
                    {},
                )
            ),
            attention_weights=data.get(
                "attention_weights",
                {},
            ),
            concerns=data.get(
                "concerns",
                [],
            ),
            contextual_information=data.get(
                "contextual_information",
                {},
            ),
        )