import { useState } from 'react';
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
      <div className="flex flex-col gap-1.5">
        <label htmlFor="display-name" className="text-[12px] font-medium text-[var(--text-muted)]">
          Display name
        </label>
        <input
          id="display-name"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g. Alice"
          maxLength={32}
          required
          autoComplete="nickname"
          className="h-9 bg-[var(--surface-2)] border border-[var(--border-2)] rounded-lg px-2.5 text-[13px] text-foreground outline-none transition-colors focus:border-[var(--accent)]"
        />
        <div className="text-[11px] text-[var(--text-dim)]">
          Letters, numbers, spaces, _ and - only.
        </div>
      </div>
      {error && <p className="text-[12px] text-[var(--red)]">{error}</p>}
      <button
        type="submit"
        disabled={submitting || !name.trim()}
        className="h-9 bg-[var(--accent)] text-white border-none rounded-lg text-[13px] font-semibold cursor-pointer transition-all hover:scale-[1.03] hover:shadow-[0_0_18px_rgba(124,158,248,0.35)] active:scale-[0.97] disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Continue
      </button>
    </form>
  );
}
