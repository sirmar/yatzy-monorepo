import type { components } from '@/api';
import { Badge } from '@/components/ui/badge';

type GameMode = components['schemas']['GameMode'];

interface Props {
  mode: GameMode;
}

const LABELS: Record<GameMode, string> = {
  maxi: 'Maxi Yatzy',
  maxi_sequential: 'Maxi Yatzy Sequential',
  yatzy: 'Yatzy',
  yatzy_sequential: 'Yatzy Sequential',
};

export function ModeBadge({ mode }: Props) {
  const isSequential = mode === 'maxi_sequential' || mode === 'yatzy_sequential';
  return (
    <Badge
      className={`text-xs pointer-events-none ${
        isSequential
          ? 'bg-blue-500/20 text-blue-300 border-blue-500/30'
          : 'bg-gray-500/20 text-gray-300 border-gray-500/30'
      }`}
    >
      {LABELS[mode]}
    </Badge>
  );
}
