from collections import defaultdict
from dataclasses import dataclass
from functools import cached_property

from openrarity.models.chain import Chain
from typing import Hashable
from openrarity.models.collection_identifier import (
    CollectionIdentifier,
    OpenseaCollectionIdentifier,
    ContractAddressCollectionIdentifier,
)
from openrarity.models.token_identifier import EVMContractTokenIdentifier

from openrarity.models.token_metadata import (
    AttributeName,
    AttributeValue,
    StringAttributeValue,
)

from openrarity.models.token import Token


@dataclass
class Collection(Hashable):
    """Class represents collection of tokens

    Attributes
    ----------
    identifier : CollectionIdentifier
        how a collection is identified (e.g. by the contract address or some other metadata)
    name : str
        name of the collection
    chain : Chain
        chain identifier
    token_total_supply : int
        total supply of the tokens for the address
    tokens : list[Token]
        list of all Tokens that belong to the collection
    attributes_distribution: dict[AttributeName, dict[AttributeValue, int]]
        dictionary of attributes and the distribution of
        the number of tokens in this collection that has a specific value.
        Example:
            {"hair": {"brown": 500, "blonde": 100}
            which means 500 tokens has hair=brown, 100 token has hair=blonde

    """

    identifier: CollectionIdentifier
    name: str
    chain: Chain
    attributes_distribution: dict[AttributeName, dict[AttributeValue, int]]
    _tokens: list[Token] = []

    @property
    def tokens(self) -> list[Token]:
        return self._tokens

    @tokens.setter
    def tokens(self, v: list[Token]) -> None:
        self._tokens = v
        # Reset caches that calculate on tokens
        if self.token_identifier_types:
            del self.token_identifier_types
        if self.extract_null_attributes:
            del self.extract_null_attributes

    @property
    def token_total_supply(self) -> int:
        return len(self.tokens)

    @cached_property
    def token_identifier_types(self) -> list[str]:
        """Returns the list of unique token identifier types that tokens
        in this collection exhibits.
        This property is intended for easier processing for identifier/chain-specific logic.
        """
        return list(set([token.token_identifier.identifier_type for token in self.tokens]))

    @cached_property
    def contract_addresses(self) -> list[str]:
        """Returns unique list of all contract addresses that tokens of this collection
        belong to, if relevant.
        Note: Currently only relevant to EVM tokens
        """
        if isinstance(self.identifier, ContractAddressCollectionIdentifier):
            return self.identifier.contract_addresses
        elif self.token_identifier_types == [EVMContractTokenIdentifier.identifier_type]:
            return list(set([token.token_identifier.contract_address for token in self.tokens]))  # type: ignore
        else:
            return []

    @property
    def opensea_slug(self) -> str | None:
        """Sugar for a collection's slug in opensea.
        Made as a property since other api's also use the same slug as input and may be needed
        to pull rarity data (e.g. raritysniper api).
        """
        if isinstance(self.identifier, OpenseaCollectionIdentifier):
            return self.identifier.slug
        return None

    @cached_property
    def extract_null_attributes(self) -> dict[AttributeName, StringAttributeValue]:
        """Compute probabilities of Null attributes.

        Returns
        -------
        dict[AttributeName(str), StringAttributeValue(str)]
            dict of attribute name to the number of assets without the attribute
            (e.g. # of assets where AttributeName=NULL)
        """
        result = {}

        if self.attributes_distribution:
            for trait_name, trait_values in self.attributes_distribution.items():

                total_trait_count = 0
                # To obtain probabilities for missing attributes
                # e.g. value of trait not set for the asset
                #
                # We sum all values counts for particular
                # attributes and subtract it from total supply.
                # This number divided by total supply is a
                # probability of Null attribute
                for count in trait_values.values():
                    total_trait_count = total_trait_count + count

                # compute null trait probability
                # only if there is a positive number of assets without
                # this trait
                assets_without_trait = self.token_total_supply - total_trait_count
                if assets_without_trait > 0:
                    result[trait_name] = StringAttributeValue(
                        trait_name,
                        "Null",
                        assets_without_trait,
                    )

        return result

    def extract_collection_attributes(
        self,
    ) -> dict[str, list[StringAttributeValue]]:
        """Extracts the map of collection traits with it's respective counts

        Returns
        -------
        dict[str, StringAttributeValue]
            dict of  attribute name to count of assets missing the attribute
        """

        collection_traits: dict[str, list[StringAttributeValue]] = defaultdict(list)

        if self.attributes_distribution:
            for trait_name, trait_value_dict in self.attributes_distribution.items():
                for trait_value, trait_count in trait_value_dict.items():
                    collection_traits[trait_name].append(
                        StringAttributeValue(trait_name, str(trait_value), trait_count)
                    )

        return collection_traits

    def __str(self):
        return f"Collection[{self.identifier}]"
