import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { authClient } from '@/auth/authClient';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/hooks/AuthContext';

export function VerifyEmailScreen() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const navigate = useNavigate();
  const { loginWithTokens } = useAuth();
  const [error, setError] = useState('');
  const attempted = useRef(false);

  // biome-ignore lint/correctness/useExhaustiveDependencies: loginWithTokens and navigate are stable enough; attempted ref prevents re-runs
  useEffect(() => {
    if (attempted.current) return;
    attempted.current = true;
    if (!token) {
      setError('Invalid or missing verification link.');
      return;
    }
    authClient
      .verifyEmail(token)
      .then(async (tokens) => {
        await loginWithTokens(tokens);
        navigate('/');
      })
      .catch(() => {
        setError('This verification link is invalid or has expired.');
      });
  }, [token]);

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center p-4">
      <Card className="w-full max-w-md bg-gray-900 border-gray-800">
        <CardHeader>
          <CardTitle className="text-3xl font-bold text-center text-white">Yatzy</CardTitle>
        </CardHeader>
        <CardContent>
          {error ? (
            <div className="flex flex-col gap-3">
              <p className="text-center text-red-400">{error}</p>
              <p className="text-center text-sm text-gray-400">
                <Link to="/login" className="text-white underline">
                  Back to sign in
                </Link>
              </p>
            </div>
          ) : (
            <p className="text-center text-gray-300">Verifying your email…</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
