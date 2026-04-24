import { useState } from 'react';
import { Link } from 'react-router-dom';
import { authClient } from '@/auth/authClient';
import { AuthScreenLayout } from '@/components/AuthScreenLayout';
import { useFormSubmit } from '@/hooks/useFormSubmit';

export function ForgotPasswordScreen() {
  const [email, setEmail] = useState('');
  const [sent, setSent] = useState(false);
  const { submitting, error, submit } = useFormSubmit();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    await submit(async () => {
      await authClient.forgotPassword(email);
      setSent(true);
    });
  }

  return (
    <AuthScreenLayout>
      <div className="p-6 flex flex-col gap-4">
        {sent ? (
          <>
            <p className="text-[13px] text-center text-foreground/70 leading-relaxed">
              If an account with that email exists, a password reset link has been sent.
            </p>
            <p className="text-center text-[12px] text-[var(--text-muted)]">
              <Link to="/login" className="text-foreground underline">
                Back to sign in
              </Link>
            </p>
          </>
        ) : (
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div className="flex flex-col gap-1.5">
              <label htmlFor="email" className="text-[12px] font-medium text-[var(--text-muted)]">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
                className="h-9 bg-[var(--surface-2)] border border-[var(--border-2)] rounded-lg px-2.5 text-[13px] text-foreground outline-none transition-colors focus:border-[var(--accent)]"
              />
            </div>
            {error && <p className="text-[12px] text-[var(--red)]">{error}</p>}
            <button
              type="submit"
              disabled={submitting}
              className="h-9 bg-[var(--accent)] text-white border-none rounded-lg text-[13px] font-semibold cursor-pointer transition-all hover:scale-[1.03] hover:shadow-[0_0_18px_rgba(124,158,248,0.35)] active:scale-[0.97] disabled:opacity-50"
            >
              Send reset link
            </button>
            <p className="text-center text-[12px] text-[var(--text-muted)]">
              <Link to="/login" className="text-foreground underline">
                Back to sign in
              </Link>
            </p>
          </form>
        )}
      </div>
    </AuthScreenLayout>
  );
}
