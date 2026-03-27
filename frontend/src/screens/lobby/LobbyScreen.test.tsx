import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { HttpResponse, http } from 'msw';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createMockServer, renderWithProviders } from '@/test/helpers';
import { LobbyScreen } from './LobbyScreen';

const mockNavigate = vi.hoisted(() => vi.fn());
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return { ...actual, useNavigate: () => mockNavigate };
});

const server = createMockServer();
afterEach(() => {
  mockNavigate.mockReset();
  sessionStorage.clear();
});

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
      await thenPlayerNameIsVisible('Bob');
    });

    it('shows creator name on game cards', async () => {
      givenPlayers([PLAYER, BOB]);
      givenGames([{ id: 10, status: 'lobby', creator_id: 2, player_ids: [2], created_at: '' }]);
      whenRendered();
      await thenCreatorNameIsVisible('Bob');
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
      thenStaysOnLobby();
    });

    it('shows error toast when create fails', async () => {
      givenCreateGameFails();
      whenRendered();
      await whenNewGameClicked();
      await thenErrorToastIsVisible('Failed to create game');
    });

    it('creates a sequential game when sequential mode is selected', async () => {
      const { getMode } = givenCreateGameCapturingMode();
      whenRendered();
      await whenModeSelected('maxi_sequential');
      await whenNewGameClicked();
      thenCreatedWithMode(getMode(), 'maxi_sequential');
    });

    it('creates a standard game by default', async () => {
      const { getMode } = givenCreateGameCapturingMode();
      whenRendered();
      await whenNewGameClicked();
      thenCreatedWithMode(getMode(), 'maxi');
    });

    it('shows own game with Start and Delete buttons', async () => {
      givenGames([{ id: 42, status: 'lobby', creator_id: 1, player_ids: [1], created_at: '' }]);
      whenRendered();
      await thenButtonIsVisible('Start game 42');
      await thenButtonIsVisible('Delete game 42');
    });

    it('shows yours badge on own game', async () => {
      givenGames([{ id: 42, status: 'lobby', creator_id: 1, player_ids: [1], created_at: '' }]);
      whenRendered();
      await thenYoursBadgeIsVisible();
    });

    it('shows Maxi Sequential badge on sequential games', async () => {
      givenGames([
        {
          id: 42,
          status: 'lobby',
          creator_id: 1,
          player_ids: [1],
          created_at: '',
          mode: 'maxi_sequential',
        },
      ]);
      whenRendered();
      await thenBadgeVisible('Maxi Yatzy Sequential');
    });

    it('shows Maxi Standard badge on standard games', async () => {
      givenGames([
        {
          id: 42,
          status: 'lobby',
          creator_id: 1,
          player_ids: [1],
          created_at: '',
          mode: 'maxi',
        },
      ]);
      whenRendered();
      await thenBadgeVisible('Maxi Yatzy');
    });

    it('shows Yatzy Standard badge on yatzy games', async () => {
      givenGames([
        { id: 42, status: 'lobby', creator_id: 1, player_ids: [1], created_at: '', mode: 'yatzy' },
      ]);
      whenRendered();
      await thenBadgeVisible('Yatzy');
    });

    it('shows Yatzy Sequential badge on yatzy_sequential games', async () => {
      givenGames([
        {
          id: 42,
          status: 'lobby',
          creator_id: 1,
          player_ids: [1],
          created_at: '',
          mode: 'yatzy_sequential',
        },
      ]);
      whenRendered();
      await thenBadgeVisible('Yatzy Sequential');
    });

    it('creates a yatzy game when yatzy mode is selected', async () => {
      const { getMode } = givenCreateGameCapturingMode();
      whenRendered();
      await whenModeSelected('yatzy');
      await whenNewGameClicked();
      thenCreatedWithMode(getMode(), 'yatzy');
    });

    it('creates a yatzy sequential game when yatzy_sequential mode is selected', async () => {
      const { getMode } = givenCreateGameCapturingMode();
      whenRendered();
      await whenModeSelected('yatzy_sequential');
      await whenNewGameClicked();
      thenCreatedWithMode(getMode(), 'yatzy_sequential');
    });
  });

  describe('joining a game', () => {
    it('shows error toast when join fails', async () => {
      givenGames([{ id: 10, status: 'lobby', creator_id: 2, player_ids: [2], created_at: '' }]);
      givenJoinGameFails(10);
      whenRendered();
      await whenJoinClicked(10);
      await thenErrorToastIsVisible('Failed to join game');
    });

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
      thenStaysOnLobby();
    });

    it('shows Waiting and Leave button after joining', async () => {
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
      await thenWaitingIsVisible();
      await thenButtonIsVisible('Leave game 10');
    });

    it('shows Waiting on a game already joined', async () => {
      givenGames([{ id: 10, status: 'lobby', creator_id: 2, player_ids: [2, 1], created_at: '' }]);
      whenRendered();
      await thenWaitingIsVisible();
    });
  });

  describe('deleting a game (creator)', () => {
    it('clicking delete opens confirmation dialog', async () => {
      givenGames([{ id: 42, status: 'lobby', creator_id: 1, player_ids: [1], created_at: '' }]);
      whenRendered();
      await whenDeleteButtonClicked(42);
      await thenConfirmDialogIsVisible();
    });

    it('cancelling delete dialog keeps game in list', async () => {
      givenGames([{ id: 42, status: 'lobby', creator_id: 1, player_ids: [1], created_at: '' }]);
      whenRendered();
      await whenDeleteButtonClicked(42);
      await whenConfirmDialogCancelled();
      await thenButtonIsVisible('Delete game 42');
    });

    it('shows error toast when delete fails', async () => {
      givenGames([{ id: 42, status: 'lobby', creator_id: 1, player_ids: [1], created_at: '' }]);
      givenDeleteGameFails(42);
      whenRendered();
      await whenDeleteClicked(42);
      await thenErrorToastIsVisible('Failed to delete game');
    });

    it('deletes own game and removes it from the list', async () => {
      givenGames([{ id: 42, status: 'lobby', creator_id: 1, player_ids: [1], created_at: '' }]);
      givenDeleteGameSucceeds(42);
      whenRendered();
      await whenDeleteClicked(42);
      await thenEmptyStateIsVisible();
    });
  });

  describe('starting a game (creator)', () => {
    it('shows error toast when start fails', async () => {
      givenGames([{ id: 42, status: 'lobby', creator_id: 1, player_ids: [1], created_at: '' }]);
      givenStartGameFails(42);
      whenRendered();
      await whenStartClicked(42);
      await thenErrorToastIsVisible('Failed to start game');
    });

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

  describe('leaving a game', () => {
    it('shows error toast when leave fails', async () => {
      givenGames([{ id: 10, status: 'lobby', creator_id: 2, player_ids: [2, 1], created_at: '' }]);
      givenLeaveGameFails(10);
      whenRendered();
      await whenLeaveClicked(10);
      await thenErrorToastIsVisible('Failed to leave game');
    });

    it('leaves a game and stays on lobby', async () => {
      givenGames([{ id: 10, status: 'lobby', creator_id: 2, player_ids: [2, 1], created_at: '' }]);
      givenLeaveGameSucceeds(10);
      whenRendered();
      await whenLeaveClicked(10);
      thenStaysOnLobby();
    });

    it('shows Join button after leaving', async () => {
      givenGames([{ id: 10, status: 'lobby', creator_id: 2, player_ids: [2, 1], created_at: '' }]);
      givenLeaveGameSucceeds(10);
      whenRendered();
      await whenLeaveClicked(10);
      await thenButtonIsVisible('Join game 10');
    });
  });

  type GameData = {
    id: number;
    status: string;
    creator_id: number;
    player_ids: number[];
    created_at: string;
    mode?: string;
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

  function givenCreateGameFails() {
    server.use(http.post(GAMES_URL, () => HttpResponse.json({ detail: 'Error' }, { status: 500 })));
  }

  function givenJoinGameFails(gameId: number) {
    server.use(
      http.post(JOIN_URL(gameId), () => HttpResponse.json({ detail: 'Error' }, { status: 500 }))
    );
  }

  function givenDeleteGameFails(gameId: number) {
    server.use(
      http.delete(DELETE_URL(gameId), () => HttpResponse.json({ detail: 'Error' }, { status: 500 }))
    );
  }

  function givenStartGameFails(gameId: number) {
    server.use(
      http.post(START_URL(gameId), () => HttpResponse.json({ detail: 'Error' }, { status: 500 }))
    );
  }

  function givenLeaveGameFails(gameId: number) {
    server.use(
      http.delete(LEAVE_URL(gameId, PLAYER.id), () =>
        HttpResponse.json({ detail: 'Error' }, { status: 500 })
      )
    );
  }

  function givenJoinGameSucceeds(gameId: number, game: GameData) {
    server.use(
      http.post(JOIN_URL(gameId), () => {
        givenGames([game]);
        return HttpResponse.json(game);
      })
    );
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
        givenGames([
          { id: gameId, status: 'lobby', creator_id: 2, player_ids: [2], created_at: '' },
        ]);
        return HttpResponse.json({
          id: gameId,
          status: 'lobby',
          creator_id: 2,
          player_ids: [2],
          created_at: '',
        });
      })
    );
  }

  function whenRendered() {
    renderWithProviders(<LobbyScreen />);
  }

  async function whenNewGameClicked() {
    await userEvent.click(await screen.findByRole('button', { name: /new game/i }));
  }

  async function whenModeSelected(mode: string) {
    await userEvent.selectOptions(await screen.findByRole('combobox', { name: /mode/i }), mode);
  }

  async function whenJoinClicked(gameId: number) {
    await userEvent.click(await screen.findByRole('button', { name: `Join game ${gameId}` }));
  }

  async function whenStartClicked(gameId: number) {
    await userEvent.click(await screen.findByRole('button', { name: `Start game ${gameId}` }));
  }

  async function whenDeleteButtonClicked(gameId: number) {
    await userEvent.click(await screen.findByRole('button', { name: `Delete game ${gameId}` }));
  }

  async function whenDeleteClicked(gameId: number) {
    await whenDeleteButtonClicked(gameId);
    await userEvent.click(await screen.findByRole('button', { name: /^delete$/i }));
  }

  async function whenConfirmDialogCancelled() {
    await userEvent.click(await screen.findByRole('button', { name: /cancel/i }));
  }

  async function thenConfirmDialogIsVisible() {
    await screen.findByRole('heading', { name: /delete game/i });
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

  async function thenPlayerNameIsVisible(name: string) {
    await screen.findByText(name);
  }

  async function thenCreatorNameIsVisible(name: string) {
    await screen.findByText(new RegExp(`created by ${name}`, 'i'));
  }

  async function thenButtonIsVisible(name: string) {
    await screen.findByRole('button', { name });
  }

  async function thenWaitingIsVisible() {
    await screen.findByText('Waiting...');
  }

  async function thenYoursBadgeIsVisible() {
    await screen.findByText('★ yours');
  }

  function thenStaysOnLobby() {
    expect(mockNavigate).not.toHaveBeenCalled();
  }

  async function thenNavigatedTo(path: string) {
    await vi.waitFor(() => expect(mockNavigate).toHaveBeenCalledWith(path));
  }

  async function thenErrorToastIsVisible(title: string) {
    await screen.findByText(title);
  }

  function givenCreateGameCapturingMode() {
    let capturedMode: unknown;
    server.use(
      http.post(GAMES_URL, async ({ request }) => {
        const body = (await request.json()) as Record<string, unknown>;
        capturedMode = body.mode;
        return HttpResponse.json(
          { id: 42, status: 'lobby', creator_id: 1, player_ids: [1], created_at: '' },
          { status: 201 }
        );
      })
    );
    return { getMode: () => capturedMode };
  }

  function thenCreatedWithMode(mode: unknown, expected: string) {
    expect(mode).toBe(expected);
  }

  async function thenBadgeVisible(label: string) {
    await screen.findByText(label);
  }
});
