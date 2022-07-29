from dataclasses import dataclass
from enum import Enum
from openrarity.models.token import Token

class RankProvider(Enum):
    # external ranking providers
    TRAITS_SNIPER = 'traits_sniper'
    RARITY_SNIFFER = 'rarity_sniffer'
    # open rarity scoring
    OR_ARITHMETIC = 'or_arithmetic'
    OR_GEOMETRIC = 'or_geometric'
    OR_HARMONIC = 'or_harmonic'
    OR_SUM = 'or_sum'
    OR_INFORMATION_CONTENT = 'or_information_content'

Rank = int
Score = int | float

@dataclass
class RarityData:
    provider: RankProvider
    rank: Rank
    score: Score | None

@dataclass
class TokenWithRarityData:
    token: Token
    rarities: list[RarityData]
