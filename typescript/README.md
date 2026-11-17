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
