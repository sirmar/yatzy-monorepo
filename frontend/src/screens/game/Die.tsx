import { useEffect, useRef, useState } from 'react';
import type { components } from '@/api';
import { cn } from '@/lib/utils';

type DieType = components['schemas']['Die'];

const F = false;
const T = true;

const FACES: Record<number, boolean[]> = {
  1: [F, F, F, F, T, F, F, F, F],
  2: [F, F, T, F, F, F, T, F, F],
  3: [F, F, T, F, T, F, T, F, F],
  4: [T, F, T, F, F, F, T, F, T],
  5: [T, F, T, F, T, F, T, F, T],
  6: [T, F, T, T, F, T, T, F, T],
};

const GRID_KEYS = ['tl', 'tm', 'tr', 'ml', 'mm', 'mr', 'bl', 'bm', 'br'];

const ANIMATION_DURATION = 500;
const ANIMATION_INTERVAL = 70;

interface Props {
  die: DieType;
  rollCount: number;
  hasRolled: boolean;
  onToggle: () => void;
}

export function Die({ die, rollCount, hasRolled, onToggle }: Props) {
  const [displayValue, setDisplayValue] = useState<number | null>(die.value ?? null);
  const prevRollCountRef = useRef(rollCount);

  useEffect(() => {
    const prev = prevRollCountRef.current;
    prevRollCountRef.current = rollCount;

    const value = die.value ?? null;
    const didRoll = rollCount !== prev;

    if (!didRoll || value === null || die.kept) {
      setDisplayValue(value);
      return;
    }

    setDisplayValue(Math.ceil(Math.random() * 6));

    let elapsed = 0;
    const timer = setInterval(() => {
      elapsed += ANIMATION_INTERVAL;
      if (elapsed >= ANIMATION_DURATION) {
        clearInterval(timer);
        setDisplayValue(value);
      } else {
        setDisplayValue(Math.ceil(Math.random() * 6));
      }
    }, ANIMATION_INTERVAL);

    return () => clearInterval(timer);
  }, [rollCount, die.value, die.kept]);

  const pips = displayValue !== null ? (FACES[displayValue] ?? []) : null;

  return (
    <button
      type="button"
      aria-label={`Die ${die.index}`}
      aria-pressed={die.kept}
      data-value={die.value ?? ''}
      disabled={!hasRolled}
      onClick={onToggle}
      className={cn(
        'h-14 w-14 rounded-lg border-2 p-1.5 grid grid-cols-3 grid-rows-3 gap-1 transition-colors',
        die.kept
          ? 'border-yellow-400 bg-yellow-400/20 text-yellow-300'
          : 'border-gray-600 bg-gray-800 text-white',
        !hasRolled && 'opacity-50 cursor-not-allowed'
      )}
    >
      {pips?.map((hasPip, i) => (
        <div key={GRID_KEYS[i]} className={cn('rounded-full', hasPip ? 'bg-current' : '')} />
      ))}
    </button>
  );
}
