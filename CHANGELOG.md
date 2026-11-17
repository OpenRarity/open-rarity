# Changelog

## Unreleased

### Added

- Python ordered collection inputs support creator-config exclusions and exact-decimal higher-is-rarer scoring while retaining source duplicate traits.

- The TypeScript package can score and rank categorical collections using the 0.7.5 compatibility rules and deterministic token ID order.
- The TypeScript package can parse creator rarity settings from a contractURI document or a direct rarity object.
- Python callers can construct typed creator settings or parse them from contract-level metadata.

### Changed

- Equal unique-count and score ties now use numeric token ID order, then raw ID order. Scores and equal-score ranks are unchanged. This changes the order of tied tokens compared with 0.7.5.

### Fixed

- OpenSea traits with numeric values and no `display_type` are parsed as numeric instead of raising an `AttributeError` during string normalization.
