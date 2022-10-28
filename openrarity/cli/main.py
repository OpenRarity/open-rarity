import typer

from . import opensea

app = typer.Typer()
app.add_typer(opensea.app)


@app.command()
def rank():
    typer.echo("Hello OpenRarity!!! The cli isn't available yet but, keep an eye out!")


if __name__ == "__main__":
    app()
