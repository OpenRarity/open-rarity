from itertools import chain
from math import prod
from typing import cast

from satchel.aggregate import groupapply

from openrarity.token import RawToken, TokenAttribute, ValidatedTokenAttribute
from openrarity.token.types import TokenId, TokenStatistic


def   flatten_token_data(
    tokens: dict[TokenId, RawToken], token_supply: int | dict[str | int, int]
) -> list[ValidatedTokenAttribute]:
    """Denormalized and flatten token data. Attributes move to the top level and are
    assign a `token_id: <id>` key.

    Parameters
    ----------
    tokens : dict[TokenId, RawToken]
        Validated tokens data.
    token_supply: int | dict[str | int, int]
        Token supply value.

    Returns
    -------
    list[ValidatedTokenAttribute]
        Flattened list of token attributes data.
        Example : [{'token_id': '0', 'name': 'eyes', 'value': 'x eyes', 'token.supply': 1,'display_type':'string'},..]
    """
    is_nft = isinstance(token_supply, int)
    return list(
        chain(
            *[
                [
                    cast(
                        TokenAttribute,
                        {
                            "token_id": tid,
                            **attr,
                            "token.supply": 1 if is_nft else token_supply[tid],  # type: ignore
                        },
                    )
                    for attr in token["attributes"]
                ]
                for tid, token in tokens.items()
            ]
        )
    )


def calculate_token_statistics(
    attributes: list[TokenStatistic], entropy: float
) -> list[TokenStatistic]:
    """Calculates token statistics such as
        - metric.probability
        - metric.max_trait_information
        - metric.information
        - metric.unique_trait_count
        - metric.information_entropy
    Please look at the `TokenCollection` class and `rank_collection()` method for definitions.

    Parameters
    ----------
    attributes : list[TokenStatistic]
        List of intermediatery token statistics for a token.
    entropy : float
        Entropy value. Entropy is a measure of information in terms of uncertainity.

    Returns
    -------
    list[TokenStatistic]
        Returns aggregated token statistics from intermediatery token statistics.
    """
    stats = {
        "metric.probability": prod((t["metric.probability"] for t in attributes)),
        "metric.max_trait_information": max(
            (t["metric.information"] for t in attributes)
        ),
        "metric.information": sum((t["metric.information"] for t in attributes)),
        "metric.unique_trait_count": sum(
            t["attribute.token_count"]
            for t in attributes
            if t["attribute.token_count"] == 1
            # and t["value"] not in ["openrarity.null_trait"]
            # and t["name"] not in ["openrarity.trait_count"]
        ),
    }
    stats["metric.information_entropy"] = stats["metric.information"] / entropy
    return stats  # type: ignore


def aggregate_tokens(
    tokens: list[TokenStatistic], entropy: float | None = None
) -> list[TokenStatistic]:
    """Aggregate by the token_id and combine desired statistics for eventual ranking.

    Parameters
    ----------
    tokens : list[TokenStatistic]
        List of intermediatery token statistics for each token.
    entropy : float | None = None, optional
        Entropy value. Entropy is a measure of information in terms of uncertainity.

    Returns
    -------
    list[TokenStatistic]
        Agregated statistics for each token_id.
    """

    if entropy is None or entropy == 0.0:
        entropy = 1

    return [
        cast(
            TokenStatistic,
            {"token_id": tid, **cast(dict[str, str | float | int], stats)},
        )
        for tid, stats in groupapply(
            tokens,
            "token_id",
            lambda group: calculate_token_statistics(group, entropy),  # type: ignore
        ).items()
    ]
