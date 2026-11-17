# Changelog

## Unreleased

### Added

- The TypeScript package can score and rank categorical collections using the 0.7.5 compatibility rules and deterministic token ID order.
- The TypeScript package can parse creator rarity settings from a contractURI document or a direct rarity object.

### Changed

- Equal unique-count and score ties now use numeric token ID order, then raw ID order. Scores and equal-score ranks are unchanged. This changes the order of tied tokens compared with 0.7.5.

### Fixed

- OpenSea traits with numeric values and no `display_type` are parsed as numeric instead of raising an `AttributeError` during string normalization.
