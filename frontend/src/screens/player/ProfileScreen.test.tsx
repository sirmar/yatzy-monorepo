import { screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { HttpResponse, http } from 'msw';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import type { components } from '@/api/schema';
import { createMockServer, renderWithProviders } from '@/test/helpers';
import { ProfileScreen } from './ProfileScreen';

type ModeStats = components['schemas']['ModeStats'];

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

  describe('editing display name', () => {
    it('shows edit form pre-filled with current name after clicking Edit', async () => {
      givenMyPlayer({ id: 1, account_id: ACCOUNT_ID, name: 'Alice', created_at: '' });
      whenRendered();
      await whenEditClicked();
      await thenInputHasValue('Alice');
    });

    it('saves updated name and closes the form', async () => {
      givenMyPlayer({ id: 1, account_id: ACCOUNT_ID, name: 'Alice', created_at: '' });
      givenUpdatePlayerSucceeds({ id: 1, account_id: ACCOUNT_ID, name: 'Alicia', created_at: '' });
      whenRendered();
      await whenEditClicked();
      await whenNameChangedTo('Alicia');
      await whenSaveClicked();
      await thenEditFormIsClosed();
    });

    it('closes form without navigating', async () => {
      givenMyPlayer({ id: 1, account_id: ACCOUNT_ID, name: 'Alice', created_at: '' });
      givenUpdatePlayerSucceeds({ id: 1, account_id: ACCOUNT_ID, name: 'Alicia', created_at: '' });
      whenRendered();
      await whenEditClicked();
      await whenNameChangedTo('Alicia');
      await whenSaveClicked();
      expect(mockNavigate).not.toHaveBeenCalled();
    });
  });

  describe('stats', () => {
    it('shows total games count in summary grid', async () => {
      givenMyPlayer({ id: 1, account_id: ACCOUNT_ID, name: 'Alice', created_at: '' });
      givenPlayerStats({
        maxi: { games_played: 3 },
        maxi_sequential: { games_played: 2 },
      });
      whenRendered();
      await thenSummaryGamesVisible(5);
    });

    it('shows all four mode rows in the table', async () => {
      givenMyPlayer({ id: 1, account_id: ACCOUNT_ID, name: 'Alice', created_at: '' });
      whenRendered();
      await thenModeRowsVisible(['Maxi Yatzy', 'Maxi Sequential', 'Yatzy', 'Yatzy Sequential']);
    });

    it('shows games played per mode row', async () => {
      givenMyPlayer({ id: 1, account_id: ACCOUNT_ID, name: 'Alice', created_at: '' });
      givenPlayerStats({
        maxi: { games_played: 3 },
        yatzy: { games_played: 7 },
      });
      whenRendered();
      await thenModeRowGameCount('Maxi Yatzy', 3);
      await thenModeRowGameCount('Yatzy', 7);
    });

    it('shows — for high score and average score when null', async () => {
      givenMyPlayer({ id: 1, account_id: ACCOUNT_ID, name: 'Alice', created_at: '' });
      givenPlayerStats({
        maxi: { games_played: 1, high_score: null, average_score: null },
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

  function emptyModeStats(): ModeStats {
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
          maxi: { ...emptyModeStats(), ...overrides.maxi },
          maxi_sequential: { ...emptyModeStats(), ...overrides.maxi_sequential },
          yatzy: { ...emptyModeStats(), ...overrides.yatzy },
          yatzy_sequential: { ...emptyModeStats(), ...overrides.yatzy_sequential },
        })
      )
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

  async function whenEditClicked() {
    await userEvent.click(await screen.findByRole('button', { name: /edit/i }));
  }

  async function whenNameChangedTo(name: string) {
    const input = screen.getByRole('textbox');
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

  async function thenEditFormIsClosed() {
    await screen.findByRole('button', { name: /edit/i });
    expect(screen.queryByRole('textbox')).not.toBeInTheDocument();
  }

  async function thenSummaryGamesVisible(count: number) {
    await screen.findAllByText('Games');
    expect(await screen.findByText(String(count))).toBeInTheDocument();
  }

  async function thenModeRowsVisible(labels: string[]) {
    for (const label of labels) {
      expect(await screen.findByText(label)).toBeInTheDocument();
    }
  }

  async function thenModeRowGameCount(modeLabel: string, count: number) {
    const cell = await screen.findByText(modeLabel);
    const row = cell.closest('tr') as HTMLElement;
    expect(within(row).getByText(String(count))).toBeInTheDocument();
  }

  async function thenNullScoresShowDash() {
    const dashes = await screen.findAllByText('—');
    expect(dashes.length).toBeGreaterThanOrEqual(2);
  }
});
