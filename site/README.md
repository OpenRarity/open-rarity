# Site preview

Build the TypeScript package, then the static site:

```sh
npm ci --prefix typescript
npm run build --prefix typescript
npm ci --prefix site
npm run build --prefix site
python3 -m http.server 4173 --directory site/dist
```

The site uses relative URLs so the same build works at the repository's GitHub Pages path or a custom domain. CI builds and tests a downloadable preview artifact. Publishing is a separate step after the preview is approved; this workflow does not deploy.

The browser demo imports the compiled TypeScript scorer and supports its current categorical input subset. It sends no metadata to a server. The spec, changelog, and Python guide are generated from repository Markdown.

Still needed before the full 1.0 site launch: configured scoring and per-trait explanations in the browser, final API quickstarts, the reviewed adopter/community list, social preview artwork, and deployment configuration. Automated accessibility tests and a local mobile Lighthouse audit now pass; see evidence/AUDIT.md. Set SITE_URL when building for a custom domain so the sitemap uses its final address. DNS and the existing site are outside this preview PR.
