import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { HttpResponse, http } from 'msw';
import { setupServer } from 'msw/node';
import { afterAll, afterEach, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import { renderWithProviders } from '@/test/helpers';
import { NavBar } from './NavBar';

const mockNavigate = vi.hoisted(() => vi.fn());
const mockUseParams = vi.hoisted(() => vi.fn());
const mockUseLocation = vi.hoisted(() => vi.fn());
vi.mock('react-router-dom', async () => ({
  ...(await vi.importActual('react-router-dom')),
  useNavigate: () => mockNavigate,
  useParams: mockUseParams,
  useLocation: mockUseLocation,
}));

const server = setupServer();
beforeAll(() => server.listen());
afterEach(() => {
  server.resetHandlers();
  mockNavigate.mockReset();
  sessionStorage.clear();
});
afterAll(() => server.close());

const GAMES_URL = 'http://localhost/api/games';

const ALICE = { id: 1, name: 'Alice', created_at: '' };

describe('NavBar', () => {
  beforeEach(() => {
    sessionStorage.setItem('yatzy_player', JSON.stringify(ALICE));
    mockUseParams.mockReturnValue({});
    mockUseLocation.mockReturnValue({ pathname: '/lobby' });
    givenActiveGames([]);
  });

  describe('display', () => {
    it('shows "Yatzy" brand text', () => {
      whenRendered();
      expect(screen.getByText('Yatzy')).toBeInTheDocument();
    });

    it('shows "Lobby" link', () => {
      whenRendered();
      expect(screen.getByRole('link', { name: 'Lobby' })).toBeInTheDocument();
    });

    it('shows player name in the dropdown trigger', () => {
      whenRendered();
      expect(screen.getByRole('button', { name: /alice/i })).toBeInTheDocument();
    });
  });

  describe('active game — on game screen', () => {
    it('shows current game immediately before fetch completes', async () => {
      mockUseParams.mockReturnValue({ gameId: '42' });
      mockUseLocation.mockReturnValue({ pathname: '/games/42' });
      givenActiveGames([{ id: 42, player_ids: [ALICE.id] }]);
      whenRendered();
      await userEvent.click(screen.getByText('Active Games ▾'));
      expect(screen.getByRole('menuitem', { name: 'Game #42' })).toBeInTheDocument();
    });

    it('shows all active games including other games the player is in', async () => {
      mockUseParams.mockReturnValue({ gameId: '42' });
      mockUseLocation.mockReturnValue({ pathname: '/games/42' });
      givenActiveGames([
        { id: 42, player_ids: [ALICE.id] },
        { id: 7, player_ids: [ALICE.id] },
      ]);
      whenRendered();
      await userEvent.click(screen.getByText('Active Games ▾'));
      expect(await screen.findByRole('menuitem', { name: 'Game #42' })).toBeInTheDocument();
      expect(await screen.findByRole('menuitem', { name: 'Game #7' })).toBeInTheDocument();
    });
  });

  describe('Active Games dropdown', () => {
    it('always shows "Active Games ▾" trigger', () => {
      whenRendered();
      expect(screen.getByText('Active Games ▾')).toBeInTheDocument();
    });

    it('shows "No games" when player has no active games', async () => {
      givenActiveGames([]);
      whenRendered();
      await userEvent.click(screen.getByText('Active Games ▾'));
      expect(screen.getByRole('menuitem', { name: 'No games' })).toBeInTheDocument();
    });

    it('shows "Game #7" in dropdown when player has one active game', async () => {
      givenActiveGames([{ id: 7, player_ids: [ALICE.id] }]);
      whenRendered();
      await userEvent.click(screen.getByText('Active Games ▾'));
      expect(await screen.findByRole('menuitem', { name: 'Game #7' })).toBeInTheDocument();
    });

    it('lists all active games in dropdown when player is in several', async () => {
      givenActiveGames([
        { id: 7, player_ids: [ALICE.id] },
        { id: 8, player_ids: [ALICE.id] },
      ]);
      whenRendered();
      await userEvent.click(screen.getByText('Active Games ▾'));
      expect(await screen.findByRole('menuitem', { name: 'Game #7' })).toBeInTheDocument();
      expect(await screen.findByRole('menuitem', { name: 'Game #8' })).toBeInTheDocument();
    });

    it('does not list games the player is not in', async () => {
      givenActiveGames([{ id: 9, player_ids: [99] }]);
      whenRendered();
      await userEvent.click(screen.getByText('Active Games ▾'));
      expect(screen.queryByRole('menuitem', { name: 'Game #9' })).not.toBeInTheDocument();
    });
  });

  describe('sign out', () => {
    it('shows Sign out option in player dropdown', async () => {
      whenRendered();
      await userEvent.click(screen.getByRole('button', { name: /alice/i }));
      expect(screen.getByRole('menuitem', { name: 'Sign out' })).toBeInTheDocument();
    });

    it('navigates to /login after sign out', async () => {
      server.use(
        http.post('http://localhost/auth/logout', () => new HttpResponse(null, { status: 204 }))
      );
      whenRendered();
      await userEvent.click(screen.getByRole('button', { name: /alice/i }));
      await userEvent.click(screen.getByRole('menuitem', { name: 'Sign out' }));
      expect(mockNavigate).toHaveBeenCalledWith('/login');
    });
  });

  describe('Statistics dropdown', () => {
    it('always shows "Statistics ▾" trigger', () => {
      whenRendered();
      thenStatisticsTriggerIsVisible();
    });

    it('shows "High Scores" menu item when Statistics dropdown is opened', async () => {
      whenRendered();
      await whenStatisticsDropdownOpened();
      thenMenuItemIsVisible('High Scores');
    });

    it('highlights Statistics trigger on /statistics/high-scores', () => {
      givenOnPath('/statistics/high-scores');
      whenRendered();
      thenStatisticsTriggerIsActive();
    });

    it('does not highlight Statistics trigger on /lobby', () => {
      givenOnPath('/lobby');
      whenRendered();
      thenStatisticsTriggerIsInactive();
    });

    function givenOnPath(pathname: string) {
      mockUseLocation.mockReturnValue({ pathname });
    }

    async function whenStatisticsDropdownOpened() {
      await userEvent.click(screen.getByText('Statistics ▾'));
    }

    function thenStatisticsTriggerIsVisible() {
      expect(screen.getByText('Statistics ▾')).toBeInTheDocument();
    }

    function thenMenuItemIsVisible(name: string) {
      expect(screen.getByRole('menuitem', { name })).toBeInTheDocument();
    }

    function thenStatisticsTriggerIsActive() {
      expect(screen.getByText('Statistics ▾')).toHaveClass('text-yellow-400');
    }

    function thenStatisticsTriggerIsInactive() {
      expect(screen.getByText('Statistics ▾')).not.toHaveClass('text-yellow-400');
    }
  });

  describe('active link highlighting', () => {
    it('highlights Lobby link on /lobby', () => {
      mockUseLocation.mockReturnValue({ pathname: '/lobby' });
      whenRendered();
      expect(screen.getByRole('link', { name: 'Lobby' })).toHaveClass('text-yellow-400');
    });

    it('does not highlight Lobby link on /games/42', () => {
      mockUseParams.mockReturnValue({ gameId: '42' });
      mockUseLocation.mockReturnValue({ pathname: '/games/42' });
      whenRendered();
      expect(screen.getByRole('link', { name: 'Lobby' })).not.toHaveClass('text-yellow-400');
    });

    it('highlights Active Games trigger on /games/42', () => {
      mockUseParams.mockReturnValue({ gameId: '42' });
      mockUseLocation.mockReturnValue({ pathname: '/games/42' });
      whenRendered();
      expect(screen.getByText('Active Games ▾')).toHaveClass('text-yellow-400');
    });

    it('highlights Active Games trigger on /games/42/end', () => {
      mockUseParams.mockReturnValue({ gameId: '42' });
      mockUseLocation.mockReturnValue({ pathname: '/games/42/end' });
      whenRendered();
      expect(screen.getByText('Active Games ▾')).toHaveClass('text-yellow-400');
    });
  });

  function whenRendered() {
    renderWithProviders(<NavBar />);
  }

  function givenActiveGames(games: { id: number; player_ids: number[] }[]) {
    server.use(
      http.get(GAMES_URL, () =>
        HttpResponse.json(
          games.map((g) => ({
            id: g.id,
            status: 'active',
            creator_id: g.player_ids[0] ?? 1,
            player_ids: g.player_ids,
            created_at: '',
          }))
        )
      )
    );
  }
});
