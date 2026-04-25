import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { components } from '@/api';
import { apiClient } from '@/api';
import { Card } from '@/components/Card';
import { FilterPill } from '@/components/FilterPill';
import { PageLayout } from '@/components/PageLayout';
import { usePlayer } from '@/hooks/PlayerContext';
import { useErrorToast } from '@/hooks/use-toast';
import { useEventSource } from '@/hooks/useEventSource';
import { usePlayerNames } from '@/hooks/usePlayerNames';
import { GameList } from './GameList';

type Game = components['schemas']['Game'];
type GameMode = components['schemas']['GameMode'];

const MODES: { value: GameMode; label: string }[] = [
  { value: 'maxi', label: 'Maxi Yatzy' },
  { value: 'maxi_sequential', label: 'Maxi Sequential' },
  { value: 'yatzy', label: 'Yatzy' },
  { value: 'yatzy_sequential', label: 'Yatzy Sequential' },
];

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

function NewGamePanel({
  mode,
  botCount,
  creating,
  onModeChange,
  onBotCountChange,
  onCreate,
}: {
  mode: GameMode;
  botCount: number;
  creating: boolean;
  onModeChange: (m: GameMode) => void;
  onBotCountChange: (n: number) => void;
  onCreate: () => void;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  useClickOutside(ref, () => setOpen(false));

  return (
    <div ref={ref} className="relative flex-shrink-0">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-1.5 h-9 px-3 bg-[var(--surface)] border border-[var(--border-2)] rounded-[10px] text-[13px] font-medium text-foreground cursor-pointer transition-all hover:bg-[var(--surface-2)] hover:border-white/20 hover:scale-[1.04] active:scale-[0.97]"
      >
        <span
          className={[
            'w-4 h-4 rounded-full bg-[var(--accent)] text-white flex items-center justify-center text-[12px] leading-none flex-shrink-0 transition-transform duration-200',
            open ? 'rotate-45' : '',
          ].join(' ')}
        >
          +
        </span>
        New game
      </button>

      {open && (
        <div
          data-testid="new-game-panel"
          className="absolute top-[calc(100%+6px)] right-0 w-60 flex flex-col gap-2.5 p-3 bg-[var(--surface-2)] border border-[var(--border-2)] rounded-[12px] shadow-[0_8px_32px_rgba(0,0,0,0.4)] z-10"
        >
          <div className="text-[10px] font-bold uppercase tracking-[0.08em] text-[var(--text-dim)]">
            Game mode
          </div>
          <div className="grid grid-cols-2 gap-[5px]">
            {MODES.map((m) => (
              <button
                key={m.value}
                type="button"
                onClick={() => onModeChange(m.value)}
                className={[
                  'text-[11px] font-semibold px-2.5 py-1 rounded-full border cursor-pointer text-center transition-colors',
                  mode === m.value
                    ? 'bg-[var(--accent-dim)] border-[var(--accent)] text-[var(--accent)]'
                    : 'bg-[var(--surface-2)] border-[var(--border-2)] text-[var(--text-muted)] hover:text-foreground hover:border-white/20',
                ].join(' ')}
              >
                {m.label}
              </button>
            ))}
          </div>

          <div className="text-[10px] font-bold uppercase tracking-[0.08em] text-[var(--text-dim)]">
            Bots
          </div>
          <div className="flex items-center bg-[var(--surface-2)] border border-[var(--border-2)] rounded-lg overflow-hidden">
            <button
              type="button"
              onClick={() => onBotCountChange(Math.max(0, botCount - 1))}
              disabled={botCount === 0}
              className="w-[30px] h-[30px] flex items-center justify-center text-[var(--text-muted)] hover:text-foreground hover:bg-white/[0.06] transition-colors disabled:opacity-25 disabled:cursor-default cursor-pointer"
            >
              −
            </button>
            <div className="flex-1 flex items-center justify-center border-x border-[var(--border-2)] h-[30px]">
              <span className="text-[13px] font-bold text-foreground">{botCount}</span>
            </div>
            <button
              type="button"
              onClick={() => onBotCountChange(Math.min(5, botCount + 1))}
              disabled={botCount === 5}
              className="w-[30px] h-[30px] flex items-center justify-center text-[var(--text-muted)] hover:text-foreground hover:bg-white/[0.06] transition-colors disabled:opacity-25 disabled:cursor-default cursor-pointer"
            >
              +
            </button>
          </div>

          <button
            type="button"
            onClick={() => {
              onCreate();
              setOpen(false);
            }}
            disabled={creating}
            className="h-[30px] w-full bg-[var(--accent)] text-white border-none rounded-[7px] text-[13px] font-semibold cursor-pointer transition-all hover:scale-[1.06] hover:shadow-[0_0_18px_rgba(124,158,248,0.4)] active:scale-[0.96] disabled:opacity-50"
          >
            Create
          </button>
        </div>
      )}
    </div>
  );
}

type VariantFilter = 'all' | 'maxi' | 'yatzy';
type TypeFilter = 'all' | 'regular' | 'sequential';

function applyFilters(games: Game[], variant: VariantFilter, type: TypeFilter): Game[] {
  return games.filter((g) => {
    if (variant === 'maxi' && !g.mode.startsWith('maxi')) return false;
    if (variant === 'yatzy' && !g.mode.startsWith('yatzy')) return false;
    if (type === 'sequential' && !g.mode.endsWith('_sequential')) return false;
    if (type === 'regular' && g.mode.endsWith('_sequential')) return false;
    return true;
  });
}

export function LobbyScreen() {
  const [games, setGames] = useState<Game[]>([]);
  const [creating, setCreating] = useState(false);
  const [mode, setMode] = useState<GameMode>('maxi');
  const [botCount, setBotCount] = useState(0);
  const [variantFilter, setVariantFilter] = useState<VariantFilter>('all');
  const [typeFilter, setTypeFilter] = useState<TypeFilter>('all');
  const [playerNames, refetchPlayerNames] = usePlayerNames();
  const { player } = usePlayer();
  const navigate = useNavigate();
  const errorToast = useErrorToast();

  const fetchGames = useCallback(async () => {
    if (!player) return;
    const { data } = await apiClient.GET('/games', { params: { query: { status: 'lobby' } } });
    setGames(data ?? []);
  }, [player]);

  useEffect(() => {
    if (!player) return;
    const controller = new AbortController();
    apiClient
      .GET('/games', { params: { query: { status: 'lobby' } }, signal: controller.signal })
      .then(({ data }) => setGames(data ?? []));
    return () => controller.abort();
  }, [player]);

  useEventSource('/api/games/lobby/events', fetchGames);

  async function withMutation(title: string, fn: () => Promise<{ error?: unknown }>) {
    const { error } = await fn();
    if (error) {
      errorToast(title);
      return;
    }
    await fetchGames();
  }

  async function handleCreate() {
    if (!player) return;
    setCreating(true);
    try {
      const { error } = await apiClient.POST('/games', {
        body: { creator_id: player.id, mode, bot_count: botCount },
      });
      if (error) throw error;
    } catch {
      errorToast('Failed to create game');
      return;
    } finally {
      setCreating(false);
    }
    refetchPlayerNames();
    await fetchGames();
  }

  async function handleJoin(game: Game) {
    if (!player) return;
    await withMutation('Failed to join game', () =>
      apiClient.POST('/games/{game_id}/join', {
        params: { path: { game_id: game.id } },
        body: { player_id: player.id },
      })
    );
  }

  async function handleDelete(game: Game) {
    await withMutation('Failed to delete game', () =>
      apiClient.DELETE('/games/{game_id}', {
        params: { path: { game_id: game.id } },
      })
    );
  }

  async function handleLeave(game: Game) {
    if (!player) return;
    await withMutation('Failed to leave game', () =>
      apiClient.DELETE('/games/{game_id}/players/{player_id}', {
        params: { path: { game_id: game.id, player_id: player.id } },
      })
    );
  }

  async function handleStart(game: Game) {
    if (!player) return;
    try {
      const { data, error } = await apiClient.POST('/games/{game_id}/start', {
        params: { path: { game_id: game.id } },
        body: { player_id: player.id },
      });
      if (error || !data) throw error ?? new Error('Failed to start game');
      navigate(`/games/${data.id}`);
    } catch {
      errorToast('Failed to start game');
    }
  }

  const visible = applyFilters(games, variantFilter, typeFilter);
  const available = visible.filter((g) => !g.player_ids.includes(player?.id ?? 0));

  return (
    <PageLayout>
      <Card className="px-4 py-3 flex items-center gap-3 flex-wrap">
        <span className="text-[13px] font-semibold text-foreground">Games</span>
        <div className="flex items-center gap-1.5 flex-wrap">
          <div className="flex items-center gap-1">
            {(['all', 'maxi', 'yatzy'] as VariantFilter[]).map((v) => (
              <FilterPill key={v} active={variantFilter === v} onClick={() => setVariantFilter(v)}>
                {v === 'all' ? 'All' : v === 'maxi' ? 'Maxi' : 'Yatzy'}
              </FilterPill>
            ))}
          </div>
          <div className="flex items-center gap-1">
            {(['all', 'regular', 'sequential'] as TypeFilter[]).map((t) => (
              <FilterPill key={t} active={typeFilter === t} onClick={() => setTypeFilter(t)}>
                {t === 'all' ? 'All' : t === 'regular' ? 'Regular' : 'Sequential'}
              </FilterPill>
            ))}
          </div>
        </div>
        <div className="ml-auto">
          <NewGamePanel
            mode={mode}
            botCount={botCount}
            creating={creating}
            onModeChange={setMode}
            onBotCountChange={setBotCount}
            onCreate={handleCreate}
          />
        </div>
      </Card>

      <Card className="px-4 py-3">
        <GameList
          games={visible}
          currentPlayerId={player?.id ?? 0}
          playerNames={playerNames}
          onJoin={handleJoin}
          onDelete={handleDelete}
          onStart={handleStart}
          onLeave={handleLeave}
        />
        <div className="flex items-center justify-between pt-2 mt-1 border-t border-[var(--border)]">
          <span className="text-[11px] text-[var(--text-dim)] uppercase font-bold tracking-[0.08em]">
            Available
          </span>
          <span className="text-[12px] text-[var(--text-muted)]">
            {available.length} {available.length === 1 ? 'game' : 'games'}
          </span>
        </div>
      </Card>
    </PageLayout>
  );
}
