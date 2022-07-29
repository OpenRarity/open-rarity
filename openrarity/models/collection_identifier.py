from dataclasses import dataclass
from typing import Literal, Annotated
from pydantic import Field

@dataclass
class OpenseaCollectionIdentifier:
    '''This collection is based on the nfts that belong to the same opensea
    collection as described in the opensea api, which takes in slug as identifier.
    This may contain nfts belonging to several contract addresses if the
    collection creators/owners chose to merge.
    '''
    identifier_type: Literal['opensea']
    slug: str

    def __str__(self):
        return f"slug={self.slug}"

@dataclass
class ContractAddressCollectionIdentifier:
    '''This collection only consists of nfts from these contract addresses
    '''
    identifier_type: Literal['contract_address']
    contract_addresses: list[str]

    def __str__(self):
        return f"contract_addresses={self.contract_addresses}"

@dataclass
class SolanaMetaplexCollectionIdentifier:
    '''
    This collection consists of nfts that have the same on-chain verified
    collection address defined in metaplex metadata.
    '''
    identifier_type: Literal['solana_metaplex_collection_address']
    metaplex_collection_address: str

    def __str__(self):
        return f"metaplex_collection_address={self.metaplex_collection_address}"

# This is used to specifies how the collection is identified and the
# logic used to group the NFTs together
CollectionIdentifier = Annotated[
    (
		OpenseaCollectionIdentifier |
		ContractAddressCollectionIdentifier |
		SolanaMetaplexCollectionIdentifier
    )
  ,
  Field(discriminator='identifier_type')
]