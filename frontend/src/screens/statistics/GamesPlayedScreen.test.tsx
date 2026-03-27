import { screen } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import { HttpResponse, http } from 'msw';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { ALICE, createMockServer, renderWithProviders } from '@/test/helpers';
import { GamesPlayedScreen } from './GamesPlayedScreen';

const server = createMockServer();
afterEach(() => {
  sessionStorage.clear();
});

const LEADERBOARD_URL = 'http://localhost/api/games-played-leaderboard';

function makeEntry(
  overrides: Partial<{
    player_id: number;
    player_name: string;
    total: number;
    maxi: number;
    maxi_sequential: number;
    yatzy: number;
    yatzy_sequential: number;
  }> = {}
) {
  return {
    player_id: 1,
    player_name: 'Alice',
    total: 3,
    maxi: 2,
    maxi_sequential: 1,
    yatzy: 0,
    yatzy_sequential: 0,
    ...overrides,
  };
}

function givenLeaderboard(sortBy: string, entries: ReturnType<typeof makeEntry>[]) {
  server.use(
    http.get(LEADERBOARD_URL, ({ request }) => {
      const url = new URL(request.url);
      if (url.searchParams.get('sort_by') === sortBy) return HttpResponse.json(entries);
      return HttpResponse.json([]);
    })
  );
}

function givenLeaderboardPending() {
  server.use(http.get(LEADERBOARD_URL, () => new Promise(() => {})));
}

function givenLeaderboardFails() {
  server.use(
    http.get(LEADERBOARD_URL, () => HttpResponse.json({ detail: 'Error' }, { status: 500 }))
  );
}

describe('GamesPlayedScreen', () => {
  beforeEach(() => {
    sessionStorage.setItem('yatzy_player', JSON.stringify(ALICE));
    server.use(http.get(LEADERBOARD_URL, () => HttpResponse.json([])));
  });

  describe('loading state', () => {
    it('shows loading indicator before data arrives', () => {
      givenLeaderboardPending();
      whenRendered();
      thenTextIsVisible('Loading...');
    });
  });

  describe('mode selector', () => {
    it('shows all mode buttons', async () => {
      whenRendered();
      await thenModeButtonsVisible([
        'Total',
        'Maxi Yatzy',
        'Maxi Yatzy Sequential',
        'Yatzy',
        'Yatzy Sequential',
      ]);
    });

    it('defaults to Total', async () => {
      givenLeaderboard('total', [makeEntry({ player_name: 'Alice', total: 5 })]);
      whenRendered();
      await thenPlayerVisible('Alice');
    });

    it('switches to Maxi Standard on click', async () => {
      givenLeaderboard('maxi', [makeEntry({ player_name: 'Bob', maxi: 3 })]);
      whenRendered();
      await whenModeSelected('Maxi Yatzy');
      await thenPlayerVisible('Bob');
    });

    it('switches to Maxi Sequential on click', async () => {
      givenLeaderboard('maxi_sequential', [
        makeEntry({ player_name: 'Carol', maxi_sequential: 2 }),
      ]);
      whenRendered();
      await whenModeSelected('Maxi Yatzy Sequential');
      await thenPlayerVisible('Carol');
    });

    it('switches to Yatzy Standard on click', async () => {
      givenLeaderboard('yatzy', [makeEntry({ player_name: 'Dave', yatzy: 4 })]);
      whenRendered();
      await whenModeSelected('Yatzy');
      await thenPlayerVisible('Dave');
    });

    it('switches to Yatzy Sequential on click', async () => {
      givenLeaderboard('yatzy_sequential', [
        makeEntry({ player_name: 'Eve', yatzy_sequential: 1 }),
      ]);
      whenRendered();
      await whenModeSelected('Yatzy Sequential');
      await thenPlayerVisible('Eve');
    });
  });

  describe('leaderboard display', () => {
    it('shows the heading', async () => {
      whenRendered();
      await thenHeadingVisible('Games Played');
    });

    it('shows player name and game count', async () => {
      givenLeaderboard('total', [makeEntry({ player_name: 'Alice', total: 5 })]);
      whenRendered();
      await thenPlayerVisible('Alice');
      await thenTextEventuallyVisible('5');
    });

    it('numbers rows by rank', async () => {
      givenLeaderboard('total', [
        makeEntry({ player_id: 1, player_name: 'Alice', total: 5 }),
        makeEntry({ player_id: 2, player_name: 'Bob', total: 3 }),
      ]);
      whenRendered();
      await thenPlayerVisible('Alice');
      await thenRowHasTrophy(0, '🥇');
      await thenRowHasTrophy(1, '🥈');
    });

    it('shows "No games played yet" when empty', async () => {
      whenRendered();
      await thenTextEventuallyVisible('No games played yet');
    });
  });

  describe('error handling', () => {
    it('shows error message when fetch fails', async () => {
      givenLeaderboardFails();
      whenRendered();
      await thenTextEventuallyVisible('Failed to load games played');
    });
  });

  function whenRendered() {
    renderWithProviders(<GamesPlayedScreen />);
  }

  function thenTextIsVisible(text: string) {
    expect(screen.getByText(text)).toBeInTheDocument();
  }

  async function thenTextEventuallyVisible(text: string) {
    await screen.findByText(new RegExp(text));
  }

  async function thenModeButtonsVisible(labels: string[]) {
    for (const label of labels) {
      expect(await screen.findByRole('button', { name: label })).toBeInTheDocument();
    }
  }

  async function whenModeSelected(label: string) {
    await userEvent.click(screen.getByRole('button', { name: label }));
  }

  async function thenPlayerVisible(name: string) {
    await screen.findByText(name);
  }

  async function thenHeadingVisible(name: string) {
    await screen.findByRole('heading', { name });
  }

  async function thenRowHasTrophy(index: number, trophy: string) {
    const rows = document.querySelectorAll('tbody tr');
    expect(rows[index]).toHaveTextContent(trophy);
  }
});
