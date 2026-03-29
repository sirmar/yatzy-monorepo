import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { authClient } from '@/auth/authClient';
import { AuthScreenLayout } from '@/components/AuthScreenLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
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
        <p className="text-center text-red-400">Invalid or missing reset link.</p>
        <p className="mt-3 text-center text-sm text-gray-400">
          <Link to="/forgot-password" className="text-white underline">
            Request a new one
          </Link>
        </p>
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
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="password" className="text-gray-400">
            New password
          </Label>
          <Input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="new-password"
          />
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="confirm-password" className="text-gray-400">
            Confirm new password
          </Label>
          <Input
            id="confirm-password"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            autoComplete="new-password"
          />
        </div>
        {error && <p className="text-red-400 text-sm">{error}</p>}
        <Button type="submit" disabled={submitting}>
          Reset password
        </Button>
      </form>
    </AuthScreenLayout>
  );
}
