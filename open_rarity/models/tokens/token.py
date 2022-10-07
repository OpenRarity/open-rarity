from pydantic import BaseModel, parse_obj_as

from . import RawToken, TokenMetadata


class Token(BaseModel):
    token_id: int | str
    attributes: list[TokenMetadata]


def validate_tokens(tokens: list[RawToken]) -> tuple[int, dict[int | str, RawToken]]:
    tokens = [t.dict() for t in parse_obj_as(list[Token], tokens)]
    return len(tokens), tokens
