import type { components } from '@/api';
import { GameCard } from './GameCard';

type Game = components['schemas']['Game'];

interface Props {
  games: Game[];
  currentPlayerId: number;
  playerNames: Record<number, string>;
  onJoin: (game: Game) => Promise<void>;
  onDelete: (game: Game) => Promise<void>;
  onStart: (game: Game) => Promise<void>;
  onLeave: (game: Game) => Promise<void>;
}

export function GameList({
  games,
  currentPlayerId,
  playerNames,
  onJoin,
  onDelete,
  onStart,
  onLeave,
}: Props) {
  if (games.length === 0) {
    return (
      <p className="text-center text-gray-500 py-8">No open games — create one to get started!</p>
    );
  }

  return (
    <ul className="flex flex-col gap-3">
      {games.map((game) => (
        <li key={game.id}>
          <GameCard
            game={game}
            currentPlayerId={currentPlayerId}
            playerNames={playerNames}
            onJoin={onJoin}
            onDelete={onDelete}
            onStart={onStart}
            onLeave={onLeave}
          />
        </li>
      ))}
    </ul>
  );
}
