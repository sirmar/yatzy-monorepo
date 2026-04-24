import { useState } from 'react';
import { Link } from 'react-router-dom';
import { authClient } from '@/auth/authClient';
import { AuthScreenLayout } from '@/components/AuthScreenLayout';
import { Button } from '@/components/Button';
import { ErrorMessage } from '@/components/ErrorMessage';
import { FormField } from '@/components/FormField';
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
            <FormField
              id="email"
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
            <ErrorMessage error={error} />
            <Button type="submit" disabled={submitting}>
              Send reset link
            </Button>
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
