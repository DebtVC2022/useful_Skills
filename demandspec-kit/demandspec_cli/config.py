from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .resource_access import resource_path


def load_config(project: Path) -> dict[str, Any]:
    project_config = project.resolve() / ".demandspec" / "config.yaml"
    config_path = (
        project_config
        if project_config.exists()
        else resource_path("configs", "config.yaml")
    )
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Invalid DemandSpec config: {config_path}")
    return data
