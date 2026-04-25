import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { HttpResponse, http } from 'msw';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { createMockServer, renderWithProviders } from '@/test/helpers';
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

const server = createMockServer();
afterEach(() => {
  mockNavigate.mockReset();
  mockUseAuth.mockReset();
  sessionStorage.clear();
});

const PLAYERS_URL = 'http://localhost/api/players';
const PLAYERS_ME_URL = 'http://localhost/api/players/me';

const ACCOUNT_ID = '550e8400-e29b-41d4-a716-446655440000';

describe('PlayerScreen', () => {
  describe('existing player check', () => {
    it('auto-navigates to lobby when account already has a player', async () => {
      givenMyPlayer({ id: 1, account_id: ACCOUNT_ID, name: 'Alice', created_at: '' });
      whenRendered({ accountId: ACCOUNT_ID });
      await thenNavigatedTo('/lobby');
    });

    it('shows create form when account has no player', async () => {
      givenNoMyPlayer();
      whenRendered({ accountId: ACCOUNT_ID });
      await thenCreateFormIsVisible();
    });
  });

  describe('creating a player', () => {
    it('creates a new player and navigates to lobby', async () => {
      givenNoMyPlayer();
      givenCreatePlayerSucceeds({ id: 3, account_id: ACCOUNT_ID, name: 'Carol', created_at: '' });
      whenRendered({ accountId: ACCOUNT_ID });
      await whenPlayerNameEntered('Carol');
      await whenContinueClicked();
      await thenNavigatedTo('/lobby');
    });

    it('shows error when player creation fails', async () => {
      givenNoMyPlayer();
      givenCreatePlayerFails();
      whenRendered({ accountId: ACCOUNT_ID });
      await whenPlayerNameEntered('Carol');
      await whenContinueClicked();
      await thenErrorIsVisible();
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

  function whenRendered({ accountId }: { accountId?: string } = {}) {
    mockUseAuth.mockReturnValue({
      user: accountId
        ? { id: accountId, email: 'test@example.com', email_verified: true, created_at: '' }
        : null,
      accessToken: accountId ? 'test-token' : null,
      isLoading: false,
      login: vi.fn(),
      register: vi.fn(),
      logout: vi.fn(),
    });
    renderWithProviders(<PlayerScreen />);
  }

  async function whenPlayerNameEntered(name: string) {
    await userEvent.type(await screen.findByRole('textbox'), name);
  }

  async function whenContinueClicked() {
    await userEvent.click(screen.getByRole('button', { name: /continue/i }));
  }

  async function thenCreateFormIsVisible() {
    await screen.findByLabelText(/display name/i);
  }

  async function thenErrorIsVisible() {
    await screen.findByText(/something went wrong/i);
  }

  async function thenNavigatedTo(path: string) {
    await waitFor(() => expect(mockNavigate).toHaveBeenCalledWith(path));
  }
});
