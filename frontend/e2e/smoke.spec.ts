import { expect, test } from '@playwright/test';

test('app loads and shows player screen', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('Yatzy')).toBeVisible();
});

test('protected routes redirect to player screen when no player selected', async ({ page }) => {
  await page.goto('/lobby');
  await expect(page).toHaveURL('/');
});
