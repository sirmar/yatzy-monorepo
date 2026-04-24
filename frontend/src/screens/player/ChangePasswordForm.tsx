import { useState } from 'react';
import { Button } from '@/components/Button';
import { ErrorMessage } from '@/components/ErrorMessage';
import { FormField } from '@/components/FormField';
import { useAuth } from '@/hooks/AuthContext';
import { useFormSubmit } from '@/hooks/useFormSubmit';
import { validatePassword, validatePasswordsMatch } from '@/lib/utils';

interface Props {
  onDone?: () => void;
}

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
      <FormField
        id="current-password"
        label="Current password"
        type="password"
        value={currentPassword}
        onChange={(e) => setCurrentPassword(e.target.value)}
        required
        autoComplete="current-password"
        inputClassName="h-9 bg-[var(--surface)] border border-[var(--border-2)] rounded-lg px-2.5 text-[13px] text-foreground outline-none transition-colors focus:border-[var(--accent)] w-full"
      />
      <FormField
        id="new-password"
        label="New password"
        type="password"
        value={newPassword}
        onChange={(e) => setNewPassword(e.target.value)}
        required
        autoComplete="new-password"
        inputClassName="h-9 bg-[var(--surface)] border border-[var(--border-2)] rounded-lg px-2.5 text-[13px] text-foreground outline-none transition-colors focus:border-[var(--accent)] w-full"
      />
      <FormField
        id="confirm-new-password"
        label="Confirm new password"
        type="password"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
        required
        autoComplete="new-password"
        inputClassName="h-9 bg-[var(--surface)] border border-[var(--border-2)] rounded-lg px-2.5 text-[13px] text-foreground outline-none transition-colors focus:border-[var(--accent)] w-full"
      />
      <ErrorMessage error={error} />
      <div className="flex justify-end gap-2">
        {onDone && (
          <Button type="button" variant="ghost" size="sm" onClick={onDone}>
            Cancel
          </Button>
        )}
        <Button type="submit" size="sm" disabled={submitting}>
          Update password
        </Button>
      </div>
    </form>
  );
}
