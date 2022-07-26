from collections import defaultdict
from dataclasses import dataclass
from functools import cached_property

from openrarity.models.chain import Chain
from typing import TYPE_CHECKING, Hashable

from openrarity.models.token_metadata import StringAttributeValue

# to avoid circular dependency
if TYPE_CHECKING:
    from openrarity.models.token import Token


@dataclass
class Collection(Hashable):
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

    @cached_property
    def extract_null_attributes(self) -> dict[str, StringAttributeValue]:
        """Compute probabilities of Null attributes.


        Returns
        -------
        dict[str, StringAttributeValue]
            dict of  attribute name to count of assets missing the attribute
        """
        result = {}

        if self.attributes_count:
            for trait_name, trait_values in self.attributes_count.items():

                total_trait_count = 0
                # To obtain probabilities for missing attributes
                # e.g. value of trait not set for the asset
                #
                # We sum all values counts for particular
                # attributes and subtract it from total supply.
                # This number divided by total supply is a
                # probability of Null attribute
                for _, count in trait_values.items():
                    total_trait_count = total_trait_count + count

                # compute null trait probability
                # only if there is a positive number of assets without
                # this trait
                assets_without_trait = (
                    self.token_total_supply - total_trait_count
                )
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

        collection_traits: dict[str, list[StringAttributeValue]] = defaultdict(
            list
        )

        if self.attributes_count:

            for trait_name, trait_value_dict in self.attributes_count.items():

                for trait_value, trait_count in trait_value_dict.items():

                    collection_traits[trait_name].append(
                        StringAttributeValue(
                            trait_name, trait_value, trait_count
                        )
                    )

        return collection_traits
