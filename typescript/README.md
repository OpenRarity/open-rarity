# OpenRarity for TypeScript

Pure NFT rarity scoring for Node.js 24+ and modern browsers. This package is in
1.0 development and is not yet published to npm. Build from this repository with
`npm ci && npm run build` in `typescript/`.

```js
import {parseCollectionJson, parseCreatorRarityConfig, scoreCollection, explainCollection} from './dist/index.js';

const input = parseCollectionJson(source);
const config = parseCreatorRarityConfig(JSON.parse(source));
const ranked = scoreCollection(input, config);
const explained = explainCollection(input, config);
```

Supply a complete collection. Keep token IDs as strings and pass original JSON
text to `parseCollectionJson` so numeric traits retain precision. Explanation
source values are strings tagged with `value_kind`, preserving duplicate order.

[API and examples](https://openrarity.github.io/open-rarity/api.html) ·
[Specification](https://openrarity.github.io/open-rarity/spec.html) ·
[Source and issues](https://github.com/OpenRarity/open-rarity)

## Fetch a collection from OpenSea

Use the optional `open-rarity/opensea` export in Node.js. From a built checkout,
import the same function from `./dist/opensea.js`.

```js
import { fetchOpenSeaCollection } from "open-rarity/opensea";
import { scoreCollection } from "open-rarity";

const collection = await fetchOpenSeaCollection("doodles-official", {
  apiKey: process.env.OPENSEA_API_KEY,
});
const scores = scoreCollection(collection);
```

Keep the API key on the server. The helper reads [collection
metadata](https://docs.opensea.io/reference/get_collection) and
[paginated NFT data](https://docs.opensea.io/reference/get_nfts_by_collection)
for one ERC721 contract. Specify `chain` or `contract` when the collection makes
either choice ambiguous. Set `testnet: true` for the testnet host.

The helper preserves source trait order and exact JSON numbers. It rejects
duplicate IDs, repeated cursors, and runs that hit the page limit. Each request
has a 30-second timeout. HTTP errors go back to the caller so the application can
handle rate limits and decide when to retry.
