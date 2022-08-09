from dataclasses import dataclass
from open_rarity.models.collection import Collection


@dataclass
class CollectionWithMetadata:
    # This class is just used for resolving different rarity ranks from
    # various providers and allowing us to compare across rarity providers.
    collection: Collection
    contract_addresses: list[str]
    token_total_supply: int
    opensea_slug: str
