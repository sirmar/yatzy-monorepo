import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';

interface Props {
  onCreate: () => Promise<void>;
  loading: boolean;
}

export function CreateGameButton({ onCreate, loading }: Props) {
  return (
    <Button
      onClick={onCreate}
      disabled={loading}
      className="gap-2 bg-yellow-500 text-gray-950 font-semibold hover:bg-yellow-400 border-0"
    >
      <Plus className="h-4 w-4" />
      New Game
    </Button>
  );
}
