import { useState } from 'react';
import { useAuth } from '@/hooks/AuthContext';
import { useFormSubmit } from '@/hooks/useFormSubmit';
import { validatePassword, validatePasswordsMatch } from '@/lib/utils';

interface Props {
  onDone?: () => void;
}

const inputCls =
  'h-9 bg-[var(--surface)] border border-[var(--border-2)] rounded-lg px-2.5 text-[13px] text-foreground outline-none transition-colors focus:border-[var(--accent)] w-full';

export function ChangePasswordForm({ onDone }: Props) {
  const { changePassword } = useAuth();
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [success, setSuccess] = useState(false);
  const { submitting, error, setError, submit } = useFormSubmit();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const pwError =
      validatePassword(newPassword) ?? validatePasswordsMatch(newPassword, confirmPassword);
    if (pwError) {
      setError(pwError);
      return;
    }
    await submit(async () => {
      await changePassword(currentPassword, newPassword);
      setSuccess(true);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    });
  }

  if (success) {
    return <p className="text-[12px] text-[var(--green)]">Password changed successfully.</p>;
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-2.5">
      <div className="flex flex-col gap-1.5">
        <label
          htmlFor="current-password"
          className="text-[11px] font-medium text-[var(--text-muted)]"
        >
          Current password
        </label>
        <input
          id="current-password"
          type="password"
          value={currentPassword}
          onChange={(e) => setCurrentPassword(e.target.value)}
          required
          autoComplete="current-password"
          className={inputCls}
        />
      </div>
      <div className="flex flex-col gap-1.5">
        <label htmlFor="new-password" className="text-[11px] font-medium text-[var(--text-muted)]">
          New password
        </label>
        <input
          id="new-password"
          type="password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          required
          autoComplete="new-password"
          className={inputCls}
        />
      </div>
      <div className="flex flex-col gap-1.5">
        <label
          htmlFor="confirm-new-password"
          className="text-[11px] font-medium text-[var(--text-muted)]"
        >
          Confirm new password
        </label>
        <input
          id="confirm-new-password"
          type="password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
          autoComplete="new-password"
          className={inputCls}
        />
      </div>
      {error && <p className="text-[12px] text-[var(--red)]">{error}</p>}
      <div className="flex justify-end gap-2">
        {onDone && (
          <button
            type="button"
            onClick={onDone}
            className="h-8 px-3 text-[12px] font-medium text-[var(--text-muted)] bg-none border border-[var(--border-2)] rounded-lg cursor-pointer hover:bg-[var(--surface-2)] hover:text-foreground transition-colors"
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          disabled={submitting}
          className="h-8 px-3 bg-[var(--accent)] text-white border-none rounded-lg text-[12px] font-semibold cursor-pointer transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50"
        >
          Update password
        </button>
      </div>
    </form>
  );
}
