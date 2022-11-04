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
        help="Boolean flag to write results.",
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
    if token_ids_file is None:
        if start_token_id is None or end_token_id is None:
            raise ValueError(
                "Either a list of token-ids must be provided or both --start-token-id AND --end-token-id must be set."
            )
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


@app.command("transform-assets")
def transform_assets(
    input: Path = typer.Argument(..., help="Json file with Opensea assets response."),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Json file to write transformed data."
    ),
):
    transformed = OpenseaApi.transform_assets_response(
        json.loads(input.read_text())["assets"]
    )
    if output:
        output.write_text(json.dumps(transformed, indent=2))
    else:
        print(json.dumps(transformed))
