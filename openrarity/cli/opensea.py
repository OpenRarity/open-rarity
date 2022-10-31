import asyncio as aio
import json
import logging
import sys
from inspect import cleandoc
from pathlib import Path
from typing import Optional

import typer
from tqdm import tqdm  # type: ignore

from openrarity.providers import OpenseaApi  # type: ignore

logger = logging.getLogger(__name__)
app = typer.Typer(name="opensea")


@app.command("fetch-assets")
def fetch_assets(
    token_ids: Optional[list[str]] = typer.Argument(
        None,
        help="Space delimited list of token_ids. Used in place of start and end values.",
    ),
    slug: str = typer.Option(..., help="Collection slug to fetch"),
    start_token_id: Optional[int] = typer.Option(
        None, help="Start id value for contiguous token_id collections"
    ),
    end_token_id: Optional[int] = typer.Option(
        None, help="End id value for contiguous token_id collections"
    ),
    output: Path = typer.Option(
        None,
        "-o",
        "--output",
        help="Json file path to write data to. Defaults to stdout",
    ),
):
    if not token_ids:
        if start_token_id is None or end_token_id is None:
            raise ValueError(
                "Either a list of token-ids must be provided or both --start-token-id AND --end-token-id must be set."
            )
        if end_token_id < start_token_id:
            raise ValueError("--end-token-id must be greater than --start-token-id")

        token_ids = [str(i) for i in range(start_token_id, end_token_id + 1)]

    # typer.echo(f"Fetching tokens for {slug}")

    tokens = aio.run(
        OpenseaApi.fetch_opensea_assets_data(slug=slug, token_ids=token_ids)
    )

    if output is None:
        print(json.dumps(tokens))
    else:
        output.write_text(json.dumps(tokens, indent=2))
        typer.echo(f"Writing {str(output)}...")


@app.command("transform-assets")
def transform_assets(
    data: str = typer.Argument(... if sys.stdin.isatty() else sys.stdin.read().strip()),
):
    print(json.dumps(OpenseaApi.transform_assets_response(json.loads(data))))


@app.command(
    "transform-assets-bulk",
    help=cleandoc(
        """
        Transform a directory of json files containing Opensea Asset data.

        Provided paths must be directories that already exist.
        """
    ),
)
def transform_assets_bulk(
    input_path: Path = typer.Argument(
        ..., help="Directory to read json files with asset data from"
    ),
    output_path: Path = typer.Argument(
        ..., help="Directory to write transformed data to"
    ),
):
    if not input_path.is_dir() and output_path.is_dir():
        raise ValueError("Input and Output paths must be existing directories.")
    for p in tqdm(list(input_path.glob("*.json"))):
        try:
            (output_path / p.name).write_text(
                json.dumps(OpenseaApi.transform(json.loads(p.read_text())))
            )
        except Exception:
            typer.echo(f"Input File: {str(p)}")
            raise
