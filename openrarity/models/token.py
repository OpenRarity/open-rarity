from dataclasses import dataclass, field
from enum import Enum

from openrarity.models.token_metadata import TokenMetadata
from openrarity.models.collection import Collection


class RankProvider(Enum):
    # external ranks
    TRAITS_SNIPER = 1
    RARITY_SNIFFER = 2
    RARITY_SNIPER = 3
    # open rarity scorring
    OR_ARITHMETIC = 4
    OR_GEOMETRIC = 5
    OR_HARMONIC = 6
    OR_SUM = 7
    OR_INFORMATION_CONTENT = 8


Rank = tuple[RankProvider, int]


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
    ranks: list[Rank] = field(default_factory=list)
