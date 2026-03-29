import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAuth } from '@/hooks/AuthContext';
import { useFormSubmit } from '@/hooks/useFormSubmit';
import { INPUT_CLASS } from '@/lib/styles';
import { validatePassword, validatePasswordsMatch } from '@/lib/utils';

export function ChangePasswordForm() {
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

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3">
      <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wider">
        Change Password
      </h2>
      <div className="flex flex-col gap-1">
        <label htmlFor="current-password" className="text-sm text-gray-400">
          Current password
        </label>
        <Input
          id="current-password"
          type="password"
          value={currentPassword}
          onChange={(e) => setCurrentPassword(e.target.value)}
          required
          autoComplete="current-password"
          className={INPUT_CLASS}
        />
      </div>
      <div className="flex flex-col gap-1">
        <label htmlFor="new-password" className="text-sm text-gray-400">
          New password
        </label>
        <Input
          id="new-password"
          type="password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          required
          autoComplete="new-password"
          className={INPUT_CLASS}
        />
      </div>
      <div className="flex flex-col gap-1">
        <label htmlFor="confirm-password" className="text-sm text-gray-400">
          Confirm new password
        </label>
        <Input
          id="confirm-password"
          type="password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
          autoComplete="new-password"
          className={INPUT_CLASS}
        />
      </div>
      {error && <p className="text-red-400 text-sm">{error}</p>}
      {success && <p className="text-green-400 text-sm">Password changed successfully.</p>}
      <Button type="submit" className="w-40" disabled={submitting}>
        Change password
      </Button>
    </form>
  );
}
