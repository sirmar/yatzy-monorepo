import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useState } from 'react';

interface Props {
  onCreated: (name: string) => Promise<void>;
}

export function CreatePlayerForm({ onCreated }: Props) {
  const [name, setName] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    setLoading(true);
    setError(null);
    try {
      await onCreated(name.trim());
      setName('');
    } catch {
      setError('Failed to create player. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3">
      <div className="flex gap-2">
        <Input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Enter your name"
          disabled={loading}
          className="border-gray-600 bg-gray-800 text-white placeholder:text-gray-500 hover:border-yellow-400/50 focus-visible:ring-yellow-400/50"
        />
        <Button
          type="submit"
          variant="outline"
          disabled={loading || !name.trim()}
          className="bg-gray-800 text-white border-gray-600 transition-colors hover:!bg-yellow-400/10 hover:!text-yellow-300 hover:border-yellow-400/50"
        >
          Create
        </Button>
      </div>
      {error && <p className="text-sm text-red-400">{error}</p>}
    </form>
  );
}
