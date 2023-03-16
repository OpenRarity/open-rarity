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
        Ranks data which need to print on STDOUT.
        Sample list[RankedToken] will be like `[{'token_id': '0', 'metric.probability': 0.0078125, 'metric.max_trait_information': 1.0, 'metric.information': 7.0, 'metric.unique_trait_count': 7,'rank':1}]`
    columns : list[str]
        A subset of columns to print for the ranks.
        Example : ["token_id","metric.unique_trait_count","metric.information","rank"]
    """
    data = [[str(row[c]) for c in columns] for row in ranks]  # type: ignore
    print(tabulate(data, headers=columns))


def check_file_existence(file_path: str | Path, rank: bool) -> tuple[bool, bool, bool]:
    """
    Utility method to check the existence of a file and it sets boolean values to `file_exists`,`overwrite_flag`,`rank_with_existing_assets_flag`.

    Parameters
    ----------
    file_path : str
        File path to check the existence status.
    rank : bool
        Boolean value informs whether to calculate ranks.

    Returns
    -------
    tuple[bool,bool,bool]
        Returns boolean status of `file_exists`,`overwrite_flag`,`rank_with_existing_assets_flag`.
    """
    file_exists = False
    overwrite_flag = False
    rank_with_existing_assets_flag = False

    file_exists = Path(file_path).exists()
    if file_exists:
        if rank:
            # overwrite/rank-with-existing-assets/no
            answer = None
            while answer not in ("a", "b", "c"):
                typer.echo(f"File path exists. Do you want to:\nA)Overwrite\nB)rank-with-existing-assets\nC)Exit\npick an option:")
                answer = input().lower()
                if answer == "a":
                    overwrite_flag = True
                elif answer == "b":
                    rank_with_existing_assets_flag = True
                elif answer == "c":
                    typer.echo("Stopping the program...")
                    exit()
                else:
                    typer.echo(f"Please enter any one of these values('a','b','c').")
        else:
            # if files exist and provide y/n input to overwrite
            answer = None
            while answer not in ("a", "b"):
                typer.echo(f"File path exists. Do you want to: \n A)Overwrite \n B)No\npick an option:")
                answer = input().lower()
                if answer == "a":
                    overwrite_flag = True
                elif answer == "b":
                    typer.echo(f"Skipped writing...")
                else:
                    typer.echo(f"Please enter any one of these values('a','b').")

    return (file_exists, overwrite_flag, rank_with_existing_assets_flag)
