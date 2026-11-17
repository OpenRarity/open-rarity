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
