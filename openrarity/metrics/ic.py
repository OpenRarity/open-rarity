from math import log2

from openrarity.collection import AttributeStatistic


def information_content(
    counts: list[AttributeStatistic], total: int
) -> list[AttributeStatistic]:
    return [
        {
            **attr,
            "probability": attr["count"] / total,
            "ic": -log2(attr["count"] / total),
        }
        for attr in counts
    ]


def entropy(attr_stats: list[AttributeStatistic]):
    ...
