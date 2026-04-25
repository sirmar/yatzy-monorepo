import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { HttpResponse, http } from 'msw';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { ALICE, createMockServer, renderWithProviders } from '@/test/helpers';
import { NavBar } from './NavBar';

const mockNavigate = vi.hoisted(() => vi.fn());
const mockUseParams = vi.hoisted(() => vi.fn());
vi.mock('react-router-dom', async () => ({
  ...(await vi.importActual('react-router-dom')),
  useNavigate: () => mockNavigate,
  useParams: mockUseParams,
}));

const server = createMockServer();
afterEach(() => {
  mockNavigate.mockReset();
  sessionStorage.clear();
});

const GAMES_URL = 'http://localhost/api/games';

describe('NavBar', () => {
  beforeEach(() => {
    sessionStorage.setItem('yatzy_player', JSON.stringify(ALICE));
    mockUseParams.mockReturnValue({});
    givenActiveGames([]);
  });

  describe('display', () => {
    it('shows player name in the profile trigger', () => {
      whenRendered();
      expect(screen.getByRole('button', { name: /alice/i })).toBeInTheDocument();
    });

    it('shows "Games" when there are no active games', () => {
      whenRendered();
      expect(screen.getByText('Games')).toBeInTheDocument();
    });

    it('shows "Leaderboard" trigger', () => {
      whenRendered();
      expect(screen.getByRole('button', { name: /leaderboard/i })).toBeInTheDocument();
    });
  });

  describe('Games dropdown', () => {
    it('shows "Available games" link in games dropdown', async () => {
      whenRendered();
      await whenGamesDropdownOpened();
      expect(screen.getByRole('link', { name: /available games/i })).toBeInTheDocument();
    });

    it('shows active game link when player has an active game', async () => {
      givenActiveGames([{ id: 7, player_ids: [ALICE.id], mode: 'maxi' }]);
      whenRendered();
      await whenGamesDropdownOpened();
      const links = await screen.findAllByRole('link');
      expect(links.some((l) => l.getAttribute('href') === '/games/7')).toBe(true);
    });

    it('shows multiple active games', async () => {
      givenActiveGames([
        { id: 7, player_ids: [ALICE.id], mode: 'maxi' },
        { id: 8, player_ids: [ALICE.id], mode: 'yatzy' },
      ]);
      whenRendered();
      await whenGamesDropdownOpened();
      const links = await screen.findAllByRole('link');
      expect(links.some((l) => l.getAttribute('href') === '/games/7')).toBe(true);
      expect(links.some((l) => l.getAttribute('href') === '/games/8')).toBe(true);
    });

    it('does not show games the player is not in', async () => {
      givenActiveGames([{ id: 9, player_ids: [99], mode: 'maxi' }]);
      whenRendered();
      await whenGamesDropdownOpened();
      const links = screen.queryAllByRole('link');
      expect(links.some((l) => l.getAttribute('href') === '/games/9')).toBe(false);
    });

    it('shows mode pill for active game in trigger', async () => {
      givenActiveGames([{ id: 7, player_ids: [ALICE.id], mode: 'maxi' }]);
      whenRendered();
      await screen.findByText('Maxi Yatzy');
    });
  });

  describe('Leaderboard dropdown', () => {
    it('shows "High scores" link when leaderboard dropdown is opened', async () => {
      whenRendered();
      await whenLeaderboardDropdownOpened();
      expect(screen.getByRole('link', { name: /high scores/i })).toBeInTheDocument();
    });

    it('shows "Most games played" link when leaderboard dropdown is opened', async () => {
      whenRendered();
      await whenLeaderboardDropdownOpened();
      expect(screen.getByRole('link', { name: /most games played/i })).toBeInTheDocument();
    });
  });

  describe('Profile dropdown', () => {
    it('shows Sign out button in profile dropdown', async () => {
      whenRendered();
      await whenProfileDropdownOpened();
      expect(screen.getByRole('button', { name: /sign out/i })).toBeInTheDocument();
    });

    it('shows Profile link in profile dropdown', async () => {
      whenRendered();
      await whenProfileDropdownOpened();
      expect(screen.getByRole('link', { name: /profile/i })).toBeInTheDocument();
    });

    it('shows History link in profile dropdown', async () => {
      whenRendered();
      await whenProfileDropdownOpened();
      expect(screen.getByRole('link', { name: /history/i })).toBeInTheDocument();
    });
  });

  describe('sign out', () => {
    it('navigates to /login after sign out', async () => {
      server.use(
        http.post('http://localhost/auth/logout', () => new HttpResponse(null, { status: 204 }))
      );
      whenRendered();
      await whenProfileDropdownOpened();
      await userEvent.click(screen.getByRole('button', { name: /sign out/i }));
      expect(mockNavigate).toHaveBeenCalledWith('/login');
    });
  });

  function whenRendered() {
    renderWithProviders(<NavBar />);
  }

  async function whenGamesDropdownOpened() {
    await userEvent.click(screen.getByRole('button', { name: 'Games' }));
  }

  async function whenLeaderboardDropdownOpened() {
    await userEvent.click(screen.getByRole('button', { name: /leaderboard/i }));
  }

  async function whenProfileDropdownOpened() {
    await userEvent.click(screen.getByRole('button', { name: /alice/i }));
  }

  describe('abort game', () => {
    beforeEach(() => {
      givenActiveGames([{ id: 7, player_ids: [ALICE.id], mode: 'maxi' }]);
    });

    it('shows abort confirmation when abort button clicked', async () => {
      whenRendered();
      await whenGamesDropdownOpened();
      await userEvent.click(await screen.findByRole('button', { name: 'Abort' }));
      expect(screen.getByRole('button', { name: 'Abort' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Cancel' })).toBeInTheDocument();
    });

    it('dismisses abort confirmation when cancel is clicked', async () => {
      whenRendered();
      await whenGamesDropdownOpened();
      await userEvent.click(await screen.findByRole('button', { name: 'Abort' }));
      await userEvent.click(screen.getByRole('button', { name: 'Cancel' }));
      expect(screen.queryByRole('button', { name: 'Cancel' })).not.toBeInTheDocument();
    });

    it('calls abort endpoint and navigates to /lobby when confirmed', async () => {
      server.use(
        http.post(
          'http://localhost/api/games/7/abort',
          () => new HttpResponse(null, { status: 204 })
        )
      );
      whenRendered();
      await whenGamesDropdownOpened();
      await userEvent.click(await screen.findByRole('button', { name: 'Abort' }));
      await userEvent.click(screen.getByRole('button', { name: 'Abort' }));
      expect(mockNavigate).toHaveBeenCalledWith('/lobby');
    });
  });

  function givenActiveGames(games: { id: number; player_ids: number[]; mode?: string }[]) {
    server.use(
      http.get(GAMES_URL, () =>
        HttpResponse.json(
          games.map((g) => ({
            id: g.id,
            status: 'active',
            creator_id: g.player_ids[0] ?? 1,
            player_ids: g.player_ids,
            mode: g.mode ?? 'maxi',
            created_at: '',
          }))
        )
      )
    );
  }
});
