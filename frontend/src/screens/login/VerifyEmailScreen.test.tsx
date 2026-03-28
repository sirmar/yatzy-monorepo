import { screen } from '@testing-library/react';
import { HttpResponse, http } from 'msw';
import { setupServer } from 'msw/node';
import { afterAll, afterEach, beforeAll, describe, expect, it, vi } from 'vitest';
import { renderWithProviders } from '@/test/helpers';
import { VerifyEmailScreen } from './VerifyEmailScreen';

const VERIFY_EMAIL_URL = 'http://localhost/auth/verify-email';
const REFRESH_URL = 'http://localhost/auth/refresh';
const ME_URL = 'http://localhost/auth/me';

const mockNavigate = vi.hoisted(() => vi.fn());
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return { ...actual, useNavigate: () => mockNavigate };
});

const mockTokens = {
  access_token: 'access-tok',
  refresh_token: 'refresh-tok',
  token_type: 'bearer',
};
const mockUser = {
  id: '123',
  email: 'user@example.com',
  email_verified: true,
  created_at: '2026-01-01',
};

const server = setupServer(http.post(REFRESH_URL, () => HttpResponse.json({}, { status: 401 })));
beforeAll(() => server.listen());
afterEach(() => {
  server.resetHandlers();
  mockNavigate.mockReset();
  window.history.pushState({}, '', '/');
});
afterAll(() => server.close());

describe('VerifyEmailScreen', () => {
  it('calls verify-email on mount and redirects to / on success', async () => {
    givenVerifySucceeds();
    whenRenderedWithToken('valid-token');
    await screen.findByText(/verifying/i);
    await vi.waitFor(() => expect(mockNavigate).toHaveBeenCalledWith('/'));
  });

  it('shows error on invalid or expired token', async () => {
    givenVerifyFails();
    whenRenderedWithToken('bad-token');
    await screen.findByText(/invalid or has expired/i);
  });

  it('shows error when token query param is missing', async () => {
    whenRenderedWithoutToken();
    await screen.findByText(/invalid or missing/i);
  });

  function givenVerifySucceeds() {
    server.use(
      http.post(VERIFY_EMAIL_URL, () => HttpResponse.json(mockTokens)),
      http.get(ME_URL, () => HttpResponse.json(mockUser))
    );
  }

  function givenVerifyFails() {
    server.use(http.post(VERIFY_EMAIL_URL, () => new HttpResponse(null, { status: 400 })));
  }

  function whenRenderedWithToken(token: string) {
    window.history.pushState({}, '', `/verify-email?token=${token}`);
    renderWithProviders(<VerifyEmailScreen />);
  }

  function whenRenderedWithoutToken() {
    window.history.pushState({}, '', '/verify-email');
    renderWithProviders(<VerifyEmailScreen />);
  }
});
