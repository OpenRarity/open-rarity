# Local CLI

The CLI is part of 1.0 development. Install a repository checkout with
`python -m pip install -e .`; released PyPI 0.7.5 does not include this command.

```sh
openrarity collection.json -o results.json
openrarity collection.json --explain -o explanations.json
openrarity collection.json --format csv -o results.csv
cat collection.json | python -m open_rarity -
```

Input uses the [ordered collection format](migration.md). Supply every token to
compare. Token IDs remain strings, JSON numbers retain exact precision, and
source traits retain their order. The CLI makes no network requests.

An embedded `rarity` object supplies creator settings. `--config settings.json`
replaces those settings with a separate file containing either a direct settings
object or a `rarity` wrapper. Use `--explain` with JSON to include contributions
and selected values. CSV contains token ID, score, rank, and unique-trait count.

Successful runs exit 0. Invalid input and file errors exit 2 with a message on
stderr. Results go to stdout unless `-o` is supplied; an existing output file is
overwritten after parsing and scoring succeed.
