import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { authClient } from '@/auth/authClient';
import { AuthScreenLayout } from '@/components/AuthScreenLayout';
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
        <div className="flex flex-col gap-1.5">
          <label htmlFor="password" className="text-[12px] font-medium text-[var(--text-muted)]">
            New password
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="new-password"
            className="h-9 bg-[var(--surface-2)] border border-[var(--border-2)] rounded-lg px-2.5 text-[13px] text-foreground outline-none transition-colors focus:border-[var(--accent)]"
          />
        </div>
        <div className="flex flex-col gap-1.5">
          <label
            htmlFor="confirm-password"
            className="text-[12px] font-medium text-[var(--text-muted)]"
          >
            Confirm new password
          </label>
          <input
            id="confirm-password"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            autoComplete="new-password"
            className="h-9 bg-[var(--surface-2)] border border-[var(--border-2)] rounded-lg px-2.5 text-[13px] text-foreground outline-none transition-colors focus:border-[var(--accent)]"
          />
        </div>
        {error && <p className="text-[12px] text-[var(--red)]">{error}</p>}
        <button
          type="submit"
          disabled={submitting}
          className="h-9 bg-[var(--accent)] text-white border-none rounded-lg text-[13px] font-semibold cursor-pointer transition-all hover:scale-[1.03] hover:shadow-[0_0_18px_rgba(124,158,248,0.35)] active:scale-[0.97] disabled:opacity-50"
        >
          Reset password
        </button>
      </form>
    </AuthScreenLayout>
  );
}
