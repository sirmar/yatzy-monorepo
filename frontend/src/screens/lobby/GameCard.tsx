import { useState } from 'react';
import type { components } from '@/api';
import { AvatarStack } from '@/components/Avatar';

type Game = components['schemas']['Game'];

const MODE_LABELS: Record<string, string> = {
  maxi: 'Maxi Yatzy',
  maxi_sequential: 'Maxi Sequential',
  yatzy: 'Yatzy',
  yatzy_sequential: 'Yatzy Sequential',
};

interface Props {
  game: Game;
  currentPlayerId: number;
  playerNames: Record<number, string>;
  onJoin: (game: Game) => Promise<void>;
  onDelete: (game: Game) => Promise<void>;
  onStart: (game: Game) => Promise<void>;
  onLeave: (game: Game) => Promise<void>;
}

const btnPrimary =
  'h-[30px] px-3 bg-[var(--accent)] text-white border-none rounded-[7px] text-[12px] font-semibold cursor-pointer transition-all hover:scale-[1.04] hover:shadow-[0_0_14px_rgba(124,158,248,0.35)] active:scale-[0.97]';
const btnGhost =
  'h-[30px] px-3 bg-none border border-[var(--border-2)] rounded-[7px] text-[12px] font-medium text-[var(--text-muted)] cursor-pointer transition-colors hover:bg-[var(--surface-2)] hover:text-foreground hover:border-white/20';
const btnDanger =
  'h-[30px] px-3 bg-none border border-[var(--border-2)] rounded-[7px] text-[12px] font-medium text-[var(--text-muted)] cursor-pointer transition-colors hover:bg-[rgba(240,101,96,0.08)] hover:text-[var(--red)] hover:border-transparent';

export function GameCard({
  game,
  currentPlayerId,
  playerNames,
  onJoin,
  onDelete,
  onStart,
  onLeave,
}: Props) {
  const isCreator = game.creator_id === currentPlayerId;
  const hasJoined = game.player_ids.includes(currentPlayerId);
  const names = game.player_ids.map((id) => playerNames[id] ?? `Player ${id}`).join(', ');
  const avatarNames = game.player_ids.map((id) => playerNames[id] ?? String(id));
  const [confirmDelete, setConfirmDelete] = useState(false);

  return (
    <div className="py-2 flex items-center justify-between gap-4">
      <div className="flex items-center gap-3 min-w-0">
        <div className="w-20 flex-shrink-0">
          <AvatarStack names={avatarNames} size="md" />
        </div>
        <div className="flex flex-col gap-1 min-w-0">
          <div className="flex items-center gap-1.5">
            <span className="text-[11px] font-semibold uppercase tracking-[0.06em] border border-[var(--border-2)] bg-[var(--surface-2)] text-[var(--text-muted)] rounded-full px-2 py-0.5">
              {MODE_LABELS[game.mode] ?? game.mode}
            </span>
            {isCreator && (
              <span className="text-[10px] font-semibold px-[7px] py-0.5 rounded-full bg-[rgba(240,180,41,0.15)] border border-[rgba(240,180,41,0.3)] text-[var(--amber)]">
                ★ yours
              </span>
            )}
          </div>
          <span className="text-[12px] text-[var(--text-muted)] truncate">{names}</span>
        </div>
      </div>

      <div className="flex items-center gap-2 flex-shrink-0">
        {confirmDelete ? (
          <>
            <span className="text-[12px] text-[var(--text-dim)]">Sure?</span>
            <button type="button" className={btnGhost} onClick={() => setConfirmDelete(false)}>
              Cancel
            </button>
            <button type="button" className={btnDanger} onClick={() => onDelete(game)}>
              Delete
            </button>
          </>
        ) : isCreator ? (
          <>
            <button
              type="button"
              className={btnDanger}
              aria-label={`Delete game ${game.id}`}
              onClick={() => setConfirmDelete(true)}
            >
              Delete
            </button>
            <button
              type="button"
              className={btnPrimary}
              aria-label={`Start game ${game.id}`}
              onClick={() => onStart(game)}
            >
              Start
            </button>
          </>
        ) : hasJoined ? (
          <>
            <span className="text-[12px] text-[var(--text-dim)]">Waiting…</span>
            <button
              type="button"
              className={btnDanger}
              aria-label={`Leave game ${game.id}`}
              onClick={() => onLeave(game)}
            >
              Leave
            </button>
          </>
        ) : (
          <button
            type="button"
            className={btnPrimary}
            aria-label={`Join game ${game.id}`}
            onClick={() => onJoin(game)}
          >
            Join
          </button>
        )}
      </div>
    </div>
  );
}
