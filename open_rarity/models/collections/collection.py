from os import PathLike
from typing import Literal, overload

from open_rarity.io import read, write
from open_rarity.metrics import information_content
from open_rarity.models.tokens import (
    RankedToken,
    RawToken,
    TokenIdMetadataAttr,
    validate_tokens,
)

from . import AttributeCounted
from ._utils import count_attribute_values, enforce_schema, flatten_token_data


class Collection:
    """Class represents collection of tokens used to determine token rarity score.
    A token's rarity is influenced by the attribute frequency of all the tokens
    in a collection.

    Attributes
    ----------
    tokens : list[Token]
        list of all Tokens that belong to the collection
    attributes_frequency_counts: dict[str, dict[AttributeValue, int]]
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

    def __init__(
        self,
        address: str,
        chain: Literal["EVM"],
        tokens: list[RawToken],
        **config,
    ):
        self._address = address
        self._chain = chain

        # TODO: Total Supply will need augmented for semi fungible tokens ie: ERC1155
        (self._total_supply, self._tokens) = validate_tokens(tokens)

        # Derived data
        self._vertical_attribute_data: list[TokenIdMetadataAttr] | None = None
        self._attribute_statistics: dict[tuple[str, str, int, float], int] = None
        self._ranks: list[RankedToken] = None

    def __str__(self) -> str:
        return self._address

    def __repr__(self) -> str:
        return f"Collection({self._address}, {self._chain})"

    @property
    def total_supply(self) -> int:
        return self._total_supply

    @property
    def attribute_statistics(self) -> list[AttributeCounted]:
        if not self._attribute_statistics:
            raise AttributeError(
                f"Please run '{repr(self)}.rank_collection()' to view this property"
            )
        return self._attribute_statistics

    @property
    def ranks(self) -> list[RankedToken]:
        if not self._ranks:
            raise AttributeError(
                f"Please run '{repr(self)}.rank_collection()' to view this property"
            )
        return self._ranks

    @overload
    def rank_collection(self, return_ranks=True) -> list[RankedToken]:
        ...

    @overload
    def rank_collection(self, return_ranks=False) -> None:
        ...

    def rank_collection(self, return_ranks=True) -> list[RankedToken] | None:
        """Preprocess tokens then rank the tokens for the collection and set the
        corresponding cls.ranks attribute. Optionally, return the ranks.

        Parameters
        ----------
        return_ranks : bool, optional
            Return the set ranks attribute, by default True

        Returns
        -------
        list[RankedToken] | None
            Ranked tokens
        """
        _vertical_attribute_data = flatten_token_data(self._tokens)
        self._token_schema, self._vertical_attribute_data = enforce_schema(
            _vertical_attribute_data
        )

        # TODO: This will be replaced with a TokenStandard specific handler
        self._attribute_statistics = count_attribute_values(
            self._vertical_attribute_data
        )
        self._attribute_statistics = information_content(
            self._attribute_statistics, self._total_supply
        )

        if return_ranks:
            return self._ranks

    def from_json(self, path: str | PathLike):
        raise NotImplementedError()
        read.from_json(self._ranks, path)

    def from_csv(self, path: str | PathLike):
        raise NotImplementedError()
        read.from_csv(self._ranks, path)

    def to_json(self, path: str | PathLike):
        write.to_json(self.ranks, path)

    def to_csv(self, path: str | PathLike):
        raise NotImplementedError()
        write.to_csv(self.ranks, path)
