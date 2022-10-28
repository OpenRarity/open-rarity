from collections import defaultdict
from itertools import chain
from math import prod
from typing import Iterable, cast

from satchel.aggregate import groupapply

from openrarity.token import AttributeStatistic, RawToken, TokenAttribute, TokenSchema
from openrarity.token.types import TokenId, TokenStatistic


def flatten_token_data(tokens: dict[TokenId, RawToken]) -> list[TokenAttribute]:
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
    return list(
        chain(
            *[
                [
                    cast(TokenAttribute, {"token_id": tid, **attr})
                    for attr in token["attributes"]
                ]
                for tid, token in tokens.items()
            ]
        )
    )


def extract_token_name_key(t: TokenAttribute) -> tuple[int | str, str]:
    """Stand in for returning the tuple key for grouping tokenattributes"""
    return t["token_id"], t["name"]


def _create_token_schema(tokens: list[TokenAttribute]) -> TokenSchema:
    """Create a schema that is representative of a token containing all possible
    attribute keys and the correct number of them.

    Parameters
    ----------
    tokens : list[TokenAttribute]
        _description_

    Returns
    -------
    TokenSchema
        _description_
    """
    d: dict[str, int] = defaultdict(int)

    for key, count in cast(
        Iterable[tuple[tuple[str, str], int]],
        groupapply(tokens, extract_token_name_key, "count").items(),  # type: ignore
    ):
        attr = key[1]
        d[attr] = max(count, d[attr])
    return dict(d)


def _create_null_values(
    tokens: list[TokenAttribute], schema: TokenSchema
) -> list[TokenAttribute]:
    """Use a provide schema of {name: expected_count} to generate null attribute values
    to add to the token data.

    Parameters
    ----------
    tokens : list[TokenAttribute]
        _description_
    schema : TokenSchema
        _description_

    Returns
    -------
    list[TokenAttribute]
        _description_
    """
    itemized_schema = set(schema.items())
    null_attrs: list[TokenAttribute] = []
    # The following will loop each token_id and and the counts of its individual
    # attributes. Those cound are compared against the expected schema via set
    # subtraction. Any misalignments are then reconciled by adding new values to the
    # token data with null values.
    for tid, counted_attrs in _count_token_attrs(tokens).items():
        if counted_attrs != schema:
            diffs = itemized_schema - set(counted_attrs.items())
            for name, expected_count in diffs:
                null_attrs.extend(
                    [
                        cast(
                            TokenAttribute,
                            {
                                "token_id": tid,
                                "name": name,
                                "value": "openrarity.null_trait",
                                "display_type": "string",
                            },
                        )
                    ]
                    * (expected_count - counted_attrs.get(name, 0))
                )
    return null_attrs


def _count_token_attrs(tokens: list[TokenAttribute]) -> dict[int, dict[str, int]]:
    """Aggregate by token_id then create a count of each attribute on that token.

    Parameters
    ----------
    tokens : list[TokenAttribute]
        _description_

    Returns
    -------
    dict[int, dict[str, int]]
        _description_
    """
    # TODO: Double groupapply. This can probably be flattened using a composite key of
    # (token_id, name) which should improve performance
    return cast(
        dict[int, dict[str, int]],
        groupapply(
            tokens, "token_id", lambda attrs: groupapply(attrs, "name", "count")
        ),
    )


def count_attribute_values(
    tokens: list[TokenAttribute],
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
    return [  # type: ignore
        cast(AttributeStatistic, {"name": k[0], "value": k[1], "count": count})  # type: ignore
        for k, count in groupapply(
            tokens, lambda t: (t["name"], t["value"]), "count"  # type: ignore
        ).items()
    ]


def enforce_schema(
    tokens: list[TokenAttribute],
) -> tuple[TokenSchema, list[TokenAttribute]]:
    """Enforce the token schema across the dataset to include attribute names where
    missing and nullify the appropriate attributes.

    Parameters
    ----------
    tokens : list[TokenAttribute]
        _description_
    schema : TokenSchema
        _description_

    Returns
    -------
    list[TokenAttribute]
        _description_
    """
    schema = _create_token_schema(tokens)
    return schema, sorted(
        [*tokens, *_create_null_values(tokens, schema)], key=lambda t: t["token_id"]
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
                "probability": prod((t["probability"] for t in group)),
                "max_trait_ic": max((t["ic"] for t in group)),
                "ic": sum((t["ic"] for t in group)),
                "unique_traits": sum((t["count"] for t in group if t["count"] == 1)),
            },
        ).items()
    ]
