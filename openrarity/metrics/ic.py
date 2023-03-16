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
        List of attribute statistics. Attribute Statistics are statistics of a given collection grouped by `name` and `value` attributes.
    total : int
        Total supply value.
        Non-Fungible is the number of tokens in the collection where each token is unique while Semi-Fungible is the total quantity of tokens accounting for multiple of the same token.

    Returns
    -------
    list[AttributeStatistic]
        The original attribute statistics augmented with probability and information
        content.
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
    """
    Calculates entropy value.
    Entropy is a measure of information in terms of uncertainity. Higher uncertainity leads higher entropy.
    Example: Flipping a coin for Heads
        - Entropy is a measure of uncertainity before FLIP.
        - Information is the knowledge you have to gain after the FLIP.
    Information Entropy is the sum of the product of the probability and information content for each attribute.

    Parameters
    ----------
    attr_stats : list[AttributeStatistic]
        List of attribute statistics. Attribute Statistics are statistics of a given collection grouped by `name` and `value` attributes.

    Returns
    -------
    float
        Returns the entropy value.
    """
    return sum(
        stat["metric.probability"] * stat["metric.information"]  # type: ignore
        for stat in attr_stats
    )
