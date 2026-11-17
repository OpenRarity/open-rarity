# Releasing

We plan to release Python and TypeScript together, starting with an RC for feedback.
The equivalent RC versions are Python `1.0.0rc1` and npm `1.0.0-rc.1`; the final
version is `1.0.0` for both. Development checkouts use `1.0.0.dev0` and `1.0.0-dev.0`.
These source versions do not indicate a registry release. PyPI 0.7.5 remains the
current published Python version; TypeScript is not yet on npm.

We hope to set up automatic publishing to PyPI and npm from GitHub releases.
Publishing access and workflows are still pending. Current workflows build and
validate packages but do not publish them. Creating a GitHub release currently
deploys documentation, not packages.

## Candidate checklist

- [ ] Confirm registry access and the final npm package name.
- [ ] Update Python and npm versions together, including the npm lockfile.
- [ ] Pass the Python runtime matrix, TypeScript tests, both cross-language parity checks, and browser tests.
- [ ] Regenerate schemas and pass the freshness check.
- [ ] Run `python -m scripts.check_distributions` with Python build tools and TypeScript dependencies installed. This builds the wheel and sdist, installs the wheel and npm tarball in clean consumers, and checks the console command, exports, types, README, and license.
- [ ] Review the specification, migration notes, CLI guide, and benchmark limitations.
- [ ] Resolve or explicitly defer every remaining feature in the [1.0 tracker](https://github.com/OpenRarity/open-rarity/issues/154), including the optional TypeScript fetching helper.
- [ ] Obtain maintainer approval before publishing an RC. Remove npm's `private` guard only when publishing is configured; use the `next` dist-tag for prereleases.
- [ ] Verify both registry artifacts by installing the exact published versions, then collect RC feedback.
- [ ] Address feedback and obtain approval before publishing the final release with npm's `latest` dist-tag.

## Publishing workflow plan

Build from the approved release tag, validate matching versions and release type,
and publish the already-tested artifacts. Configure registry trusted publishing
and protected release environments before enabling those jobs. Historical GitHub
release backfills must not trigger package publication. Keep documentation deployment
separate from package publication so either can be retried independently.

Release notes should describe user-visible changes and link to migration guidance.
If only one registry succeeds, inspect both registries before retrying; never
attempt to overwrite an existing published version.
