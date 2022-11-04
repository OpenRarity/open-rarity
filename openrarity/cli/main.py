import json
import sys
from pathlib import Path
from typing import Optional

import typer

from openrarity import TokenCollection

from . import opensea
from .utils import DEFAULT_COLUMNS, print_rankings

app = typer.Typer()
app.add_typer(opensea.app)


@app.command()
def rank(
    tokens: Path = typer.Argument(..., help="Json file containing token metadata."),
    semi_fungible: bool = typer.Option(False),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Json file to write rank data."
    ),
    columns: str = typer.Option(
        DEFAULT_COLUMNS,
        "--columns",
        "-C",
        help="Columns to print or write to file.",
    ),
):

    if tokens.name == "-":
        data = json.loads(sys.stdin.read())
    else:
        data = json.loads(tokens.read_text())

    tc = TokenCollection("non-fungible" if not semi_fungible else "semi-fungible", data)  # type: ignore
    column_values = columns.split(",")  # type: ignore
    ranks = tc.rank_collection()  # type: ignore
    if output is not None:
        ranks = [[str(row[c]) for c in columns] for row in ranks]  # type: ignore
        output.write_text(json.dumps(ranks, indent=2))
    else:
        print_rankings(ranks, column_values)


if __name__ == "__main__":
    app()
