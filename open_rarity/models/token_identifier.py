from dataclasses import dataclass
from typing import Annotated, Literal

from pydantic import Field


@dataclass
class EVMContractTokenIdentifier:
    """This token is identified by the contract address and token ID number.

    This identifier is based off of the interface as defined by ERC721 and ERC1155,
    where unique tokens belong to the same contract but have their own numeral token id.
    """

    contract_address: str
    token_id: int
    identifier_type: Literal["evm_contract"] = "evm_contract"

    def __str__(self):
        return f"Contract({self.contract_address}) #{self.token_id}"

    def __eq__(self, other):
        if not isinstance(other, EVMContractTokenIdentifier):
            return False

        return (
            self.contract_address == other.contract_address
            and self.token_id == other.token_id
            and self.identifier_type == other.identifier_type
        )

    def __hash__(self):
        return hash(
            (self.contract_address, self.token_id, self.identifier_type)
        )


@dataclass
class SolanaMintAddressTokenIdentifier:
    """This token is identified by their solana account address.

    This identifier is based off of the interface defined by the Solana SPL token
    standard where every such token is declared by creating a mint account.
    """

    mint_address: str
    identifier_type: Literal["solana_mint_address"] = "solana_mint_address"

    def __str__(self):
        return f"MintAddress({self.mint_address})"

    def __eq__(self, other):
        if not isinstance(other, SolanaMintAddressTokenIdentifier):
            return False

        return (
            self.mint_address == other.mint_address
            and self.identifier_type == other.identifier_type
        )

    def __hash__(self):
        return hash((self.mint_address, self.identifier_type))


# This is used to specifies how the collection is identified and the
# logic used to group the NFTs together
TokenIdentifier = Annotated[
    (EVMContractTokenIdentifier | SolanaMintAddressTokenIdentifier),
    Field(discriminator="identifier_type"),
]
