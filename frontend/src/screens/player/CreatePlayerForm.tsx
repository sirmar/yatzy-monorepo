import { useState } from 'react';
import { Button } from '@/components/Button';
import { ErrorMessage } from '@/components/ErrorMessage';
import { FormField } from '@/components/FormField';
import { useFormSubmit } from '@/hooks/useFormSubmit';

interface Props {
  onCreated: (name: string) => Promise<void>;
}

export function CreatePlayerForm({ onCreated }: Props) {
  const [name, setName] = useState('');
  const { submitting, error, submit } = useFormSubmit();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    await submit(() => onCreated(name.trim()));
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3">
      <FormField
        id="display-name"
        label="Display name"
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="e.g. Alice"
        maxLength={32}
        required
        autoComplete="nickname"
        hint="Letters, numbers, spaces, _ and - only."
      />
      <ErrorMessage error={error} />
      <Button type="submit" disabled={submitting || !name.trim()}>
        Continue
      </Button>
    </form>
  );
}
