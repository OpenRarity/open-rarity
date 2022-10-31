import json
import sys

import typer

from openrarity import TokenCollection

from . import opensea

app = typer.Typer()
app.add_typer(opensea.app)


@app.command()
def rank(semi_fungible: bool = False, data: str = typer.Argument(... if sys.stdin.isatty() else sys.stdin.read().strip())):  # type: ignore
    data = json.loads(data)
    tc = TokenCollection("non-fungible" if not semi_fungible else "semi-fungible", data)  # type: ignore
    print(json.dumps(tc.rank_collection(return_ranks=True)))


if __name__ == "__main__":
    app()
