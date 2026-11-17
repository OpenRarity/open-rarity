import {test, expect} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
for (const theme of ['light','dark']) for (const path of ['/','/readme.html','/spec.html','/changelog.html','/migration.html','/agents.html','/api.html']) {
 test(`${theme} accessibility: ${path}`, async ({page}) => {
  await page.emulateMedia({colorScheme:theme});
  await page.goto(path);
  const result=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
  expect(result.violations).toEqual([]);
 });
}
