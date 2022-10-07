from open_rarity.models.tokens.types import AttributeName, TokenIdMetadataAttr

from ..base import TokenStandard


class ERC721(TokenStandard):
    @staticmethod
    def count_token_attributes(
        tokens: list[TokenIdMetadataAttr],
    ) -> dict[AttributeName, int]:
        ...
