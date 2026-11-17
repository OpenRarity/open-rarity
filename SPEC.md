# OpenRarity 1.0 scoring specification

Status: draft for conformance work. The `1.0.0rc1` release will freeze this document and the shared fixtures. Python and TypeScript must produce the same ranks and scores within the tolerance below.

## Scope and input

The core scores a complete collection supplied by the caller. Fetching metadata, discovering supply, refreshing a marketplace, and assigning display colors belong outside the core. The collection contains an ordered list of tokens. Each token has a unique identifier and an ordered list of traits. A trait has a string `trait_type` and a string, number, or null `value`; `display_type` may identify a numeric or date value. The JSON Schema will define the exact field names and limits.

Token identifiers are carried as strings in shared JSON so large integers do not lose precision. EVM token IDs use unsigned base-10 digits. Other identifiers remain strings. A collection must not contain the same identifier twice. ERC1155 quantities are outside 1.0: each input token contributes one item to supply.

The collection's total supply is the number of input tokens, not a contract's maximum possible supply. A caller must provide every token it wants ranked. An empty collection returns an empty ranking. The core must not guess missing IDs from supply.

## Compatibility and normalization

When no effective creator config is supplied, 1.0 preserves the 0.7.5 categorical score and rank calculations on inputs that 0.7.5 supports. The one intended ranking change is deterministic ordering of equal unique-count and score values by token ID. The checked-in 0.7.5 golden fixtures define this compatibility boundary.

In this compatibility path, string trait names and values are lowercased and trimmed, as in 0.7.5. Empty and case-insensitive `none` values do not contribute to the synthetic trait count. The 0.7.5 scorer still treats them as categorical values when computing frequencies, scores, and unique counts. This behavior is preserved for unconfigured collections. A missing trait is different from an explicit empty or `none` value in this path.

Creator config opts into the 1.0 preprocessing path. In that path, trim leading and trailing whitespace from names and string values. Treat a null value, an empty string, and a string whose trimmed value equals `none` without regard to case as missing. Retain the ordered source traits in input and explanations. For scoring, keep one nonmissing value per trimmed, case-sensitive trait type: the lexicographically smallest normalized string representation. An exact tie keeps the earlier input entry. This matches the duplicate reduction used by os2-core after missing-value filtering. Config names match these trimmed trait types case-sensitively.

Numeric values are compared as exact finite decimals. Parse JSON integers and finite JSON decimals without first converting them to binary floating point; accept decimal strings only for a trait configured as `higher_is_rarer`. A numeric `display_type` with a null display value must not call a string method on an integer. Date values use Unix seconds as exact integers in the input model. Invalid numeric or date values are missing for `higher_is_rarer`; they remain categorical strings for ordinary frequency scoring when a nonempty source value exists. The shared fixtures will cover signed decimals, exponents, large integers, and malformed inputs.

## Frequencies and score

Let `N` be the number of input tokens. For each included trait type, count each selected value once per token. A token without that trait has an implicit null value. Let `c(t,v)` be the number of tokens with trait type `t` and value `v`, including null, and `p(t,v) = c(t,v) / N`.

The ordinary information contribution for a token's value is `-log2(p(t,v))`. Its unnormalized score is the sum of those contributions over included trait types. Excluded traits make no contribution. The collection entropy is `H = -sum_t sum_v p(t,v) * log2(p(t,v))` over the included trait distributions. Use `H = 1` when the sum is zero. The normalized token score is its unnormalized score divided by `H`. This retains the 0.7.5 information-content formula; the configured path changes which values enter the distributions.

Add a synthetic `meta_trait:trait_count` trait unless its mode is `exclude`. Its value is the number of selected, nonmissing trait types on that token after excluding traits with mode `exclude` or `higher_is_rarer`. The synthetic trait is a normal categorical distribution unless its mode is `higher_is_rarer`. Source metadata cannot override this synthetic value.

For a trait with mode `higher_is_rarer`, a token with numeric value `v` contributes `-log2(n_at_least_v / N)`, where `n_at_least_v` is the number of input tokens whose selected numeric value for that trait is at least `v`. Compare the exact decimal values before converting the probability to a score. A missing or nonnumeric value contributes zero. The trait remains in the collection entropy distribution, matching os2-core, but never contributes to the unique-trait tie-break or the synthetic trait count. An excluded trait is removed from both score and entropy distributions.

The unique-trait count is the number of a token's included selected trait values with collection frequency exactly one. Excluded and `higher_is_rarer` traits do not count. In the compatibility path, this count follows 0.7.5, including its treatment of explicit empty and `none` values.

## Creator config

The optional config is the `rarity` object from contract-level metadata, or the same object supplied directly:

```json
{
  "trait_count": "exclude",
  "traits": [
    {"trait_type": "Level", "mode": "higher_is_rarer"}
  ]
}
```

Supported modes are `exclude` and `higher_is_rarer`. Parse only the first 100 `traits` entries. Skip entries whose `trait_type` or `mode` is not a string, whose trimmed name is blank or exceeds 256 UTF-16 code units, whose mode is unknown, or whose name is `meta_trait:trait_count`. Trim names without changing case. The last valid entry for an identical name wins. An invalid entry must not invalidate another entry. The top-level `trait_count` mode sets the synthetic trait's mode; an invalid value is ignored. An empty or wholly invalid config has no effect and uses the compatibility path. A typed constructor must express the same modes without JSON parsing.

## Ranking and numeric tolerance

Sort tokens by unique-trait count descending, score descending, numeric token ID ascending, then raw token ID ascending. Numeric IDs are compared as arbitrary-precision integers. Nonnumeric IDs sort after numeric IDs at an equal count and score. An exact tie after those keys retains input order.

Assign competition ranks, such as `1, 2, 2, 4`. Equal scores receive the same rank even when unique-trait counts differ. This follows os2-core's rank rule; the token ID tie-break changes output order, not the rank. To preserve 0.7.5 rank outcomes, the compatibility path uses `isclose` with relative tolerance `1e-9` and absolute tolerance zero when comparing adjacent scores. The configured path uses exact equality on the computed score, as os2-core does. A conformance score passes when its absolute difference from the fixture is at most `1e-12`; ranks and output order must match exactly. Output scores are binary64 values and must not be rounded before ranking. Display rounding is a caller concern.

## Differences from 0.7.5 and os2-core

- The token ID tie-break is new for Python and follows os2-core's numeric then raw ordering. Equal-score ranks remain shared.
- The no-config path retains 0.7.5 treatment of explicit empty and `none` scoring values. The configured path filters them as os2-core does. This protects existing scores while making creator settings predictable.
- os2-core compares score equality exactly. The no-config Python path keeps its 0.7.5 approximate rank comparison for compatibility.
- The 1.0 input model retains duplicate traits before reduction. The 0.7.5 dictionary model silently overwrites them.

Every future change to these rules requires a spec edit, a conformance fixture update, and a changelog entry in the same behavior PR.
