from dataclasses import dataclass

from pydantic import BaseModel, parse_obj_as

from .identifier import (
    EVMContractTokenIdentifier,
    TokenIdentifier,
    get_identifier_class_from_dict,
)
from .metadata import TokenMetadata
from .standards import TokenStandard
from .types import MetadataAttribute, RawToken, TokenData


class Token(BaseModel):
    token_id: int | str
    attributes: list[TokenMetadata]


def validate_tokens(tokens: list[RawToken]) -> dict[int | str, TokenData]:
    tokens = [t.dict() for t in parse_obj_as(list[Token], tokens)]
    return len(tokens), tokens
