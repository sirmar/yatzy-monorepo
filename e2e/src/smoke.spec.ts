import type { APIRequestContext, Page } from '@playwright/test';
import { expect, test } from '@playwright/test';

async function registerUser(
  request: APIRequestContext,
  page: Page
): Promise<{ accessToken: string }> {
  const email = `test-${Date.now()}-${Math.random().toString(36).slice(2)}@e2e.com`;
  const registerRes = await request.post('/auth/register', {
    data: { email, password: 'password123' },
  });
  if (!registerRes.ok()) {
    throw new Error(
      `Auth registration failed: ${registerRes.status()} ${await registerRes.text()}`
    );
  }
  const tokenRes = await request.get(
    `/auth/dev/verification-token?email=${encodeURIComponent(email)}`
  );
  if (!tokenRes.ok()) {
    throw new Error(
      `Failed to get verification token: ${tokenRes.status()} ${await tokenRes.text()}`
    );
  }
  const { token } = await tokenRes.json();
  const verifyRes = await request.post('/auth/verify-email', {
    data: { token },
  });
  if (!verifyRes.ok()) {
    throw new Error(`Email verification failed: ${verifyRes.status()} ${await verifyRes.text()}`);
  }
  const body = await verifyRes.json();
  await page.addInitScript((refreshToken) => {
    localStorage.setItem('yatzy_refresh_token', refreshToken);
  }, body.refresh_token);
  return { accessToken: body.access_token };
}

async function gotoAuthenticated(page: Page, url: string) {
  await page.goto(url);
  await page.waitForLoadState('load');
}

