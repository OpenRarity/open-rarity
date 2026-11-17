# Releasing

We plan to publish the Python and TypeScript packages together. The first 1.0 release will be `1.0.0rc1` so users can try it and report problems before `1.0.0`.

We hope to set up automatic publishing to PyPI and npm from GitHub releases. The publishing workflows are not in place yet. Until they are, creating a GitHub release does not publish either package.

Before publishing a release:

1. Confirm that both packages use the same version and pass their tests and shared conformance fixtures.
2. Check the contents of the Python distributions and npm package.
3. Publish the release candidate, verify that both registries show it, and collect feedback.
4. Fix any reported problems before publishing the final 1.0 release.

Release notes should describe user-visible changes and link to the migration guide when an API changes.
