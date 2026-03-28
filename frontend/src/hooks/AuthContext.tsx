import { createContext, useContext, useEffect, useRef, useState } from 'react';
import { setAuthToken } from '@/api/client';
import { type AuthUser, authClient } from '@/auth/authClient';

interface AuthContextValue {
  user: AuthUser | null;
  accessToken: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  loginWithTokens: (tokens: { access_token: string; refresh_token: string }) => Promise<void>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
  deleteAccount: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const REFRESH_TOKEN_KEY = 'yatzy_refresh_token';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const refreshAttempted = useRef(false);

  async function applyTokens(tokens: { access_token: string; refresh_token: string }) {
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
    setAccessToken(tokens.access_token);
    setAuthToken(tokens.access_token);
    const me = await authClient.me(tokens.access_token);
    setUser(me);
  }

  // biome-ignore lint/correctness/useExhaustiveDependencies: applyTokens uses only stable state setters
  useEffect(() => {
    if (refreshAttempted.current) return;
    refreshAttempted.current = true;
    const storedToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    if (!storedToken) {
      setIsLoading(false);
      return;
    }
    authClient
      .refresh(storedToken)
      .then(applyTokens)
      .catch(() => {
        localStorage.removeItem(REFRESH_TOKEN_KEY);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  async function login(email: string, password: string) {
    await applyTokens(await authClient.login(email, password));
  }

  async function register(email: string, password: string) {
    await authClient.register(email, password);
  }

  async function logout() {
    const storedToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    if (storedToken) {
      await authClient.logout(storedToken).catch(() => {});
    }
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    setAccessToken(null);
    setAuthToken(null);
    setUser(null);
  }

  async function loginWithTokens(tokens: { access_token: string; refresh_token: string }) {
    await applyTokens(tokens);
  }

  async function changePassword(currentPassword: string, newPassword: string) {
    if (!accessToken) throw new Error('Not authenticated');
    await authClient.changePassword(currentPassword, newPassword, accessToken);
  }

  async function deleteAccount() {
    if (!accessToken) throw new Error('Not authenticated');
    await authClient.deleteAccount(accessToken);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    setAccessToken(null);
    setAuthToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        accessToken,
        isLoading,
        login,
        register,
        logout,
        loginWithTokens,
        changePassword,
        deleteAccount,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
