from abc import ABC, abstractstaticmethod

from ..types import AttributeName, TokenIdMetadataAttr


class TokenStandard(ABC):
    @abstractstaticmethod
    def count_token_attributes(
        tokens: list[TokenIdMetadataAttr], **extras
    ) -> dict[AttributeName, int]:
        raise NotImplementedError()
