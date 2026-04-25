import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { HttpResponse, http } from 'msw';
import { setupServer } from 'msw/node';
import { afterAll, afterEach, beforeAll, describe, it } from 'vitest';
import { renderWithProviders } from '@/test/helpers';
import { ChangePasswordForm } from './ChangePasswordForm';

const CHANGE_PASSWORD_URL = 'http://localhost/auth/password';
const REFRESH_URL = 'http://localhost/auth/refresh';
const ME_URL = 'http://localhost/auth/me';

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

const server = setupServer(
  http.post(REFRESH_URL, () => HttpResponse.json(mockTokens)),
  http.get(ME_URL, () => HttpResponse.json(mockUser))
);
beforeAll(() => server.listen());
afterEach(() => {
  server.resetHandlers();
  localStorage.clear();
});
afterAll(() => server.close());

describe('ChangePasswordForm', () => {
  it('shows current password, new password and confirm fields and submit button', () => {
    whenRendered();
    thenFieldIsVisible(/current password/i);
    thenFieldIsVisible('New password');
    thenFieldIsVisible('Confirm new password');
    thenButtonIsVisible(/update password/i);
  });

  it('shows success message on 204', async () => {
    givenAuthenticated();
    givenChangePasswordSucceeds();
    whenRendered();
    await whenCurrentPasswordEntered('oldpassword');
    await whenNewPasswordEntered('newpassword123');
    await whenConfirmPasswordEntered('newpassword123');
    await whenFormSubmitted();
    await screen.findByText(/password changed successfully/i);
  });

  it('shows error on wrong current password', async () => {
    givenAuthenticated();
    givenChangePasswordFails();
    whenRendered();
    await whenCurrentPasswordEntered('wrongpassword');
    await whenNewPasswordEntered('newpassword123');
    await whenConfirmPasswordEntered('newpassword123');
    await whenFormSubmitted();
    await screen.findByText(/request failed/i);
  });

  it('shows error when passwords do not match', async () => {
    whenRendered();
    await whenCurrentPasswordEntered('oldpassword');
    await whenNewPasswordEntered('newpassword123');
    await whenConfirmPasswordEntered('different123');
    await whenFormSubmitted();
    await screen.findByText(/passwords do not match/i);
  });

  function givenAuthenticated() {
    localStorage.setItem('yatzy_refresh_token', 'valid-token');
  }

  function givenChangePasswordSucceeds() {
    server.use(http.put(CHANGE_PASSWORD_URL, () => new HttpResponse(null, { status: 204 })));
  }

  function givenChangePasswordFails() {
    server.use(http.put(CHANGE_PASSWORD_URL, () => new HttpResponse(null, { status: 401 })));
  }

  function whenRendered() {
    renderWithProviders(<ChangePasswordForm />);
  }

  function thenFieldIsVisible(label: string | RegExp) {
    screen.getByLabelText(label);
  }

  function thenButtonIsVisible(name: string | RegExp) {
    screen.getByRole('button', { name });
  }

  async function whenCurrentPasswordEntered(password: string) {
    await userEvent.type(screen.getByLabelText(/current password/i), password);
  }

  async function whenNewPasswordEntered(password: string) {
    await userEvent.type(screen.getByLabelText('New password'), password);
  }

  async function whenConfirmPasswordEntered(password: string) {
    await userEvent.type(screen.getByLabelText('Confirm new password'), password);
  }

  async function whenFormSubmitted() {
    await userEvent.click(screen.getByRole('button', { name: /update password/i }));
  }
});
