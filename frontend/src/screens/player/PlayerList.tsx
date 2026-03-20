import type { components } from '@/api';
import { PlayerRow } from './PlayerRow';

type Player = components['schemas']['Player'];

interface Props {
  players: Player[];
  onSelect: (player: Player) => void;
  onUpdate: (player: Player, newName: string) => Promise<void>;
  onDelete: (player: Player) => Promise<void>;
}

export function PlayerList({ players, onSelect, onUpdate, onDelete }: Props) {
  if (players.length === 0) {
    return <p className="text-center text-gray-500 py-4">No players yet</p>;
  }

  return (
    <ul className="flex flex-col gap-2">
      {players.map((player) => (
        <li key={player.id}>
          <PlayerRow player={player} onSelect={onSelect} onUpdate={onUpdate} onDelete={onDelete} />
        </li>
      ))}
    </ul>
  );
}
