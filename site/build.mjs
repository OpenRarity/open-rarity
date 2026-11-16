import { mkdir, readFile, writeFile, cp } from 'node:fs/promises';
import { marked } from 'marked';
const out = new URL('./dist/', import.meta.url);
await mkdir(out, { recursive: true });
for (const file of ['index.html','style.css','demo.js']) await cp(new URL(file, import.meta.url), new URL(file, out));
await cp(new URL('../typescript/dist/', import.meta.url), new URL('scorer/', out), { recursive: true });
await writeFile(new URL('.nojekyll', out), '');
await cp(new URL('../img/', import.meta.url), new URL('img/', out), { recursive: true });
for (const [slug, file, title] of [['spec','../SPEC.md','Scoring specification'],['changelog','../CHANGELOG.md','Changelog'],['readme','../README.md','Python guide']]) {
 const source = await readFile(new URL(file, import.meta.url), 'utf8');
 const html = marked.parse(source).replace(/<img[^>]+src="https?:[^>]*>/g, '').replaceAll('href="/scripts/"','href="https://github.com/OpenRarity/open-rarity/tree/main/scripts"');
 await writeFile(new URL(`${slug}.html`, out), `<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${title} | OpenRarity</title><link rel="stylesheet" href="style.css"><body><a class="skip" href="#content">Skip to content</a><header><a class="brand" href="./">◈ OpenRarity</a><a href="./#docs">Back to documentation</a></header><main id="content" class="document">${html}</main><footer>OpenRarity · Open source, reproducible rarity.</footer></body></html>`);
}
