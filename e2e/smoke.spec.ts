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
    throw new Error(`Auth registration failed: ${registerRes.status()} ${await registerRes.text()}`);
  }
  const tokenRes = await request.get(`/auth/dev/verification-token?email=${encodeURIComponent(email)}`);
  if (!tokenRes.ok()) {
    throw new Error(`Failed to get verification token: ${tokenRes.status()} ${await tokenRes.text()}`);
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
  await expect(page.getByPlaceholder('Enter your name')).toBeVisible();
});

test('creating a player navigates to lobby', async ({ page, request }) => {
  await registerUser(request, page);
  await gotoAuthenticated(page, '/');
  await page.getByPlaceholder('Enter your name').fill('Alice');
  await page.getByRole('button', { name: 'Create' }).click();
  await page.waitForURL('/lobby');
  await expect(page.getByRole('heading', { name: 'Lobby' })).toBeVisible();
});

test('existing player auto-navigates to lobby on login', async ({ page, request }) => {
  const { accessToken } = await registerUser(request, page);
  await createPlayer(request, 'Alice', accessToken);
  await gotoAuthenticated(page, '/');
  await page.waitForURL('/lobby');
  await expect(page.getByRole('heading', { name: 'Lobby' })).toBeVisible();
});

test('editing player name via nav updates the displayed name', async ({ page, request }) => {
  const { accessToken } = await registerUser(request, page);
  const player = await createPlayer(request, 'Alice', accessToken);
  await loginAs(page, player);
  await gotoAuthenticated(page, '/lobby');
  await page.getByRole('button', { name: /alice/i }).click();
  await page.getByRole('menuitem', { name: 'Profile' }).click();
  await page.waitForURL('/profile');
  await page.getByLabel('Name').fill('Alicia');
  await page.getByRole('button', { name: 'Save' }).click();
  await page.waitForURL('/lobby');
  await expect(page.getByRole('button', { name: /alicia/i })).toBeVisible();
});

test('creating a game shows it in the lobby', async ({ page, request }) => {
  const { accessToken } = await registerUser(request, page);
  const player = await createPlayer(request, 'Alice', accessToken);
  await loginAs(page, player);
  await gotoAuthenticated(page, '/lobby');
  await page.getByRole('button', { name: 'New Game' }).click();
  await expect(page.getByRole('button', { name: /Start game/ })).toBeVisible();
});

