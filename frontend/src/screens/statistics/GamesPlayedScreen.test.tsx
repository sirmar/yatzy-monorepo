import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
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

describe('GamesPlayedScreen', () => {
  beforeEach(() => {
    sessionStorage.setItem('yatzy_player', JSON.stringify(ALICE));
    server.use(http.get(LEADERBOARD_URL, () => HttpResponse.json([])));
  });

  describe('mode selector', () => {
    it('shows all mode buttons', async () => {
      whenRendered();
      await thenModeButtonsVisible(['Total', 'Maxi Yatzy', 'Maxi Seq.', 'Yatzy', 'Yatzy Seq.']);
    });

    it('defaults to Total', async () => {
      givenLeaderboard('total', [makeEntry({ player_name: 'Alice', total: 5 })]);
      whenRendered();
      await thenPlayerVisible('Alice');
    });

    it('switches to Maxi Yatzy on click', async () => {
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
      await whenModeSelected('Maxi Seq.');
      await thenPlayerVisible('Carol');
    });

    it('switches to Yatzy on click', async () => {
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
      await whenModeSelected('Yatzy Seq.');
      await thenPlayerVisible('Eve');
    });
  });

  describe('leaderboard display', () => {
    it('shows the heading text', async () => {
      whenRendered();
      await thenTextEventuallyVisible('Most Games Played');
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
      await thenRowHasRank(0, '1');
      await thenRowHasRank(1, '2');
    });

    it('shows "No games played yet" when empty', async () => {
      whenRendered();
      await thenTextEventuallyVisible('No games played yet');
    });
  });

  function givenLeaderboard(sortBy: string, entries: ReturnType<typeof makeEntry>[]) {
    server.use(
      http.get(LEADERBOARD_URL, ({ request }) => {
        const url = new URL(request.url);
        if (url.searchParams.get('sort_by') === sortBy) return HttpResponse.json(entries);
        return HttpResponse.json([]);
      })
    );
  }

  function whenRendered() {
    renderWithProviders(<GamesPlayedScreen />);
  }

  async function whenModeSelected(label: string) {
    await userEvent.click(await screen.findByRole('button', { name: label }));
  }

  async function thenTextEventuallyVisible(text: string) {
    await screen.findByText(new RegExp(text));
  }

  async function thenModeButtonsVisible(labels: string[]) {
    for (const label of labels) {
      expect(await screen.findByRole('button', { name: label })).toBeInTheDocument();
    }
  }

  async function thenPlayerVisible(name: string) {
    await screen.findByText(name);
  }

  async function thenRowHasRank(index: number, rank: string) {
    const rows = document.querySelectorAll('tbody tr');
    expect(rows[index]).toHaveTextContent(rank);
  }
});
