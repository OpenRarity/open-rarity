import { test, expect } from '@playwright/test';
for (const width of [390, 1440]) {
 test(`playground and layout at ${width}px`, async ({page}, testInfo) => {
  await page.setViewportSize({width,height:1000});
  await page.goto('/');
  await expect(page.locator('#results tr')).toHaveCount(4);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.locator('#collection').fill('{');
  await page.locator('#score').click();
  await expect(page.locator('#status')).toHaveClass('error');
  await expect(page.locator('#results tr')).toHaveCount(0);
  await page.locator('#reset').click();
  await expect(page.locator('#results tr')).toHaveCount(4);
  await page.screenshot({path:testInfo.outputPath(`site-${width}.png`),fullPage:true});
  await page.emulateMedia({colorScheme:'dark'});
  await page.screenshot({path:testInfo.outputPath(`site-${width}-dark.png`),fullPage:true});
  await page.goto('/spec.html');
  await expect(page.locator('h1')).toContainText('scoring specification');
 });
}
test('token IDs are rendered as text', async ({page}, testInfo) => {
 await page.goto('/');
 await page.locator('#collection').fill(JSON.stringify({tokens:[{token_id:'<img src=x onerror=alert(1)>',token_id_kind:'raw',traits:[]}]}));
 await page.locator('#score').click();
 await expect(page.locator('#results img')).toHaveCount(0);
 await expect(page.locator('#results')).toContainText('<img');
});
test('local file upload and result download', async ({page}) => {
 await page.goto('/');
 await page.locator('#upload').setInputFiles({name:'collection.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify({tokens:[{token_id:'7',traits:[]}]}))});
 await expect(page.locator('#results tr')).toHaveCount(1);
 await expect(page.locator('#results')).toContainText('7');
 const pending = page.waitForEvent('download');
 await page.locator('#download').click();
 const download = await pending;
 expect(download.suggestedFilename()).toBe('openrarity-results.json');
 const stream = await download.createReadStream();
 const chunks=[]; for await (const chunk of stream) chunks.push(chunk);
 const results=JSON.parse(Buffer.concat(chunks).toString());
 expect(results[0].token_id).toBe('7');
 await page.locator('#collection').fill('{'); await page.locator('#score').click();
 await expect(page.locator('#download')).toBeDisabled();
});
test('creator settings preserve exact JSON numbers', async ({page}) => {
 await page.goto('/');
 await page.locator('#collection').fill('{"tokens":[{"token_id":"1","traits":[{"trait_type":"Level","value":9007199254740992}]},{"token_id":"2","traits":[{"trait_type":"Level","value":9007199254740993}]}],"rarity":{"trait_count":"exclude","traits":[{"trait_type":"Level","mode":"higher_is_rarer"}]}}');
 await page.locator('#score').click();
 await expect(page.locator('#results tr').first().locator('td').nth(1)).toHaveText('2');
 await expect(page.locator('#results tr').first().locator('td').nth(2)).toHaveText('1.000000');
});
test('legacy anchors and local documentation links exist', async ({page}) => {
 await page.goto('/');
 for (const id of ['Dev-docs','Community','FAQ']) await expect(page.locator(`[id="${id}"]`)).toHaveCount(1);
 for (const path of ['readme.html','migration.html','spec.html','changelog.html']) {
  const response=await page.request.get('/'+path);expect(response.status()).toBe(200);
 }
});
test('numeric example and reset keep creator settings', async ({page}) => {
 await page.goto('/');
 await page.locator('#sample').selectOption('numeric');
 await expect(page.locator('#results tr')).toHaveCount(3);
 await expect(page.locator('#results tr').first().locator('td').nth(1)).toHaveText('2');
 await page.locator('#collection').fill('{'); await page.locator('#score').click();
 await page.locator('#reset').click();
 await expect(page.locator('#results tr')).toHaveCount(3);
 await page.locator('#sample').selectOption('categorical');
 await expect(page.locator('#results tr')).toHaveCount(4);
});
test('install command copies to clipboard', async ({page,context}) => {
 await context.grantPermissions(['clipboard-read','clipboard-write']);
 await page.goto('/');
 await page.locator('#copy-install').click();
 await expect(page.locator('#copy-install')).toHaveText('Copied');
 expect(await page.evaluate(()=>navigator.clipboard.readText())).toBe('pip install open-rarity');
});

test('agent index links to published Markdown and generated schemas', async ({request}) => {
 const response = await request.get('/llms.txt');
 expect(response.status()).toBe(200);
 const text = await response.text();
 expect(text).toContain('1.0 development');
 for (const [, url] of text.matchAll(/\]\((https:\/\/openrarity.github.io\/open-rarity\/[^)]+)\)/g)) {
  const path = new URL(url).pathname.replace('/open-rarity', '');
  expect((await request.get(path)).status(), path).toBe(200);
 }
 const schema = await (await request.get('/schemas/collection.schema.json')).json();
 expect(schema.$schema).toContain('2020-12');
 expect(schema.$defs.TokenInput.required).toContain('traits');
});
for (const width of [390, 1440]) for (const theme of ['light', 'dark']) {
 test(`agent documentation layout: ${width}px ${theme}`, async ({page}, testInfo) => {
  await page.setViewportSize({width, height:1000});
  await page.emulateMedia({colorScheme:theme});
  for (const path of ['/agents.html', '/api.html']) {
   await page.goto(path);
   await page.screenshot({path:testInfo.outputPath(path.slice(1)+'.png'),fullPage:true});
   expect(await page.evaluate(()=>document.documentElement.scrollWidth <= innerWidth)).toBe(true);
   for (const href of await page.locator('main a[href]').evaluateAll(links=>links.map(a=>a.getAttribute('href')))) {
    if (!href.startsWith('http')) expect((await page.request.get(new URL(href, page.url()).href)).status(), href).toBe(200);
   }
  }
 });
}
