import { useState } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { AuthScreenLayout } from '@/components/AuthScreenLayout';
import { useAuth } from '@/hooks/AuthContext';
import { useFormSubmit } from '@/hooks/useFormSubmit';
import { validatePassword } from '@/lib/utils';

function AuthLink({ children, onClick }: { children: React.ReactNode; onClick: () => void }) {
  return (
    <button
      type="button"
      className="text-foreground underline cursor-pointer bg-none border-none font-inherit"
      onClick={onClick}
    >
      {children}
    </button>
  );
}

export function LoginScreen() {
  const { user, isLoading, login, register } = useAuth();
  const navigate = useNavigate();
  const { submitting, error, setError, submit } = useFormSubmit();
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [registered, setRegistered] = useState(false);
  const [emailNotVerified, setEmailNotVerified] = useState(false);

  if (!isLoading && user) return <Navigate to="/" replace />;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const pwError = validatePassword(password);
    if (pwError) {
      setError(pwError);
      return;
    }
    setEmailNotVerified(false);
    await submit(
      async () => {
        if (mode === 'login') {
          await login(email, password);
          navigate('/');
        } else {
          await register(email, password);
          setRegistered(true);
        }
      },
      (err) => {
        if (err.message === 'Email not verified') {
          setEmailNotVerified(true);
        } else {
          setError(err.message);
        }
      }
    );
  }

  if (registered) {
    return (
      <AuthScreenLayout>
        <div className="p-7 flex flex-col gap-4">
          <p className="text-[13px] text-center text-foreground/70 leading-relaxed">
            Check your email to verify your account, then{' '}
            <AuthLink
              onClick={() => {
                setRegistered(false);
                setMode('login');
              }}
            >
              sign in
            </AuthLink>
            .
          </p>
          <p className="text-center text-[12px] text-[var(--text-muted)]">
            Wrong email?{' '}
            <AuthLink
              onClick={() => {
                setRegistered(false);
                setMode('register');
                setEmail('');
                setPassword('');
              }}
            >
              Register again
            </AuthLink>
          </p>
        </div>
      </AuthScreenLayout>
    );
  }

  return (
    <AuthScreenLayout>
      {/* Tabs */}
      <div className="flex border-b border-[var(--border-2)]">
        {(['login', 'register'] as const).map((tab) => (
          <button
            key={tab}
            type="button"
            onClick={() => {
              setMode(tab);
              setError('');
            }}
            className={[
              'flex-1 py-2 text-[12px] font-semibold border-b-2 -mb-px transition-colors duration-150',
              mode === tab
                ? 'text-[var(--accent)] border-[var(--accent)]'
                : 'text-[var(--text-muted)] border-transparent',
            ].join(' ')}
          >
            {tab === 'login' ? 'Sign in' : 'Register'}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="p-6 flex flex-col gap-4">
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
        <div className="flex flex-col gap-1.5">
          <label htmlFor="password" className="text-[12px] font-medium text-[var(--text-muted)]">
            Password
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
            className="h-9 bg-[var(--surface-2)] border border-[var(--border-2)] rounded-lg px-2.5 text-[13px] text-foreground outline-none transition-colors focus:border-[var(--accent)]"
          />
        </div>

        <div className="h-9 text-[12px] leading-relaxed">
          {error && <span className="text-[var(--red)]">{error}</span>}
          {emailNotVerified && (
            <span className="text-[var(--amber)]">
              Email not verified. Check your inbox, or{' '}
              <AuthLink
                onClick={() => {
                  setEmailNotVerified(false);
                  setMode('register');
                }}
              >
                re-register
              </AuthLink>{' '}
              to get a new link.
            </span>
          )}
        </div>

        <button
          type="submit"
          disabled={submitting}
          className="h-9 bg-[var(--accent)] text-white border-none rounded-lg text-[13px] font-semibold cursor-pointer transition-all hover:scale-[1.03] hover:shadow-[0_0_18px_rgba(124,158,248,0.35)] active:scale-[0.97] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {mode === 'login' ? 'Sign in' : 'Create account'}
        </button>

        {mode === 'login' && (
          <p className="text-center text-[12px] text-[var(--text-muted)]">
            <Link to="/forgot-password" className="text-foreground underline">
              Forgot password?
            </Link>
          </p>
        )}
      </form>
    </AuthScreenLayout>
  );
}
