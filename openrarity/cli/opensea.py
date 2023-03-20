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
        None, "--output", "-o", help="Output directory path to write results."
    ),
    columns: str = typer.Option(
        DEFAULT_COLUMNS,
        "--columns",
        "-C",
        help="Column names of the result data. Available columns are `token_id`,`metric.unique_trait_count`,`metric.information`,`rank`.",
    ),
):
    """
    Given a list of token_ids or start and end token ids for numbered collections, fetch the token metadata from Opensea. Optionally, the fetched tokens can be ranked by passing the `--rank` flag and written to a file by passing the `--output` flag.

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
        Output directory path to write token attributes data and calculated ranks data.
        Output filenames are formated like below
            - <output>/<slug>_opensea.json
            - <output>/<slug>_ranks.json
    columns: str
        Column names of the resultant rank data. Available columns are `token_id`,`metric.unique_trait_count`,`metric.information`,`rank`.
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

    if output:
        tokens_path = output / f"{slug}_opensea.json"
        write_flag = check_file_existence(tokens_path,rank)

        if write_flag:
            tokens = aio.run(
                OpenseaApi.fetch_opensea_assets_data(slug=slug, token_ids=token_ids)
            )
            tokens_path.write_text(json.dumps(tokens, indent=2))
            typer.echo(f"Writing {str(tokens_path)}...")
        else:
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
    if output and ranks:
        ranks = [[str(row[c]) for c in column_values] for row in ranks]  # type: ignore
        ranks_path = output / f"{slug}_ranks.json"
        ranks_path.write_text(json.dumps(ranks, indent=2))
        typer.echo(f"Writing {str(ranks_path)}...")
    elif ranks:
        print_rankings(ranks, column_values)
    else:
        print(json.dumps(tokens))


@app.command("fetch-collections")
def fetch_collections(
    slug: str = typer.Option(..., help="Collection slug to fetch."),
    output: Optional[Path] = typer.Option(
        ".", "--output", "-o", help="Output directory path to write results."
    )
):
    """
    For a given collection_slug, fetch the collection data from Opensea. And then, it writes to a output path. By default, it writes to current directory.

    Parameters
    ----------
    slug: str
        Collection slug from opensea ie: `boredapeyachtclub`.
    output : Path, optional
        Output directory path to write collection data. By default, it writes to current directory.
        Output filename is formated like below
            - <output>/<slug>_opensea_collection.json
    """
    if output:
        file_path = output / f"{slug}_opensea_collection.json"
        write_flag = check_file_existence(file_path,False)

        if write_flag:
            collection_data = OpenseaApi.fetch_opensea_collection_data(slug=slug)
            file_path.write_text(json.dumps(collection_data, indent=2))
            typer.echo(f"Writing {str(file_path)}...")
        else:
            typer.echo(f"Skipped Writing {str(file_path)}...")
