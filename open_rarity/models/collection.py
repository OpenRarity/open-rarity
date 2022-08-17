from collections import defaultdict
from dataclasses import dataclass

from open_rarity.models.token import Token
from open_rarity.models.token_metadata import (
    AttributeName,
    AttributeValue,
    NumericAttribute,
    StringAttribute,
)


@dataclass
class CollectionAttribute:
    """Class represents an attribute that at least one token in a Collection has.
    E.g. "hat" = "cap" would be one attribute, and "hat" = "beanie" would be another
    unique attribute, even though they may belong to the same attribute type (id=name).

    Attributes
     ----------
    attribute : StringAttribute
        the unique attribute pair
    total_tokens : int
        total number of tokens in the collection that have this attribute
    """

    attribute: StringAttribute
    total_tokens: int


@dataclass
class Collection:
    """Class represents collection of tokens used to determine token rarity score.
    A token's rarity is influenced by the attribute frequency of all the tokens
    in a collection.

    Attributes
    ----------
    tokens : list[Token]
        list of all Tokens that belong to the collection
    attributes_frequency_counts: dict[AttributeName, dict[AttributeValue, int]]
        dictionary of attributes to the number of tokens in this collection that has
        a specific value for every possible value for the given attribute.

        Example:
            {"hair": {"brown": 500, "blonde": 100}
            which means 500 tokens has hair=brown, 100 token has hair=blonde
    name: A reference string only used for debugger log lines

    """

    attributes_frequency_counts: dict[AttributeName, dict[AttributeValue, int]]
    tokens: list[Token]
    name: str | None = ""

    @property
    def token_total_supply(self) -> int:
        return len(self.tokens)

    def total_tokens_with_attribute(self, attribute: StringAttribute) -> int:
        """Returns the numbers of tokens in this collection with the attribute
        based on the attributes frequency counts.

        Returns:
            int: The number of tokens with attribute (attribute_name, attribute_value)
        """
        return self.attributes_frequency_counts.get(attribute.name, {}).get(
            attribute.value, 0
        )

    def total_attribute_values(self, attribute_name: str) -> int:
        return len(self.attributes_frequency_counts.get(attribute_name, {}))

    def extract_null_attributes(
        self,
    ) -> dict[AttributeName, CollectionAttribute]:
        """Compute probabilities of Null attributes.

        Returns
        -------
        dict[AttributeName(str), CollectionAttribute(str)]
            dict of attribute name to the number of assets without the attribute
            (e.g. # of assets where AttributeName=NULL)
        """
        result = {}
        for (
            trait_name,
            trait_values,
        ) in self.attributes_frequency_counts.items():
            # To obtain probabilities for missing attributes
            # e.g. value of trait not set for the asset
            #
            # We sum all values counts for particular
            # attributes and subtract it from total supply.
            # This number divided by total supply is a
            # probability of Null attribute
            total_trait_count = sum(trait_values.values())

            # compute null trait probability
            # only if there is a positive number of assets without
            # this trait
            assets_without_trait = self.token_total_supply - total_trait_count
            if assets_without_trait > 0:
                result[trait_name] = CollectionAttribute(
                    attribute=StringAttribute(trait_name, "Null"),
                    total_tokens=assets_without_trait,
                )

        return result

    def extract_collection_attributes(
        self,
    ) -> dict[AttributeName, list[CollectionAttribute]]:
        """Extracts the map of collection traits with it's respective counts

        Returns
        -------
        dict[str, CollectionAttribute]
            dict of attribute name to count of assets missing the attribute
        """

        collection_traits: dict[str, list[CollectionAttribute]] = defaultdict(
            list
        )

        for (
            trait_name,
            trait_value_dict,
        ) in self.attributes_frequency_counts.items():
            for trait_value, trait_count in trait_value_dict.items():
                collection_traits[trait_name].append(
                    CollectionAttribute(
                        attribute=StringAttribute(
                            trait_name, str(trait_value)
                        ),
                        total_tokens=trait_count,
                    )
                )

        return collection_traits

    def __str__(self) -> str:
        return f"Collection[{self.name}]"
