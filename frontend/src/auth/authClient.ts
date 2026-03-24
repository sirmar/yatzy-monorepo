const AUTH_BASE = '/auth';

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface AuthUser {
  id: string;
  email: string;
  created_at: string;
}

async function request<T>(path: string, options: RequestInit): Promise<T> {
  const res = await fetch(`${AUTH_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error((body as { detail?: string }).detail ?? `${res.status} ${res.statusText}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const authClient = {
  register: (email: string, password: string) =>
    request<AuthTokens>('/register', { method: 'POST', body: JSON.stringify({ email, password }) }),

  login: (email: string, password: string) =>
    request<AuthTokens>('/login', { method: 'POST', body: JSON.stringify({ email, password }) }),

  refresh: (refreshToken: string) =>
    request<AuthTokens>('/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    }),

  logout: (refreshToken: string) =>
    request<void>('/logout', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    }),

  me: (accessToken: string) =>
    request<AuthUser>('/me', {
      method: 'GET',
      headers: { Authorization: `Bearer ${accessToken}` },
    }),
};
