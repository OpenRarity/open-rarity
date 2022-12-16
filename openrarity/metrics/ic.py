from math import log2
from typing import cast

from openrarity.collection import AttributeStatistic


def information_content(
    counts: list[AttributeStatistic], total: int
) -> list[AttributeStatistic]:
    """Information Content is defined as the information in bits contained gained by
    some piece of data. It is the -log2(p(x)) and has units of `bits` for log base 2.

    This function uses a count of occurances and a total to calculate the information.

    Parameters
    ----------
    counts : list[AttributeStatistic]
        _description_
    total : int
        _description_

    Returns
    -------
    list[AttributeStatistic]
        The original attribute statistics augmented with probability and information
        content
    """

    return [
        cast(
            AttributeStatistic,
            {
                **attr,
                "metric.probability": min(1, attr["attribute.supply"] / total),
                "metric.information": max(0, -log2(attr["attribute.supply"] / total)),
            },
        )
        for attr in counts
    ]


def calculate_entropy(attr_stats: list[AttributeStatistic]) -> float:
    return sum(
        stat["metric.probability"] * stat["metric.information"]  # type: ignore
        for stat in attr_stats
    )
