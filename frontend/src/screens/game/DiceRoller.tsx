import type { components } from '@/api';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

type Die = components['schemas']['Die'];

interface Props {
  dice: Die[];
  canRoll: boolean;
  hasRolled: boolean;
  rollsRemaining: number;
  savedRolls: number;
  isMyTurn: boolean;
  onRoll: () => void;
  onToggle: (index: number) => void;
}

export function DiceRoller({
  dice,
  canRoll,
  hasRolled,
  rollsRemaining,
  savedRolls,
  isMyTurn,
  onRoll,
  onToggle,
}: Props) {
  if (!isMyTurn) return null;

  return (
    <div className="flex items-center gap-4">
      <div className="flex gap-2">
        {dice.map((die) => (
          <button
            key={die.index}
            type="button"
            aria-label={`Die ${die.index}`}
            aria-pressed={die.kept}
            disabled={!hasRolled}
            onClick={() => onToggle(die.index)}
            className={cn(
              'h-12 w-12 rounded-lg border-2 flex items-center justify-center text-lg font-bold transition-colors',
              die.kept
                ? 'border-yellow-400 bg-yellow-400/20 text-yellow-300'
                : 'border-gray-600 bg-gray-800 text-white',
              !hasRolled && 'opacity-50 cursor-not-allowed'
            )}
          >
            {die.value ?? '—'}
          </button>
        ))}
      </div>
      <Button onClick={onRoll} disabled={!canRoll}>
        Roll
      </Button>
      <div className="ml-auto text-sm text-gray-300 text-right flex flex-col gap-1">
        <span>Rolls remaining: {rollsRemaining}</span>
        <span>Saved rolls: {savedRolls}</span>
      </div>
    </div>
  );
}
