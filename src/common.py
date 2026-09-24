"""Shared project configuration and validation helpers."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml


def find_project_root(start_path: str | Path | None = None) -> Path:
    """Find the project root containing the environment ``configs`` directory.

    Args:
        start_path: Directory from which to begin walking toward parent directories.
            Defaults to the current working directory.

    Returns:
        Path: The project root containing the ``configs`` directory.

    Raises:
        FileNotFoundError: If no project root can be found from the configured or
            supplied starting paths.
    """
    configured_root = os.environ.get("P1_PROJECT_ROOT")
    candidates: list[Path] = []
    if configured_root:
        candidates.append(Path(configured_root))

    start = Path(start_path) if start_path is not None else Path.cwd()
    start = start.resolve()
    candidates.append(start)
    candidates.extend(start.parents)

    visited: set[Path] = set()
    for candidate in candidates:
        root = candidate.resolve()
        if root in visited:
            continue
        visited.add(root)
        if (root / "configs").is_dir():
            return root

    raise FileNotFoundError(
        "Could not find the project root containing 'configs/'. "
        "Set P1_PROJECT_ROOT to the deployed project root if needed."
    )


def load_environment_config(
    environment: str, project_root: str | Path | None = None
) -> dict[str, Any]:
    """Load and validate ``configs/{environment}.yaml`` from the project root.

    Args:
        environment: Environment name used to select the YAML configuration file.
        project_root: Optional project root. If omitted, the root is discovered from
            ``P1_PROJECT_ROOT`` or the current working directory.

    Returns:
        dict[str, Any]: Parsed environment configuration.

    Raises:
        ValueError: If the environment name is invalid or the YAML root is not a
            mapping.
        FileNotFoundError: If the project root or environment configuration file
            cannot be found.
    """
    if not re.fullmatch(r"[A-Za-z0-9_-]+", environment):
        raise ValueError("Environment name may contain only letters, numbers, '_' or '-'.")

    root = find_project_root(project_root)
    config_path = root / "configs" / f"{environment}.yaml"
    if not config_path.is_file():
        raise FileNotFoundError(f"Environment configuration not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as stream:
        config = yaml.safe_load(stream)

    if not isinstance(config, dict):
        raise ValueError(f"Configuration file {config_path} must contain a YAML mapping.")
    return config


def required_text(mapping: dict[str, Any], key: str, setting: str) -> str:
    """Return a non-empty string configuration value or raise a safe error.

    Args:
        mapping: Configuration mapping containing the requested value.
        key: Key to retrieve from the mapping.
        setting: Human-readable setting path included in validation errors.

    Returns:
        str: The non-empty, whitespace-trimmed configuration value.

    Raises:
        ValueError: If the value is missing, not a string, or blank.
    """
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Required environment setting '{setting}' is not configured.")
    return value.strip()


def quote_qualified_identifier(identifier: str) -> str:
    """Validate and quote a simple Spark catalog/database identifier.

    Args:
        identifier: One or more dot-separated identifier components.

    Returns:
        str: The identifier with each component quoted for Spark SQL.

    Raises:
        ValueError: If a component contains characters outside letters, numbers,
            and underscores, or does not start with a letter or underscore.
    """
    parts = identifier.split(".")
    if not parts or any(not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", part) for part in parts):
        raise ValueError("Configured database/catalog name contains unsupported characters.")
    return ".".join(f"`{part}`" for part in parts)
