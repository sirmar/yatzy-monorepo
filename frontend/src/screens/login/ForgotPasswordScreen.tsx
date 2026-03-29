import { useState } from 'react';
import { Link } from 'react-router-dom';
import { authClient } from '@/auth/authClient';
import { AuthScreenLayout } from '@/components/AuthScreenLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
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
      {sent ? (
        <div className="flex flex-col gap-3">
          <p className="text-center text-gray-300">
            If an account with that email exists, a password reset link has been sent.
          </p>
          <p className="text-center text-sm text-gray-400">
            <Link to="/login" className="text-white underline">
              Back to sign in
            </Link>
          </p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="email" className="text-gray-400">
              Email
            </Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </div>
          {error && <p className="text-red-400 text-sm">{error}</p>}
          <Button type="submit" disabled={submitting}>
            Send reset link
          </Button>
          <p className="text-center text-sm text-gray-400">
            <Link to="/login" className="text-white underline">
              Back to sign in
            </Link>
          </p>
        </form>
      )}
    </AuthScreenLayout>
  );
}
