from typing import Literal, cast

from pydantic import BaseModel, root_validator

from openrarity.metrics.trait_count import count_traits

from .metadata import MetadataAttributeModel
from .types import MetadataAttribute, RawToken, TokenId


class NonFungibleTokenModel(BaseModel):
    """Validator for NonFungible tokens.

    Attributes are deduplicated on (name, value, display_type) and a `trait_count`
    attribute is added.
    """

    attributes: list[MetadataAttributeModel]

    @root_validator(pre=True)
    def add_trait_count(cls, values: RawToken):
        attrs = [
            cast(MetadataAttribute, dict(deduped))
            for deduped in {tuple(attr.items()) for attr in values["attributes"]}
        ]
        values["attributes"] = count_traits(attrs)
        return values


class SemiFungibleTokenModel(NonFungibleTokenModel):
    token_supply: int


# @overload
# def validate_tokens(
#     tokens: dict[TokenId, RawToken],
#     token_type: Literal["non-fungible"] = "non-fungible",
# ) -> tuple[int, dict[TokenId, RawToken]]:
#     ...


# @overload
# def validate_tokens(
#     tokens: dict[TokenId, RawToken],
#     token_type: Literal["semi-fungible"] = "semi-fungible",
# ) -> tuple[dict[TokenId, int], dict[TokenId, RawToken]]:
#     ...


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
    validator = (
        SemiFungibleTokenModel
        if token_type == "semi-fungible"
        else NonFungibleTokenModel
    )

    tokens = {
        tid: cast(
            RawToken,
            validator(**token).dict(),  # type: ignore
        )
        for tid, token in tokens.items()
    }

    token_supply = (
        cast(
            dict[TokenId, int],
            {tid: token["token_supply"] for tid, token in tokens.items()},  # type: ignore
        )
        if token_type == "semi-fungible"
        else len(tokens)
    )

    return token_supply, tokens  # type: ignore
