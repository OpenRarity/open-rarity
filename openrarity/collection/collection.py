import json
from hashlib import md5
from logging import Logger
from pathlib import Path
from typing import Literal, cast, overload

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
    ):
        self._token_type = token_type
        self._input_checksum: str = self._hash_data(cast(JsonEncodable, tokens))
        self._ranks_checksum: str | None = None
        self._token_supply: int | dict[str | int, int]
        (self._token_supply, self._tokens) = validate_tokens(token_type, tokens)

        # Derived data
        self._vertical_attribute_data: list[TokenAttribute] | None = None
        self._attribute_statistics: list[AttributeStatistic] | None = None
        self._token_statistics: list[TokenStatistic] | None = None

        self._ranks: list[RankedToken] | None = None

    def __repr__(self) -> str:
        return f"Collection({self._token_type})"

    @property
    def tokens(self) -> dict[TokenId, RawToken]:
        return self._tokens

    @property
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
    def rank_collection(  # type: ignore
        self,
        rank_by: tuple[
            Literal["unique_traits", "ic", "probability", "trait_count"], ...
        ] = ("unique_traits", "ic"),
        return_ranks: Literal[True] = True,
    ) -> list[RankedToken]:
        ...

    @overload
    def rank_collection(  # type: ignore
        self,
        rank_by: tuple[
            Literal["unique_traits", "ic", "probability", "trait_count"], ...
        ] = ("unique_traits", "ic"),
        return_ranks: Literal[False] = False,
    ) -> None:
        ...

    def rank_collection(
        self,
        rank_by: tuple[
            Literal["unique_traits", "ic", "probability", "trait_count"], ...
        ] = ("unique_traits", "ic"),
        return_ranks: bool = True,
    ) -> list[RankedToken] | None:
        """Preprocess tokens then rank the tokens for the collection and set the
        corresponding cls.ranks attribute. Optionally, return the ranks.


        Parameters
        ----------
        rank_by : tuple[ Literal[&quot;unique_traits&quot;, &quot;ic&quot;, &quot;probability&quot;, &quot;trait_count&quot;], ... ], optional
            Metrics to sort by when ranking, by default ("unique_traits", "ic")
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
        self._attribute_statistics = cast(
            list[AttributeStatistic],
            information_content(self._attribute_statistics, self.total_supply),  # type: ignore
        )

        # TODO: Add token statistics and aggregate
        self._token_statistics = cast(
            list[TokenStatistic],
            merge(
                self._vertical_attribute_data,  # type: ignore
                self._attribute_statistics,  # type: ignore
                ("name", "value"),
            ),
        )

        self._ranks = cast(
            list[RankedToken],
            rank_over(aggregate_tokens(self._token_statistics), rank_by),  # type: ignore
        )
        self._ranks_checksum = self._hash_data(self.ranks)  # type: ignore

        if return_ranks:
            return self._ranks
        return None

    @classmethod
    def from_json(
        cls, path: str | Path, token_type: Literal["non-fungible", "semi-fungible"]
    ) -> "TokenCollection":
        """_summary_

        Parameters
        ----------
        path : str | PathLike
            _description_
        token_type : &quot;non-fungible&quot; | &quot;semi-fungible&quot;
            _description_

        Returns
        -------
        TokenCollection
            Instantiated collection with tokens from json
        """
        return cls(token_type, read.from_json(path))  # type: ignore

    @classmethod
    def from_csv(
        cls, path: str | Path, token_type: Literal["non-fungible", "semi-fungible"]
    ) -> "TokenCollection":
        """_summary_

        Parameters
        ----------
        path : str | PathLike
            Path to csv of token data
        token_type : &quot;non-fungible&quot; | &quot;semi-fungible&quot;
            _description_

        Returns
        -------
        TokenCollection
            Instantiated collection with tokens from csv
        """
        raise NotImplementedError()
        return cls(token_type, read.from_csv(path))

    def to_json(self, directory: str | Path, prefix: str, ranks_only: bool = True):
        """Dump TokenCollection class to json file.

        Parameters
        ----------
        directory : str | PathLike
            Directory to write files.
        prefix : str
            The prefix to append to the filenames constructed as <prefix>_<data-kind>
        ranks_only : bool, optional
            A value of `True` only saves the rank data. A value of `False` will write
            intermediary data as well, by default True
        """
        directory = directory if isinstance(directory, Path) else Path(directory)
        write.to_json(self.ranks, directory / f"{prefix}_ranks.json")  # type: ignore
        if not ranks_only:
            write.to_json(
                cast(
                    JsonEncodable,
                    {
                        "input": self.tokens,
                        "verticalData": self._vertical_attribute_data,
                        "attributeStatistics": self.attribute_statistics,
                        "tokenStatistics": self.token_statistics,
                    },
                ),
                directory / f"{prefix}_artifacts.json",
            )

    def to_csv(self, directory: str | Path, prefix: str, ranks_only: bool = True):
        directory = directory if isinstance(directory, Path) else Path(directory)
        write.to_csv(self.ranks, directory / f"{prefix}_ranks.csv")  # type: ignore
        if not ranks_only:
            data = {
                "input": self.tokens,
                "verticalData": self._vertical_attribute_data,
                "attributeStatistics": self.attribute_statistics,
                "tokenStatistics": self.token_statistics,
            }
            for key in data:
                write.to_csv(  # type: ignore
                    data[key],
                    directory / f"{prefix}_{key}_artifact.csv",
                )

    @classmethod
    def _hash_data(cls, data: JsonEncodable) -> str:
        """Simple hash function that first json encodes a data structure then md5 hashes
        the json string.
        """
        return md5(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()
