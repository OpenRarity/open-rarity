from typing import cast

from satchel.aggregate import groupapply

from openrarity.token import AttributeStatistic, ValidatedTokenAttribute


def count_attribute_values(
    tokens: list[ValidatedTokenAttribute],
) -> list[AttributeStatistic]:
    """Aggregate and count on the combination of (name, value).

    Parameters
    ----------
    tokens : list[TokenAttribute]
        Vertical token data to be aggregated.

    Returns
    -------
    dict[AttributeName, int]

    """

    return [  # type: ignore
        cast(AttributeStatistic, {"name": k[0], "value": k[1], **counts})  # type: ignore
        for k, counts in groupapply(
            tokens,
            lambda tokens: (tokens["name"], tokens["value"]),  # type: ignore
            lambda tokens: {
                "attribute.token_count": len(tokens),
                "attribute.supply": sum(t["token.supply"] for t in tokens),
            },
        ).items()
    ]


def process_string_dtypes(token_attrs: list[ValidatedTokenAttribute]):
    return count_attribute_values(token_attrs)
