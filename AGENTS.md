# OpenRarity

Python reference library, TypeScript scorer, and static documentation site.

- `open_rarity/`: Python models, scoring, and optional network helpers.
- `typescript/`: ESM scorer with zero runtime dependencies.
- `site/`: static site and browser tests; see `site/README.md`.
- `SPEC.md`: scoring contract. `tests/fixtures/legacy_075.json`: compatibility goldens.

Integration guidance: [docs/agents.md](docs/agents.md). Machine-readable entry point: [llms.txt](llms.txt).

## Changes

- Keep scoring pure; fetching belongs in optional helpers. Mock HTTP/RPC in tests.
- Preserve supported 0.7.5 scores and ranks without effective creator config, except the documented token-ID tie order.
- Scoring changes need a regression fixture, a spec update, and a changelog entry. Check Python/TypeScript parity, including large numbers and Unicode.
- Retain source trait entries; do not silently discard duplicates during input parsing.
- Use a worktree and focused PR. Check CI and review threads after each push.
- Never print credentials. Publishing packages or deploying the site needs explicit authorization.

## Validation

Use Python 3.12–3.15 in a virtual environment. Install the package with `python -m pip install -e '.[opensea]'` and the test/quality tools listed in `pyproject.toml`.

- Python: `python -m pytest -q`, `ruff check .`, `ruff format --check .`, `mypy open_rarity`.
- TypeScript: `npm ci --prefix typescript`, then `npm run build --prefix typescript` and `npm test --prefix typescript`.
- Site: build TypeScript first, then `npm ci --prefix site`, `npm run build --prefix site`, `npx --prefix site playwright install chromium`, and `npm test --prefix site`.

Run checks relevant to the change; CI covers the full matrix. For site edits, inspect mobile/desktop and light/dark output. Edit source files, not generated `dist/` output.
