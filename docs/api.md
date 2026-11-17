# Scoring API reference

These APIs are part of **1.0 development**, available from a repository checkout.
For released PyPI 0.7.5, use the [Python guide](python.md).
OpenRarity is a local library, so its data contracts use JSON Schema rather than
an OpenAPI document describing HTTP endpoints.

## Inputs

[Collection JSON Schema](../schemas/collection.schema.json) is generated from
`CollectionInput`, `TokenInput`, and `TraitInput` in the Python source.

| Field | Meaning |
| --- | --- |
| `tokens` | Array of every token being compared. An empty collection returns an empty result. |
| `token_id` | Nonempty string. EVM IDs contain unsigned decimal digits. IDs must be unique. |
| `token_id_kind` | `evm` (default) or `raw` for other identifiers. |
| `traits` | Required JSON array of ordered trait entries, including duplicates. |
| `trait_type` | Trait name as a string. |
| `value` | String, finite JSON number, or null. Booleans are invalid. |
| `display_type` | Optional string or null. `date` values must be integral to participate in numeric scoring. |

The schema checks structure. The scorer also validates ID rules and numeric bounds;
JSON Schema cannot enforce distinct token IDs across objects or preserve numeric
precision in your JSON decoder. Always use the exact-number parsers in the
[migration examples](migration.md).

An optional `rarity` object may accompany `tokens`. It is parsed separately and is
described by the separate [creator-config schema](../schemas/creator-config.schema.json). That schema describes well-formed settings; runtime parsing remains tolerant of malformed entries. Its `traits` array contains
`{ "trait_type": "Level", "mode": "higher_is_rarer" }` entries; the other mode is
`exclude`. `trait_count` accepts either mode. The parser considers the first 100
entries, skips malformed settings, and retains the last valid setting per name.
See the [specification](../SPEC.md) for normalization and bounds.

## Functions

| Python | TypeScript | Result |
| --- | --- | --- |
| `parse_collection_json(text)` | `parseCollectionJson(text)` | Ordered input with exact numeric values. |
| `parse_rarity_config(document)` | `parseCreatorRarityConfig(document)` | Settings parsed from a document or its `rarity` object. |
| `score_collection(collection, config)` | `scoreCollection(collection, config)` | Ranked results for the complete input. Config is optional. |

Python imports are in `open_rarity.collection_input`,
`open_rarity.creator_config`, and `open_rarity.collection_scorer`, respectively.
TypeScript exports these functions from its built `typescript/dist/index.js`.
Parsing and scoring invalid collection data can raise errors; handle them at your
application boundary. Creator settings deliberately tolerate malformed entries.

## Results

[Results JSON Schema](../schemas/results.schema.json) is generated from
`TokenRarityResult`. Python returns dataclass instances; serialize them with
`dataclasses.asdict`. TypeScript returns plain objects.

| Field | Meaning |
| --- | --- |
| `token_id` | Original string identifier. |
| `score` | Normalized rarity score. |
| `rank` | One-based rank, with shared ranks for ties. |
| `unique_trait_count` | Count of qualifying unique traits used by the ranking rules. |

Results arrive in ranking order. See the [scoring specification](../SPEC.md) for
unique-trait priority and deterministic token-ID tie ordering.

## Explanations and CLI

Use Python `explain_collection(collection, config)` or TypeScript
`explainCollection(collection, config)` to receive the same ranking with per-trait
contributions. Python imports the function from `open_rarity.collection_scorer`.
See the [explanation schema](../schemas/explanations.schema.json) for the result,
normalization divisor, selected traits, and ordered source traits. Source numbers
are encoded as strings with a `value_kind` tag to retain precision in output JSON.

Each trait reports `count`, `probability`, `information` (bits), `contribution`
(normalized score), and `unique`. Excluded traits and invalid numeric inputs
contribute zero; their count and probability are null. Explanations preserve all
source entries while identifying the reduced value used for scoring. The playground
shows the selected contributions under each token's Explain control.

The [local CLI](cli.md) exports rankings as JSON/CSV and explanations as JSON.
See [benchmarks](benchmarks.md) for reproducible 10k/100k scoring measurements.

## Regenerate

From an installed repository checkout, run `python -m scripts.generate_schemas`.
CI runs `python -m scripts.generate_schemas --check` before building the site.
The site publishes the checked-in artifacts and these guides from the same commit.
