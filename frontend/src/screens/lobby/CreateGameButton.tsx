import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface Props {
  onCreate: () => Promise<void>;
  loading: boolean;
}

export function CreateGameButton({ onCreate, loading }: Props) {
  return (
    <Button onClick={onCreate} disabled={loading} className="font-semibold">
      <Plus className="h-4 w-4" />
      New Game
    </Button>
  );
}
