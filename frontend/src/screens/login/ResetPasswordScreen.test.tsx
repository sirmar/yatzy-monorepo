import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { HttpResponse, http } from 'msw';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { createMockServer, renderWithProviders } from '@/test/helpers';
import { ResetPasswordScreen } from './ResetPasswordScreen';

const RESET_PASSWORD_URL = 'http://localhost/auth/reset-password';
const REFRESH_URL = 'http://localhost/auth/refresh';

const mockNavigate = vi.hoisted(() => vi.fn());
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return { ...actual, useNavigate: () => mockNavigate };
});

const server = createMockServer();
server.use(http.post(REFRESH_URL, () => HttpResponse.json({}, { status: 401 })));
afterEach(() => {
  mockNavigate.mockReset();
  window.history.pushState({}, '', '/');
});

describe('ResetPasswordScreen', () => {
  it('shows new password input and submit button when token is present', () => {
    whenRenderedWithToken('some-token');
    expect(screen.getByLabelText('New password')).toBeInTheDocument();
    expect(screen.getByLabelText('Confirm new password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /reset password/i })).toBeInTheDocument();
  });

  it('shows error when token query param is missing', () => {
    whenRenderedWithoutToken();
    expect(screen.getByText(/invalid or missing reset link/i)).toBeInTheDocument();
  });

  it('redirects to /login on success', async () => {
    givenResetSucceeds();
    whenRenderedWithToken('valid-token');
    await whenPasswordEntered('newpassword123');
    await whenConfirmPasswordEntered('newpassword123');
    await whenFormSubmitted();
    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });

  it('shows error on invalid or expired token', async () => {
    givenResetFails('Invalid or expired token');
    whenRenderedWithToken('bad-token');
    await whenPasswordEntered('newpassword123');
    await whenConfirmPasswordEntered('newpassword123');
    await whenFormSubmitted();
    await screen.findByText('Invalid or expired token');
  });

  it('shows validation error for short password without network call', async () => {
    whenRenderedWithToken('some-token');
    await whenPasswordEntered('short');
    await whenConfirmPasswordEntered('short');
    await whenFormSubmitted();
    await screen.findByText(/at least 8 characters/i);
  });

  it('shows error when passwords do not match', async () => {
    whenRenderedWithToken('some-token');
    await whenPasswordEntered('newpassword123');
    await whenConfirmPasswordEntered('different123');
    await whenFormSubmitted();
    await screen.findByText(/passwords do not match/i);
  });

  function givenResetSucceeds() {
    server.use(http.post(RESET_PASSWORD_URL, () => new HttpResponse(null, { status: 204 })));
  }

  function givenResetFails(detail: string) {
    server.use(http.post(RESET_PASSWORD_URL, () => HttpResponse.json({ detail }, { status: 400 })));
  }

  function whenRenderedWithToken(token: string) {
    window.history.pushState({}, '', `/reset-password?token=${token}`);
    renderWithProviders(<ResetPasswordScreen />);
  }

  function whenRenderedWithoutToken() {
    window.history.pushState({}, '', '/reset-password');
    renderWithProviders(<ResetPasswordScreen />);
  }

  async function whenPasswordEntered(password: string) {
    await userEvent.type(screen.getByLabelText('New password'), password);
  }

  async function whenConfirmPasswordEntered(password: string) {
    await userEvent.type(screen.getByLabelText('Confirm new password'), password);
  }

  async function whenFormSubmitted() {
    await userEvent.click(screen.getByRole('button', { name: /reset password/i }));
  }
});
