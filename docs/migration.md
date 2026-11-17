# Migrating to 1.0

1.0 is in development. PyPI currently distributes 0.7.5; TypeScript is not yet on npm.
Use a repository checkout to try the new APIs.

## Scoring inputs

The new Python `CollectionInput` and TypeScript `CollectionInput` use ordered trait
arrays instead of dictionaries, preserving duplicate source entries. Token IDs are
strings so large integers retain precision. Set `token_id_kind` to `raw` for mint
addresses or other non-EVM identifiers.

Without effective creator settings, supported categorical scores and ranks retain
0.7.5 behavior. Equal results are ordered deterministically by token ID. Creator
settings opt into the normalization rules in the [specification](../SPEC.md).

## Fetching

The OpenSea helper now uses v2 cursor pagination instead of contiguous token-ID guesses.
It reads `OPENSEA_API_KEY` when the client is created. Supply comes from fetched tokens,
and failures propagate instead of silently returning partial results. Legacy caches
are not reused. See the [Python guide](python.md) for usage.

## Runtime and dependencies

Python 3.12 through 3.15 and Pydantic 2 are supported. Install the optional `opensea`
extra for network helpers. TypeScript builds as ESM and has no runtime dependencies.

The existing `Token`, `Collection`, and `RarityRanker` imports remain available.
The new ordered API adds numeric and creator-config scoring; the old model API
retains its historical scoring behavior.

## Ordered input example

```json
{
  "tokens": [
    {"token_id": "1", "traits": [{"trait_type": "Level", "value": 10}]},
    {"token_id": "2", "traits": [{"trait_type": "Level", "value": 20}]}
  ],
  "rarity": {
    "trait_count": "exclude",
    "traits": [{"trait_type": "Level", "mode": "higher_is_rarer"}]
  }
}
```

Python:

```python
import json

from open_rarity.collection_input import parse_collection_json
from open_rarity.collection_scorer import score_collection
from open_rarity.creator_config import parse_rarity_config

# source is the JSON text above.
results = score_collection(
    parse_collection_json(source), parse_rarity_config(json.loads(source))
)
```

TypeScript (from a built repository checkout):

```js
import { parseCollectionJson, parseCreatorRarityConfig, scoreCollection } from "./typescript/dist/index.js";

const results = scoreCollection(
  parseCollectionJson(source), parseCreatorRarityConfig(JSON.parse(source))
);
```

Use these parsers for numeric JSON so large integers and decimals are not rounded
before scoring. TypeScript requires modern JSON reviver-source support (Node 24 or
a current browser). The browser playground accepts the same document, including
its optional `rarity` object. Results contain token ID, score, rank, and unique-trait count.
