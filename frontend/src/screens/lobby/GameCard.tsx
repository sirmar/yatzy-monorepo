import { Users } from 'lucide-react';
import type { components } from '@/api';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

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
  const creatorName = playerNames[game.creator_id] ?? `Player ${game.creator_id}`;

  return (
    <Card className="bg-gray-800 border-gray-700">
      <CardContent className="flex items-center justify-between p-4">
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-white">Game #{game.id}</span>
            {isCreator && (
              <Badge className="text-xs bg-yellow-500/20 text-yellow-300 border-yellow-500/30">
                ★ yours
              </Badge>
            )}
          </div>
          <span className="text-xs text-gray-500">Created by {creatorName}</span>
          <span className="flex items-center gap-1 text-sm text-gray-400">
            <Users className="h-3 w-3" />
            {names}
          </span>
        </div>
        <div className="flex items-center gap-2">
          {isCreator ? (
            <>
              <Button
                variant="ghost"
                aria-label={`Delete game ${game.id}`}
                onClick={() => onDelete(game)}
                className="text-gray-500 hover:text-red-400 hover:bg-red-400/10"
              >
                Delete
              </Button>
              <Button aria-label={`Start game ${game.id}`} onClick={() => onStart(game)}>
                Start
              </Button>
            </>
          ) : hasJoined ? (
            <>
              <span className="text-gray-400 text-sm">Waiting...</span>
              <Button
                variant="ghost"
                aria-label={`Leave game ${game.id}`}
                onClick={() => onLeave(game)}
                className="text-gray-500 hover:text-red-400 hover:bg-red-400/10"
              >
                Leave
              </Button>
            </>
          ) : (
            <Button aria-label={`Join game ${game.id}`} onClick={() => onJoin(game)}>
              Join
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
