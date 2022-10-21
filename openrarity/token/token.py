from typing import Literal, overload

from pydantic import BaseModel, root_validator

from openrarity.metrics.trait_count import count_traits

from .metadata import MetadataAttributeModel
from .types import RawToken, TokenId


class NonFungibleTokenModel(BaseModel):
    attributes: list[MetadataAttributeModel]

    @root_validator(pre=True)
    def add_trait_count(cls, values):
        attrs = [
            dict(deduped)
            for deduped in {tuple(attr.items()) for attr in values["attributes"]}
        ]
        values["attributes"] = count_traits(attrs)
        return values


class SemiFungibleTokenModel(NonFungibleTokenModel):
    token_supply: int


@overload
def validate_tokens(
    tokens: dict[TokenId, RawToken], token_type="non-fungible"
) -> tuple[int, dict[TokenId, RawToken]]:
    ...


@overload
def validate_tokens(
    tokens: dict[TokenId, RawToken], token_type="semi-fungible"
) -> tuple[dict[TokenId, int], dict[TokenId, RawToken]]:
    ...


def validate_tokens(
    token_type: Literal["non-fungible", "semi-fungible"],
    tokens: dict[TokenId, RawToken],
) -> tuple[int | dict[TokenId, int], dict[TokenId, RawToken]]:
    if token_type == "semi-fungible":
        raise NotImplementedError("SemiFungible tokens are not currently supported!")

    Validator = (
        SemiFungibleTokenModel
        if token_type == "semi-fungible"
        else NonFungibleTokenModel
    )
    tokens = {tid: Validator(**token).dict() for tid, token in tokens.items()}
    token_supply = (
        {tid: token["token_supply"] for tid, token in tokens.items()}
        if token_type == "semi-fungible"
        else len(tokens)
    )
    return token_supply, tokens
