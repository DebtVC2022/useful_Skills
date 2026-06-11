from __future__ import annotations

from importlib.resources import files
from pathlib import Path


def resource_root() -> Path:
    return Path(str(files("demandspec_cli.resources")))


def resource_path(*parts: str) -> Path:
    return resource_root().joinpath(*parts)
