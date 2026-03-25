import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { HttpResponse, http } from 'msw';
import { setupServer } from 'msw/node';
import { afterAll, afterEach, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import { renderWithProviders } from '@/test/helpers';
import { EditPlayerScreen } from './EditPlayerScreen';

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

const PLAYER_URL = (id: number) => `http://localhost/api/players/${id}`;
const PLAYER_STATS_URL = (id: number) => `http://localhost/api/players/${id}/stats`;

const ACCOUNT_ID = '550e8400-e29b-41d4-a716-446655440000';

describe('ProfileScreen', () => {
  beforeEach(() => {
    givenPlayerStats({
      games_played: 5,
      high_score: 310,
      average_score: 270.5,
      bonus_count: 3,
      maxi_yatzy_count: 1,
    });
  });

  it('shows edit form pre-filled with current name', async () => {
    givenMyPlayer({ id: 1, account_id: ACCOUNT_ID, name: 'Alice', created_at: '' });
    whenRendered();
    await thenInputHasValue('Alice');
  });

  it('saves updated name and navigates to lobby', async () => {
    givenMyPlayer({ id: 1, account_id: ACCOUNT_ID, name: 'Alice', created_at: '' });
    givenUpdatePlayerSucceeds({ id: 1, account_id: ACCOUNT_ID, name: 'Alicia', created_at: '' });
    whenRendered();
    await whenNameChangedTo('Alicia');
    await whenSaveClicked();
    await thenNavigatedTo('/lobby');
  });

  it('shows error toast when update fails', async () => {
    givenMyPlayer({ id: 1, account_id: ACCOUNT_ID, name: 'Alice', created_at: '' });
    givenUpdatePlayerFails(1);
    whenRendered();
    await whenNameChangedTo('Alicia');
    await whenSaveClicked();
    await thenErrorToastIsVisible('Failed to update player');
  });

  it('navigates to lobby on cancel', async () => {
    givenMyPlayer({ id: 1, account_id: ACCOUNT_ID, name: 'Alice', created_at: '' });
    whenRendered();
    await whenCancelClicked();
    await thenNavigatedTo('/lobby');
  });

  describe('stats table', () => {
    it('shows games played, high score, average score, bonuses and maxi yatzy', async () => {
      givenMyPlayer({ id: 1, account_id: ACCOUNT_ID, name: 'Alice', created_at: '' });
      givenPlayerStats({
        games_played: 12,
        high_score: 350,
        average_score: 290.4,
        bonus_count: 7,
        maxi_yatzy_count: 2,
      });
      whenRendered();
      await thenStatVisible('Games played', '12');
      await thenStatVisible('High score', '350');
      await thenStatVisible('Average score', '290');
      await thenStatVisible('Bonuses', '7');
      await thenStatVisible('Maxi Yatzy', '2');
    });

    it('shows — for high score and average score when null', async () => {
      givenMyPlayer({ id: 1, account_id: ACCOUNT_ID, name: 'Alice', created_at: '' });
      givenPlayerStats({
        games_played: 0,
        high_score: null,
        average_score: null,
        bonus_count: 0,
        maxi_yatzy_count: 0,
      });
      whenRendered();
      const highScoreValues = await screen.findAllByText('—');
      expect(highScoreValues.length).toBeGreaterThanOrEqual(2);
    });
  });

  function givenMyPlayer(player: {
    id: number;
    account_id: string;
    name: string;
    created_at: string;
  }) {
    sessionStorage.setItem('yatzy_player', JSON.stringify(player));
  }

  function givenUpdatePlayerSucceeds(player: {
    id: number;
    account_id: string;
    name: string;
    created_at: string;
  }) {
    server.use(http.put(PLAYER_URL(player.id), () => HttpResponse.json(player)));
  }

  function givenPlayerStats(overrides: {
    games_played: number;
    high_score: number | null;
    average_score: number | null;
    bonus_count: number;
    maxi_yatzy_count: number;
  }) {
    server.use(
      http.get(PLAYER_STATS_URL(1), () =>
        HttpResponse.json({
          player_id: 1,
          player_name: 'Alice',
          member_since: '2024-01-01T00:00:00Z',
          ...overrides,
        })
      )
    );
  }

  function givenUpdatePlayerFails(id: number) {
    server.use(
      http.put(PLAYER_URL(id), () => HttpResponse.json({ detail: 'Error' }, { status: 500 }))
    );
  }

  function whenRendered() {
    mockUseAuth.mockReturnValue({
      user: { id: ACCOUNT_ID, email: 'test@example.com', created_at: '' },
      accessToken: 'test-token',
      isLoading: false,
      login: vi.fn(),
      register: vi.fn(),
      logout: vi.fn(),
    });
    renderWithProviders(<EditPlayerScreen />);
  }

  async function whenNameChangedTo(name: string) {
    const input = await screen.findByRole('textbox');
    await userEvent.clear(input);
    await userEvent.type(input, name);
  }

  async function whenSaveClicked() {
    await userEvent.click(screen.getByRole('button', { name: /save/i }));
  }

  async function whenCancelClicked() {
    await userEvent.click(await screen.findByRole('button', { name: /cancel/i }));
  }

  async function thenInputHasValue(value: string) {
    const input = await screen.findByRole('textbox');
    expect(input).toHaveValue(value);
  }

  async function thenNavigatedTo(path: string) {
    await waitFor(() => expect(mockNavigate).toHaveBeenCalledWith(path));
  }

  async function thenErrorToastIsVisible(title: string) {
    await screen.findByText(title);
  }

  async function thenStatVisible(label: string, value: string) {
    await screen.findByText(label);
    await screen.findByText(value);
  }
});
