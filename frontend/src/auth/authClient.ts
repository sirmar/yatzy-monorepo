import { authHttpClient } from './client';
import type { components } from './schema';

export type AuthTokens = components['schemas']['TokenResponse'];
export type AuthUser = components['schemas']['User'];

function extractDetail(error: unknown): string {
  return (error as { detail?: string } | undefined)?.detail ?? 'Request failed';
}

async function throwOnError<T>(promise: Promise<{ data?: T; error?: unknown }>): Promise<T> {
  const { data, error } = await promise;
  if (error) throw new Error(extractDetail(error));
  return data as T;
}

export const authClient = {
  register: (email: string, password: string) =>
    throwOnError(authHttpClient.POST('/register', { body: { email, password } })),

  login: (email: string, password: string) =>
    authHttpClient
      .POST('/login', { body: { email, password } })
      .then(({ data, error, response }) => {
        if (response.status === 403) throw new Error('Email not verified');
        if (error) throw new Error(extractDetail(error));
        return data as import('./schema').components['schemas']['TokenResponse'];
      }),

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

  verifyEmail: (token: string) =>
    throwOnError(authHttpClient.POST('/verify-email', { body: { token } })),

  forgotPassword: (email: string) =>
    throwOnError(authHttpClient.POST('/forgot-password', { body: { email } })),

  resetPassword: (token: string, new_password: string) =>
    authHttpClient
      .POST('/reset-password', { body: { token, new_password } })
      .then(({ error, response }) => {
        if (!response.ok) throw new Error(extractDetail(error));
      }),

  changePassword: (current_password: string, new_password: string, accessToken: string) =>
    authHttpClient
      .PUT('/password', {
        body: { current_password, new_password },
        headers: { Authorization: `Bearer ${accessToken}` },
      })
      .then(({ error, response }) => {
        if (!response.ok) throw new Error(extractDetail(error));
      }),

  deleteAccount: (accessToken: string) =>
    authHttpClient
      .DELETE('/me', { headers: { Authorization: `Bearer ${accessToken}` } })
      .then(({ error, response }) => {
        if (!response.ok) throw new Error(extractDetail(error));
      }),
};
