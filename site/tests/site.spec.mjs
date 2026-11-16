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
