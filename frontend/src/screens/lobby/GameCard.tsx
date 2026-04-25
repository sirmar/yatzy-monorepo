import { useState } from 'react';
import type { components } from '@/api';
import { AvatarStack } from '@/components/Avatar';
import { Button } from '@/components/Button';
import { ModePill } from '@/components/ModePill';

type Game = components['schemas']['Game'];

interface Props {
  game: Game;
  currentPlayerId: number;
  playerNames: Record<number, string>;
  onJoin: (game: Game) => Promise<void>;
  onDelete: (game: Game) => Promise<void>;
  onStart: (game: Game) => Promise<void>;
  onLeave: (game: Game) => Promise<void>;
}

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
  const [confirmDelete, setConfirmDelete] = useState(false);

  return (
    <div className="py-2 flex items-center justify-between gap-4">
      <div className="flex items-center gap-3 min-w-0">
        <div className="w-20 flex-shrink-0">
          <AvatarStack playerIds={game.player_ids} size="md" />
        </div>
        <div className="flex flex-col gap-1 min-w-0">
          <div className="flex items-center gap-1.5">
            <ModePill mode={game.mode} />
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
            <Button type="button" variant="ghost" size="sm" onClick={() => setConfirmDelete(false)}>
              Cancel
            </Button>
            <Button type="button" variant="danger" size="sm" onClick={() => onDelete(game)}>
              Delete
            </Button>
          </>
        ) : isCreator ? (
          <>
            <Button
              type="button"
              variant="danger"
              size="sm"
              aria-label={`Delete game ${game.id}`}
              onClick={() => setConfirmDelete(true)}
            >
              Delete
            </Button>
            <Button
              type="button"
              size="sm"
              aria-label={`Start game ${game.id}`}
              onClick={() => onStart(game)}
            >
              Start
            </Button>
          </>
        ) : hasJoined ? (
          <>
            <span className="text-[12px] text-[var(--text-dim)]">Waiting…</span>
            <Button
              type="button"
              variant="danger"
              size="sm"
              aria-label={`Leave game ${game.id}`}
              onClick={() => onLeave(game)}
            >
              Leave
            </Button>
          </>
        ) : (
          <Button
            type="button"
            size="sm"
            aria-label={`Join game ${game.id}`}
            onClick={() => onJoin(game)}
          >
            Join
          </Button>
        )}
      </div>
    </div>
  );
}
