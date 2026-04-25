import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { HttpResponse, http } from 'msw';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { ALICE, createMockServer, renderWithProviders } from '@/test/helpers';
import { HistoryScreen } from './HistoryScreen';

const HISTORY_URL = `http://localhost/api/players/${ALICE.id}/game-history`;

const server = createMockServer();

describe('HistoryScreen', () => {
  beforeEach(() => {
    sessionStorage.setItem('yatzy_player', JSON.stringify(ALICE));
    givenHistory([]);
  });

  afterEach(() => {
    sessionStorage.clear();
  });

  it('shows "No games found" when history is empty', async () => {
    whenRendered();
    await screen.findByText(/no games found/i);
  });

  it('shows game rows fetched from the API', async () => {
    givenHistory([makeGame({ game_id: 1, mode: 'maxi', rank: 1, score: 258 })]);
    whenRendered();
    await screen.findByText('258');
    expect(screen.getByText('Maxi Yatzy')).toBeInTheDocument();
  });

  it('shows total game count', async () => {
    givenHistory([
      makeGame({ game_id: 1, mode: 'maxi', rank: 1, score: 200 }),
      makeGame({ game_id: 2, mode: 'yatzy', rank: 2, score: 150 }),
    ]);
    whenRendered();
    await screen.findByText('2 games');
  });

  it('shows "1 game" for a single result', async () => {
    givenHistory([makeGame({ game_id: 1, mode: 'maxi', rank: 1, score: 200 })]);
    whenRendered();
    await screen.findByText('1 game');
  });

  it('shows rank as ordinal', async () => {
    givenHistory([makeGame({ game_id: 1, mode: 'maxi', rank: 2, score: 200 })]);
    whenRendered();
    await screen.findByText('2nd');
  });

  describe('filtering', () => {
    beforeEach(async () => {
      givenHistory([
        makeGame({ game_id: 1, mode: 'maxi', rank: 1, score: 200 }),
        makeGame({ game_id: 2, mode: 'yatzy', rank: 2, score: 150 }),
        makeGame({ game_id: 3, mode: 'maxi_sequential', rank: 1, score: 180 }),
      ]);
      whenRendered();
      await screen.findByText('3 games');
    });

    it('filters to maxi variant only', async () => {
      await whenFilterSelected('Maxi');
      expect(screen.getByText('2 games')).toBeInTheDocument();
    });

    it('filters to yatzy variant only', async () => {
      await whenFilterSelected('Yatzy');
      expect(screen.getByText('1 game')).toBeInTheDocument();
    });

    it('filters to wins only', async () => {
      await whenFilterSelected('Wins');
      expect(screen.getByText('2 games')).toBeInTheDocument();
    });

    it('filters to losses only', async () => {
      await whenFilterSelected('Losses');
      expect(screen.getByText('1 game')).toBeInTheDocument();
    });

    it('filters to sequential type only', async () => {
      await whenFilterSelected('Sequential');
      expect(screen.getByText('1 game')).toBeInTheDocument();
    });
  });

  function whenRendered() {
    renderWithProviders(<HistoryScreen />);
  }

  async function whenFilterSelected(label: string) {
    await userEvent.click(screen.getByRole('button', { name: label }));
  }

  function givenHistory(games: ReturnType<typeof makeGame>[]) {
    server.use(http.get(HISTORY_URL, () => HttpResponse.json(games)));
  }

  function makeGame({
    game_id,
    mode,
    rank,
    score,
  }: {
    game_id: number;
    mode: string;
    rank: number;
    score: number;
  }) {
    return {
      game_id,
      mode,
      rank,
      score,
      finished_at: '2026-01-01T12:00:00Z',
      players: [{ player_id: ALICE.id, player_name: ALICE.name }],
    };
  }
});
