from dataclasses import dataclass

from openrarity.models.chain import Chain
from openrarity.models.token import Token


@dataclass
class Collection:
    """Class represents collection of tokens

    Attributes
    ----------
        name (str): name of an attribute
        contract_address (str): contract address
        creator_address (str): original creator address
        token_standard (str): name of the token standard
        chain (Chain): chain identifier
        token_total_supply (int): total supply of the tokens for the address
        tokens (list[Token]): list of all Tokens that belong to the collection
    """

    name: str
    contract_address: str
    creator_address: str
    token_standard: str
    chain: Chain
    token_total_supply: int
    tokens: list[Token]
