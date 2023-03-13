import json
from hashlib import md5
from itertools import chain
from logging import Logger
from pathlib import Path
from typing import Literal, TypedDict, cast, overload

from satchel.aggregate import groupapply

from openrarity.io import read, write
from openrarity.metrics.ic import calculate_entropy, information_content
from openrarity.token import (
    AttributeStatistic,
    RankedToken,
    RawToken,
    TokenId,
    TokenStatistic,
    ValidatedTokenAttribute,
    enforce_schema,
    validate_tokens,
)
from openrarity.token.metadata.dtypes import (
    process_numeric_dtypes,
    process_string_dtypes,
)
from openrarity.types import JsonEncodable
from openrarity.utils import merge, rank_over

from .utils import aggregate_tokens, flatten_token_data

logger = Logger(__name__)


class AttributesStatistics(TypedDict):
    """A class to represent Attribute Statistics."""
    string: list[AttributeStatistic]
    number: list[AttributeStatistic]
    date: list[AttributeStatistic]


class TokenCollection:
    """
    The TokenCollection class is the entrypoint for the majority of OpenRarity's functionality and handles all the parsing, validation, and ranking of the tokens.
    """

    def __init__(
        self,
        token_type: Literal["non-fungible", "semi-fungible"],
        tokens: dict[TokenId, RawToken],
    ):
        """
        Constructs all the necessary attributes for the `TokenCollection` object.

        Parameters
        ----------
        token_type :Literal["non-fungible", "semi-fungible"]
            type of the token.
        tokens : dict[TokenId, RawToken]
            a dictionary of individual tokens.

        Attributes
        ----------
        _token_type : Literal["non-fungible", "semi-fungible"]
            Type of the token.
        _input_checksum : str
            md5 hash of the tokens.
        _ranks_checksum : str
            md5 hash of ranks.
        _token_supply : int | dict[str | int, int]
            token supply value.
            Non-Fungible token_supply value is length of validated tokens.
            Semi-Fungible token_supply value is a dict of token_ids with their token_supply value.
        _tokens : dict[TokenId, RawToken]
            A dict of tokens.
        _token_attribute_data : list[ValidatedTokenAttribute]
            list of token attribute data.
        _attribute_statistics : AttributesStatistics
            Statistics based on the attributes.
        _entropy : float | None
            entrophy value.
        _token_statistics : list[TokenStatistic]
            statistics based on the tokens.
        _string_types : list[ValidatedTokenAttribute]
            Validated Token attributes of string type.
        _number_types : list[ValidatedTokenAttribute]
            Validated Token attributes of number type.
        _date_types : list[ValidatedTokenAttribute]
            Validated Token attributes of date type.
        _ranks : list[RankedToken]
            Token data with statistics and rank.
        """

        self._token_type = token_type
        self._input_checksum: str = self._hash_data(cast(JsonEncodable, tokens))
        self._ranks_checksum: str | None = None
        self._token_supply: int | dict[str | int, int]
        (self._token_supply, self._tokens) = validate_tokens(token_type, tokens)

        self._token_attribute_data: list[ValidatedTokenAttribute] = []
        self._attribute_statistics: AttributesStatistics = {
            "string": [],
            "number": [],
            "date": [],
        }
        self._entropy: float | None = None
        self._token_statistics: list[TokenStatistic] = []
        self._string_types: list[ValidatedTokenAttribute] = []
        self._number_types: list[ValidatedTokenAttribute] = []
        self._date_types: list[ValidatedTokenAttribute] = []

        # Output data
        self._ranks: list[RankedToken] = []

    def __repr__(self) -> str:
        return f"Collection({self._token_type})"

    @property
    def tokens(self) -> dict[TokenId, RawToken]:
        """Get the dictionary of token_ids and their attributes."""
        return self._tokens

    @property
    def total_supply(self) -> int:
        """Get the total_supply value of a collection."""
        # Non-Fungible `total_supply` value is nothing but length of tokens
        # SemiFungible needs to sum the supply of each token
        if isinstance(self._token_supply, dict):
            return sum(self._token_supply.values())

        return self._token_supply

    @property
    def attribute_statistics(self) -> AttributesStatistics:
        """Get the attribute_statistics."""
        if not self._attribute_statistics:
            raise AttributeError(
                f"Please run '{repr(self)}.rank_collection()' to view this property"
            )
        return self._attribute_statistics

    @property
    def entropy(self) -> float | None:
        """Get the entropy value."""
        return self._entropy

    @property
    def token_statistics(self) -> list[TokenStatistic]:
        """Get the token_statistics."""
        if not self._token_statistics:
            raise AttributeError(
                f"Please run '{repr(self)}.rank_collection()' to view this property"
            )
        return self._token_statistics

    @property
    def ranks(self) -> list[RankedToken]:
        """For each Token_id, get the ranks along with statistics."""
        if not self._ranks:
            raise AttributeError(
                f"Please run '{repr(self)}.rank_collection()' to view this property"
            )
        return self._ranks

    @property
    def checksum(self) -> str:
        """Get the sum of input_checksum and ranks_checksum."""
        if not self._ranks_checksum:
            raise AttributeError(
                f"Please run '{repr(self)}.rank_collection()' to view this property"
            )
        return self._input_checksum + self._ranks_checksum

    @overload
    def rank_collection(  # type: ignore
        self,
        rank_by: tuple[
            Literal[
                "metric.probability",
                "metric.information",
                "metric.information_entropy",
                "metric.unique_trait_count",
                "metric.max_trait_information",
            ],
            ...,
        ] = ("metric.unique_trait_count", "metric.information_entropy"),
        return_ranks: Literal[True] = True,
    ) -> list[RankedToken]:
        """An overloaded `rank_collection` method with `return_ranks` flag is True, which means it returns Ranks."""
        ...

    @overload
    def rank_collection(  # type: ignore
        self,
        rank_by: tuple[
            Literal[
                "metric.probability",
                "metric.information",
                "metric.information_entropy",
                "metric.unique_trait_count",
                "metric.max_trait_information",
            ],
            ...,
        ] = ("metric.unique_trait_count", "metric.information_entropy"),
        return_ranks: Literal[False] = False,
    ) -> None:
        """An overloaded `rank_collection` method with `return_ranks` flag is False, which means it returns None."""
        ...

    def rank_collection(
        self,
        rank_by: tuple[
            Literal[
                "metric.probability",
                "metric.information",
                "metric.information_entropy",
                "metric.unique_trait_count",
                "metric.max_trait_information",
            ],
            ...,
        ] = ("metric.unique_trait_count", "metric.information_entropy"),
        return_ranks: bool = True,
    ) -> list[RankedToken] | None:
        """Preprocess tokens then rank the tokens for the collection and set the
        corresponding cls.ranks attribute. Optionally, return the ranks.

        Notes
        -----
        metric.probability : float
            It is the Product of minimum value of (1,sum of `token.supply` values divided by `total_supply` value)
        metric.information : float
            It is the Sum of maximum value of (0, -log2(sum of `token.supply` values divided by `total_supply` value))
        metric.information_entropy : float
            It is the division value of `metric.information` and `entropy`
        metric.unique_trait_count : int
            It is the sum of unique `token_count` values
        metric.max_trait_information : float
            It is the maximum value of attribute statistics `metric.information`

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

        self.token_schema, self._token_attribute_data = enforce_schema(
            flatten_token_data(self._tokens, self._token_supply), self._token_supply
        )

        dtype_groups = cast(
            dict[Literal["string", "number", "date"], list[ValidatedTokenAttribute]],
            groupapply(self._token_attribute_data, "display_type"),
        )

        self._string_types = dtype_groups.setdefault("string", [])  # type: ignore
        self._number_types = dtype_groups.setdefault("number", [])  # type: ignore
        self._date_types = dtype_groups.setdefault("date", [])  # type: ignore

        _string_stats = process_string_dtypes(self._string_types)
        _number_stats = process_numeric_dtypes(self._number_types)
        _date_stats = process_numeric_dtypes(self._date_types)

        self._attribute_statistics = {
            "string": _string_stats,
            "number": _number_stats,
            "date": _date_stats,
        }

        self._attribute_statistics = cast(
            AttributesStatistics,
            {
                dtype: information_content(
                    self._attribute_statistics[dtype],  # type: ignore
                    self.total_supply,
                )
                for dtype in self._attribute_statistics
            },
        )
        self._entropy = calculate_entropy(
            [
                *self._attribute_statistics["string"],  # type: ignore
                *self._attribute_statistics["number"],  # type: ignore
                *self._attribute_statistics["date"],  # type: ignore
            ],
        )

        self._token_statistics = cast(
            list[TokenStatistic],
            merge(
                self._token_attribute_data,  # type: ignore
                list(chain(*self._attribute_statistics.values())),  # type: ignore
                ("name", "value"),
            ),
        )

        self._ranks = cast(
            list[RankedToken],
            rank_over(aggregate_tokens(self._token_statistics, self._entropy), rank_by),  # type: ignore
        )
        self._ranks_checksum = self._hash_data(self.ranks)  # type: ignore

        if return_ranks:
            return self._ranks
        return None

    @classmethod
    def from_json(
        cls, path: str | Path, token_type: Literal["non-fungible", "semi-fungible"]
    ) -> "TokenCollection":
        """Read TokenCollection class data from a json file.

        Parameters
        ----------
        path : str | PathLike
            File path to read the data.
        token_type : `non-fungible`|`semi-fungible`
            type of token.

        Returns
        -------
        TokenCollection
            Instantiated collection with tokens from json.
        """
        return cls(token_type, read.from_json(path))  # type: ignore

    def to_json(self, directory: str | Path, prefix: str, ranks_only: bool = True):
        """Dump TokenCollection class data into a json file.

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
                        "tokenAttributeData": self._token_attribute_data,
                        "attributeStatistics": self.attribute_statistics,
                        "tokenStatistics": self.token_statistics,
                    },
                ),
                directory / f"{prefix}_artifacts.json",
            )


    @classmethod
    def _hash_data(cls, data: JsonEncodable) -> str:
        """
        Simple hash function that first json encodes a data structure then md5 hashes
        the json string.

        Parameters
        ----------
        data : JsonEncodable
            input data.

        Returns
        -------
        str :
            md5 hash.
        """
        return md5(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()
