from pydantic import BaseModel, root_validator

from openrarity.metrics.trait_count import count_traits

from .metadata import MetadataAttributeModel
from .types import RawToken, TokenId


class TokenModel(BaseModel):
    attributes: list[MetadataAttributeModel]

    @root_validator()
    def add_trait_count(cls, values):
        values["attributes"] = count_traits(values["attributes"])
        return values


def validate_tokens(
    tokens: dict[TokenId, RawToken]
) -> tuple[int, dict[int | str, RawToken]]:
    # TODO dedup (token_id, name, value)

    tokens = {tid: TokenModel(**token).dict() for tid, token in tokens.items()}
    return len(tokens), tokens
