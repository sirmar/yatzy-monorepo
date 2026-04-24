import { useCallback, useEffect, useRef, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';

import { apiClient } from '@/api';
import { Avatar, AvatarStack } from '@/components/Avatar';
import { useAuth } from '@/hooks/AuthContext';
import { usePlayer } from '@/hooks/PlayerContext';
import { useErrorToast } from '@/hooks/use-toast';
import { useEventSource } from '@/hooks/useEventSource';
import { cn } from '@/lib/utils';

interface ActiveGame {
  id: number;
  player_ids: number[];
  current_player_id?: number | null;
  creator_id: number;
  mode: string;
}

function useActiveGames(): ActiveGame[] {
  const { player } = usePlayer();
  const [games, setGames] = useState<ActiveGame[]>([]);

  const fetchActiveGames = useCallback(async () => {
    if (!player) return;
    const { data } = await apiClient.GET('/games', { params: { query: { status: 'active' } } });
    if (!data) return;
    setGames(data.filter((g) => g.player_ids.includes(player.id)) as ActiveGame[]);
  }, [player]);

  useEffect(() => {
    if (!player) return;
    const controller = new AbortController();
    apiClient
      .GET('/games', { params: { query: { status: 'active' } }, signal: controller.signal })
      .then(({ data }) => {
        if (!data) return;
        setGames(data.filter((g) => g.player_ids.includes(player.id)) as ActiveGame[]);
      });
    return () => controller.abort();
  }, [player]);

  useEventSource(
    player ? `/api/games/active/events?player_id=${player.id}` : null,
    fetchActiveGames
  );

  return games;
}

function useClickOutside(ref: React.RefObject<HTMLElement | null>, handler: () => void) {
  useEffect(() => {
    function listener(e: MouseEvent) {
      if (!ref.current || ref.current.contains(e.target as Node)) return;
      handler();
    }
    document.addEventListener('mousedown', listener);
    return () => document.removeEventListener('mousedown', listener);
  }, [ref, handler]);
}

function DropdownShell({
  trigger,
  children,
  align = 'left',
}: {
  trigger: React.ReactNode;
  children: React.ReactNode;
  align?: 'left' | 'right';
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  useClickOutside(ref, () => setOpen(false));

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-2 bg-[var(--surface)] border border-[var(--border-2)] rounded-[10px] px-3 h-9 cursor-pointer text-foreground text-[13px] font-medium transition-all hover:bg-[var(--surface-2)] hover:border-white/20 hover:scale-[1.04] active:scale-[0.97]"
      >
        {trigger}
      </button>
      {open && (
        <div
          className={cn(
            'absolute top-[calc(100%+6px)] min-w-[180px] bg-[var(--surface-2)] border border-[var(--border-2)] rounded-[12px] shadow-[0_8px_32px_rgba(0,0,0,0.4)] z-50 overflow-hidden p-1.5',
            align === 'right' ? 'right-0' : 'left-0'
          )}
          role="menu"
          onClick={() => setOpen(false)}
          onKeyDown={(e) => e.key === 'Escape' && setOpen(false)}
        >
          {children}
        </div>
      )}
    </div>
  );
}

function DropdownItem({
  children,
  danger,
  onClick,
  href,
}: {
  children: React.ReactNode;
  danger?: boolean;
  onClick?: () => void;
  href?: string;
}) {
  const cls = cn(
    'flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-[13px] font-medium cursor-pointer transition-all',
    danger
      ? 'text-[var(--text-muted)] hover:text-[var(--red)] hover:bg-[rgba(240,101,96,0.08)]'
      : 'text-[var(--text-muted)] hover:bg-white/[0.06] hover:text-foreground'
  );
  if (href) {
    return (
      <Link to={href} className={cls}>
        {children}
      </Link>
    );
  }
  return (
    <button type="button" className={cn(cls, 'w-full text-left')} onClick={onClick}>
      {children}
    </button>
  );
}

function DropdownDivider() {
  return <div className="h-px bg-[var(--border)] my-1" />;
}

function DropdownLabel({ children }: { children: React.ReactNode }) {
  return (
    <div className="px-2.5 py-1.5 text-[10px] font-bold uppercase tracking-[0.08em] text-[var(--text-dim)]">
      {children}
    </div>
  );
}

function modeLabel(mode: string) {
  const map: Record<string, string> = {
    maxi: 'Maxi Yatzy',
    maxi_sequential: 'Maxi Sequential',
    yatzy: 'Yatzy',
    yatzy_sequential: 'Yatzy Sequential',
  };
  return map[mode] ?? mode;
}

export function NavBar() {
  const { player, setPlayer } = usePlayer();
  const { logout } = useAuth();
  const navigate = useNavigate();
  const errorToast = useErrorToast();
  const { gameId: routeGameId } = useParams<{ gameId: string }>();
  const activeGames = useActiveGames();
  const [confirmAbortId, setConfirmAbortId] = useState<number | null>(null);

  async function handleLogout() {
    await logout();
    setPlayer(null);
    navigate('/login');
  }

  async function handleAbort(gameId: number) {
    setConfirmAbortId(null);
    const { error } = await apiClient.POST('/games/{game_id}/abort', {
      params: { path: { game_id: gameId } },
    });
    if (error) {
      errorToast('Failed to abort game');
      return;
    }
    if (Number(routeGameId) === gameId) navigate('/lobby');
  }

  const currentGame = activeGames.find((g) => g.id === Number(routeGameId));
  const firstGame = currentGame ?? activeGames[0];

  return (
    <header className="bg-background py-3">
      <div className="max-w-[860px] mx-auto px-4 flex items-center gap-3">
        {/* Games switcher */}
        <DropdownShell
          trigger={
            <>
              {firstGame ? (
                <AvatarStack names={firstGame.player_ids.map((id) => String(id))} size="sm" />
              ) : (
                <span className="text-[var(--text-muted)]">Games</span>
              )}
              {firstGame && (
                <span className="text-[10px] font-semibold uppercase tracking-[0.06em] bg-[var(--accent-dim)] text-[var(--accent)] rounded-full px-2 py-0.5">
                  {modeLabel(firstGame.mode)}
                </span>
              )}
              <span className="text-[11px] text-[var(--text-muted)]">▾</span>
            </>
          }
        >
          {activeGames.length > 0 && (
            <>
              <DropdownLabel>Active games</DropdownLabel>
              {activeGames.map((g) => {
                const isMyTurn = g.current_player_id === player?.id;
                const isCreator = g.creator_id === player?.id;
                const isActive = g.id === Number(routeGameId);
                return (
                  <Link
                    key={g.id}
                    to={`/games/${g.id}`}
                    className={cn(
                      'flex items-center justify-between px-[10px] py-[9px] rounded-lg transition-colors',
                      isActive ? 'bg-[var(--accent-dim)]' : 'hover:bg-white/[0.06]'
                    )}
                  >
                    <div className="flex flex-col gap-[2px]">
                      <AvatarStack names={g.player_ids.map((id) => String(id))} size="sm" />
                      <div className="flex items-center gap-1.5 mt-0.5">
                        <span className="text-[10px] font-semibold uppercase tracking-[0.06em] bg-[var(--accent-dim)] text-[var(--accent)] rounded-full px-2 py-0.5">
                          {modeLabel(g.mode)}
                        </span>
                        {isMyTurn && (
                          <span className="text-[11px] text-[var(--text-muted)]">Your turn</span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0 ml-3">
                      {isCreator &&
                        (confirmAbortId === g.id ? (
                          <>
                            <button
                              type="button"
                              onClick={(e) => {
                                e.preventDefault();
                                setConfirmAbortId(null);
                              }}
                              className="text-[11px] font-medium text-[var(--text-muted)] px-1.5 py-0.5 rounded cursor-pointer hover:text-foreground"
                            >
                              Cancel
                            </button>
                            <button
                              type="button"
                              onClick={(e) => {
                                e.preventDefault();
                                handleAbort(g.id);
                              }}
                              className="text-[11px] font-medium text-[var(--red)] px-1.5 py-0.5 rounded cursor-pointer hover:bg-[rgba(240,101,96,0.1)]"
                            >
                              Abort
                            </button>
                          </>
                        ) : (
                          <button
                            type="button"
                            onClick={(e) => {
                              e.preventDefault();
                              setConfirmAbortId(g.id);
                            }}
                            className="text-[11px] font-medium text-[var(--text-dim)] px-1 py-0.5 rounded cursor-pointer hover:text-[var(--red)] hover:bg-[rgba(240,101,96,0.1)] transition-colors"
                          >
                            Abort
                          </button>
                        ))}
                      <div
                        className={cn(
                          'w-[7px] h-[7px] rounded-full flex-shrink-0',
                          isMyTurn
                            ? 'bg-[var(--green)] shadow-[0_0_6px_var(--green)]'
                            : 'bg-[var(--text-dim)]'
                        )}
                      />
                    </div>
                  </Link>
                );
              })}
              <DropdownDivider />
            </>
          )}
          <DropdownItem href="/lobby">
            <span className="text-[var(--accent)] text-base leading-none">＋</span>
            New game
          </DropdownItem>
        </DropdownShell>

        {/* Leaderboard */}
        <div className="ml-auto">
          <DropdownShell
            align="right"
            trigger={
              <>
                <svg
                  aria-hidden="true"
                  width="15"
                  height="15"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  viewBox="0 0 24 24"
                  className="text-[var(--text-muted)]"
                >
                  <path d="M6 9H4a2 2 0 0 0-2 2v1a2 2 0 0 0 2 2h2" />
                  <path d="M18 9h2a2 2 0 0 1 2 2v1a2 2 0 0 1-2 2h-2" />
                  <path d="M6 9V5a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v4" />
                  <path d="M6 15v1a3 3 0 0 0 3 3h6a3 3 0 0 0 3-3v-1" />
                </svg>
                <span>Leaderboard</span>
                <span className="text-[11px] text-[var(--text-muted)]">▾</span>
              </>
            }
          >
            <DropdownItem href="/statistics/high-scores">
              <svg
                aria-hidden="true"
                width="14"
                height="14"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                viewBox="0 0 24 24"
              >
                <path d="M6 9H4a2 2 0 0 0-2 2v1a2 2 0 0 0 2 2h2" />
                <path d="M18 9h2a2 2 0 0 1 2 2v1a2 2 0 0 1-2 2h-2" />
                <path d="M6 9V5a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v4" />
                <path d="M6 15v1a3 3 0 0 0 3 3h6a3 3 0 0 0 3-3v-1" />
              </svg>
              High scores
            </DropdownItem>
            <DropdownItem href="/statistics/games-played">
              <svg
                aria-hidden="true"
                width="14"
                height="14"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                viewBox="0 0 24 24"
              >
                <path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01" />
              </svg>
              Most games played
            </DropdownItem>
            <DropdownItem href="/history">
              <svg
                aria-hidden="true"
                width="14"
                height="14"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                viewBox="0 0 24 24"
              >
                <path d="M12 8v4l3 3" />
                <circle cx="12" cy="12" r="9" />
              </svg>
              History
            </DropdownItem>
          </DropdownShell>
        </div>

        {/* Profile */}
        <DropdownShell
          align="right"
          trigger={
            <>
              {player && <Avatar name={player.name} index={0} size="sm" />}
              <span>{player?.name}</span>
              <span className="text-[11px] text-[var(--text-muted)]">▾</span>
            </>
          }
        >
          <DropdownItem href="/profile">
            <svg
              aria-hidden="true"
              width="14"
              height="14"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              viewBox="0 0 24 24"
            >
              <path d="M3 18v-1a5 5 0 0 1 5-5h8a5 5 0 0 1 5 5v1" />
              <circle cx="12" cy="7" r="4" />
            </svg>
            Profile
          </DropdownItem>
          <DropdownDivider />
          <DropdownItem danger onClick={handleLogout}>
            <svg
              aria-hidden="true"
              width="14"
              height="14"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              viewBox="0 0 24 24"
            >
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
              <polyline points="16 17 21 12 16 7" />
              <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
            Sign out
          </DropdownItem>
        </DropdownShell>
      </div>
    </header>
  );
}
