import type { components } from '@/api';
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
    <div className="bg-[var(--surface)] border border-[var(--border)] rounded-[14px] h-[78px] px-4 flex items-center">
      <div className="flex items-center gap-[14px] w-full">
        <div className="flex items-center gap-[10px] flex-1">
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
          <div className="flex flex-row items-stretch flex-shrink-0 outline outline-[1.5px] outline-[var(--border-2)] rounded-[13px]">
            <button
              type="button"
              onClick={onRoll}
              disabled={!canRoll}
              style={{ transitionTimingFunction: 'cubic-bezier(0.34, 1.56, 0.64, 1)' }}
              className="h-[52px] px-5 rounded-[10px] bg-[var(--accent)] text-white text-[14px] font-bold tracking-[0.02em] border-none cursor-pointer transition-[transform,box-shadow] duration-[180ms] whitespace-nowrap flex-shrink-0 hover:scale-[1.07] hover:shadow-[0_0_28px_rgba(124,158,248,0.45)] hover:z-[1] active:scale-[0.96] active:duration-[70ms] disabled:opacity-35 disabled:cursor-default disabled:pointer-events-none"
            >
              {rollsRemaining === 0 && savedRolls > 0 ? 'Roll saved' : 'Roll'}
            </button>
            <div className="flex items-center">
              <div className="flex flex-col items-center justify-center gap-[2px] px-4">
                <span className="text-[16px] font-bold text-foreground leading-none">
                  {rollsRemaining}
                </span>
                <span className="text-[9px] font-medium uppercase tracking-[0.06em] text-[var(--text-muted)]">
                  Rolls left
                </span>
              </div>
              {showSavedRolls && (
                <>
                  <div className="w-px self-stretch my-[10px] bg-[var(--border-2)]" />
                  <div className="flex flex-col items-center justify-center gap-[2px] px-4">
                    <span className="text-[16px] font-bold text-foreground leading-none">
                      {savedRolls}
                    </span>
                    <span className="text-[9px] font-medium uppercase tracking-[0.06em] text-[var(--text-muted)]">
                      Saved
                    </span>
                  </div>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
