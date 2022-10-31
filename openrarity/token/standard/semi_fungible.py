from typing import cast

from satchel.aggregate import groupapply

from openrarity.utils.data import merge

from ..types import AttributeStatistic, TokenAttribute


def count_attribute_values(
    tokens: list[TokenAttribute], token_supply: dict[str | int, int]
) -> list[AttributeStatistic]:
    """Aggregate and count on the combination of (name, value).

    Parameters
    ----------
    tokens : list[TokenAttribute]
        Vertical token data to be aggregated.

    Returns
    -------
    dict[AttributeName, int]

    """
    tokens = merge(
        tokens,  # type: ignore
        [{"token_id": k, "openrarity.supply": v} for k, v in token_supply.items()],
        ("token_id",),
    )

    return [  # type: ignore
        cast(AttributeStatistic, {"name": k[0], "value": k[1], "count": count})  # type: ignore
        for k, count in groupapply(
            tokens,  # type: ignore
            lambda t: (t["name"], t["value"]),  # type: ignore
            lambda group: sum((g["openrarity.supply"] for g in group)),  # type: ignore
        ).items()
    ]
