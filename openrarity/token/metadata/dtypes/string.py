from typing import cast

from satchel.aggregate import groupapply

from openrarity.token import AttributeStatistic, ValidatedTokenAttribute


def count_attribute_values(
    tokens: list[ValidatedTokenAttribute],
) -> list[AttributeStatistic]:
    """Aggregate and count on the combination of (name, value).

    Parameters
    ----------
    tokens : list[ValidatedTokenAttribute]
        Flattened token data to be aggregated.

    Returns
    -------
    list[AttributeStatistic]
        For each combination of (name, value), it returns attribute statistics(`attribute.token_count` and `attribute.supply`).
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
    """Process String type data by Aggregate and count on the combination of (name, value).

    Parameters
    ----------
    token_attrs : list[ValidatedTokenAttribute]
        Flattened token data to be aggregated.

    Returns
    -------
    list[AttributeStatistic]
        For each combination of (name, value), it returns attribute statistics(`attribute.token_count` and `attribute.supply`)
    """
    return count_attribute_values(token_attrs)
