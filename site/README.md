# Website

The concise landing page links the scorer, packages, releases, and longer guides.

```sh
npm ci --prefix typescript
npm run build --prefix typescript
npm ci --prefix site
npm run build --prefix site
npm exec --prefix site -- playwright install chromium
npm test --prefix site
```

CI tests pull requests and deploys successful main builds to GitHub Pages.
Pull requests cannot deploy. The browser scorer never sends metadata to a server.
Relative URLs support both the project URL and a future custom domain.
Set `SITE_URL` to the final origin when building for the custom domain.

See [DNS cutover](../docs/DNS-CUTOVER.md) for the domain-owner handoff.

Agent documentation lives in `docs/agents.md` and `docs/api.md`; the root `llms.txt`
is published with URLs adapted to `SITE_URL`. The build also publishes raw Markdown
and `schemas/`. After changing Python models, run `python -m scripts.generate_schemas`
and commit the results. CI checks freshness before building.
