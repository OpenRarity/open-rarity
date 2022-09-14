from collections import defaultdict
from dataclasses import dataclass
from functools import cached_property

from open_rarity.models.token import Token
from open_rarity.models.token_metadata import (
    AttributeName,
    AttributeValue,
    StringAttribute,
)
from open_rarity.models.token_standard import TokenStandard
from open_rarity.models.utils.attribute_utils import normalize_attribute_string


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

        If not provided, the attributes distribution will be derived from the
        attributes on the tokens provided.

        Example:
            {"hair": {"brown": 500, "blonde": 100}
            which means 500 tokens has hair=brown, 100 token has hair=blonde

        Note: All trait names and string values should be lowercased and stripped
        of leading and trialing whitespace.
        Note 2: We currently only support string attributes.

    name: A reference string only used for debugger log lines

    We do not recommend resetting @tokens attribute after Collection initialization
    as that will mess up cached property values:
        has_numeric_attributes
        get_token_standards
    """

    attributes_frequency_counts: dict[AttributeName, dict[AttributeValue, int]]
    name: str

    def __init__(
        self,
        tokens: list[Token],
        attributes_frequency_counts: dict[
            AttributeName, dict[AttributeValue, int]
        ]
        | None = None,
        name: str | None = "",
    ):
        self._tokens = tokens
        self.name = name or ""
        if attributes_frequency_counts:
            self.attributes_frequency_counts = (
                self._normalize_attributes_frequency_counts(
                    attributes_frequency_counts
                )
            )
        else:
            self.attributes_frequency_counts = (
                self._derive_normalized_attributes_frequency_counts()
            )

    @property
    def tokens(self) -> list[Token]:
        return self._tokens

    @property
    def token_total_supply(self) -> int:
        return len(self._tokens)

    @cached_property
    def has_numeric_attribute(self) -> bool:
        return (
            next(
                filter(
                    lambda t: len(t.metadata.numeric_attributes)
                    or len(t.metadata.date_attributes),
                    self._tokens,
                ),
                None,
            )
            is not None
        )

    @cached_property
    def token_standards(self) -> list[TokenStandard]:
        """Returns token standards for this collection.

        Returns
        -------
        list[TokenStandard]
            the set of unique token standards that any token in this collection
            interfaces or uses.
        """
        token_standards = set()
        for token in self._tokens:
            token_standards.add(token.token_standard)
        return list(token_standards)

    def total_tokens_with_attribute(self, attribute: StringAttribute) -> int:
        """Returns the numbers of tokens in this collection with the attribute
        based on the attributes frequency counts.

        Returns
        -------
        int
            The number of tokens with attribute (attribute_name, attribute_value)
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

    def _normalize_attributes_frequency_counts(
        self,
        attributes_frequency_counts: dict[
            AttributeName, dict[AttributeValue, int]
        ],
    ) -> dict[AttributeName, dict[AttributeValue, int]]:
        """We normalize all collection attributes to ensure that neither casing nor
        leading/trailing spaces produce different attributes:
            (e.g. 'Hat' == 'hat' == 'hat ')
        If a collection has the following in their attributes frequency counts:
            ('Hat', 'beanie') 5 tokens and
            ('hat', 'beanie') 10 tokens
        this would produce: ('hat', 'beanie') 15 tokens
        """
        normalized: dict[AttributeName, dict[AttributeValue, int]] = {}
        for (
            attr_name,
            attr_value_to_count,
        ) in attributes_frequency_counts.items():
            normalized_name = normalize_attribute_string(attr_name)
            if normalized_name not in normalized:
                normalized[normalized_name] = {}
            for attr_value, attr_count in attr_value_to_count.items():
                normalized_value = (
                    normalize_attribute_string(attr_value)
                    if isinstance(attr_value, str)
                    else attr_value
                )
                if normalized_value not in normalized[normalized_name]:
                    normalized[normalized_name][normalized_value] = attr_count
                else:
                    normalized[normalized_name][normalized_value] += attr_count

        return normalized

    def _derive_normalized_attributes_frequency_counts(
        self,
    ) -> dict[AttributeName, dict[AttributeValue, int]]:
        """Derives and constructs attributes_frequency_counts based on
        string attributes on tokens. Numeric or date attributes currently not
        supported.

        Returns
        -------
        dict[ AttributeName, dict[AttributeValue, int] ]
            dictionary of attributes to the number of tokens in this collection
            that has a specific value for every possible value for the given
            attribute, by default None.
        """
        attrs_freq_counts: dict[
            AttributeName, dict[AttributeValue, int]
        ] = defaultdict(dict)

        for token in self._tokens:
            for (
                attr_name,
                str_attr,
            ) in token.metadata.string_attributes.items():
                normalized_name = normalize_attribute_string(attr_name)
                if str_attr.value not in attrs_freq_counts[attr_name]:
                    attrs_freq_counts[normalized_name][str_attr.value] = 1
                else:
                    attrs_freq_counts[normalized_name][str_attr.value] += 1

        return dict(attrs_freq_counts)

    def __str__(self) -> str:
        return f"Collection[{self.name}]"
