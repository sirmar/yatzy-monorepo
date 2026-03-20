import { renderWithProviders } from '@/test/helpers';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { afterAll, afterEach, beforeAll, describe, expect, it, vi } from 'vitest';
import { PlayerScreen } from './PlayerScreen';

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

const PLAYERS_URL = 'http://localhost/api/players';
const PLAYER_URL = (id: number) => `http://localhost/api/players/${id}`;

describe('PlayerScreen', () => {
  describe('player list', () => {
    it('shows list of existing players', async () => {
      givenPlayers([
        { id: 1, name: 'Alice', created_at: '' },
        { id: 2, name: 'Bob', created_at: '' },
      ]);
      whenRendered();
      await thenPlayerIsVisible('Alice');
      await thenPlayerIsVisible('Bob');
    });

    it('shows empty state when no players exist', async () => {
      givenPlayers([]);
      whenRendered();
      await thenEmptyStateIsVisible();
    });
  });

  describe('selecting a player', () => {
    it('allows selecting an existing player and navigates to lobby', async () => {
      givenPlayers([{ id: 1, name: 'Alice', created_at: '' }]);
      whenRendered();
      await whenPlayerSelected('Alice');
      thenNavigatedTo('/lobby');
    });
  });

  describe('creating a player', () => {
    it('creates a new player and navigates to lobby', async () => {
      givenPlayers([]);
      givenCreatePlayerSucceeds({ id: 3, name: 'Carol', created_at: '' });
      whenRendered();
      await whenPlayerCreated('Carol');
      thenNavigatedTo('/lobby');
    });

    it('shows error when player creation fails', async () => {
      givenPlayers([]);
      givenCreatePlayerFails();
      whenRendered();
      await whenPlayerCreated('Carol');
      await thenErrorIsVisible();
    });
  });

  describe('editing a player', () => {
    it('shows error toast when update fails', async () => {
      givenPlayers([{ id: 1, name: 'Alice', created_at: '' }]);
      givenUpdatePlayerFails(1);
      whenRendered();
      await whenEditClicked('Alice');
      await whenNameUpdatedTo('Alicia');
      await thenErrorToastIsVisible('Failed to update player');
    });

    it('keeps editor open when update fails', async () => {
      givenPlayers([{ id: 1, name: 'Alice', created_at: '' }]);
      givenUpdatePlayerFails(1);
      whenRendered();
      await whenEditClicked('Alice');
      await whenNameUpdatedTo('Alicia');
      thenEditInputIsVisible();
    });

    it('shows edit input pre-filled with current name', async () => {
      givenPlayers([{ id: 1, name: 'Alice', created_at: '' }]);
      whenRendered();
      await whenEditClicked('Alice');
      thenEditInputHasValue('Alice');
    });

    it('saves updated name and shows it in the list', async () => {
      givenPlayers([{ id: 1, name: 'Alice', created_at: '' }]);
      givenUpdatePlayerSucceeds({ id: 1, name: 'Alicia', created_at: '' });
      whenRendered();
      await whenEditClicked('Alice');
      await whenNameUpdatedTo('Alicia');
      await thenPlayerIsVisible('Alicia');
    });

    it('cancels edit without saving', async () => {
      givenPlayers([{ id: 1, name: 'Alice', created_at: '' }]);
      whenRendered();
      await whenEditClicked('Alice');
      await whenEditCancelled();
      await thenPlayerIsVisible('Alice');
    });
  });

  describe('deleting a player', () => {
    it('shows error toast when delete fails', async () => {
      givenPlayers([{ id: 1, name: 'Alice', created_at: '' }]);
      givenDeletePlayerFails(1);
      whenRendered();
      await whenDeleteClicked('Alice');
      await thenErrorToastIsVisible('Failed to delete player');
    });

    it('keeps player in list when delete fails', async () => {
      givenPlayers([{ id: 1, name: 'Alice', created_at: '' }]);
      givenDeletePlayerFails(1);
      whenRendered();
      await whenDeleteClicked('Alice');
      await thenPlayerIsVisible('Alice');
    });

    it('removes player from the list', async () => {
      givenPlayers([{ id: 1, name: 'Alice', created_at: '' }]);
      givenDeletePlayerSucceeds(1);
      whenRendered();
      await whenDeleteClicked('Alice');
      await thenPlayerIsNotVisible('Alice');
    });
  });

  function givenPlayers(players: { id: number; name: string; created_at: string }[]) {
    server.use(http.get(PLAYERS_URL, () => HttpResponse.json(players)));
  }

  function givenCreatePlayerSucceeds(player: { id: number; name: string; created_at: string }) {
    server.use(http.post(PLAYERS_URL, () => HttpResponse.json(player, { status: 201 })));
  }

  function givenCreatePlayerFails() {
    server.use(
      http.post(PLAYERS_URL, () => HttpResponse.json({ detail: 'Error' }, { status: 422 }))
    );
  }

  function givenUpdatePlayerSucceeds(player: { id: number; name: string; created_at: string }) {
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

  function whenRendered() {
    renderWithProviders(<PlayerScreen />);
  }

  async function whenPlayerSelected(name: string) {
    await userEvent.click(await screen.findByRole('button', { name }));
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
    await screen.findByRole('button', { name });
  }

  async function thenPlayerIsNotVisible(_name: string) {
    await screen.findByText(/no players yet/i);
  }

  async function thenEmptyStateIsVisible() {
    await screen.findByText(/no players yet/i);
  }

  async function thenErrorIsVisible() {
    await screen.findByText(/failed to create/i);
  }

  function thenEditInputHasValue(value: string) {
    expect(screen.getByRole('textbox', { name: /edit name/i })).toHaveValue(value);
  }

  function thenNavigatedTo(path: string) {
    expect(mockNavigate).toHaveBeenCalledWith(path);
  }

  async function thenErrorToastIsVisible(title: string) {
    await screen.findByText(title);
  }

  function thenEditInputIsVisible() {
    expect(screen.getByRole('textbox', { name: /edit name/i })).toBeInTheDocument();
  }
});
