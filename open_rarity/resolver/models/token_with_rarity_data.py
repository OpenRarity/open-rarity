from dataclasses import dataclass
from enum import Enum
from open_rarity.models.token import Token


class RankProvider(Enum):
    # external ranking providers
    TRAITS_SNIPER = "traits_sniper"
    RARITY_SNIFFER = "rarity_sniffer"
    RARITY_SNIPER = "rarity_sniper"

    # open rarity scoring
    OR_ARITHMETIC = "or_arithmetic"
    OR_GEOMETRIC = "or_geometric"
    OR_HARMONIC = "or_harmonic"
    OR_SUM = "or_sum"
    OR_INFORMATION_CONTENT = "or_information_content"


EXTERNAL_RANK_PROVIDERS = [
    RankProvider.TRAITS_SNIPER,
    RankProvider.RARITY_SNIFFER,
    RankProvider.RARITY_SNIPER,
]

Rank = int
Score = float


@dataclass
class RarityData:
    provider: RankProvider
    rank: Rank
    score: Score | None = None


@dataclass
class TokenWithRarityData:
    token: Token
    rarities: list[RarityData]
