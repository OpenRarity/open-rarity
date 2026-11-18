![OpenRarity](img/OR_Github_banner_wide.png)

[![GitHub release](https://img.shields.io/github/v/release/OpenRarity/open-rarity)](https://github.com/OpenRarity/open-rarity/releases/latest)
[![PyPI](https://img.shields.io/pypi/v/open-rarity)](https://pypi.org/project/open-rarity/)
[![Python tests](https://github.com/OpenRarity/open-rarity/actions/workflows/tests.yaml/badge.svg?branch=main)](https://github.com/OpenRarity/open-rarity/actions/workflows/tests.yaml)
[![TypeScript and parity](https://github.com/OpenRarity/open-rarity/actions/workflows/typescript.yaml/badge.svg?branch=main)](https://github.com/OpenRarity/open-rarity/actions/workflows/typescript.yaml)
[![Docs and demo](https://img.shields.io/badge/docs-live-643d70)](https://openrarity.github.io/open-rarity/)
[![License](https://img.shields.io/github/license/OpenRarity/open-rarity)](LICENSE)

# OpenRarity

OpenRarity ranks NFTs by how common their traits are within a collection.
Try it in your browser or run the scoring library locally.

[Try the scorer](https://openrarity.github.io/open-rarity/) ·
[Releases](https://github.com/OpenRarity/open-rarity/releases) ·
[Scoring specification](SPEC.md) · [Report an issue](https://github.com/OpenRarity/open-rarity/issues)

## Quick start

Install the [released Python package](https://pypi.org/project/open-rarity/0.7.5/)
with Python 3.10–3.12.

```sh
python -m pip install open-rarity==0.7.5
```

```python
from open_rarity import Collection, Token
from open_rarity.rarity_ranker import RarityRanker

tokens = [
    Token.from_erc721("0x0", 1, {"Hat": "Cap"}),
    Token.from_erc721("0x0", 2, {"Hat": "Crown"}),
    Token.from_erc721("0x0", 3, {"Hat": "Cap"}),
]
for result in RarityRanker.rank_collection(Collection(tokens=tokens)):
    print(result.token.token_identifier.token_id, result.rank)
```

Token 2 ranks first. Tokens 1 and 3 tie. Supply the full collection so trait
frequencies reflect all the tokens you want ranked.

The browser scorer and this repository preview 1.0, including the ordered input
API, explanations, and CLI. Build [TypeScript from source](typescript/) to try it.

## Guides

- [Python and OpenSea fetching](docs/python.md)
- [1.0 quick start and migration](docs/migration.md) · [Local CLI](docs/cli.md)
- [Scoring rules](SPEC.md) and [changelog](CHANGELOG.md)
- [Agent guide](docs/agents.md), [API and schemas](docs/api.md), and [llms.txt](llms.txt)
- [Contributing](CONTRIBUTING.md) and [validation](AGENTS.md)
- [Community integrations](docs/community.md)
- [Release process](docs/RELEASING.md)

Licensed under [Apache 2.0](LICENSE).
