# Changelog

- Replace the retired OpenSea v1 helper with v2 cursor pagination, explicit chain/testnet selection, bounded retries, and sparse-ID support. Retire incomplete v1 disk caches and reject partial snapshots.

## Unreleased

### Added

- Python ordered collection inputs support creator-config exclusions and exact-decimal higher-is-rarer scoring while retaining source duplicate traits.

- The TypeScript package can score and rank categorical collections using the 0.7.5 compatibility rules and deterministic token ID order.
- The TypeScript package can parse creator rarity settings from a contractURI document or a direct rarity object.
- Python callers can construct typed creator settings or parse them from contract-level metadata.

### Changed

- Require Python 3.12 or newer, NumPy 2.5.5 or newer, and Pydantic 2.14.3 or newer. Python 3.11 and Pydantic 1 compatibility are removed. CI covers Python 3.12 through 3.15.

- Equal unique-count and score ties now use numeric token ID order, then raw ID order. Scores and equal-score ranks are unchanged. This changes the order of tied tokens compared with 0.7.5.

### Fixed

- OpenSea traits with numeric values and no `display_type` are parsed as numeric instead of raising an `AttributeError` during string normalization.