async function createPlayer(request: APIRequestContext, name: string, accessToken: string) {
  const res = await request.post('/api/players', {
    data: { name },
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  return await res.json();
}

async function createAndStartGame(
  request: APIRequestContext,
  playerId: number,
  accessToken: string
) {
  const gameRes = await request.post('/api/games', {
    data: { creator_id: playerId },
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  const game = await gameRes.json();
  const startRes = await request.post(`/api/games/${game.id}/start`, {
    data: { player_id: playerId },
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  return await startRes.json();
}

async function loginAs(page: Page, player: { id: number; name: string; created_at: string }) {
  await page.addInitScript((p) => {
    sessionStorage.setItem('yatzy_player', JSON.stringify(p));
  }, player);
}

async function setupPlayer(request: APIRequestContext, page: Page, path = '/lobby') {
  const { accessToken } = await registerUser(request, page);
  const player = await createPlayer(request, 'Alice', accessToken);
  await loginAs(page, player);
  await gotoAuthenticated(page, path);
  return { accessToken, player };
}

async function setupGame(request: APIRequestContext, page: Page) {
  const { accessToken } = await registerUser(request, page);
  const player = await createPlayer(request, 'Alice', accessToken);
  const game = await createAndStartGame(request, player.id, accessToken);
  await loginAs(page, player);
  await gotoAuthenticated(page, `/games/${game.id}`);
  return { player, game };
}

test('app loads and shows login screen', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('Yatzy')).toBeVisible();
});

test('unauthenticated access redirects to login', async ({ page }) => {
  await page.goto('/lobby');
  await expect(page).toHaveURL('/login');
});

test('authenticated user sees player screen', async ({ page, request }) => {
  await registerUser(request, page);
  await gotoAuthenticated(page, '/');
  await expect(page.getByLabel('Display name')).toBeVisible();
});

test('creating a player navigates to lobby', async ({ page, request }) => {
  await registerUser(request, page);
  await gotoAuthenticated(page, '/');
  await page.getByLabel('Display name').fill('Alice');
  await page.getByRole('button', { name: 'Continue' }).click();
  await page.waitForURL('/lobby');
  await expect(page.getByRole('button', { name: 'New game' })).toBeVisible();
});

test('existing player auto-navigates to lobby on login', async ({ page, request }) => {
  const { accessToken } = await registerUser(request, page);
  await createPlayer(request, 'Alice', accessToken);
  await gotoAuthenticated(page, '/');
  await page.waitForURL('/lobby');
  await expect(page.getByRole('button', { name: 'New game' })).toBeVisible();
});

test('editing player name via nav updates the displayed name', async ({ page, request }) => {
  await setupPlayer(request, page);
  await page.getByRole('button', { name: /alice/i }).click();
  await page.getByRole('link', { name: 'Profile' }).click();
  await page.waitForURL('/profile');
  await page.getByRole('button', { name: 'Edit' }).click();
  await page.getByLabel('Display name').fill('Alicia');
  await page.getByRole('button', { name: 'Save' }).click();
  await expect(page.getByRole('button', { name: /alicia/i })).toBeVisible();
});

test('creating a game shows it in the lobby', async ({ page, request }) => {
  await setupPlayer(request, page);
  await page.getByRole('button', { name: 'New game' }).click();
  await page.getByRole('button', { name: 'Create' }).click();
  await expect(page.getByRole('button', { name: /Start game/ })).toBeVisible();
});

test('starting a game navigates to the game screen', async ({ page, request }) => {
  await setupPlayer(request, page);
  await page.getByRole('button', { name: 'New game' }).click();
  await page.getByRole('button', { name: 'Create' }).click();
  await page.getByRole('button', { name: /Start game/ }).click();
  await page.waitForURL(/\/games\/\d+$/);
  await expect(page.getByRole('button', { name: 'Roll' })).toBeVisible();
});

test('rolling dice shows dice values', async ({ page, request }) => {
  await setupGame(request, page);
  await expect(page.getByRole('button', { name: 'Roll' })).toBeVisible();
  await page.getByRole('button', { name: 'Roll' }).click();
  for (let i = 0; i < 6; i++) {
    await expect(page.getByRole('button', { name: `Die ${i}` })).toHaveAttribute(
      'data-value',
      /[1-6]/
    );
  }
});

test('scoring a category completes the turn', async ({ page, request }) => {
  await setupGame(request, page);
  await expect(page.getByRole('button', { name: 'Roll' })).toBeVisible();
  await page.getByRole('button', { name: 'Roll' }).click();
  await expect(page.getByRole('button', { name: 'Die 0' })).toHaveAttribute('data-value', /[1-6]/);
  await page.getByText('Chance').click();
  await expect(page.getByRole('button', { name: 'Roll' })).toBeVisible();
});

test('profile page shows player stats', async ({ page, request }) => {
  await setupPlayer(request, page);
  await page.getByRole('button', { name: /alice/i }).click();
  await page.getByRole('link', { name: 'Profile' }).click();
  await page.waitForURL('/profile');
  await expect(page.getByText('all time').first()).toBeVisible();
});

test('high scores page shows all four mode buttons', async ({ page, request }) => {
  await setupPlayer(request, page, '/statistics/high-scores');
  await expect(page.getByText('High Scores')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Maxi Yatzy', exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Maxi Seq.', exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Yatzy', exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Yatzy Seq.', exact: true })).toBeVisible();
});

test('games played page shows all five mode buttons', async ({ page, request }) => {
  await setupPlayer(request, page, '/statistics/games-played');
  await expect(page.getByText('Most Games Played')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Total', exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Maxi Yatzy', exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Maxi Seq.', exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Yatzy', exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Yatzy Seq.', exact: true })).toBeVisible();
});

test('games played page is accessible from leaderboard nav', async ({ page, request }) => {
  await setupPlayer(request, page);
  await page.getByRole('button', { name: /leaderboard/i }).click();
  await page.getByRole('link', { name: 'Most games played' }).click();
  await page.waitForURL('/statistics/games-played');
  await expect(page.getByText('Most Games Played')).toBeVisible();
});

test('creating a maxi sequential game shows Maxi Sequential badge in lobby', async ({
  page,
  request,
}) => {
  await setupPlayer(request, page);
  await page.getByRole('button', { name: 'New game' }).click();
  await page.getByRole('button', { name: 'Maxi Sequential', exact: true }).click();
  await page.getByRole('button', { name: 'Create' }).click();
  await expect(page.getByRole('button', { name: /Start game/ })).toBeVisible();
  await expect(page.getByText('Maxi Sequential')).toBeVisible();
});

test('creating a yatzy game shows Yatzy badge in lobby', async ({ page, request }) => {
  await setupPlayer(request, page);
  await page.getByRole('button', { name: 'New game' }).click();
  await page.getByRole('button', { name: 'Yatzy', exact: true }).nth(1).click();
  await page.getByRole('button', { name: 'Create' }).click();
  await expect(page.getByRole('button', { name: /Start game/ })).toBeVisible();
  await expect(page.locator('ul').getByText('Yatzy', { exact: true })).toBeVisible();
});

test('creating a yatzy sequential game shows Yatzy Sequential badge in lobby', async ({
  page,
  request,
}) => {
  await setupPlayer(request, page);
  await page.getByRole('button', { name: 'New game' }).click();
  await page.getByRole('button', { name: 'Yatzy Sequential', exact: true }).click();
  await page.getByRole('button', { name: 'Create' }).click();
  await expect(page.getByRole('button', { name: /Start game/ })).toBeVisible();
  await expect(page.getByText('Yatzy Sequential')).toBeVisible();
});

test('game screen shows mode badge', async ({ page, request }) => {
  await setupGame(request, page);
  await expect(page.getByRole('button', { name: 'Roll' })).toBeVisible();
  await expect(page.locator('header').getByText(/Maxi Yatzy|Yatzy/)).toBeVisible();
});

test('yatzy game screen has 5 dice', async ({ page, request }) => {
  await setupPlayer(request, page);
  await page.getByRole('button', { name: 'New game' }).click();
  await page.getByRole('button', { name: 'Yatzy', exact: true }).nth(1).click();
  await page.getByRole('button', { name: 'Create' }).click();
  await page.getByRole('button', { name: /Start game/ }).click();
  await page.waitForURL(/\/games\/\d+$/);
  await page.getByRole('button', { name: 'Roll' }).click();
  for (let i = 0; i < 5; i++) {
    await expect(page.getByRole('button', { name: `Die ${i}` })).toHaveAttribute(
      'data-value',
      /[1-6]/
    );
  }
  await expect(page.getByRole('button', { name: 'Die 5' })).not.toBeVisible();
});

test('yatzy game screen does not show saved rolls', async ({ page, request }) => {
  await setupPlayer(request, page);
  await page.getByRole('button', { name: 'New game' }).click();
  await page.getByRole('button', { name: 'Yatzy', exact: true }).nth(1).click();
  await page.getByRole('button', { name: 'Create' }).click();
  await page.getByRole('button', { name: /Start game/ }).click();
  await page.waitForURL(/\/games\/\d+$/);
  await expect(page.getByText('Saved')).not.toBeVisible();
});

test('aborting a game redirects to lobby', async ({ page, request }) => {
  await setupGame(request, page);
  await expect(page.getByRole('button', { name: 'Roll' })).toBeVisible();
  await page.getByRole('button', { name: 'Games', exact: true }).click();
  await page.getByRole('button', { name: 'Abort' }).first().click();
  await page.getByRole('button', { name: 'Abort' }).click();
  await page.waitForURL('/lobby');
  await expect(page.getByRole('button', { name: 'New game' })).toBeVisible();
});
