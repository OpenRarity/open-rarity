import json
from pathlib import Path

from openrarity.types import JsonEncodable


def to_json(data: JsonEncodable, path: str | Path):
    """
    Write the Data into the given path in the form of JSON.

    Parameters
    ----------
    data : JsonEncodable
        Data to write into a file.
    path : str | Path
        File path to write the data into.
    """
    Path(path).write_text(json.dumps(data, sort_keys=True, indent=2))
