import json
from pathlib import Path

from openrarity.types import JsonEncodable


def to_json(data: JsonEncodable, path: str | Path):
    Path(path).write_text(json.dumps(data, sort_keys=True, indent=2))


def to_csv(data, path: str | Path):  # type: ignore
    raise NotImplementedError()
