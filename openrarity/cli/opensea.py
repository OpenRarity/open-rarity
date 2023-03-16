import asyncio as aio
import json
import logging
from pathlib import Path
from typing import Optional

import typer

from openrarity import TokenCollection
from openrarity.providers import OpenseaApi

from .utils import DEFAULT_COLUMNS, print_rankings,check_file_existence

logger = logging.getLogger(__name__)
app = typer.Typer(name="opensea")


@app.command("fetch-assets")
def fetch_assets(
    token_ids_file: Path = typer.Argument(
        None,
        help="Either a newline delimited text file or json file with an array of token ids.",
    ),
    slug: str = typer.Option(..., help="Collection slug to fetch."),
    start_token_id: Optional[int] = typer.Option(
        None, help="Start id value for contiguous token_id collections."
    ),
    end_token_id: Optional[int] = typer.Option(
        None, help="End id value for contiguous token_id collections."
    ),
    semi_fungible: bool = typer.Option(False),
    rank: bool = typer.Option(False),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output path to write results."
    ),
    columns: str = typer.Option(
        DEFAULT_COLUMNS,
        "--columns",
        "-C",
        help="Column names of the result data.",
    ),
):
    """
    Given a list of token_ids or start and end token ids for numbered collections, fetch the token metadata from Opensea. Optionally, the fetched tokens can be ranked by passing the `--rank` flag and write to a file by passing the `--output` flag.

    Parameters
    ----------
    token_ids_file: Path
        Token ids file path. Either a newline delimited text file or json file with an array of token ids.
    slug: str
        Collection slug from opensea ie: `boredapeyachtclub`.
    start_token_id: int,optional
        Start token_id of the collection.
        Example: start_token_id for `boredapeyachtclub` is `0`.
    end_token_id: int,optional
        End token_id of the collection.
        Example: end_token_id for `boredapeyachtclub` is `9999`.
    semi_fungible: bool
        Boolean value to inform ranker that the collection contains Semi-Fungible tokens.
    rank: bool
        Boolean value informs whether to calculate ranks. By Default it is False.
    output : Path, optional
        Output path to write token attributes data and calculated ranks data.
    columns: str
        Column names of the resultant rank data.
    """
    if token_ids_file is None:
        if start_token_id is None or end_token_id is None:
            raise ValueError(
                "Either a list of token-ids must be provided or both --start-token-id AND --end-token-id must be set."
            )
        if start_token_id < 0 or end_token_id < 0:
            raise ValueError("--start-token-id and --end-token-id must be greater than zero.")
        if end_token_id < start_token_id:
            raise ValueError("--end-token-id must be greater than --start-token-id.")

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

    file_exists = False
    overwrite_flag = False
    rank_with_existing_assets_flag = False
    if output:
        tokens_path = output / f"{slug}_opensea.json"
        # Check the existance of token collection file and populate `file_exists`,`overwrite_flag` and `rank_with_existing_assets_flag` accordingly.
        file_exists,overwrite_flag,rank_with_existing_assets_flag = check_file_existence(tokens_path,rank)

    # Fetch token collection data from opensea api or read from the tokens path.
    if output and rank_with_existing_assets_flag:
        tokens_path = output / f"{slug}_opensea.json"
        contents = tokens_path.read_text()
        tokens = json.loads(contents)
    else:
        tokens = aio.run(
            OpenseaApi.fetch_opensea_assets_data(slug=slug, token_ids=token_ids)
        )

    ranks = None
    if rank:
        ranks = TokenCollection(
            "non-fungible" if not semi_fungible else "semi-fungible", tokens
        ).rank_collection()

    column_values = columns.split(",")  # type: ignore
    if output is not None:
        if overwrite_flag or not file_exists:
            tokens_path = output / f"{slug}_opensea.json"
            tokens_path.write_text(json.dumps(tokens, indent=2))
            typer.echo(f"Writing {str(tokens_path)}...")

        if ranks is not None:
            ranks = [[str(row[c]) for c in column_values] for row in ranks]  # type: ignore
            ranks_path = output / f"{slug}_ranks.json"
            ranks_path.write_text(json.dumps(ranks, indent=2))
            typer.echo(f"Writing {str(ranks_path)}...")
    elif ranks is not None:
        print_rankings(ranks, column_values)
    else:
        print(json.dumps(tokens))
