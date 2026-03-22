import { renderWithProviders } from '@/test/helpers';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { afterAll, afterEach, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import { EndScreen } from './EndScreen';

const mockNavigate = vi.hoisted(() => vi.fn());
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return { ...actual, useNavigate: () => mockNavigate, useParams: () => ({ gameId: '42' }) };
});

const server = setupServer();
beforeAll(() => server.listen());
afterEach(() => {
  server.resetHandlers();
  mockNavigate.mockReset();
  sessionStorage.clear();
});
afterAll(() => server.close());

const STATE_URL = 'http://localhost/api/games/42/state';
const PLAYERS_URL = 'http://localhost/api/players';

const ALICE = { id: 1, name: 'Alice', created_at: '' };
const BOB = { id: 2, name: 'Bob', created_at: '' };

describe('EndScreen', () => {
  beforeEach(() => {
    sessionStorage.setItem('yatzy_player', JSON.stringify(ALICE));
  });

  describe('results display', () => {
    it('shows player names and their scores', async () => {
      givenPlayers([ALICE, BOB]);
      givenFinishedGame({
        winnerIds: [1],
        scores: [
          { player_id: 1, total: 287 },
          { player_id: 2, total: 241 },
        ],
      });
      whenRendered();
      await thenTextIsVisible('Alice');
      await thenTextIsVisible('287');
      await thenTextIsVisible('Bob');
      await thenTextIsVisible('241');
    });

    it('highlights the winner', async () => {
      givenPlayers([ALICE, BOB]);
      givenFinishedGame({
        winnerIds: [1],
        scores: [
          { player_id: 1, total: 287 },
          { player_id: 2, total: 241 },
        ],
      });
      whenRendered();
      const winnerRow = await screen.findByTestId('winner-row-1');
      expect(winnerRow).toHaveClass('text-yellow-400');
    });

    it('shows the winner announcement text', async () => {
      givenPlayers([ALICE, BOB]);
      givenFinishedGame({
        winnerIds: [1],
        scores: [
          { player_id: 1, total: 287 },
          { player_id: 2, total: 241 },
        ],
      });
      whenRendered();
      await thenTextIsVisible('Alice wins!');
    });

    it('handles a tie (two winners)', async () => {
      givenPlayers([ALICE, BOB]);
      givenFinishedGame({
        winnerIds: [1, 2],
        scores: [
          { player_id: 1, total: 260 },
          { player_id: 2, total: 260 },
        ],
      });
      whenRendered();
      await thenTextIsVisible('Alice & Bob win!');
    });
  });

  describe('navigation', () => {
    it('clicking "Back to Lobby" navigates to /lobby', async () => {
      givenPlayers([ALICE]);
      givenFinishedGame({ winnerIds: [1], scores: [{ player_id: 1, total: 287 }] });
      whenRendered();
      await whenBackToLobbyClicked();
      expect(mockNavigate).toHaveBeenCalledWith('/lobby');
    });

    it('redirects to /games/42 if game is not finished', async () => {
      givenPlayers([ALICE]);
      givenActiveGame();
      whenRendered();
      await vi.waitFor(() => expect(mockNavigate).toHaveBeenCalledWith('/games/42'));
    });
  });

  describe('error handling', () => {
    it('shows error toast when state fetch fails', async () => {
      givenPlayers([ALICE]);
      givenStateFetchFails();
      whenRendered();
      await thenTextIsVisible('Failed to load results');
    });
  });

  function givenPlayers(players: { id: number; name: string; created_at: string }[]) {
    server.use(http.get(PLAYERS_URL, () => HttpResponse.json(players)));
  }

  function givenFinishedGame({
    winnerIds,
    scores,
  }: {
    winnerIds: number[];
    scores: { player_id: number; total: number }[];
  }) {
    server.use(
      http.get(STATE_URL, () =>
        HttpResponse.json({
          status: 'finished',
          winner_ids: winnerIds,
          final_scores: scores,
        })
      )
    );
  }

  function givenActiveGame() {
    server.use(
      http.get(STATE_URL, () =>
        HttpResponse.json({
          status: 'active',
          current_player_id: 1,
          dice: [],
          rolls_remaining: 3,
        })
      )
    );
  }

  function givenStateFetchFails() {
    server.use(http.get(STATE_URL, () => HttpResponse.json({ detail: 'Error' }, { status: 500 })));
  }

  function whenRendered() {
    renderWithProviders(<EndScreen />);
  }

  async function whenBackToLobbyClicked() {
    await userEvent.click(await screen.findByRole('button', { name: /back to lobby/i }));
  }

  async function thenTextIsVisible(text: string) {
    await screen.findAllByText(new RegExp(text));
  }
});
