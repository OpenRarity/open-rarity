from itertools import chain
from math import prod
from typing import cast

from satchel.aggregate import groupapply

from openrarity.token import RawToken, TokenAttribute, ValidatedTokenAttribute
from openrarity.token.types import TokenId, TokenStatistic


def flatten_token_data(
    tokens: dict[TokenId, RawToken], token_supply: int | dict[str | int, int]
) -> list[ValidatedTokenAttribute]:
    """Denormalized and flatten token data. Attributes move to the top level and are
    assign a `token_id: <id>` key.

    Parameters
    ----------
    tokens : list[Token]
        _description_

    Returns
    -------
    list[TokenAttribute]
        _description_
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


def aggregate_tokens(tokens: list[TokenStatistic]) -> list[TokenStatistic]:
    """Aggregate by the token_id and combine desired statistics for eventual ranking.

    Parameters
    ----------
    tokens : list[TokenStatistic]
        Input token statistics with the following data structure.

        [
            {
                token_id: int,
                name: str,
                value: str | float | int,
                count: int,
                probability: float,
                ic: float,
            }
        ]

    Returns
    -------
    list[TokenStatistic]
        Agregated statistics for each token_id.

        [
            {
                token_id: int,
                count: int,
                probability: float,
                max_trait_ic: float,
                ic: float,
                unique_traits: int,
            }
        ]
    """
    return [
        cast(
            TokenStatistic,
            {"token_id": tid, **cast(dict[str, str | float | int], stats)},
        )
        for tid, stats in groupapply(
            tokens,
            "token_id",
            lambda group: {
                "metric.probability": prod((t["metric.probability"] for t in group)),
                "metric.max_trait_information": max(
                    (t["metric.information"] for t in group)
                ),
                "metric.information": sum((t["metric.information"] for t in group)),
                "metric.unique_trait_count": sum(
                    (
                        t["attribute.token_count"]
                        for t in group
                        if t["attribute.token_count"] == 1
                    )
                ),
            },
        ).items()
    ]
