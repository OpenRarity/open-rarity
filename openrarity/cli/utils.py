from tabulate import tabulate  # type: ignore

from openrarity.token.types import RankedToken
import typer
from pathlib import Path

DEFAULT_COLUMNS = "token_id,metric.unique_trait_count,metric.information,rank"


def print_rankings(ranks: list[RankedToken], columns: list[str]):
    """
    Prints the given rank data in the form of a table to STDOUT.

    Parameters
    ----------
    ranks : list[RankedToken]
        Ranks to be printed.
        Sample list[RankedToken] will be like `[{'token_id': '0', 'metric.probability': 0.0078125, 'metric.max_trait_information': 1.0, 'metric.information': 7.0, 'metric.unique_trait_count': 7,'rank':1}]`.
    columns : list[str]
        A subset of columns to print for the ranks.
        Example : ["token_id","metric.unique_trait_count","metric.information","rank"]
    """
    data = [[str(row[c]) for c in columns] for row in ranks]  # type: ignore
    print(tabulate(data, headers=columns))


def check_file_existence(file_path: str | Path, rank: bool) -> bool:
    """
    Utility method to check the existence of a file and it sets the boolean value for `write_flag`.

    Parameters
    ----------
    file_path : str
        File path to check the existence status.
    rank : bool
        Boolean value informs whether to calculate ranks.

    Returns
    -------
    bool
        Returns boolean status of `write_flag`.
    """
    write_flag = True

    file_exists = Path(file_path).exists()
    if file_exists:
        if rank:
            # overwrite/rank-with-existing-assets/no
            answer = None
            while answer not in ("1", "2", "3"):
                answer = input(f"File path exists. Do you want to:\n1)Overwrite\n2)rank-with-existing-assets\n3)Exit\npick an option:").lower()
                if answer == "1":
                    write_flag = True
                elif answer == "2":
                    write_flag = False
                elif answer == "3":
                    typer.echo("Stopping the program...")
                    exit()
                else:
                    typer.echo(f"Please enter any one of these values('1','2','3')\n")
        else:
            # if files exist and provide y/N input to overwrite
            answer = input(f"Output file exist. Would you like to overwrite? (y/N)")
            if answer.lower() == "y":
                write_flag = True
            else:
                write_flag = False
                typer.echo("Stopped further processing...")

    return write_flag
