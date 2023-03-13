from typing import Literal, cast

from openrarity.metrics.trait_count import count_traits

from .metadata import validate_metadata
from .types import RawToken, TokenId


def trait_count(values: RawToken) -> RawToken:
    """Count the number of traits on a given token and append it as an attribute named
    openrarity.trait_count.

    Parameters
    ----------
    tokens : RawToken
        Tokens to be augmented with openrarity.trait_count.

    Returns
    -------
    RawToken
        RawToken augmented with openrarity.trait_count.
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
    """Utitily function for validating attributes of individual tokens.

    Parameters
    ----------
    token : RawToken
        a dictionary containing token attributes.
    token_type :`non-fungible`|`semi-fungible`
        type of the token.

    Returns
    -------
    RawToken
        Tokens augmented with openrarity.trait_count.

    Raises
    ------
    ValueError
        if we pass `semi-fungible` as a token_type and didn't provide `token_supply` then it will throw ValueError.
    """
    if token_type == "semi-fungible" and "token_supply" not in token:
        raise ValueError("token_supply")

    token["attributes"] = [validate_metadata(attr) for attr in token["attributes"]]

    return trait_count(token)


def validate_tokens(
    token_type: Literal["non-fungible", "semi-fungible"],
    tokens: dict[TokenId, RawToken],
) -> tuple[dict[TokenId, int] | int, dict[TokenId, RawToken]]:
    """Utitily function for validating a dictionary input of tokens mapped to an id.
    Non-Fungible token_supply value is length of validated tokens.
    Semi-Fungible token_supply value is a dict of token_ids with their token_supply value.

    Parameters
    ----------
    token_type : &quot;non-fungible&quot; | &quot;semi-fungible&quot;
        non-fungible or semi-fungible token type.
    tokens : dict[TokenId, RawToken]
        a dictionary of indivdual tokens.

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
