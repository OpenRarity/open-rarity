from itertools import chain
from typing import cast

import numpy as np
from satchel.aggregate import groupapply

from openrarity.token import AttributeStatistic
from openrarity.token.types import (
    ValidatedTokenAttribute,
    ValidatedTokenNumericAttribute,
)
from openrarity.utils.data import merge


def generate_bins(values: list[float | int]) -> np.ndarray:
    """Create bin edges for a set of values. Automatically sets the number of bins to
    the count of unique values in the set.

    Parameters
    ----------
    values : list[float  |  int]
        Numeric values to be binned.

    Returns
    -------
    np.ndarray
        Edges.
    """
    return np.histogram_bin_edges(values, len(set(values)))


def pick_bin(name: str, value: float | int, attr_bins: dict[str, np.ndarray]) -> float:
    """Assigns a value to a particular bin based on its name and value.

    Parameters
    ----------
    name : str
        The trait name.
    value : float | int
        Numeric value to be binned.
    attr_bins : dict[str, np.ndarray]
        A dictionary of trait name keys and an array of bin edges.

    Returns
    -------
    float
        The bin a value is assigned to.
    """
    bins = attr_bins[name]
    bin: float = bins[np.where(bins <= value)[0][-1]]
    return bin


# TODO: There is likely a lot of improvement on code efficiency/readability that can be done below
def process_numeric_dtypes(
    token_attrs: list[ValidatedTokenAttribute],
):
    """Process all numeric dtypes by assigning bins and counting the values.

    Parameters
    ----------
    token_attrs : list[ValidatedTokenAttribute]
        Flattened list of token attributes data. All the token attributes appeared in the same level as opposed to nested structure.

    Returns
    -------
    list[AttributeStatistic]
        AttributeStatistic augmented with `token_count` and `supply`.
    """
    # Find all null_traits and automatically assign them the null bin.
    null_trait_binned = cast(
        dict[str, list[dict[str, int | float | str]]],
        groupapply(
            token_attrs,
            "name",
            lambda lst: [
                {"name": l["name"], "value": l["value"], "bin": l["value"]}
                for l in lst
                if l["value"] == "openrarity.null_trait"
            ],
        ),
    )
    # TODO: this can likely be combined with the above step somehow to avoid an extra grouping
    # Group all other traits by their name and exclude null_trait
    grouped_values = groupapply(
        token_attrs,
        "name",
        lambda lst: [l["value"] for l in lst if l["value"] != "openrarity.null_trait"],
    )

    # Generate bin edges from the non null traits
    bins = {
        k: generate_bins(v)
        for k, v in cast(dict[str, list[int | float]], grouped_values).items()
    }

    # Assign each non null trait value to a bin
    non_null_binned = [
        [
            {
                "name": name,
                "value": value,
                "bin": pick_bin(name, value, bins),
            }
            for value in cast(list[float | int], values)
        ]
        for name, values in grouped_values.items()
    ]

    binned = list(chain(*non_null_binned, *null_trait_binned.values()))

    # Merge the original token_attrs with the superset of binned values
    # type: ignore
    def _token_key(token: ValidatedTokenNumericAttribute) -> tuple[str, float]:
        return (token["name"], token["bin"])

    merged_with_counts = [  # type: ignore
        cast(AttributeStatistic, {"name": k[0], "bin": k[1], **counts})  # type: ignore
        for k, counts in groupapply(
            merge(token_attrs, binned, ("name", "value")),  # type: ignore
            _token_key,
            lambda tokens: {
                "attribute.token_count": len(tokens),
                "attribute.supply": sum(t["token.supply"] for t in tokens),  # type: ignore
            },
        ).items()
    ]

    # Create the superset of bins and their token counts.
    return cast(
        list[AttributeStatistic],
        merge(
            cast(list[dict[str, int | float | str]], binned),
            merged_with_counts,  # type: ignore
            ("name", "bin"),
        ),
    )
