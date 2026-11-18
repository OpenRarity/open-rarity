# Python guide

## Released package (0.7.5)

Use Python 3.10–3.12 for this release.

```sh
python -m pip install open-rarity==0.7.5
```

Score a complete local collection. No API key or blockchain connection is needed:

```python
from open_rarity import Collection, Token
from open_rarity.rarity_ranker import RarityRanker

tokens = [
    Token.from_erc721("0x0", 1, {"Hat": "Cap"}),
    Token.from_erc721("0x0", 2, {"Hat": "Crown"}),
    Token.from_erc721("0x0", 3, {"Hat": "Cap"}),
]
for result in RarityRanker.rank_collection(Collection(tokens=tokens)):
    print(result.token.token_identifier.token_id, result.rank, result.score)
```

Results sort by unique-trait count, then score. Token 2 ranks first because its
Crown is unique. Tokens 1 and 3 share a rank. Use the full collection to get
representative trait frequencies, including how often a trait is missing.

## Development version

The repository contains unreleased 1.0 work and requires Python 3.12 through 3.15.
From the repository root, run `python -m pip install -e .` and follow the
[ordered input example](migration.md) for local scoring.

### Fetch from OpenSea

Install the optional dependency with `python -m pip install -e '.[opensea]'`. Set `OPENSEA_API_KEY` in your environment to use the optional v2 helper:

```python
from open_rarity.resolver.opensea_api_helpers import get_collection_from_opensea

collection = get_collection_from_opensea("your-collection", chain="arbitrum")
```

The helper follows cursors, includes sparse IDs and empty metadata, and uses fetched
items as supply. It rejects duplicate or incomplete snapshots. Multi-chain collections
require a chain; ambiguous contract addresses are rejected. Only ERC721 is supported.
Use `testnet=True` for the testnet API. Requests have timeouts and bounded retries.
`OpenSeaClient` exposes `collection`, `iter_nfts`, and `nft` for explicit fetching.
The old disk cache is retired; `use_cache` no longer reuses it.

The PyPI 0.7.5 helper uses retired v1 endpoints. Use the development version for v2.

See the [migration guide](migration.md) for the new ordered scoring API and
[scoring specification](../SPEC.md) for normalization and ranking rules.
