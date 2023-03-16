from typing_extensions import NotRequired, TypedDict

AttributeName = str
AttributeValue = str | int | float
TokenId = int | str


class MetadataAttribute(TypedDict):
    """This class represents specific metadata information of a token. This metadata information is also known as trait of a token, traits are the specific properties of each NFT has."""
    name: str
    value: str | int | float
    display_type: NotRequired[str | None]


class RawToken(TypedDict):
    """This represents all the metadata information of a token. In otherwords, it represents a list of properties that each token has."""
    attributes: list[MetadataAttribute]
    token_supply: NotRequired[dict[str | int, int]]


class TokenAttribute(TypedDict):
    """
    This class is to represent tokens and their attributes in the same level as opposed to nested structure.
    Example : [{'token_id': '0', 'name': 'eyes', 'value': 'x eyes', 'display_type':string}].
    """
    token_id: int
    name: str
    value: str | int | float
    display_type: NotRequired[str | None]


ValidatedTokenAttribute = TypedDict(
    "ValidatedTokenAttribute",
    {
        "token_id": int,
        "name": str,
        "value": str | int | float,
        "display_type": str,
        "token.supply": int,
    },
)
ValidatedTokenNumericAttribute = TypedDict(
    "ValidatedTokenNumericAttribute",
    {
        "token_id": int,
        "name": str,
        "value": str | int | float,
        "display_type": str,
        "token.supply": int,
        "bin": float,
    },
)


AttributeStatistic = TypedDict(
    "AttributeStatistic",
    {
        "name": str,
        "value": str | int | float,
        "attribute.token_count": int,
        "attribute.supply": int,
        "metric.probability": float,
        "metric.information": float,
    },
)

TokenStatistic = TypedDict(
    "TokenStatistic",
    {
        "token_id": str | int,
        "name": str,
        "value": str,
        "attribute.token_count": int,
        "attribute.supply": int,
        "metric.probability": float,
        "metric.information": float,
        "metric.information_entropy": NotRequired[float],
        "metric.unique_trait_count": NotRequired[int],
        "metric.max_trait_information": NotRequired[float],
    },
)


RankedToken = TypedDict(
    "RankedToken",
    {
        "token_id": str | int,
        "metric.probability": float,
        "metric.information": float,
        "metric.unique_trait_count": int,
        "metric.max_trait_information": float,
        "rank": int,
    },
)

TokenSchema = dict[tuple[AttributeName, str], int]

__all__ = [
    "AttributeName",
    "AttributeValue",
    "MetadataAttribute",
    "RawToken",
    "TokenAttribute",
    "AttributeStatistic",
    "RankedToken",
    "TokenSchema",
    "TokenId",
    "TokenStatistic",
    "ValidatedTokenAttribute",
]
