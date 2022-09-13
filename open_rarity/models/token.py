from dataclasses import dataclass

from open_rarity.models.token_identifier import TokenIdentifier
from open_rarity.models.token_metadata import TokenMetadata
from open_rarity.models.token_standard import TokenStandard


@dataclass
class Token:
    """Class represents a token on the blockchain.
    Examples of these are non-fungible tokens, or semi-fungible tokens.

    Attributes
    ----------
    token_identifier : TokenIdentifier
        data representing how the token is identified, which may be based
        on the token_standard or chain it lives on.
    token_standard : TokenStandard
        name of token standard (e.g. EIP-721 or EIP-1155)
    metadata: TokenMetadata
        contains the metadata of this specific token
    """

    token_identifier: TokenIdentifier
    token_standard: TokenStandard
    metadata: TokenMetadata

    def __str__(self):
        return f"Token[{self.token_identifier}]"
