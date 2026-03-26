import { authHttpClient } from './client';
import type { components } from './schema';

export type AuthTokens = components['schemas']['TokenResponse'];
export type AuthUser = components['schemas']['User'];

async function throwOnError<T>(promise: Promise<{ data?: T; error?: unknown }>): Promise<T> {
  const { data, error } = await promise;
  if (error) {
    const detail = (error as { detail?: string }).detail;
    throw new Error(detail ?? 'Request failed');
  }
  return data as T;
}

export const authClient = {
  register: (email: string, password: string) =>
    throwOnError(authHttpClient.POST('/register', { body: { email, password } })),

  login: (email: string, password: string) =>
    throwOnError(authHttpClient.POST('/login', { body: { email, password } })),

  refresh: (refresh_token: string) =>
    throwOnError(authHttpClient.POST('/refresh', { body: { refresh_token } })),

  logout: (refresh_token: string) =>
    authHttpClient.POST('/logout', { body: { refresh_token } }).then(() => undefined),

  me: (accessToken: string) =>
    throwOnError(
      authHttpClient.GET('/me', {
        headers: { Authorization: `Bearer ${accessToken}` },
      })
    ),
};
