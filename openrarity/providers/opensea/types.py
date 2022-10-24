from typing import Literal, TypedDict

TraitType = str
TraitValue = str | float | int


class TokenIdentifier(TypedDict):
    contract_address: str
    token_id: int | str


class TokenAsset(TypedDict):
    token_identifier: TokenIdentifier
    token_standard: str | Literal["ERC721", "ERC1155"]
    metadata_dict: dict[TraitType, TraitValue]
