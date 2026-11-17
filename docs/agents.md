# OpenRarity for agents

Rank a complete NFT collection locally. Scoring does not require a server or API key.
Rarity measures traits, not price or investment value.

## Choose the right version

- Released PyPI 0.7.5 uses `Token`, `Collection`, and `RarityRanker`. Follow the [Python guide](python.md).
- For 1.0 development, this repository and the browser playground use the ordered 1.0 API below. TypeScript is available from source, not npm. Follow the [migration examples](migration.md) for both languages.

## Use the scorer

1. Supply every token to compare. Partial collections produce different scores.
2. Keep token IDs as strings and traits as ordered arrays. Retain duplicate entries. Use `token_id_kind: "raw"` for non-EVM IDs.
3. Pass original JSON text to Python `parse_collection_json` or TypeScript `parseCollectionJson` to preserve numeric precision. Do not round-trip numeric traits through JavaScript `JSON.parse` before scoring.
4. Parse optional creator settings separately with `parse_rarity_config` or `parseCreatorRarityConfig`, then call `score_collection` or `scoreCollection`.
5. Use the returned rank and ordering. Unique traits take priority over score; rank is not a sort of score alone.

See the [API reference and schemas](api.md) for input and output shapes, and the
[specification](../SPEC.md) for missing values, duplicates, numeric modes, and ties.
The [playground](https://openrarity.github.io/open-rarity/#demo) accepts local JSON
and exports results without uploading collection data.

## Work on the repository

Read [AGENTS.md](https://github.com/OpenRarity/open-rarity/blob/main/AGENTS.md)
for contribution checks. Change model sources, then run
`python -m scripts.generate_schemas`; do not edit generated schema files.
Keep Python and TypeScript behavior covered by shared conformance fixtures.
Use [release notes](https://github.com/OpenRarity/open-rarity/releases) to check
published availability before suggesting installation commands.
