from itertools import chain
from typing import Any, cast

import numpy as np
from satchel.aggregate import groupapply

from openrarity.token import AttributeStatistic
from openrarity.token.types import ValidatedTokenAttribute
from openrarity.utils.data import merge


def generate_bins(values: list[float | int]) -> np.ndarray:
    return np.histogram_bin_edges(values, len(set(values)))


def pick_bin(name: str, value: float | int, attr_bins: dict[str, np.ndarray]):
    bins = attr_bins[name]
    bin: float = bins[np.where(bins <= value)[0][-1]]
    return bin


def process_numeric_dtypes(
    token_attrs: list[ValidatedTokenAttribute],
):
    grouped_values = groupapply(
        token_attrs,
        "name",
        lambda lst: [l["value"] for l in lst if l["value"] != "openrarity.null_trait"],
    )

    bins = {
        k: generate_bins(v)
        for k, v in cast(dict[str, list[int | float]], grouped_values).items()
    }
    binned = cast(
        list[dict[str, Any]],
        list(
            chain(
                *[
                    [
                        {
                            "name": name,
                            "value": value,
                            "bin": pick_bin(name, value, bins),
                        }
                        for value in cast(list[float | int], values)
                    ]
                    for name, values in grouped_values.items()
                ],
                *groupapply(
                    token_attrs,
                    "name",
                    lambda lst: [
                        {"name": l["name"], "value": l["value"], "bin": l["value"]}
                        for l in lst
                        if l["value"] == "openrarity.null_trait"
                    ],
                ).values()  # type: ignore
            )
        ),
    )
    merged = merge(
        token_attrs,  # type: ignore
        binned,
        ("name", "value"),
    )

    return cast(
        list[AttributeStatistic],
        merge(
            binned,
            [  # type: ignore
                cast(AttributeStatistic, {"name": k[0], "bin": k[1], **counts})  # type: ignore
                for k, counts in groupapply(  # type: ignore
                    merged,
                    lambda token: (token["name"], token["bin"]),  # type: ignore
                    lambda tokens: {
                        "attribute.token_count": len(tokens),
                        "attribute.supply": sum(t["token.supply"] for t in tokens),  # type: ignore
                    },
                ).items()
            ],
            ("name", "bin"),
        ),
    )
