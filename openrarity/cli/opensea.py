import typer

app = typer.Typer(name="opensea")


@app.command("fetch-assets")
def fetch_assets(address: str):
    print(f"Fetching tokens for {address}")
