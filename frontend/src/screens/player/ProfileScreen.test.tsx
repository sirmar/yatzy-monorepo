import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { HttpResponse, http } from 'msw';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import type { components } from '@/api/schema';
import { createMockServer, renderWithProviders } from '@/test/helpers';

type ModeStats = components['schemas']['ModeStats'];

import { ProfileScreen } from './ProfileScreen';

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

const PLAYER_URL = (id: number) => `http://localhost/api/players/${id}`;
const PLAYER_STATS_URL = (id: number) => `http://localhost/api/players/${id}/stats`;

const ACCOUNT_ID = '550e8400-e29b-41d4-a716-446655440000';

describe('ProfileScreen', () => {
  beforeEach(() => {
    givenPlayerStats();
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

  describe('stats', () => {
    it('shows total games played', async () => {
      givenMyPlayer({ id: 1, account_id: ACCOUNT_ID, name: 'Alice', created_at: '' });
      givenPlayerStats({ total_games_played: 5 });
      whenRendered();
      await thenTotalGamesPlayedVisible(5);
    });

    it('shows tabs for all four modes', async () => {
      givenMyPlayer({ id: 1, account_id: ACCOUNT_ID, name: 'Alice', created_at: '' });
      whenRendered();
      await thenModeTabsVisible([
        'Maxi Yatzy',
        'Maxi Yatzy Sequential',
        'Yatzy',
        'Yatzy Sequential',
      ]);
    });

    it('defaults to Maxi Yatzy and shows its stats', async () => {
      givenMyPlayer({ id: 1, account_id: ACCOUNT_ID, name: 'Alice', created_at: '' });
      givenPlayerStats({
        maxi: {
          games_played: 3,
          high_score: 350,
          average_score: 290,
          bonus_count: 2,
          yatzy_hit_count: 1,
        },
      });
      whenRendered();
      await thenGamesPlayedVisible(3);
    });

    it('switches stats when another tab is clicked', async () => {
      givenMyPlayer({ id: 1, account_id: ACCOUNT_ID, name: 'Alice', created_at: '' });
      givenPlayerStats({
        maxi: {
          games_played: 3,
          high_score: 350,
          average_score: 290,
          bonus_count: 2,
          yatzy_hit_count: 1,
        },
        yatzy: {
          games_played: 7,
          high_score: 200,
          average_score: 180,
          bonus_count: 1,
          yatzy_hit_count: 0,
        },
      });
      whenRendered();
      await whenModeTabClicked('Yatzy');
      await thenGamesPlayedVisible(7);
    });

    it('shows — for high score and average score when null', async () => {
      givenMyPlayer({ id: 1, account_id: ACCOUNT_ID, name: 'Alice', created_at: '' });
      givenPlayerStats({
        maxi: {
          games_played: 1,
          high_score: null,
          average_score: null,
          bonus_count: 0,
          yatzy_hit_count: 0,
        },
      });
      whenRendered();
      await thenNullScoresShowDash();
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

  function emptyModeStats() {
    return {
      games_played: 0,
      high_score: null,
      average_score: null,
      bonus_count: 0,
      yatzy_hit_count: 0,
    };
  }

  function givenPlayerStats(
    overrides: {
      total_games_played?: number;
      maxi?: Partial<ModeStats>;
      maxi_sequential?: Partial<ModeStats>;
      yatzy?: Partial<ModeStats>;
      yatzy_sequential?: Partial<ModeStats>;
    } = {}
  ) {
    server.use(
      http.get(PLAYER_STATS_URL(1), () =>
        HttpResponse.json({
          player_id: 1,
          player_name: 'Alice',
          member_since: '2024-01-01T00:00:00Z',
          total_games_played: overrides.total_games_played ?? 0,
          maxi: { ...emptyModeStats(), ...overrides.maxi },
          maxi_sequential: { ...emptyModeStats(), ...overrides.maxi_sequential },
          yatzy: { ...emptyModeStats(), ...overrides.yatzy },
          yatzy_sequential: { ...emptyModeStats(), ...overrides.yatzy_sequential },
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
      user: { id: ACCOUNT_ID, email: 'test@example.com', email_verified: true, created_at: '' },
      accessToken: 'test-token',
      isLoading: false,
      login: vi.fn(),
      register: vi.fn(),
      logout: vi.fn(),
    });
    renderWithProviders(<ProfileScreen />);
  }

  async function whenNameChangedTo(name: string) {
    const input = await screen.findByRole('textbox');
    await userEvent.clear(input);
    await userEvent.type(input, name);
  }

  async function whenSaveClicked() {
    await userEvent.click(screen.getByRole('button', { name: /save/i }));
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

  async function thenTotalGamesPlayedVisible(count: number) {
    await screen.findByText(/Total games played/);
    expect(screen.getByText(String(count))).toBeInTheDocument();
  }

  async function thenModeTabsVisible(labels: string[]) {
    for (const label of labels) {
      expect(await screen.findByRole('button', { name: label })).toBeInTheDocument();
    }
  }

  async function whenModeTabClicked(label: string) {
    await userEvent.click(await screen.findByRole('button', { name: label }));
  }

  async function thenGamesPlayedVisible(count: number) {
    await screen.findByText(String(count));
  }

  async function thenNullScoresShowDash() {
    const dashes = await screen.findAllByText('—');
    expect(dashes.length).toBeGreaterThanOrEqual(2);
  }
});
