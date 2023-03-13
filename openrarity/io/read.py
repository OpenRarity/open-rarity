import json
from pathlib import Path
from typing import Any


def from_json(
    path: str | Path,
) -> dict[str | int, dict[Any, Any]]:
    """
    Reads data from the given path and returns to the calling method.

    Parameters
    ----------
    path : str | Path
        File path to read the data from.

    Returns
    -------
    dict
        Returns the data back to calling method as a dict object.
    """
    return json.loads(Path(path).read_text())
