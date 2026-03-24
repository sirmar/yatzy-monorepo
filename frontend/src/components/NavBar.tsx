import { useCallback, useEffect, useState } from 'react';
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom';
import { apiClient } from '@/api';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useAuth } from '@/hooks/AuthContext';
import { usePlayer } from '@/hooks/PlayerContext';
import { usePolling } from '@/hooks/usePolling';

const activeClass = 'text-yellow-400';
const inactiveClass = 'text-gray-400 hover:text-white transition-colors';

function useActiveGameIds(): number[] {
  const { gameId } = useParams<{ gameId: string }>();
  const { player } = usePlayer();
  const [gameIds, setGameIds] = useState<number[]>(() => (gameId ? [Number(gameId)] : []));

  const fetchActiveGames = useCallback(async () => {
    if (!player) return;
    const { data } = await apiClient.GET('/games', { params: { query: { status: 'active' } } });
    if (!data) return;
    const ids = data.filter((g) => g.player_ids.includes(player.id)).map((g) => g.id);
    setGameIds(ids);
  }, [player]);

  useEffect(() => {
    fetchActiveGames();
  }, [fetchActiveGames]);

  usePolling(fetchActiveGames);

  return gameIds;
}

export function NavBar() {
  const { player, setPlayer } = usePlayer();
  const { logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const activeGameIds = useActiveGameIds();

  async function handleLogout() {
    await logout();
    setPlayer(null);
    navigate('/login');
  }

  const isActive = (path: string) => location.pathname.startsWith(path);
  const anyGameActive = activeGameIds.some((id) => isActive(`/games/${id}`));

  return (
    <nav className="bg-gray-900 border-b border-gray-800">
      <div className="max-w-4xl mx-auto px-4 h-12 flex items-center justify-between">
        <span className="text-white font-bold text-sm">Yatzy</span>
        <div className="flex items-center gap-6 text-sm">
          <Link to="/lobby" className={isActive('/lobby') ? activeClass : inactiveClass}>
            Lobby
          </Link>
          <DropdownMenu>
            <DropdownMenuTrigger className={anyGameActive ? activeClass : inactiveClass}>
              Games ▾
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              {activeGameIds.length === 0 ? (
                <DropdownMenuItem disabled className="text-gray-400">
                  No games
                </DropdownMenuItem>
              ) : (
                activeGameIds.map((id) => (
                  <DropdownMenuItem key={id} asChild>
                    <Link to={`/games/${id}`}>{`Game #${id}`}</Link>
                  </DropdownMenuItem>
                ))
              )}
            </DropdownMenuContent>
          </DropdownMenu>
          <DropdownMenu>
            <DropdownMenuTrigger className={inactiveClass}>{player?.name} ▾</DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem asChild>
                <Link to="/">Change player</Link>
              </DropdownMenuItem>
              <DropdownMenuItem onSelect={handleLogout}>Sign out</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </nav>
  );
}
