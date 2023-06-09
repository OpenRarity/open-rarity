from collections import defaultdict
from datetime import datetime
from logging import Logger
from typing import Iterable, cast

from satchel.aggregate import groupapply

from openrarity.token import AttributeName, TokenSchema, ValidatedTokenAttribute
from openrarity.validators.string import clean_lower_string

logger = Logger(__name__)

NULL_TRAIT = "openrarity.null_trait"


def validate_metadata(values):
    """
    Validates `trait_type` defaulting to `string` and formats the `name` and `value` fields.

    Parameters
    ----------
    values : dict
        Input token attributes to validate.

    Returns
    -------
    values : dict
        Returns the validated attributes dictionary.
    """
    if "trait_type" in values:
        values["name"] = values.pop("trait_type")

    values["display_type"] = values.setdefault("display_type", "string")
    value = values["value"]
    # Force a coercion to `string` if the display_type is unknown
    match values["display_type"]:
        case "number":
            values["value"] = float(value)
        case "date":
            values["value"] = (
                value
                if isinstance(value, (int | float))
                else float(value) if isinstance(value, str) and value.replace(".", "").isdigit()
                else datetime.fromisoformat(value).timestamp()
            )
        case _:
            values["display_type"] = "string"
            # values["value"] = (
            #     NULL_TRAIT
            #     if (string := clean_lower_string(str(value))) in ("none", "")
            #     else string
            # )
            values["value"] = clean_lower_string(str(value))

    values["name"] = clean_lower_string(str(values["name"]))

    return values


def extract_token_name_key(t: ValidatedTokenAttribute) -> tuple[int | str, str, str]:
    """Stand in for returning the tuple key for grouping token attributes."""
    return t["token_id"], t["name"], t["display_type"]


def _create_token_schema(tokens: list[ValidatedTokenAttribute]) -> TokenSchema:
    """Create a schema that is representative of a token containing all possible
    attribute keys and the correct number of them.

    Parameters
    ----------
    tokens : list[ValidatedTokenAttribute]
        List of Validated Token attributes.

    Returns
    -------
    TokenSchema
        Returns the schema that is representative of a token, containing every available trait name across all tokens in the collection and the correct number of them.
        Example schema will be {('eyes', 'string'): 1,('hat', 'string'): 1}.

    """
    d: dict[tuple[str, str], int] = defaultdict(int)

    for key, count in cast(
        Iterable[tuple[tuple[str, str, str], int]],
        groupapply(tokens, extract_token_name_key, "count").items(),  # type: ignore
    ):
        attr = (key[1], key[2])
        d[attr] = max(count, d[attr])
    return dict(d)


def _count_token_attrs(
    tokens: list[ValidatedTokenAttribute],
) -> dict[int, dict[tuple[str, str], int]]:
    """Aggregate by token_id then create a count of each attribute on that token.

    Parameters
    ----------
    tokens : list[ValidatedTokenAttribute]
        List of validated token attribute data.

    Returns
    -------
    dict[int, dict[tuple[str, str], int]]
        Returns the aggregated data grouped by token_id.
    """
    # TODO: Double groupapply. This can probably be flattened using a composite key of
    # (token_id, name) which should improve performance
    return cast(
        dict[int, dict[str, int]],
        groupapply(
            tokens,
            "token_id",
            lambda attrs: groupapply(
                attrs, lambda a: (a["name"], a["display_type"]), "count"  # type: ignore
            ),
        ),
    )


def _create_null_values(
    tokens: list[ValidatedTokenAttribute],
    schema: TokenSchema,
    token_supply: int | dict[str | int, int],
) -> list[ValidatedTokenAttribute]:
    """Use a provide schema of {name: expected_count} to generate null attribute values
    to add to the token data.

    Parameters
    ----------
    tokens : list[ValidatedTokenAttribute]
        List of validated token attributes.
    schema : TokenSchema
        Schema that is representative of a token containing all possible attribute keys and the correct number of them.
    token_supply : int | dict[str | int, int]
        Token Supply Value.
        Non-Fungible is the number of tokens in the collection where each token is unique.
        Semi-Fungible token_supply value is a dict of token_ids with their token_supply value.

    Returns
    -------
    list[ValidatedTokenAttribute]
        Returns a list of token attributes which is having null_trait.
    """
    is_nft = isinstance(token_supply, int)
    itemized_schema = set(schema.items())
    null_attrs: list[ValidatedTokenAttribute] = []
    # The following will loop each token_id and and the counts of its individual
    # attributes. Those cound are compared against the expected schema via set
    # subtraction. Any misalignments are then reconciled by adding new values to the
    # token data with null values.
    for tid, counted_attrs in _count_token_attrs(tokens).items():
        if counted_attrs != schema:
            diffs = itemized_schema - set(counted_attrs.items())
            for (name, dtype), expected_count in diffs:
                name = cast(AttributeName, name)
                null_attrs.extend(
                    [
                        cast(
                            ValidatedTokenAttribute,
                            {
                                "token_id": tid,
                                "name": name,
                                "value": NULL_TRAIT,
                                "display_type": dtype,
                                "token.supply": 1 if is_nft else token_supply[tid],  # type: ignore
                            },
                        )
                    ]
                    * (expected_count - counted_attrs.get((name, dtype), 0))
                )
    return null_attrs


def enforce_schema(
    tokens: list[ValidatedTokenAttribute], token_supply: int | dict[str | int, int]
) -> tuple[TokenSchema, list[ValidatedTokenAttribute]]:
    """Enforce the token schema across the dataset to include attribute names where
    missing and nullify the appropriate attributes.

    Parameters
    ----------
    tokens : list[ValidatedTokenAttribute]
        Validated token attribute data.
    token_supply: int | dict[str | int, int]
        Token supply value.
        Non-Fungible is the number of tokens in the collection where each token is unique.
        Semi-Fungible token_supply value is a dict of token_ids with their token_supply value.

    Returns
    -------
    tuple[TokenSchema, list[ValidatedTokenAttribute]]
        A tuple of token schema and token data. Here null_trait attribute data is appended to the given attribute data.
    """
    schema = _create_token_schema(tokens)
    return schema, [*tokens, *_create_null_values(tokens, schema, token_supply)]
