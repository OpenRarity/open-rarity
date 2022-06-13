from dataclasses import dataclass

from openrarity.models.collection import Collection
from openrarity.models.token_metadata import TokenMetadata


@dataclass
class Token:
    """Class represents Token class

    Attributes
    ----------
    token_id : int
        id of the token
    token_standard : str
        name of token standard (e.g. EIP-721 or EIP-1155)
    """

    token_id: int
    token_standard: str
    collection: Collection
    metadata: TokenMetadata
