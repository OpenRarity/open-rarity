import asyncio as aio
import json
import logging
from pathlib import Path
from typing import Optional

import typer

from openrarity import TokenCollection
from openrarity.providers import OpenseaApi

from .utils import DEFAULT_COLUMNS, print_rankings

logger = logging.getLogger(__name__)
app = typer.Typer(name="opensea")


@app.command("fetch-assets")
def fetch_assets(
    token_ids_file: Path = typer.Argument(
        None,
        help="Either a newline delimited text file or json file with an array of token ids.",
    ),
    slug: str = typer.Option(..., help="Collection slug to fetch"),
    start_token_id: Optional[int] = typer.Option(
        None, help="Start id value for contiguous token_id collections"
    ),
    end_token_id: Optional[int] = typer.Option(
        None, help="End id value for contiguous token_id collections"
    ),
    semi_fungible: bool = typer.Option(False),
    rank: bool = typer.Option(False),
    write: bool = typer.Option(
        False,
        "-w",
        "--write",
        help="Boolean flag to write results into stdout or local specified path.",
    ),
    dir: Path = typer.Option(
        ".", "-d", "--dir", help="Directory to write outputs files."
    ),
    columns: str = typer.Option(
        DEFAULT_COLUMNS,
        "--columns",
        "-C",
        help="Columns to print or write to file.",
    ),
):
    """
    If we provide token_ids data as a input, using OpenseaApi, it will collect assets data. And based on the 'rank' boolean flag it will calculate ranks. At the end, based on the 'write' flag it will write the data to either stdout or to a file.
    If we didnt provide token_ids data as a input, it uses 'start_token_id' and 'end_token_id' as a range.Using OpenseaApi, it will collect assets data. And based on the 'rank' boolean flag it will calculate ranks. At the end, based on the 'write' flag it will write the data to either stdout or to a file.
    Parameters
    ----------
    token_ids_file: Path
        Token ids file.
    slug: str
        Collection slug.
    start_token_id: int,optional
        start token_id of the collection.
    end_token_id: int,optional
        end token_id of the collection.
    semi_fungible: bool
        Boolean value whether it is semi_fungible or not.
    rank: bool
        A boolean value whether calculate ranks or not.
    write: bool
        Boolean flag to write results into stdout or local specified path.
    dir: Path
        Directory to write outputs files.
    columns: str
        Columns to print or write to file.
    """
    if token_ids_file is None:
        if start_token_id is None or end_token_id is None:
            raise ValueError(
                "Either a list of token-ids must be provided or both --start-token-id AND --end-token-id must be set."
            )
        if start_token_id < 0 or end_token_id < 0:
            raise ValueError("--start-token-id and --end-token-id must be greater than zero.")
        if end_token_id < start_token_id:
            raise ValueError("--end-token-id must be greater than --start-token-id")

        token_ids = [str(i) for i in range(start_token_id, end_token_id + 1)]
    else:
        contents = token_ids_file.read_text()
        match token_ids_file.suffix:
            case ".txt":
                token_ids = contents.split()
            case ".json":
                token_ids = json.loads(contents)
            case _:
                raise ValueError("Input file must be either a .txt or .json file.")

    tokens = aio.run(
        OpenseaApi.fetch_opensea_assets_data(slug=slug, token_ids=token_ids)
    )
    ranks = None
    if rank:
        ranks = TokenCollection(
            "non-fungible" if not semi_fungible else "semi-fungible", tokens
        ).rank_collection()

    column_values = columns.split(",")  # type: ignore
    if write:
        tokens_path = dir / f"{slug}_opensea.json"
        tokens_path.write_text(json.dumps(tokens, indent=2))
        typer.echo(f"Writing {str(tokens_path)}...")
        if ranks is not None:
            ranks = [[str(row[c]) for c in columns] for row in ranks]  # type: ignore
            ranks_path = dir / f"{slug}_ranks.json"
            ranks_path.write_text(json.dumps(ranks, indent=2))
            typer.echo(f"Writing {str(ranks_path)}...")
    elif ranks is not None:
        print_rankings(ranks, column_values)
    else:
        print(json.dumps(tokens))
