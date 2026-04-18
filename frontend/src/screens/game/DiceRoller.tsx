import type { components } from '@/api';
import { Button } from '@/components/ui/button';
import { Die } from './Die';

type DieType = components['schemas']['Die'];

interface Props {
  dice: DieType[];
  rollCount: number;
  canRoll: boolean;
  hasRolled: boolean;
  rollsRemaining: number;
  savedRolls: number;
  showSavedRolls: boolean;
  isMyTurn: boolean;
  onRoll: () => void;
  onToggle: (index: number) => void;
}

export function DiceRoller({
  dice,
  rollCount,
  canRoll,
  hasRolled,
  rollsRemaining,
  savedRolls,
  showSavedRolls,
  isMyTurn,
  onRoll,
  onToggle,
}: Props) {
  if (dice.length === 0) return null;

  return (
    <div className="flex items-center gap-4">
      <div className="flex gap-2">
        {dice.map((die) => (
          <Die
            key={die.index}
            die={die}
            rollCount={rollCount}
            hasRolled={hasRolled}
            onToggle={() => onToggle(die.index)}
          />
        ))}
      </div>
      {isMyTurn && (
        <>
          <Button onClick={onRoll} disabled={!canRoll} style={{ minWidth: '7rem' }}>
            {rollsRemaining === 0 ? 'Roll saved' : 'Roll'}
          </Button>
          <div className="ml-auto text-sm text-gray-300 text-right flex flex-col gap-1">
            <span>Rolls remaining: {rollsRemaining}</span>
            {showSavedRolls && <span>Saved rolls: {savedRolls}</span>}
          </div>
        </>
      )}
    </div>
  );
}
