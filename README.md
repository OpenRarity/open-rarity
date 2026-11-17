# OpenRarity

An open standard and library for reproducible NFT rarity. Rank a complete collection
from its traits, with public scoring rules and matching Python/TypeScript fixtures.

[Try the scorer](https://openrarity.github.io/open-rarity/) ·
[Releases](https://github.com/OpenRarity/open-rarity/releases) ·
[Scoring specification](SPEC.md) · [Report an issue](https://github.com/OpenRarity/open-rarity/issues)

## Install

```sh
pip install open-rarity
```

[PyPI 0.7.5](https://pypi.org/project/open-rarity/) is the current release. This
repository contains 1.0 development work, including the v2 OpenSea helper and
[TypeScript scorer](typescript/). TypeScript is not yet published to npm.

## Quick start

```python
from open_rarity import Collection, Token
from open_rarity.rarity_ranker import RarityRanker

tokens = [
    Token.from_erc721("0x0", 1, {"Hat": "Cap"}),
    Token.from_erc721("0x0", 2, {"Hat": "Crown"}),
    Token.from_erc721("0x0", 3, {"Hat": "Cap"}),
]
for result in RarityRanker.rank_collection(Collection(tokens=tokens)):
    print(result.token.token_identifier, result.rank, result.score)
```

Unique traits take priority, then score. Supply every token you want compared.
Rarity measures trait frequency, not market value.

## Guides

- [Python and OpenSea fetching](docs/python.md)
- [Migrating to 1.0](docs/migration.md)
- [Scoring rules](SPEC.md) and [changelog](CHANGELOG.md)
- [Contributing and validation](AGENTS.md)
- [Release process](docs/RELEASING.md)

Licensed under [Apache 2.0](LICENSE).
