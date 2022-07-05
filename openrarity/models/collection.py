from dataclasses import dataclass

from openrarity.models.chain import Chain
from typing import TYPE_CHECKING

# to avoid circular dependency
if TYPE_CHECKING:
    from openrarity.models.token import Token


@dataclass
class Collection:
    """Class represents collection of tokens

    Attributes
    ----------
    name : str
        name of the collection
    slug : str
        collection slug
    contract_address : str
        contract address
    creator_address : str
        original creator address
    token_standard : str
        name of the token standard
    chain : Chain
        chain identifier
    token_total_supply : int
        total supply of the tokens for the address
    tokens : list[Token]
        list of all Tokens that belong to the collection
    attributes_count: dict[str, dict[str, int]]
        dictionary of attributes and their total counts
    """

    name: str
    slug: str
    contract_address: str
    creator_address: str
    token_standard: str
    chain: Chain
    token_total_supply: int
    tokens: list["Token"]
    attributes_count: dict[str, dict[str, int]]
