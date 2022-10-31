from typing import cast

from satchel.aggregate import groupapply

from ..types import AttributeStatistic, TokenAttribute


def count_attribute_values(tokens: list[TokenAttribute]) -> list[AttributeStatistic]:
    """Aggregate and count on the combination of (name, value).

    Parameters
    ----------
    tokens : list[TokenAttribute]
        Vertical token data to be aggregated.

    Returns
    -------
    dict[AttributeName, int]

    """

    return [  # type: ignore
        cast(AttributeStatistic, {"name": k[0], "value": k[1], "count": count})  # type: ignore
        for k, count in groupapply(
            tokens, lambda t: (t["name"], t["value"]), "count"  # type: ignore
        ).items()
    ]
