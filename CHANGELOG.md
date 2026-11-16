# Changelog

## Unreleased

### Changed

- Equal unique-count and score ties now use numeric token ID order, then raw ID order. Scores and equal-score ranks are unchanged. This changes the order of tied tokens compared with 0.7.5.

### Fixed

- OpenSea traits with numeric values and no `display_type` are parsed as numeric instead of raising an `AttributeError` during string normalization.
