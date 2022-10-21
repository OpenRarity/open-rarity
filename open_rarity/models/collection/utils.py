from collections import defaultdict
from itertools import chain

from satchel import groupapply

from open_rarity.models.token import (
    AttributeName,
    RawToken,
    TokenAttribute,
    TokenSchema,
)
from open_rarity.models.token.types import TokenId


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
                [{"token_id": tid, **attr} for attr in token["attributes"]]
                for tid, token in tokens.items()
            ]
        )
    )


def extract_token_name_key(t: TokenAttribute) -> tuple[int | str, str]:
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
    d = defaultdict(int)
    for key, count in groupapply(tokens, extract_token_name_key, "count").items():
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
    null_attrs = []
    for tid, counted_attrs in _count_token_attrs(tokens).items():
        if counted_attrs != schema:
            diffs = itemized_schema - set(counted_attrs.items())
            for name, expected_count in diffs:
                null_attrs.extend(
                    [
                        {
                            "token_id": tid,
                            "name": name,
                            "value": "openrarity.null_trait",
                            "display_type": "string",
                        }
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
    return groupapply(
        tokens, "token_id", lambda attrs: groupapply(attrs, "name", "count")
    )


def count_attribute_values(
    tokens: list[TokenAttribute],
) -> dict[AttributeName, int]:
    """Aggregate and count on the combination of (name, value).

    Parameters
    ----------
    tokens : list[TokenAttribute]
        Vertical token data to be aggregated.

    Returns
    -------
    dict[AttributeName, int]

    """
    return [
        {"name": k[0], "value": k[1], "count": count}
        for k, count in groupapply(
            tokens, lambda t: (t["name"], t["value"]), "count"
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
