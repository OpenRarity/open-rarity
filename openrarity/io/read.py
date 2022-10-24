import csv
import json
from os import PathLike
from pathlib import Path


def from_json(path: str | PathLike) -> list | dict:
    return json.loads(Path(path).read_text())


def from_csv(path: str | PathLike) -> list | dict:
    raise NotImplementedError()
