import { renderWithProviders } from '@/test/helpers';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { afterAll, afterEach, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import { LobbyScreen } from './LobbyScreen';

const mockNavigate = vi.hoisted(() => vi.fn());
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return { ...actual, useNavigate: () => mockNavigate };
});

const server = setupServer();
beforeAll(() => server.listen());
afterEach(() => {
  server.resetHandlers();
  mockNavigate.mockReset();
  sessionStorage.clear();
});
afterAll(() => server.close());

const GAMES_URL = 'http://localhost/api/games';
const PLAYERS_URL = 'http://localhost/api/players';
const JOIN_URL = (id: number) => `http://localhost/api/games/${id}/join`;
const START_URL = (id: number) => `http://localhost/api/games/${id}/start`;
const DELETE_URL = (id: number) => `http://localhost/api/games/${id}`;
const LEAVE_URL = (id: number, playerId: number) =>
  `http://localhost/api/games/${id}/players/${playerId}`;

const PLAYER = { id: 1, name: 'Alice', created_at: '' };
const BOB = { id: 2, name: 'Bob', created_at: '' };

describe('LobbyScreen', () => {
  beforeEach(() => {
    sessionStorage.setItem('yatzy_player', JSON.stringify(PLAYER));
    givenPlayers([PLAYER]);
    givenGames([]);
  });

  describe('game list', () => {
    it('shows list of open games', async () => {
      givenGames([
        { id: 10, status: 'lobby', creator_id: 2, player_ids: [2], created_at: '' },
        { id: 11, status: 'lobby', creator_id: 3, player_ids: [3], created_at: '' },
      ]);
      whenRendered();
      await thenGameIsVisible(10);
      await thenGameIsVisible(11);
    });

    it('shows empty state when no open games', async () => {
      givenGames([]);
      whenRendered();
      await thenEmptyStateIsVisible();
    });

    it('does not show active or finished games', async () => {
      givenGames([
        { id: 10, status: 'active', creator_id: 2, player_ids: [2], created_at: '' },
        { id: 11, status: 'finished', creator_id: 2, player_ids: [2], created_at: '' },
      ]);
      whenRendered();
      await thenEmptyStateIsVisible();
    });

    it('shows player names on game cards', async () => {
      givenPlayers([PLAYER, BOB]);
      givenGames([{ id: 10, status: 'lobby', creator_id: 2, player_ids: [2], created_at: '' }]);
      whenRendered();
      await screen.findByText('Bob');
    });

    it('shows creator name on game cards', async () => {
      givenPlayers([PLAYER, BOB]);
      givenGames([{ id: 10, status: 'lobby', creator_id: 2, player_ids: [2], created_at: '' }]);
      whenRendered();
      await screen.findByText(/created by Bob/i);
    });
  });

  describe('creating a game', () => {
    it('creates a game and stays on lobby', async () => {
      givenCreateGameSucceeds({
        id: 42,
        status: 'lobby',
        creator_id: 1,
        player_ids: [1],
        created_at: '',
      });
      whenRendered();
      await whenNewGameClicked();
      expect(mockNavigate).not.toHaveBeenCalled();
    });

    it('shows own game with Start button', async () => {
      givenGames([{ id: 42, status: 'lobby', creator_id: 1, player_ids: [1], created_at: '' }]);
      whenRendered();
      await screen.findByRole('button', { name: 'Start game 42' });
    });
  });

  describe('joining a game', () => {
    it('joins a game and stays on lobby', async () => {
      givenGames([{ id: 10, status: 'lobby', creator_id: 2, player_ids: [2], created_at: '' }]);
      givenJoinGameSucceeds(10, {
        id: 10,
        status: 'lobby',
        creator_id: 2,
        player_ids: [2, 1],
        created_at: '',
      });
      whenRendered();
      await whenJoinClicked(10);
      expect(mockNavigate).not.toHaveBeenCalled();
    });

    it('shows Waiting on a game already joined', async () => {
      givenGames([{ id: 10, status: 'lobby', creator_id: 2, player_ids: [2, 1], created_at: '' }]);
      whenRendered();
      await screen.findByText('Waiting...');
    });
  });

  describe('deleting a game (creator)', () => {
    it('deletes own game and removes it from the list', async () => {
      givenGames([{ id: 42, status: 'lobby', creator_id: 1, player_ids: [1], created_at: '' }]);
      givenDeleteGameSucceeds(42);
      whenRendered();
      await whenDeleteClicked(42);
      await thenEmptyStateIsVisible();
    });
  });

  describe('starting a game (creator)', () => {
    it('starts the game and navigates to it', async () => {
      givenGames([{ id: 42, status: 'lobby', creator_id: 1, player_ids: [1], created_at: '' }]);
      givenStartGameSucceeds(42, {
        id: 42,
        status: 'active',
        creator_id: 1,
        player_ids: [1],
        created_at: '',
      });
      whenRendered();
      await whenStartClicked(42);
      await thenNavigatedTo('/games/42');
    });
  });

  describe('changing player', () => {
    it('shows the current player name', async () => {
      whenRendered();
      await screen.findByText('Alice');
    });

    it('navigates to player screen when Change is clicked', async () => {
      whenRendered();
      await userEvent.click(await screen.findByRole('button', { name: /change player/i }));
      expect(mockNavigate).toHaveBeenCalledWith('/');
    });
  });

  describe('leaving a game', () => {
    it('leaves a game and stays on lobby', async () => {
      givenGames([{ id: 10, status: 'lobby', creator_id: 2, player_ids: [2, 1], created_at: '' }]);
      givenLeaveGameSucceeds(10);
      whenRendered();
      await whenLeaveClicked(10);
      expect(mockNavigate).not.toHaveBeenCalled();
    });
  });

  describe('auto-redirect', () => {
    it('redirects to active game if player is already in one', async () => {
      givenGames([{ id: 99, status: 'active', creator_id: 1, player_ids: [1, 2], created_at: '' }]);
      whenRendered();
      await thenNavigatedTo('/games/99');
    });
  });

  type GameData = {
    id: number;
    status: string;
    creator_id: number;
    player_ids: number[];
    created_at: string;
  };

  type PlayerData = { id: number; name: string; created_at: string };

  function givenPlayers(players: PlayerData[]) {
    server.use(http.get(PLAYERS_URL, () => HttpResponse.json(players)));
  }

  function givenGames(games: GameData[]) {
    server.use(
      http.get(GAMES_URL, ({ request }) => {
        const status = new URL(request.url).searchParams.get('status');
        return HttpResponse.json(games.filter((g) => !status || g.status === status));
      })
    );
  }

  function givenCreateGameSucceeds(game: GameData) {
    server.use(http.post(GAMES_URL, () => HttpResponse.json(game, { status: 201 })));
  }

  function givenJoinGameSucceeds(gameId: number, game: GameData) {
    server.use(http.post(JOIN_URL(gameId), () => HttpResponse.json(game)));
  }

  function givenStartGameSucceeds(gameId: number, game: GameData) {
    server.use(http.post(START_URL(gameId), () => HttpResponse.json(game)));
  }

  function givenDeleteGameSucceeds(gameId: number) {
    server.use(
      http.delete(DELETE_URL(gameId), () => {
        givenGames([]);
        return new HttpResponse(null, { status: 204 });
      })
    );
  }

  function givenLeaveGameSucceeds(gameId: number) {
    server.use(
      http.delete(LEAVE_URL(gameId, PLAYER.id), () => {
        givenGames([{ id: gameId, status: 'lobby', creator_id: 2, player_ids: [2], created_at: '' }]);
        return HttpResponse.json({ id: gameId, status: 'lobby', creator_id: 2, player_ids: [2], created_at: '' });
      })
    );
  }

  function whenRendered() {
    renderWithProviders(<LobbyScreen />);
  }

  async function whenNewGameClicked() {
    await userEvent.click(await screen.findByRole('button', { name: /new game/i }));
  }

  async function whenJoinClicked(gameId: number) {
    await userEvent.click(await screen.findByRole('button', { name: `Join game ${gameId}` }));
  }

  async function whenStartClicked(gameId: number) {
    await userEvent.click(await screen.findByRole('button', { name: `Start game ${gameId}` }));
  }

  async function whenDeleteClicked(gameId: number) {
    await userEvent.click(await screen.findByRole('button', { name: `Delete game ${gameId}` }));
  }

  async function whenLeaveClicked(gameId: number) {
    await userEvent.click(await screen.findByRole('button', { name: `Leave game ${gameId}` }));
  }

  async function thenGameIsVisible(gameId: number) {
    await screen.findByText(`Game #${gameId}`);
  }

  async function thenEmptyStateIsVisible() {
    await screen.findByText(/no open games/i);
  }

  async function thenNavigatedTo(path: string) {
    await vi.waitFor(() => expect(mockNavigate).toHaveBeenCalledWith(path));
  }
});
