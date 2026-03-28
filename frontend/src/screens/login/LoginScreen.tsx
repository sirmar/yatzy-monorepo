import { useState } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useAuth } from '@/hooks/AuthContext';

export function LoginScreen() {
  const { user, isLoading, login, register } = useAuth();
  const navigate = useNavigate();
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [registered, setRegistered] = useState(false);
  const [emailNotVerified, setEmailNotVerified] = useState(false);

  if (!isLoading && user) return <Navigate to="/" replace />;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }
    setError('');
    setEmailNotVerified(false);
    setSubmitting(true);
    try {
      if (mode === 'login') {
        await login(email, password);
        navigate('/');
      } else {
        await register(email, password);
        setRegistered(true);
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Something went wrong';
      if (msg === 'Email not verified') {
        setEmailNotVerified(true);
      } else {
        setError(msg);
      }
    } finally {
      setSubmitting(false);
    }
  }

  if (registered) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center p-4">
        <Card className="w-full max-w-md bg-gray-900 border-gray-800">
          <CardHeader>
            <CardTitle className="text-3xl font-bold text-center text-white">Yatzy</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            <p className="text-center text-gray-300">
              Check your email to verify your account, then{' '}
              <button
                type="button"
                className="text-white underline"
                onClick={() => {
                  setRegistered(false);
                  setMode('login');
                }}
              >
                sign in
              </button>
              .
            </p>
            <p className="text-center text-sm text-gray-400">
              Wrong email?{' '}
              <button
                type="button"
                className="text-white underline"
                onClick={() => {
                  setRegistered(false);
                  setMode('register');
                  setEmail('');
                  setPassword('');
                }}
              >
                Register again
              </button>
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center p-4">
      <Card className="w-full max-w-md bg-gray-900 border-gray-800">
        <CardHeader>
          <CardTitle className="text-3xl font-bold text-center text-white">Yatzy</CardTitle>
        </CardHeader>
        <CardContent>
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
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="password" className="text-gray-400">
                Password
              </Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              />
            </div>
            {error && <p className="text-red-400 text-sm">{error}</p>}
            {emailNotVerified && (
              <p className="text-yellow-400 text-sm">
                Email not verified. Check your inbox, or{' '}
                <button
                  type="button"
                  className="underline"
                  onClick={() => {
                    setEmailNotVerified(false);
                    setMode('register');
                  }}
                >
                  re-register
                </button>{' '}
                to get a new link.
              </p>
            )}
            <Button type="submit" disabled={submitting}>
              {mode === 'login' ? 'Sign in' : 'Create account'}
            </Button>
          </form>
          {mode === 'login' && (
            <p className="mt-2 text-center text-sm text-gray-400">
              <Link to="/forgot-password" className="text-white underline">
                Forgot password?
              </Link>
            </p>
          )}
          <p className="mt-4 text-center text-sm text-gray-400">
            {mode === 'login' ? (
              <>
                No account?{' '}
                <button
                  type="button"
                  className="text-white underline"
                  onClick={() => {
                    setMode('register');
                    setError('');
                  }}
                >
                  Register
                </button>
              </>
            ) : (
              <>
                Already have an account?{' '}
                <button
                  type="button"
                  className="text-white underline"
                  onClick={() => {
                    setMode('login');
                    setError('');
                  }}
                >
                  Sign in
                </button>
              </>
            )}
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
