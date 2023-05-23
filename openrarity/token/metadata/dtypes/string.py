from typing import cast

from satchel.aggregate import groupapply

from openrarity.token import AttributeStatistic, ValidatedTokenAttribute


def count_attribute_values(
    tokens: list[ValidatedTokenAttribute],
) -> list[AttributeStatistic]:
    """Process String type data by aggregating on the combination of (name, value).

    Parameters
    ----------
    tokens : list[ValidatedTokenAttribute]
        Flattened list of token attributes data.
        Example : [{'token_id': '0', 'name': 'eyes', 'value': 'x eyes', 'token.supply': 1,'display_type':'string'},..]

    Returns
    -------
    list[AttributeStatistic]
        AttributeStatistic augmented with `token_count` and `supply`.
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
    """Process String type data by aggregating on the combination of (name, value). It calculates `token_count` and `supply`.

    Parameters
    ----------
    token_attrs : list[ValidatedTokenAttribute]
        Flattened list of token attributes data.
        Example : [{'token_id': '0', 'name': 'eyes', 'value': 'x eyes', 'token.supply': 1,'display_type':'string'},..]

    Returns
    -------
    list[AttributeStatistic]
        AttributeStatistic augmented with `token_count` and `supply`.

    """
    return count_attribute_values(token_attrs)
