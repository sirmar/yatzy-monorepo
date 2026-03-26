import type { components } from '@/api';
import { Badge } from '@/components/ui/badge';

type GameMode = components['schemas']['GameMode'];

interface Props {
  mode: GameMode;
}

export function ModeBadge({ mode }: Props) {
  if (mode === 'sequential') {
    return (
      <Badge className="text-xs bg-blue-500/20 text-blue-300 border-blue-500/30 pointer-events-none">
        Sequential
      </Badge>
    );
  }
  return (
    <Badge className="text-xs bg-gray-500/20 text-gray-300 border-gray-500/30 pointer-events-none">
      Standard
    </Badge>
  );
}
