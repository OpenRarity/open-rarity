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
        Augmented Tokens.
    """
    return []


def count_traits(
    attributes: list[MetadataAttribute],
) -> list[MetadataAttribute]:
    """Count the number of traits on a given token attributes and append it as an attribute named
    `openrarity.trait_count`.
    Trait can be defined as specific properties each NFT has. trait_count is total number of properties of a token.

    Parameters
    ----------
    attributes: list[MetadataAttribute]
        Token attributes to be augmented with `openrarity.trait_count`.

    Returns
    -------
    list[MetadataAttribute]
        Token attributes augmented with `openrarity.trait_count`.
    """
    return attributes + [
        {
            "name": "openrarity.trait_count",
            "value": int(
                len(
                    [
                        a
                        for a in attributes
                        if a["value"] not in ["openrarity.null_trait", "none", ""]
                    ]
                )
            ),
            "display_type": "string",
        }
    ]
