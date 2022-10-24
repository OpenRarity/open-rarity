import json
from functools import cache
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
    TokenId,
    TokenStatistic,
    validate_tokens,
)
from openrarity.types import JsonEncodable
from openrarity.utils import merge, rank_over

from . import AttributeStatistic
from .utils import (
    aggregate_tokens,
    count_attribute_values,
    enforce_schema,
    flatten_token_data,
)

logger = Logger(__name__)


class TokenCollection:
    """ """

    def __init__(
        self,
        token_type: Literal["non-fungible", "semi-fungible"],
        tokens: dict[TokenId, RawToken],
        **config,
    ):
        self._token_type = token_type
        self._input_checksum: str = self._hash_data(tokens)
        self._ranks_checksum: str | None = None
        (self._token_supply, self._tokens) = validate_tokens(token_type, tokens)

        # Derived data
        self._vertical_attribute_data: list[TokenAttribute] | None = None
        self._attribute_statistics: list[AttributeStatistic] = None
        self._token_statistics: list[TokenStatistic] = None

        self._ranks: list[RankedToken] = None

    def __repr__(self) -> str:
        return f"Collection({self._token_type})"

    @property
    def tokens(self) -> list[RawToken]:
        return self._tokens

    @property
    @cache
    def total_supply(self) -> int:
        # SemiFungible needs to sum the supply of each token
        if isinstance(self._token_supply, dict):
            return sum(self._token_supply.values())

        return self._token_supply

    @property
    def attribute_statistics(self) -> list[AttributeStatistic]:
        if not self._attribute_statistics:
            raise AttributeError(
                f"Please run '{repr(self)}.rank_collection()' to view this property"
            )
        return self._attribute_statistics

    @property
    def token_statistics(self) -> list[TokenStatistic]:
        if not self._token_statistics:
            raise AttributeError(
                f"Please run '{repr(self)}.rank_collection()' to view this property"
            )
        return self._token_statistics

    @property
    def ranks(self) -> list[RankedToken]:
        if not self._ranks:
            raise AttributeError(
                f"Please run '{repr(self)}.rank_collection()' to view this property"
            )
        return self._ranks

    @property
    def checksum(self) -> str:
        if not self._ranks_checksum:
            raise AttributeError(
                f"Please run '{repr(self)}.rank_collection()' to view this property"
            )
        return self._input_checksum + self._ranks_checksum

    @overload
    def rank_collection(
        self,
        rank_by: tuple[
            Literal["unique_traits", "ic", "probability", "trait_count"], ...
        ] = ("unique_traits", "ic"),
        return_ranks=True,
    ) -> list[RankedToken]:
        ...

    @overload
    def rank_collection(
        self,
        rank_by: tuple[
            Literal["unique_traits", "ic", "probability", "trait_count"], ...
        ] = ("unique_traits", "ic"),
        return_ranks=False,
    ) -> None:
        ...

    def rank_collection(
        self,
        rank_by: tuple[
            Literal["unique_traits", "ic", "probability", "trait_count"], ...
        ] = ("unique_traits", "ic"),
        return_ranks=True,
    ) -> list[RankedToken] | None:
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

        # TODO: Process number/date display_type

        # TODO: This will be replaced with a TokenStandard specific handler
        self._attribute_statistics = count_attribute_values(
            self._vertical_attribute_data
        )
        self._attribute_statistics = information_content(
            self._attribute_statistics, self.total_supply
        )

        # TODO: Add token statistics and aggregate
        self._token_statistics = merge(
            self._vertical_attribute_data, self._attribute_statistics, ("name", "value")
        )

        self._ranks = rank_over(aggregate_tokens(self._token_statistics), rank_by)
        self._ranks_checksum = self._hash_data(self.ranks)

        if return_ranks:
            return self._ranks

    @classmethod
    def from_json(
        cls, path: str | PathLike, token_type: Literal["non-fungible", "semi-fungible"]
    ):
        return cls(token_type, read.from_json(path))

    @classmethod
    def from_csv(
        cls, path: str | PathLike, token_type: Literal["non-fungible", "semi-fungible"]
    ):
        return cls(token_type, read.from_csv(path))

    def to_json(self, directory: str | PathLike, prefix: str, ranks_only: bool = True):
        write.to_json(self.ranks, directory / f"{prefix}_ranks.json")
        if not ranks_only:
            write.to_json(
                {
                    "input": self.tokens,
                    "verticalData": self._vertical_attribute_data,
                    "attributeStatistics": self.attribute_statistics,
                    "tokenStatistics": self.token_statistics,
                },
                directory / f"{prefix}_artifacts.json",
            )

    def to_csv(self, directory: str | PathLike, prefix: str, ranks_only: bool = True):
        write.to_csv(self.ranks, directory / f"{prefix}_ranks.json")
        if not ranks_only:
            data = {
                "input": self.tokens,
                "verticalData": self._vertical_attribute_data,
                "attributeStatistics": self.attribute_statistics,
                "tokenStatistics": self.token_statistics,
            }
            for key in data:
                write.to_csv(
                    data[key],
                    directory / f"{prefix}_{key}_artifact.csv",
                )

    @classmethod
    def _hash_data(cls, data: JsonEncodable) -> str:
        return md5(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()
