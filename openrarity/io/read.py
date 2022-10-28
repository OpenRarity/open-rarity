import json
from pathlib import Path
from typing import Any


def from_json(
    path: str | Path,
) -> dict[str | int, dict[Any, Any]]:
    return json.loads(Path(path).read_text())


def from_csv(path: str | Path) -> dict[str | int, dict[Any, Any]]:
    raise NotImplementedError()
