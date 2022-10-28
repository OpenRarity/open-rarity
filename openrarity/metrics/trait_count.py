from openrarity.token.types import AttributeStatistic, MetadataAttribute


def unique_trait_count(tokens: list[AttributeStatistic]) -> list[AttributeStatistic]:
    """Add a statistic to each token with the count of unique traits on that token.

    Parameters
    ----------
    tokens : list[AttributeStatistic]
        Tokens to be augmented.

    Returns
    -------
    list[AttributeStatistic]
        Augmented Tokens
    """
    return []


def count_traits(
    attributes: list[MetadataAttribute],
) -> list[MetadataAttribute]:
    """Count the number of traits on a given token and append it as an attribute named
    openrarity.trait_count

    Parameters
    ----------
    tokens : list[RawToken]
        Tokens to be augmented with openrarity.trait_count

    Returns
    -------
    list[RawToken]
        Tokens augmented with openrarity.trait_count
    """
    return attributes + [
        {
            "name": "openrarity.trait_count",
            "value": int(len(attributes)),
            "display_type": "string",
        }
    ]
