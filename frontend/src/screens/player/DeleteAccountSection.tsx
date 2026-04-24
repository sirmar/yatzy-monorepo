import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/Button';
import { ErrorMessage } from '@/components/ErrorMessage';
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
            <Button type="button" variant="ghost" size="sm" onClick={onCancel}>
              Cancel
            </Button>
          )}
          <Button type="button" variant="danger" size="sm" onClick={() => setConfirmed(true)}>
            Delete account
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-2">
      <p className="text-[12px] text-[var(--red)] font-medium">
        Are you sure? This cannot be undone.
      </p>
      <ErrorMessage error={error} />
      <div className="flex justify-end gap-2">
        <Button
          type="button"
          variant="ghost"
          size="sm"
          disabled={deleting}
          onClick={() => setConfirmed(false)}
        >
          Cancel
        </Button>
        <Button
          type="button"
          size="sm"
          disabled={deleting}
          onClick={handleConfirm}
          className="bg-[var(--red)] hover:shadow-[0_0_18px_rgba(240,101,96,0.35)]"
        >
          {deleting ? 'Deleting…' : 'Yes, delete'}
        </Button>
      </div>
    </div>
  );
}
