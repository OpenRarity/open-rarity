from dataclasses import dataclass

from open_rarity.models.token_identifier import TokenIdentifier
from open_rarity.models.token_metadata import TokenMetadata
from open_rarity.models.token_standard import TokenStandard
from open_rarity.models.utils.attribute_utils import normalize_attribute_string


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

    def __post_init__(self):
        self.metadata = self._normalize_metadata(self.metadata)

    def _normalize_metadata(self, metadata: TokenMetadata) -> TokenMetadata:
        """Normalizes token metadata to ensure the attribute names are lower cased
        and whitespace stripped to ensure equality consistency.

        Parameters
        ----------
        metadata : TokenMetadata
            The original token metadata

        Returns
        -------
        TokenMetadata
            A new normalized token metadata
        """

        def normalize_and_reset(attributes_dict: dict):
            """Helper function that takes in an attributes dictionary
            and normalizes both attribute name in the dictionary as the key
            and the repeated field inside the <Type>Attribute class
            """
            normalized_attributes_dict = {}

            for attribute_name, attr in attributes_dict.items():
                normalized_attr_name = normalize_attribute_string(
                    attribute_name
                )
                normalized_attributes_dict[normalized_attr_name] = attr
                if attr.name != normalized_attr_name:
                    attr.name = normalized_attr_name
            return normalized_attributes_dict

        return TokenMetadata(
            string_attributes=normalize_and_reset(metadata.string_attributes),
            numeric_attributes=normalize_and_reset(
                metadata.numeric_attributes
            ),
            date_attributes=normalize_and_reset(metadata.date_attributes),
        )

    def __str__(self):
        return f"Token[{self.token_identifier}]"
