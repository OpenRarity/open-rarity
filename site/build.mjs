import { mkdir, readFile, writeFile, cp } from 'node:fs/promises';
import { marked } from 'marked';
const out = new URL('./dist/', import.meta.url);
await mkdir(out, { recursive: true });
for (const file of ['index.html','style.css','demo.js','favicon.svg']) await cp(new URL(file, import.meta.url), new URL(file, out));
await cp(new URL('../typescript/dist/', import.meta.url), new URL('scorer/', out), { recursive: true });
await writeFile(new URL('.nojekyll', out), '');
await cp(new URL('../img/', import.meta.url), new URL('img/', out), { recursive: true });
for (const [slug, file, title] of [['spec','../SPEC.md','Scoring specification'],['changelog','../CHANGELOG.md','Changelog'],['readme','../README.md','Python guide']]) {
 const source = await readFile(new URL(file, import.meta.url), 'utf8');
 const html = marked.parse(source).replace(/<img[^>]+src="https?:[^>]*>/g, tag => tag.match(/alt="([^"]*)"/)?.[1] || 'Reference').replaceAll('href="/scripts/"','href="https://github.com/OpenRarity/open-rarity/tree/main/scripts"');
 await writeFile(new URL(`${slug}.html`, out), `<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="favicon.svg" type="image/svg+xml"><title>${title} | OpenRarity</title><link rel="stylesheet" href="style.css"><body><a class="skip" href="#content">Skip to content</a><header><a class="brand" href="./">◈ OpenRarity</a><a href="./#docs">Back to documentation</a></header><main id="content" class="document">${html}</main><footer>OpenRarity · Open source, reproducible rarity.</footer></body></html>`);
}

const base = (process.env.SITE_URL || 'https://openrarity.github.io/open-rarity').replace(/\/$/, '');
await writeFile(new URL('robots.txt', out), `User-agent: *\nAllow: /\nSitemap: ${base}/sitemap.xml\n`);
await writeFile(new URL('sitemap.xml', out), `<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${['','spec.html','readme.html','changelog.html'].map(path => `<url><loc>${base}/${path}</loc></url>`).join('')}</urlset>`);
