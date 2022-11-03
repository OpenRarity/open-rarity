from typing import Literal, cast

from openrarity.metrics.trait_count import count_traits

from .metadata import validate_metadata
from .types import RawToken, TokenId


def trait_count(values: RawToken) -> RawToken:
    attrs = [
        dict(deduped)
        for deduped in {tuple(attr.items()) for attr in values["attributes"]}
    ]
    values["attributes"] = count_traits(attrs)  # type: ignore
    return values


def validate_token(
    token: RawToken, token_type: Literal["non-fungible", "semi-fungible"]
) -> RawToken:
    if token_type == "semi-fungible" and "token_supply" not in token:
        raise ValueError("token_supply")

    token["attributes"] = [validate_metadata(attr) for attr in token["attributes"]]

    return trait_count(token)


def validate_tokens(
    token_type: Literal["non-fungible", "semi-fungible"],
    tokens: dict[TokenId, RawToken],
) -> tuple[dict[TokenId, int] | int, dict[TokenId, RawToken]]:
    """Utitily function for validating a dictionary input of tokens mapped to an id.

    Parameters
    ----------
    token_type : &quot;non-fungible&quot; | &quot;semi-fungible&quot;
        _description_
    tokens : dict[TokenId, RawToken]
        _description_

    Returns
    -------
    tuple[int | dict[TokenId, int], dict[TokenId, RawToken]]
        _description_

    Raises
    ------
    NotImplementedError
        _description_
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
