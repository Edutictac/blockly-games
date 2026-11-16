const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

for (const lang of ['es', 'ca']) {
  test(`teacher guides can be found and used in ${lang}`, async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto(`/index.html?lang=${lang}`);
    const entry = page.locator('#teacherGuides');
    await expect(entry).toBeVisible();
    await entry.click();
    await expect(page).toHaveURL(new RegExp(`/guias/${lang}/index.html$`));
    await expect(page.locator('h1')).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    const guideLinks = await page.locator('article a[href$=".html"]').evaluateAll(
        (links) => [...new Set(links.map((link) => link.href))]);
    expect(guideLinks).toHaveLength(9);
    for (const url of guideLinks) {
      await page.goto(url);
      await expect(page.locator('h1')).toBeVisible();
      await expect(page.locator('#print-guide')).toBeVisible();
      const play = page.locator('a.button');
      const gameUrl = await play.getAttribute('href');
      const response = await page.request.get(new URL(gameUrl, page.url()).href);
      expect(response.status()).toBe(200);
      expect(gameUrl).toContain(`lang=${lang}`);
      const other = page.locator('nav a[hreflang]');
      const translated = new URL(await other.getAttribute('href'), page.url()).href;
      expect((await page.request.get(translated)).status()).toBe(200);
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    }
  });
}

test('guide reading and print layouts remain accessible', async ({ page }) => {
  await page.goto('/guias/es/maze.html');
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations.filter((v) => ['serious', 'critical'].includes(v.impact))).toEqual([]);
  await page.emulateMedia({ media: 'print' });
  await expect(page.locator('.actions')).toBeHidden();
  await expect(page.locator('article')).toBeVisible();
});
