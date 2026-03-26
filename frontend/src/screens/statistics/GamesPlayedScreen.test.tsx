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
    standard: number;
    sequential: number;
  }> = {}
) {
  return {
    player_id: 1,
    player_name: 'Alice',
    total: 3,
    standard: 2,
    sequential: 1,
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
    it('shows Total, Standard and Sequential buttons', async () => {
      whenRendered();
      await screen.findByRole('button', { name: 'Total' });
      await screen.findByRole('button', { name: 'Standard' });
      await screen.findByRole('button', { name: 'Sequential' });
    });

    it('defaults to Total', async () => {
      givenLeaderboard('total', [makeEntry({ player_name: 'Alice', total: 5 })]);
      whenRendered();
      await screen.findByText('Alice');
    });

    it('switches to Standard on click', async () => {
      givenLeaderboard('standard', [makeEntry({ player_name: 'Bob', standard: 3 })]);
      whenRendered();
      await userEvent.click(screen.getByRole('button', { name: 'Standard' }));
      await screen.findByText('Bob');
    });

    it('switches to Sequential on click', async () => {
      givenLeaderboard('sequential', [makeEntry({ player_name: 'Carol', sequential: 2 })]);
      whenRendered();
      await userEvent.click(screen.getByRole('button', { name: 'Sequential' }));
      await screen.findByText('Carol');
    });
  });

  describe('leaderboard display', () => {
    it('shows the heading', async () => {
      whenRendered();
      await screen.findByRole('heading', { name: 'Games Played' });
    });

    it('shows player name and game count', async () => {
      givenLeaderboard('total', [makeEntry({ player_name: 'Alice', total: 5 })]);
      whenRendered();
      await screen.findByText('Alice');
      expect(screen.getByText('5')).toBeInTheDocument();
    });

    it('numbers rows by rank', async () => {
      givenLeaderboard('total', [
        makeEntry({ player_id: 1, player_name: 'Alice', total: 5 }),
        makeEntry({ player_id: 2, player_name: 'Bob', total: 3 }),
      ]);
      whenRendered();
      await screen.findByText('Alice');
      const rows = document.querySelectorAll('tbody tr');
      expect(rows[0]).toHaveTextContent('🥇');
      expect(rows[1]).toHaveTextContent('🥈');
    });

    it('shows "No games played yet" when empty', async () => {
      whenRendered();
      await screen.findByText('No games played yet');
    });
  });

  describe('error handling', () => {
    it('shows error message when fetch fails', async () => {
      givenLeaderboardFails();
      whenRendered();
      await screen.findByText('Failed to load games played');
    });
  });

  function whenRendered() {
    renderWithProviders(<GamesPlayedScreen />);
  }

  function thenTextIsVisible(text: string) {
    expect(screen.getByText(text)).toBeInTheDocument();
  }
});
