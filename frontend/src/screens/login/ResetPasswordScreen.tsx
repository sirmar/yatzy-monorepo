import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { authClient } from '@/auth/authClient';
import { AuthScreenLayout } from '@/components/AuthScreenLayout';
import { Button } from '@/components/Button';
import { ErrorMessage } from '@/components/ErrorMessage';
import { FormField } from '@/components/FormField';
import { useFormSubmit } from '@/hooks/useFormSubmit';
import { validatePassword, validatePasswordsMatch } from '@/lib/utils';

export function ResetPasswordScreen() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const navigate = useNavigate();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const { submitting, error, setError, submit } = useFormSubmit();

  if (!token) {
    return (
      <AuthScreenLayout>
        <div className="p-6 flex flex-col gap-3">
          <p className="text-center text-[13px] text-[var(--red)]">
            Invalid or missing reset link.
          </p>
          <p className="text-center text-[12px] text-[var(--text-muted)]">
            <Link to="/forgot-password" className="text-foreground underline">
              Request a new one
            </Link>
          </p>
        </div>
      </AuthScreenLayout>
    );
  }

  const validToken = token as string;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const pwError = validatePassword(password) ?? validatePasswordsMatch(password, confirmPassword);
    if (pwError) {
      setError(pwError);
      return;
    }
    await submit(async () => {
      await authClient.resetPassword(validToken, password);
      navigate('/login');
    });
  }

  return (
    <AuthScreenLayout>
      <form onSubmit={handleSubmit} className="p-6 flex flex-col gap-4">
        <FormField
          id="password"
          label="New password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          autoComplete="new-password"
        />
        <FormField
          id="confirm-password"
          label="Confirm new password"
          type="password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
          autoComplete="new-password"
        />
        <ErrorMessage error={error} />
        <Button type="submit" disabled={submitting}>
          Reset password
        </Button>
      </form>
    </AuthScreenLayout>
  );
}
