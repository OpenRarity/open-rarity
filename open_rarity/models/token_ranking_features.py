from dataclasses import dataclass


@dataclass
class TokenRankingFeatures:
    """Class represents all standardized ranking features
    that should be considered by the ranking function.

    Attributes
    ----------
    unique_attribute_count : int
        count of unique attributes in the asset ( 1 of 1)
    """

    unique_attribute_count: int
