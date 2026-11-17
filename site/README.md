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
