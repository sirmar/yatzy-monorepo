import { Clock, List, LogOut, Trophy, User } from 'lucide-react';
import { useCallback, useEffect, useRef, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';

import type { components } from '@/api';
import { apiClient } from '@/api';
import { Avatar, AvatarStack } from '@/components/Avatar';
import { ModePill } from '@/components/ModePill';
import { useAuth } from '@/hooks/AuthContext';
import { usePlayer } from '@/hooks/PlayerContext';
import { useErrorToast } from '@/hooks/use-toast';
import { useEventSource } from '@/hooks/useEventSource';
import { cn } from '@/lib/utils';

type ActiveGame = components['schemas']['Game'];

function useActiveGames(): ActiveGame[] {
  const { player } = usePlayer();
  const [games, setGames] = useState<ActiveGame[]>([]);

  const fetchActiveGames = useCallback(async () => {
    if (!player) return;
    const { data } = await apiClient.GET('/games', { params: { query: { status: 'active' } } });
    if (!data) return;
    setGames(data.filter((g) => g.player_ids.includes(player.id)));
  }, [player]);

  useEffect(() => {
    if (!player) return;
    const controller = new AbortController();
    apiClient
      .GET('/games', { params: { query: { status: 'active' } }, signal: controller.signal })
      .then(({ data }) => {
        if (!data) return;
        setGames(data.filter((g) => g.player_ids.includes(player.id)));
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
            'absolute top-[calc(100%+6px)] min-w-[260px] bg-[var(--surface-2)] border border-[var(--border-2)] rounded-[12px] shadow-[0_8px_32px_rgba(0,0,0,0.4)] z-50 overflow-hidden p-1.5',
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
              {firstGame && <ModePill mode={firstGame.mode} />}
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
                        <ModePill mode={g.mode} />
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
                                e.stopPropagation();
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
                                e.stopPropagation();
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
                              e.stopPropagation();
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
                <Trophy
                  aria-hidden="true"
                  width="15"
                  height="15"
                  className="text-[var(--text-muted)]"
                />
                <span>Leaderboard</span>
                <span className="text-[11px] text-[var(--text-muted)]">▾</span>
              </>
            }
          >
            <DropdownItem href="/statistics/high-scores">
              <Trophy aria-hidden="true" width="14" height="14" />
              High scores
            </DropdownItem>
            <DropdownItem href="/statistics/games-played">
              <List aria-hidden="true" width="14" height="14" />
              Most games played
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
            <User aria-hidden="true" width="14" height="14" />
            Profile
          </DropdownItem>
          <DropdownItem href="/history">
            <Clock aria-hidden="true" width="14" height="14" />
            History
          </DropdownItem>
          <DropdownDivider />
          <DropdownItem danger onClick={handleLogout}>
            <LogOut aria-hidden="true" width="14" height="14" />
            Sign out
          </DropdownItem>
        </DropdownShell>
      </div>
    </header>
  );
}
