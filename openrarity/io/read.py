import json
from pathlib import Path
from typing import Any


def from_json(
    path: str | Path,
) -> dict[str | int, dict[Any, Any]]:
    """
    Parses json file at provided path into python object.

    Parameters
    ----------
    path : str | Path
        File path to read the data from.

    Returns
    -------
    dict
        Returns Parsed json file at provided path into python object.
    """
    return json.loads(Path(path).read_text())
