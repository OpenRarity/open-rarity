"""Define ranking algorithms for token standards. Ranking is done with with a RANK style
methodology as opposed to DENSE RANK. This means that ties would show up as 1, 1, 1, 4
as opposed to 1, 1, 1, 2.
"""
from openrarity.token import RankedToken, AttributeStatistic


def rank_semi_fungible_tokens(
    tokens: list[AttributeStatistic],
) -> list[RankedToken]:
    """Semi-fungible tokens such as ERC1155 shall be ranked based on total discrete
    tokens rather than total supply. This requires deduplicating prior to ranking.

    Parameters
    ----------
    tokens : list[AttributeStatistic]
        _description_

    Returns
    -------
    list[RankedToken]
        _description_
    """
    ...


def rank_non_fungible_tokens(
    tokens: list[AttributeStatistic],
) -> list[RankedToken]:
    """Non-fungible tokens such as ERC721 can be ranked based on total supply of
    tokens.

    Parameters
    ----------
    tokens : list[AttributeStatistic]
        _description_

    Returns
    -------
    list[RankedToken]
        _description_
    """
    ...
