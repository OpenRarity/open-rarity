from tabulate import tabulate  # type: ignore

from openrarity.token.types import RankedToken

DEFAULT_COLUMNS = "token_id,metric.unique_trait_count,metric.information,rank"


def print_rankings(ranks: list[RankedToken], columns: list[str]):
    """
    Prints the given rank data in the form of a table to STDOUT.

    Parameters
    ----------
    ranks : list[RankedToken]
        Ranks which need to print on STDOUT.
    columns : list[str]
        list of the column names.
    """
    data = [[str(row[c]) for c in columns] for row in ranks]  # type: ignore
    print(tabulate(data, headers=columns))
