from .identifier import (
    EVMContractTokenIdentifier,
    TokenIdentifier,
    get_identifier_class_from_dict,
)
from .metadata import TokenMetadata
from .standard import TokenStandard
from .types import MetadataAttribute, TokenData


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

    @classmethod
    def from_erc721(
        cls,
        contract_address: str,
        token_id: int,
        metadata: list[MetadataAttribute],
    ):
        """Creates a Token class representing an ERC721 evm token given the following
        parameters.

        Parameters
        ----------
        contract_address : str
            Contract address of the token
        token_id : int
            Token ID number of the token
        metadata : list[MetadataAttribute]
            Dictionary of attribute name to attribute value for the given token.
            The type of the value determines whether the attribute is a string,
            numeric or date attribute.

            class           attribute type
            ------------    -------------
            string          string attribute
            int | float     numeric_attribute
            datetime        date_attribute (stored as timestamp, seconds from epoch)

        Returns
        -------
        Token
            A Token instance with EVMContractTokenIdentifier and ERC721 standard set.
        """
        return cls(
            token_identifier=EVMContractTokenIdentifier(
                contract_address=contract_address, token_id=token_id
            ),
            token_standard=TokenStandard.ERC721,
            metadata=TokenMetadata.parse(metadata),
        )

    @classmethod
    def from_dict(cls, data_dict: TokenData):
        identifier_class = get_identifier_class_from_dict(data_dict["token_identifier"])

        return cls(
            token_identifier=identifier_class.from_dict(data_dict["token_identifier"]),
            token_standard=TokenStandard[data_dict["token_standard"]],
            metadata=TokenMetadata.parse(data_dict["metadata_dict"]),
        )

    def to_dict(self) -> dict:
        return {
            "token_identifier": self.token_identifier.to_dict(),
            "metadata_dict": self.metadata.to_attributes(),
            "token_standard": self.tokens.standard.name,
        }

    def __str__(self):
        return f"Token[{self.token_identifier}]"
