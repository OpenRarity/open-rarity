import json
from hashlib import md5
from logging import Logger
from os import PathLike
from typing import Literal, overload

from openrarity.io import read, write
from openrarity.metrics.ic import information_content
from openrarity.token import (
    AttributeStatistic,
    RankedToken,
    RawToken,
    TokenAttribute,
    validate_tokens,
)

from . import AttributeCounted
from .utils import count_attribute_values, enforce_schema, flatten_token_data

logger = Logger(__name__)


class TokenCollection:
    """ """

    def __init__(
        self,
        token_type: Literal["non-fungible", "semi-fungible"],
        tokens: list[RawToken],  # TODO Change to dictionary with token_id key
        **config,
    ):
        self._token_type = token_type

        # TODO: Total Supply will need augmented for semi fungible tokens ie: ERC1155
        (self._total_supply, self._tokens) = validate_tokens(tokens)

        # Derived data
        self._vertical_attribute_data: list[TokenAttribute] | None = None
        self._attribute_statistics: list[AttributeStatistic] = None
        self._ranks: list[RankedToken] = None

    def __repr__(self) -> str:
        return f"Collection({self._token_type})"

    @property
    def tokens(self) -> list[RawToken]:
        return self._tokens

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

        # TODO: Process number display_type

        # TODO: This will be replaced with a TokenStandard specific handler
        self._attribute_statistics = count_attribute_values(
            self._vertical_attribute_data
        )
        self._attribute_statistics = information_content(
            self._attribute_statistics, self._total_supply
        )

        # TODO: Add token statistics and aggregate

        # TODO: Placeholder to suppress error
        self._ranks = ["ranks"]
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

    def checksum(self) -> str:
        logger.warn(
            "The checksum method has not been validated and should not be relied on for production use."
        )
        return (
            md5(json.dumps(self.tokens).encode("utf-8")).hexdigest()
            + md5(json.dumps(self.ranks).encode("utf-8")).hexdigest()
        )
