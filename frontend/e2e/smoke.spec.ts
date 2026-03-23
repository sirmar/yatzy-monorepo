import type { APIRequestContext, Page } from '@playwright/test';
import { expect, test } from '@playwright/test';

async function createPlayer(request: APIRequestContext, name: string) {
  const res = await request.post('/api/players', { data: { name } });
  return await res.json();
}

async function createAndStartGame(request: APIRequestContext, playerId: number) {
  const gameRes = await request.post('/api/games', { data: { creator_id: playerId } });
  const game = await gameRes.json();
  const startRes = await request.post(`/api/games/${game.id}/start`, {
    data: { player_id: playerId },
  });
  return await startRes.json();
}

async function loginAs(page: Page, player: { id: number; name: string; created_at: string }) {
  await page.addInitScript((p) => {
    sessionStorage.setItem('yatzy_player', JSON.stringify(p));
  }, player);
}

test('app loads and shows player screen', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('Yatzy')).toBeVisible();
});

test('protected routes redirect to player screen when no player selected', async ({ page }) => {
  await page.goto('/lobby');
  await expect(page).toHaveURL('/');
});

test('creating a player navigates to lobby', async ({ page }) => {
  await page.goto('/');
  await page.getByPlaceholder('Enter your name').fill('Alice');
  await page.getByRole('button', { name: 'Create' }).click();
  await page.waitForURL('/lobby');
  await expect(page.getByRole('heading', { name: 'Lobby' })).toBeVisible();
});

test('creating a game shows it in the lobby', async ({ page, request }) => {
  const player = await createPlayer(request, 'Alice');
  await loginAs(page, player);
  await page.goto('/lobby');
  await page.getByRole('button', { name: 'New Game' }).click();
  await expect(page.getByRole('button', { name: /Start game/ })).toBeVisible();
});

test('starting a game navigates to the game screen', async ({ page, request }) => {
  const player = await createPlayer(request, 'Alice');
  await loginAs(page, player);
  await page.goto('/lobby');
  await page.getByRole('button', { name: 'New Game' }).click();
  await page.getByRole('button', { name: /Start game/ }).click();
  await page.waitForURL(/\/games\/\d+$/);
  await expect(page.getByRole('heading', { name: /Game #/ })).toBeVisible();
});

test('rolling dice shows dice values', async ({ page, request }) => {
  const player = await createPlayer(request, 'Alice');
  const game = await createAndStartGame(request, player.id);
  await loginAs(page, player);
  await page.goto(`/games/${game.id}`);
  await page.getByRole('button', { name: 'Roll' }).click();
  for (let i = 0; i < 6; i++) {
    await expect(page.getByRole('button', { name: `Die ${i}` })).toHaveAttribute(
      'data-value',
      /[1-6]/
    );
  }
});

test('scoring a category completes the turn', async ({ page, request }) => {
  const player = await createPlayer(request, 'Alice');
  const game = await createAndStartGame(request, player.id);
  await loginAs(page, player);
  await page.goto(`/games/${game.id}`);
  await page.getByRole('button', { name: 'Roll' }).click();
  await expect(page.getByRole('button', { name: 'Die 0' })).toHaveAttribute('data-value', /[1-6]/);
  await page.getByRole('rowheader', { name: 'Chance' }).click();
  await expect(page.getByRole('button', { name: 'Roll' })).toBeVisible();
});

test('aborting a game redirects to lobby', async ({ page, request }) => {
  const player = await createPlayer(request, 'Alice');
  const game = await createAndStartGame(request, player.id);
  await loginAs(page, player);
  await page.goto(`/games/${game.id}`);
  await page.getByRole('button', { name: /abort game/i }).click();
  await page.waitForURL('/lobby');
  await expect(page.getByRole('heading', { name: 'Lobby' })).toBeVisible();
});
