import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/AuthContext';
import { usePlayer } from '@/hooks/PlayerContext';
import { useFormSubmit } from '@/hooks/useFormSubmit';

interface Props {
  onCancel?: () => void;
}

export function DeleteAccountSection({ onCancel }: Props) {
  const { deleteAccount } = useAuth();
  const { setPlayer } = usePlayer();
  const navigate = useNavigate();
  const [confirmed, setConfirmed] = useState(false);
  const { submitting: deleting, error, submit } = useFormSubmit();

  async function handleConfirm() {
    await submit(async () => {
      await deleteAccount();
      setPlayer(null);
      navigate('/login');
    });
  }

  if (!confirmed) {
    return (
      <div className="flex flex-col gap-2">
        <p className="text-[12px] text-[var(--text-muted)] leading-relaxed">
          This will permanently delete your account, stats, and game history. This cannot be undone.
        </p>
        <div className="flex justify-end gap-2">
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="h-8 px-3 text-[12px] font-medium text-[var(--text-muted)] bg-none border border-[var(--border-2)] rounded-lg cursor-pointer hover:bg-[var(--surface-2)] hover:text-foreground transition-colors"
            >
              Cancel
            </button>
          )}
          <button
            type="button"
            onClick={() => setConfirmed(true)}
            className="h-8 px-3 text-[12px] font-semibold text-[var(--red)] bg-none border border-[var(--border-2)] rounded-lg cursor-pointer transition-colors hover:bg-[rgba(240,101,96,0.08)] hover:border-transparent"
          >
            Delete account
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-2">
      <p className="text-[12px] text-[var(--red)] font-medium">
        Are you sure? This cannot be undone.
      </p>
      {error && <p className="text-[12px] text-[var(--red)]">{error}</p>}
      <div className="flex justify-end gap-2">
        <button
          type="button"
          onClick={() => setConfirmed(false)}
          disabled={deleting}
          className="h-8 px-3 text-[12px] font-medium text-[var(--text-muted)] bg-none border border-[var(--border-2)] rounded-lg cursor-pointer hover:bg-[var(--surface-2)] hover:text-foreground transition-colors disabled:opacity-50"
        >
          Cancel
        </button>
        <button
          type="button"
          onClick={handleConfirm}
          disabled={deleting}
          className="h-8 px-3 bg-[var(--red)] text-white border-none rounded-lg text-[12px] font-semibold cursor-pointer transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50"
        >
          {deleting ? 'Deleting…' : 'Yes, delete'}
        </button>
      </div>
    </div>
  );
}