test('starting a game navigates to the game screen', async ({ page, request }) => {
  const { accessToken } = await registerUser(request, page);
  const player = await createPlayer(request, 'Alice', accessToken);
  await loginAs(page, player);
  await gotoAuthenticated(page, '/lobby');
  await page.getByRole('button', { name: 'New Game' }).click();
  await page.getByRole('button', { name: /Start game/ }).click();
  await page.waitForURL(/\/games\/\d+$/);
  await expect(page.getByRole('heading', { name: /Game #/ })).toBeVisible();
});

test('rolling dice shows dice values', async ({ page, request }) => {
  const { accessToken } = await registerUser(request, page);
  const player = await createPlayer(request, 'Alice', accessToken);
  const game = await createAndStartGame(request, player.id, accessToken);
  await loginAs(page, player);
  await gotoAuthenticated(page, `/games/${game.id}`);
  await expect(page.getByRole('heading', { name: /Game #/ })).toBeVisible();
  await page.getByRole('button', { name: 'Roll' }).click();
  for (let i = 0; i < 6; i++) {
    await expect(page.getByRole('button', { name: `Die ${i}` })).toHaveAttribute(
      'data-value',
      /[1-6]/
    );
  }
});

test('scoring a category completes the turn', async ({ page, request }) => {
  const { accessToken } = await registerUser(request, page);
  const player = await createPlayer(request, 'Alice', accessToken);
  const game = await createAndStartGame(request, player.id, accessToken);
  await loginAs(page, player);
  await gotoAuthenticated(page, `/games/${game.id}`);
  await expect(page.getByRole('heading', { name: /Game #/ })).toBeVisible();
  await page.getByRole('button', { name: 'Roll' }).click();
  await expect(page.getByRole('button', { name: 'Die 0' })).toHaveAttribute('data-value', /[1-6]/);
  await page.getByRole('rowheader', { name: 'Chance' }).click();
  await expect(page.getByRole('button', { name: 'Roll' })).toBeVisible();
});

test('profile page shows player stats', async ({ page, request }) => {
  const { accessToken } = await registerUser(request, page);
  const player = await createPlayer(request, 'Alice', accessToken);
  await loginAs(page, player);
  await gotoAuthenticated(page, '/lobby');
  await page.getByRole('button', { name: /alice/i }).click();
  await page.getByRole('menuitem', { name: 'Profile' }).click();
  await page.waitForURL('/profile');
  await expect(page.getByText(/Total games played/)).toBeVisible();
});

test('high scores page shows all four mode buttons', async ({ page, request }) => {
  const { accessToken } = await registerUser(request, page);
  const player = await createPlayer(request, 'Alice', accessToken);
  await loginAs(page, player);
  await gotoAuthenticated(page, '/statistics/high-scores');
  await expect(page.getByRole('heading', { name: 'High Scores' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Maxi Yatzy', exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Maxi Yatzy Sequential', exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Yatzy', exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Yatzy Sequential', exact: true })).toBeVisible();
});

test('games played page shows all five mode buttons', async ({ page, request }) => {
  const { accessToken } = await registerUser(request, page);
  const player = await createPlayer(request, 'Alice', accessToken);
  await loginAs(page, player);
  await gotoAuthenticated(page, '/statistics/games-played');
  await expect(page.getByRole('heading', { name: 'Games Played' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Total', exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Maxi Yatzy', exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Maxi Yatzy Sequential', exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Yatzy', exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Yatzy Sequential', exact: true })).toBeVisible();
});

test('games played page is accessible from statistics nav', async ({ page, request }) => {
  const { accessToken } = await registerUser(request, page);
  const player = await createPlayer(request, 'Alice', accessToken);
  await loginAs(page, player);
  await gotoAuthenticated(page, '/lobby');
  await page.getByRole('button', { name: 'Statistics ▾' }).click();
  await page.getByRole('menuitem', { name: 'Games Played' }).click();
  await page.waitForURL('/statistics/games-played');
  await expect(page.getByRole('heading', { name: 'Games Played' })).toBeVisible();
});

test('creating a maxi sequential game shows Maxi Yatzy Sequential badge in lobby', async ({
  page,
  request,
}) => {
  const { accessToken } = await registerUser(request, page);
  const player = await createPlayer(request, 'Alice', accessToken);
  await loginAs(page, player);
  await gotoAuthenticated(page, '/lobby');
  await page.getByRole('combobox', { name: /mode/i }).selectOption('maxi_sequential');
  await page.getByRole('button', { name: 'New Game' }).click();
  await expect(page.getByRole('button', { name: /Start game/ })).toBeVisible();
  await expect(page.locator('ul').getByText('Maxi Yatzy Sequential')).toBeVisible();
});

test('creating a yatzy game shows Yatzy badge in lobby', async ({
  page,
  request,
}) => {
  const { accessToken } = await registerUser(request, page);
  const player = await createPlayer(request, 'Alice', accessToken);
  await loginAs(page, player);
  await gotoAuthenticated(page, '/lobby');
  await page.getByRole('combobox', { name: /mode/i }).selectOption('yatzy');
  await page.getByRole('button', { name: 'New Game' }).click();
  await expect(page.getByRole('button', { name: /Start game/ })).toBeVisible();
  await expect(page.locator('ul').getByText('Yatzy', { exact: true })).toBeVisible();
});

test('creating a yatzy sequential game shows Yatzy Sequential badge in lobby', async ({
  page,
  request,
}) => {
  const { accessToken } = await registerUser(request, page);
  const player = await createPlayer(request, 'Alice', accessToken);
  await loginAs(page, player);
  await gotoAuthenticated(page, '/lobby');
  await page.getByRole('combobox', { name: /mode/i }).selectOption('yatzy_sequential');
  await page.getByRole('button', { name: 'New Game' }).click();
  await expect(page.getByRole('button', { name: /Start game/ })).toBeVisible();
  await expect(page.locator('ul').getByText('Yatzy Sequential', { exact: true })).toBeVisible();
});

test('game screen shows mode badge', async ({ page, request }) => {
  const { accessToken } = await registerUser(request, page);
  const player = await createPlayer(request, 'Alice', accessToken);
  const game = await createAndStartGame(request, player.id, accessToken);
  await loginAs(page, player);
  await gotoAuthenticated(page, `/games/${game.id}`);
  await expect(page.getByText(/Alice's turn/)).toBeVisible();
  await expect(page.locator('h1').getByText(/Maxi Yatzy|Yatzy/)).toBeVisible();
});

test('yatzy game screen has 5 dice', async ({ page, request }) => {
  const { accessToken } = await registerUser(request, page);
  const player = await createPlayer(request, 'Alice', accessToken);
  await loginAs(page, player);
  await gotoAuthenticated(page, '/lobby');
  await page.getByRole('combobox', { name: /mode/i }).selectOption('yatzy');
  await page.getByRole('button', { name: 'New Game' }).click();
  await page.getByRole('button', { name: /Start game/ }).click();
  await page.waitForURL(/\/games\/\d+$/);
  await page.getByRole('button', { name: 'Roll' }).click();
  for (let i = 0; i < 5; i++) {
    await expect(page.getByRole('button', { name: `Die ${i}` })).toHaveAttribute('data-value', /[1-6]/);
  }
  await expect(page.getByRole('button', { name: 'Die 5' })).not.toBeVisible();
});

test('yatzy game screen does not show saved rolls', async ({ page, request }) => {
  const { accessToken } = await registerUser(request, page);
  const player = await createPlayer(request, 'Alice', accessToken);
  await loginAs(page, player);
  await gotoAuthenticated(page, '/lobby');
  await page.getByRole('combobox', { name: /mode/i }).selectOption('yatzy');
  await page.getByRole('button', { name: 'New Game' }).click();
  await page.getByRole('button', { name: /Start game/ }).click();
  await page.waitForURL(/\/games\/\d+$/);
  await expect(page.getByText(/Saved rolls/)).not.toBeVisible();
});


test('aborting a game redirects to lobby', async ({ page, request }) => {
  const { accessToken } = await registerUser(request, page);
  const player = await createPlayer(request, 'Alice', accessToken);
  const game = await createAndStartGame(request, player.id, accessToken);
  await loginAs(page, player);
  await gotoAuthenticated(page, `/games/${game.id}`);
  await expect(page.getByRole('heading', { name: /Game #/ })).toBeVisible();
  await page.getByRole('button', { name: /abort game/i }).click();
  await page.getByRole('button', { name: /^abort$/i }).click();
  await page.waitForURL('/lobby');
  await expect(page.getByRole('heading', { name: 'Lobby' })).toBeVisible();
});
