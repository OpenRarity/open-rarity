from typing import Literal

from pydantic import BaseModel


class EVMContractTokenIdentifier(BaseModel):
    """This token is identified by the contract address and token ID number.

    This identifier is based off of the interface as defined by ERC721 and ERC1155,
    where unique tokens belong to the same contract but have their own numeral token id.
    """

    contract_address: str
    token_id: int
    identifier_type: Literal["evm_contract"] = "evm_contract"


class SolanaMintAddressTokenIdentifier(BaseModel):
    """This token is identified by their solana account address.

    This identifier is based off of the interface defined by the Solana SPL token
    standard where every such token is declared by creating a mint account.
    """

    mint_address: str
    identifier_type: Literal["solana_mint_address"] = "solana_mint_address"
