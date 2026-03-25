import { Check, Pencil, Trash2, X } from 'lucide-react';
import { useState } from 'react';
import type { components } from '@/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

type Player = components['schemas']['Player'];

interface Props {
  player: Player;
  isOwner?: boolean;
  onUpdate: (player: Player, newName: string) => Promise<void>;
  onDelete: (player: Player) => Promise<void>;
}

export function PlayerRow({ player, isOwner, onUpdate, onDelete }: Props) {
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState(player.name);

  async function handleSave() {
    if (!name.trim() || name === player.name) {
      setEditing(false);
      setName(player.name);
      return;
    }
    try {
      await onUpdate(player, name.trim());
      setEditing(false);
    } catch {
      // parent already toasted; keep editor open
    }
  }

  function handleCancel() {
    setName(player.name);
    setEditing(false);
  }

  if (editing) {
    return (
      <div className="flex gap-2">
        <Input
          aria-label="Edit name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') handleSave();
            if (e.key === 'Escape') handleCancel();
          }}
          className="border-gray-600 bg-gray-800 text-white placeholder:text-gray-500 focus-visible:ring-yellow-400/50"
          autoFocus
        />
        <Button
          size="icon"
          variant="outline"
          aria-label="Save"
          onClick={handleSave}
          className="bg-gray-800 border-gray-600 text-white hover:!bg-yellow-400/10 hover:!text-yellow-300 hover:border-yellow-400/50 shrink-0"
        >
          <Check />
        </Button>
        <Button
          size="icon"
          variant="outline"
          aria-label="Cancel"
          onClick={handleCancel}
          className="bg-gray-800 border-gray-600 text-white hover:!bg-red-400/10 hover:!text-red-300 hover:border-red-400/50 shrink-0"
        >
          <X />
        </Button>
      </div>
    );
  }

  return (
    <div className="group flex gap-2">
      <div className="flex-1 flex items-center px-4 py-2 rounded-md bg-gray-800 text-white border border-gray-600 text-sm font-medium">
        {player.name}
      </div>
      {isOwner && (
        <>
          <Button
            size="icon"
            variant="outline"
            aria-label={`Edit ${player.name}`}
            onClick={() => setEditing(true)}
            className="bg-gray-800 border-gray-600 text-gray-500 opacity-0 group-hover:opacity-100 transition-opacity hover:!bg-yellow-400/10 hover:!text-yellow-300 hover:border-yellow-400/50 shrink-0"
          >
            <Pencil />
          </Button>
          <Button
            size="icon"
            variant="outline"
            aria-label={`Delete ${player.name}`}
            onClick={() => onDelete(player)}
            className="bg-gray-800 border-gray-600 text-gray-500 opacity-0 group-hover:opacity-100 transition-opacity hover:!bg-red-400/10 hover:!text-red-300 hover:border-red-400/50 shrink-0"
          >
            <Trash2 />
          </Button>
        </>
      )}
    </div>
  );
}
