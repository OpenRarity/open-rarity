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
    """
    A class to represent Attribute Statistic.
    AttributeStatistic :
        Attribute Statistics can be calculated by grouping `name` and `value` attributes.
        Attribute Statistics include
            - attribute.token_count
            - attribute.supply
            - metric.probability
            - metric.information
        For definitions, Please take a look at `rank_collection()` method.
    """
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
        token_type : Literal["non-fungible", "semi-fungible"]
            Type of the token.
        tokens : dict[TokenId, RawToken]
            A dictionary of raw token data.
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
        """Returns the raw input to the TokenCollection class.

        Attributes
        ----------
        _tokens : dict[TokenId, RawToken]
            A dictionary of tokens data.
        """
        return self._tokens

    @property
    def total_supply(self) -> int:
        """
        Get the total_supply value of a collection.
        Non-Fungible total_supply is the number of tokens in the collection where each token is unique while Semi-Fungible total_supply is the total quantity of tokens accounting for multiple of the same token.

        Attributes
        ----------
        _token_supply : int | dict[str | int, int]
            Token supply value.
            Non-Fungible is the number of tokens in the collection where each token is unique.
            Semi-Fungible token_supply value is a dict of token_ids with their token_supply value.
        """
        if isinstance(self._token_supply, dict):
            return sum(self._token_supply.values())

        return self._token_supply

    @property
    def attribute_statistics(self) -> AttributesStatistics:
        """
        Returns attribute_statistics. The attribute_statistics of a given collection is calculated by grouping `name` and `value` attributes.
        Attribute_statistics are
            - attribute.token_count
            - attribute.supply
            - metric.probability
            - metric.information
        For definitions, Please take a look at `rank_collection()` method.

        Attributes
        ----------
        _attribute_statistics : AttributesStatistics
            Statistics of a given collection grouped by `name` and `value` attributes.
        """
        if not self._attribute_statistics:
            raise AttributeError(
                f"Please run '{repr(self)}.rank_collection()' to view this property."
            )
        return self._attribute_statistics

    @property
    def entropy(self) -> float | None:
        """
        Returns the entropy value. It is a measure of information in terms of uncertainty.

        Attributes
        ----------
        _entropy : float | None
            Entropy value. Entropy is a measure of information in terms of uncertainity.
        """
        return self._entropy

    @property
    def token_statistics(self) -> list[TokenStatistic]:
        """Returns token_statistics. The Statistics of each token in a given collection grouped by `name` and `value` attributes.
        Token statistics are
            - attribute.token_count
            - attribute.supply
            - metric.probability
            - metric.information
            - metric.information_entropy
            - metric.unique_trait_count
            - metric.max_trait_information
        For definitions, Please take a look at `rank_collection()` method.

        Attributes
        ----------
        _token_statistics : list[TokenStatistic]
            Statistics of each token in a given collection grouped by `name` and `value` attributes.
        """
        if not self._token_statistics:
            raise AttributeError(
                f"Please run '{repr(self)}.rank_collection()' to view this property"
            )
        return self._token_statistics

    @property
    def ranks(self) -> list[RankedToken]:
        """For a given collection of tokens, returns rarity_ranks.

        Attributes
        ----------
        _ranks : list[RankedToken]
            Rarity ranks of each token.
        """
        if not self._ranks:
            raise AttributeError(
                f"Please run '{repr(self)}.rank_collection()' to view this property"
            )
        return self._ranks

    @property
    def checksum(self) -> str:
        """Calculates the checksum of both input and output data of a given collection.

        Attributes
        ----------
        _input_checksum : str
            MD5 hash of the raw token data.
        _ranks_checksum : str
            MD5 hash of ranks data.
        """
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
        """Preprocess tokens then rank the tokens for the collection and set the corresponding `cls.ranks` attribute. Optionally, return the ranks.

        Notes
        -----
        metric.probability
            The statistical probability/likelihood that a token exists in a collection.
            Example : The statistical probability that a token exists in a collection with orange background and blue eyes is calculated by the number of occurences of a token(orange background and blue eyes) to the total number of a tokens in a collection.
        metric.information
            The total information we gain from the token attributes. This information can be important in establishing the value and authenticity of the token.
            Example : Token attributes
                NFTs can have different attributes, such as color, size, or shape, which can be considered as information associated with the token.
        metric.information_entropy
            It is a measure of information in terms of uncertainty. Information Entropy is the sum of the product of probability and information content for each attribute.
            Example : Token attributes
                NFTs can have different attributes, such as color, size, shape, or even properties that change over time. The more diverse and unpredictable these attributes are, the higher the entropy of the NFT.
        metric.unique_trait_count
            It is the count of traits that are unique across the entire collection. Such as a NFT having the only blue hat in the collection.
        metric.max_trait_information
            It is the maximum information we gain from a single attribute of a token.
        attribute.token_count
            It is the number of tokens that have a particular name/value attribute pair.

        Parameters
        ----------
        rank_by : tuple[ Literal[&quot;unique_traits&quot;, &quot;ic&quot;, &quot;probability&quot;, &quot;trait_count&quot;], ... ], optional
            Metrics to sort by when ranking, by default ("unique_traits", "ic").
        return_ranks : bool, optional
            Return the set ranks attribute, by default True.

        Returns
        -------
        list[RankedToken] | None
            Returns a list of tokens with its rarity ranks.
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
            Json File path to read the data.
        token_type : Literal["non-fungible", "semi-fungible"]
            Type of a token.

        Returns
        -------
        TokenCollection
            Instantiated collection with tokens from json file.
        """
        return cls(token_type, read.from_json(path))  # type: ignore

    def to_json(self, directory: str | Path, prefix: str, ranks_only: bool = True):
        """Dump TokenCollection class data into a json file.

        Parameters
        ----------
        directory : str | PathLike
            Directory to write files.
        prefix : str
            The prefix to append to the filenames constructed as <prefix>_<data-kind>.
        ranks_only : bool, optional
            A value of `True` only saves the rank data. A value of `False` will write
            intermediary data as well, by default True.
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
            Input data.

        Returns
        -------
        str :
            MD5 hash value.
        """
        return md5(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()
