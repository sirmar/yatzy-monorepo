import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { HttpResponse, http } from 'msw';
import { setupServer } from 'msw/node';
import { afterAll, afterEach, beforeAll, describe, expect, it, vi } from 'vitest';
import { renderWithProviders } from '@/test/helpers';
import { PlayerScreen } from './PlayerScreen';

const mockUseAuth = vi.hoisted(() => vi.fn());
vi.mock('@/hooks/AuthContext', async () => {
  const actual = await vi.importActual('@/hooks/AuthContext');
  return { ...actual, useAuth: mockUseAuth };
});

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
  mockUseAuth.mockReset();
  sessionStorage.clear();
});
afterAll(() => server.close());

const PLAYERS_URL = 'http://localhost/api/players';
const PLAYERS_ME_URL = 'http://localhost/api/players/me';
const PLAYER_URL = (id: number) => `http://localhost/api/players/${id}`;

const ACCOUNT_ID = '550e8400-e29b-41d4-a716-446655440000';
const OTHER_ACCOUNT_ID = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee';

describe('PlayerScreen', () => {
  describe('existing player check', () => {
    it('auto-navigates to lobby when account already has a player', async () => {
      givenMyPlayer({ id: 1, account_id: ACCOUNT_ID, name: 'Alice', created_at: '' });
      givenPlayers([]);
      whenRendered({ accountId: ACCOUNT_ID });
      await thenNavigatedTo('/lobby');
    });

    it('shows create form when account has no player', async () => {
      givenNoMyPlayer();
      givenPlayers([]);
      whenRendered({ accountId: ACCOUNT_ID });
      await thenCreateFormIsVisible();
    });
  });

  describe('player list', () => {
    it('shows list of existing players', async () => {
      givenNoMyPlayer();
      givenPlayers([
        { id: 1, account_id: OTHER_ACCOUNT_ID, name: 'Alice', created_at: '' },
        { id: 2, account_id: OTHER_ACCOUNT_ID, name: 'Bob', created_at: '' },
      ]);
      whenRendered();
      await thenPlayerIsVisible('Alice');
      await thenPlayerIsVisible('Bob');
    });

    it('shows empty state when no players exist', async () => {
      givenNoMyPlayer();
      givenPlayers([]);
      whenRendered();
      await thenEmptyStateIsVisible();
    });
  });

  describe('creating a player', () => {
    it('creates a new player and navigates to lobby', async () => {
      givenNoMyPlayer();
      givenPlayers([]);
      givenCreatePlayerSucceeds({ id: 3, account_id: ACCOUNT_ID, name: 'Carol', created_at: '' });
      whenRendered({ accountId: ACCOUNT_ID });
      await whenPlayerCreated('Carol');
      thenNavigatedTo('/lobby');
    });

    it('shows error when player creation fails', async () => {
      givenNoMyPlayer();
      givenPlayers([]);
      givenCreatePlayerFails();
      whenRendered({ accountId: ACCOUNT_ID });
      await whenPlayerCreated('Carol');
      await thenErrorIsVisible();
    });
  });

  describe('editing own player', () => {
    it('shows error toast when update fails', async () => {
      givenNoMyPlayer();
      givenPlayers([{ id: 1, account_id: ACCOUNT_ID, name: 'Alice', created_at: '' }]);
      givenUpdatePlayerFails(1);
      whenRendered({ accountId: ACCOUNT_ID });
      await whenEditClicked('Alice');
      await whenNameUpdatedTo('Alicia');
      await thenErrorToastIsVisible('Failed to update player');
    });

    it('keeps editor open when update fails', async () => {
      givenNoMyPlayer();
      givenPlayers([{ id: 1, account_id: ACCOUNT_ID, name: 'Alice', created_at: '' }]);
      givenUpdatePlayerFails(1);
      whenRendered({ accountId: ACCOUNT_ID });
      await whenEditClicked('Alice');
      await whenNameUpdatedTo('Alicia');
      thenEditInputIsVisible();
    });

    it('shows edit input pre-filled with current name', async () => {
      givenNoMyPlayer();
      givenPlayers([{ id: 1, account_id: ACCOUNT_ID, name: 'Alice', created_at: '' }]);
      whenRendered({ accountId: ACCOUNT_ID });
      await whenEditClicked('Alice');
      thenEditInputHasValue('Alice');
    });

    it('saves updated name and shows it in the list', async () => {
      givenNoMyPlayer();
      givenPlayers([{ id: 1, account_id: ACCOUNT_ID, name: 'Alice', created_at: '' }]);
      givenUpdatePlayerSucceeds({ id: 1, account_id: ACCOUNT_ID, name: 'Alicia', created_at: '' });
      whenRendered({ accountId: ACCOUNT_ID });
      await whenEditClicked('Alice');
      await whenNameUpdatedTo('Alicia');
      await thenPlayerIsVisible('Alicia');
    });

    it('cancels edit without saving', async () => {
      givenNoMyPlayer();
      givenPlayers([{ id: 1, account_id: ACCOUNT_ID, name: 'Alice', created_at: '' }]);
      whenRendered({ accountId: ACCOUNT_ID });
      await whenEditClicked('Alice');
      await whenEditCancelled();
      await thenPlayerIsVisible('Alice');
    });
  });

  describe('deleting own player', () => {
    it('shows error toast when delete fails', async () => {
      givenNoMyPlayer();
      givenPlayers([{ id: 1, account_id: ACCOUNT_ID, name: 'Alice', created_at: '' }]);
      givenDeletePlayerFails(1);
      whenRendered({ accountId: ACCOUNT_ID });
      await whenDeleteClicked('Alice');
      await thenErrorToastIsVisible('Failed to delete player');
    });

    it('keeps player in list when delete fails', async () => {
      givenNoMyPlayer();
      givenPlayers([{ id: 1, account_id: ACCOUNT_ID, name: 'Alice', created_at: '' }]);
      givenDeletePlayerFails(1);
      whenRendered({ accountId: ACCOUNT_ID });
      await whenDeleteClicked('Alice');
      await thenPlayerIsVisible('Alice');
    });

    it('removes player from the list', async () => {
      givenNoMyPlayer();
      givenPlayers([{ id: 1, account_id: ACCOUNT_ID, name: 'Alice', created_at: '' }]);
      givenDeletePlayerSucceeds(1);
      whenRendered({ accountId: ACCOUNT_ID });
      await whenDeleteClicked('Alice');
      await thenPlayerIsNotVisible('Alice');
    });
  });

  describe('other players', () => {
    it('does not show edit/delete for players owned by other accounts', async () => {
      givenNoMyPlayer();
      givenPlayers([{ id: 1, account_id: OTHER_ACCOUNT_ID, name: 'Alice', created_at: '' }]);
      whenRendered({ accountId: ACCOUNT_ID });
      await thenPlayerIsVisible('Alice');
      thenEditButtonNotPresent('Alice');
      thenDeleteButtonNotPresent('Alice');
    });
  });

  function givenMyPlayer(player: {
    id: number;
    account_id: string;
    name: string;
    created_at: string;
  }) {
    server.use(http.get(PLAYERS_ME_URL, () => HttpResponse.json(player)));
  }

  function givenNoMyPlayer() {
    server.use(http.get(PLAYERS_ME_URL, () => new HttpResponse(null, { status: 404 })));
  }

  function givenPlayers(
    players: { id: number; account_id: string; name: string; created_at: string }[]
  ) {
    server.use(http.get(PLAYERS_URL, () => HttpResponse.json(players)));
  }

  function givenCreatePlayerSucceeds(player: {
    id: number;
    account_id: string;
    name: string;
    created_at: string;
  }) {
    server.use(http.post(PLAYERS_URL, () => HttpResponse.json(player, { status: 201 })));
  }

  function givenCreatePlayerFails() {
    server.use(
      http.post(PLAYERS_URL, () => HttpResponse.json({ detail: 'Error' }, { status: 422 }))
    );
  }

  function givenUpdatePlayerSucceeds(player: {
    id: number;
    account_id: string;
    name: string;
    created_at: string;
  }) {
    server.use(http.put(PLAYER_URL(player.id), () => HttpResponse.json(player)));
  }

  function givenUpdatePlayerFails(id: number) {
    server.use(
      http.put(PLAYER_URL(id), () => HttpResponse.json({ detail: 'Error' }, { status: 500 }))
    );
  }

  function givenDeletePlayerSucceeds(id: number) {
    server.use(http.delete(PLAYER_URL(id), () => new HttpResponse(null, { status: 204 })));
  }

  function givenDeletePlayerFails(id: number) {
    server.use(
      http.delete(PLAYER_URL(id), () => HttpResponse.json({ detail: 'Error' }, { status: 500 }))
    );
  }

  function whenRendered({ accountId }: { accountId?: string } = {}) {
    mockUseAuth.mockReturnValue({
      user: accountId ? { id: accountId, email: 'test@example.com', created_at: '' } : null,
      accessToken: accountId ? 'test-token' : null,
      isLoading: false,
      login: vi.fn(),
      register: vi.fn(),
      logout: vi.fn(),
    });
    renderWithProviders(<PlayerScreen />);
  }

  async function whenPlayerCreated(name: string) {
    await userEvent.type(await screen.findByRole('textbox'), name);
    await userEvent.click(screen.getByRole('button', { name: /create/i }));
  }

  async function whenEditClicked(playerName: string) {
    await userEvent.click(await screen.findByRole('button', { name: `Edit ${playerName}` }));
  }

  async function whenNameUpdatedTo(newName: string) {
    const input = screen.getByRole('textbox', { name: /edit name/i });
    await userEvent.clear(input);
    await userEvent.type(input, newName);
    await userEvent.click(screen.getByRole('button', { name: /save/i }));
  }

  async function whenEditCancelled() {
    await userEvent.click(screen.getByRole('button', { name: /cancel/i }));
  }

  async function whenDeleteClicked(playerName: string) {
    await userEvent.click(await screen.findByRole('button', { name: `Delete ${playerName}` }));
  }

  async function thenPlayerIsVisible(name: string) {
    await screen.findByText(name);
  }

  async function thenPlayerIsNotVisible(_name: string) {
    await screen.findByText(/no players yet/i);
  }

  async function thenEmptyStateIsVisible() {
    await screen.findByText(/no players yet/i);
  }

  async function thenCreateFormIsVisible() {
    await screen.findByPlaceholderText(/enter your name/i);
  }

  async function thenErrorIsVisible() {
    await screen.findByText(/failed to create/i);
  }

  function thenEditInputHasValue(value: string) {
    expect(screen.getByRole('textbox', { name: /edit name/i })).toHaveValue(value);
  }

  async function thenNavigatedTo(path: string) {
    await waitFor(() => expect(mockNavigate).toHaveBeenCalledWith(path));
  }

  async function thenErrorToastIsVisible(title: string) {
    await screen.findByText(title);
  }

  function thenEditInputIsVisible() {
    expect(screen.getByRole('textbox', { name: /edit name/i })).toBeInTheDocument();
  }

  function thenEditButtonNotPresent(playerName: string) {
    expect(screen.queryByRole('button', { name: `Edit ${playerName}` })).not.toBeInTheDocument();
  }

  function thenDeleteButtonNotPresent(playerName: string) {
    expect(screen.queryByRole('button', { name: `Delete ${playerName}` })).not.toBeInTheDocument();
  }
});
