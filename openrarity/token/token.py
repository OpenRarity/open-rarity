from typing import Literal, cast

from openrarity.metrics.trait_count import count_traits

from .metadata import validate_metadata
from .types import RawToken, TokenId


def calculate_trait_count(values: RawToken) -> RawToken:
    """Count the number of traits on a given token and append it as an attribute named
    `openrarity.trait_count`.

    Parameters
    ----------
    tokens : RawToken
        Token attributes to be augmented with `openrarity.trait_count`.

    Returns
    -------
    RawToken
        Token attributes augmented with `openrarity.trait_count`.
    """
    attrs = [
        dict(deduped)
        for deduped in {tuple(attr.items()) for attr in values["attributes"]}
    ]
    values["attributes"] = count_traits(attrs)  # type: ignore
    return values


def validate_token(
    token: RawToken, token_type: Literal["non-fungible", "semi-fungible"]
) -> RawToken:
    """Utitily function for validating attributes a token.

    Parameters
    ----------
    token : RawToken
        A dictionary of token attributes.
    token_type : Literal["non-fungible", "semi-fungible"]
        Type of the token.

    Returns
    -------
    RawToken
        Validated token attributes augmented with `openrarity.trait_count`.

    Raises
    ------
    ValueError
        If we pass `semi-fungible` as a token_type and didn't provide `token_supply` then it will throw ValueError.
    """
    if token_type == "semi-fungible" and "token_supply" not in token:
        raise ValueError("token_supply")

    token["attributes"] = [validate_metadata(attr) for attr in token["attributes"]]

    return calculate_trait_count(token)


def validate_tokens(
    token_type: Literal["non-fungible", "semi-fungible"],
    tokens: dict[TokenId, RawToken],
) -> tuple[dict[TokenId, int] | int, dict[TokenId, RawToken]]:
    """
    Utitily function for validating a dictionary input of tokens mapped to an id. In the same time, it also returns `token_supply` value.
    Non-Fungible is the number of tokens in the collection where each token is unique while Semi-Fungible is a dict of token_ids with their token_supply value.

    Parameters
    ----------
    token_type : Literal["non-fungible", "semi-fungible"]
        Type of the token.
    tokens : dict[TokenId, RawToken]
        A dictionary of indivdual tokens to validate.

    Returns
    -------
    tuple[int | dict[TokenId, int], dict[TokenId, RawToken]]
        Returns the token_supply value and dictionary of validated tokens.
    """
    tokens = {id: validate_token(token, token_type) for id, token in tokens.items()}
    token_supply = (
        cast(
            dict[TokenId, int],
            {tid: token["token_supply"] for tid, token in tokens.items()},  # type: ignore
        )
        if token_type == "semi-fungible"
        else len(tokens)
    )
    return token_supply, tokens  # type: ignore
