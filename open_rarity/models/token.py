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

    def __init__(
        self,
        token_identifier: TokenIdentifier,
        token_standard: TokenStandard,
        metadata: TokenMetadata,
    ):
        self.token_identifier = token_identifier
        self.token_standard = token_standard
        self.metadata = self._normalize_metadata(metadata)

    def _normalize_metadata(self, metadata: TokenMetadata) -> TokenMetadata:
        def normalize_and_reset(attributes_dict, acc):
            # Helper function that takes in an attributes dictionary and accumulator
            # and normalizes both attribute name in the dictionary as the key
            # and the repeated field inside the <Type>Attribute class
            for attribute_name, str_attr in attributes_dict.items():
                normalized_attr_name = self._normalize_attribute_name(
                    attribute_name
                )
                acc[normalized_attr_name] = str_attr
                if str_attr.name != normalized_attr_name:
                    str_attr.name = normalized_attr_name
            return acc

        return TokenMetadata(
            string_attributes=normalize_and_reset(
                metadata.string_attributes, {}
            ),
            numeric_attributes=normalize_and_reset(
                metadata.numeric_attributes, {}
            ),
            date_attributes=normalize_and_reset(metadata.date_attributes, {}),
        )

    def _normalize_attribute_name(self, attribute_name: str) -> str:
        return attribute_name.lower().strip()

    def __str__(self):
        return f"Token[{self.token_identifier}]"
