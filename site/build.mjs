import { mkdir, readFile, writeFile, cp } from 'node:fs/promises';
import { marked } from 'marked';
const base = (process.env.SITE_URL || 'https://openrarity.github.io/open-rarity').replace(/\/$/, '');
const out = new URL('./dist/', import.meta.url);
await mkdir(out, { recursive: true });
for (const file of ['index.html','style.css','demo.js','favicon.svg']) await cp(new URL(file, import.meta.url), new URL(file, out));
await cp(new URL('../typescript/dist/', import.meta.url), new URL('scorer/', out), { recursive: true });
await writeFile(new URL('.nojekyll', out), '');
await cp(new URL('../img/', import.meta.url), new URL('img/', out), { recursive: true });
await cp(new URL('../schemas/', import.meta.url), new URL('schemas/', out), { recursive: true });
const llms = await readFile(new URL('../llms.txt', import.meta.url), 'utf8');
await writeFile(new URL('llms.txt', out), llms.replaceAll('https://openrarity.github.io/open-rarity', base));
for (const [slug, file, title] of [['cli','../docs/cli.md','Local CLI'],['benchmarks','../docs/benchmarks.md','Scoring benchmarks'],['agents','../docs/agents.md','Agent guide'],['api','../docs/api.md','Scoring API reference'],['spec','../SPEC.md','Scoring specification'],['changelog','../CHANGELOG.md','Changelog'],['readme','../docs/python.md','Python guide'],['migration','../docs/migration.md','Migrating to 1.0']]) {
 const source = await readFile(new URL(file, import.meta.url), 'utf8');
 await writeFile(new URL(file.split('/').at(-1), out), source.replaceAll('(../SPEC.md)', '(SPEC.md)').replaceAll('(../schemas/', '(schemas/'));
 const html = marked.parse(source).replaceAll('<table>', '<div class="document-table" tabindex="0" role="region" aria-label="Reference table"><table>').replaceAll('</table>', '</table></div>').replaceAll('<pre>', '<pre tabindex="0">').replaceAll('href="cli.md"','href="cli.html"').replaceAll('href="benchmarks.md"','href="benchmarks.html"').replaceAll('href="api.md"','href="api.html"').replaceAll('href="../schemas/','href="schemas/').replaceAll('href="migration.md"','href="migration.html"').replaceAll('href="python.md"','href="readme.html"').replaceAll('href="../SPEC.md"','href="spec.html"').replace(/<img[^>]+src="https?:[^>]*>/g, tag => tag.match(/alt="([^"]*)"/)?.[1] || 'Reference').replaceAll('href="/scripts/"','href="https://github.com/OpenRarity/open-rarity/tree/main/scripts"');
 await writeFile(new URL(`${slug}.html`, out), `<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="favicon.svg" type="image/svg+xml"><title>${title} | OpenRarity</title><link rel="stylesheet" href="style.css"><body><a class="skip" href="#content">Skip to content</a><header><a class="brand" href="./">◈ OpenRarity</a><a href="./#docs">Back to documentation</a></header><main id="content" class="document">${html}</main><footer>OpenRarity · Open source, reproducible rarity.</footer></body></html>`);
}


await writeFile(new URL('robots.txt', out), `User-agent: *\nAllow: /\nSitemap: ${base}/sitemap.xml\n`);
await writeFile(new URL('sitemap.xml', out), `<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${['','cli.html','benchmarks.html','agents.html','api.html','spec.html','readme.html','changelog.html','migration.html'].map(path => `<url><loc>${base}/${path}</loc></url>`).join('')}</urlset>`);

const homepage = await readFile(new URL('index.html', out), 'utf8');
await writeFile(new URL('index.html', out), homepage.replace('</head>', `<link rel="canonical" href="${base}/"><meta property="og:url" content="${base}/"><meta property="og:image" content="${base}/img/OR_Github_banner.jpg"></head>`));
