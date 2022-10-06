import csv
import json
from os import PathLike
from pathlib import Path
from typing import Any


def to_json(data, path: str | PathLike):
    Path(path).write_text(json.dumps(data))


def to_csv(data, path: str | PathLike):
    ...
