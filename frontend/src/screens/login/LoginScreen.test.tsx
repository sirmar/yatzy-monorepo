import { fireEvent, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { HttpResponse, http } from 'msw';
import { setupServer } from 'msw/node';
import { afterAll, afterEach, beforeAll, describe, expect, it, vi } from 'vitest';
import { renderWithProviders } from '@/test/helpers';
import { LoginScreen } from './LoginScreen';

const mockNavigate = vi.hoisted(() => vi.fn());
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return { ...actual, useNavigate: () => mockNavigate };
});

const LOGIN_URL = 'http://localhost/auth/login';
const REGISTER_URL = 'http://localhost/auth/register';
const REFRESH_URL = 'http://localhost/auth/refresh';
const ME_URL = 'http://localhost/auth/me';

const mockUser = {
  id: '123',
  email: 'user@example.com',
  email_verified: true,
  created_at: '2026-01-01',
};
const mockTokens = {
  access_token: 'access-tok',
  refresh_token: 'refresh-tok',
  token_type: 'bearer',
};

const server = setupServer(
  http.post(REFRESH_URL, () => HttpResponse.json({ detail: 'Unauthorized' }, { status: 401 }))
);
beforeAll(() => server.listen());
afterEach(() => {
  server.resetHandlers();
  mockNavigate.mockReset();
  localStorage.clear();
});
afterAll(() => server.close());

describe('LoginScreen', () => {
  describe('login form', () => {
    it('shows email and password inputs', () => {
      whenRendered();
      thenEmailInputIsVisible();
      thenPasswordInputIsVisible();
    });

    it('signs in and navigates to / on success', async () => {
      givenLoginSucceeds();
      whenRendered();
      await whenEmailEntered('user@example.com');
      await whenPasswordEntered('password123');
      await whenFormSubmitted();
      thenNavigatedTo('/');
    });

    it('shows error when login fails', async () => {
      givenLoginFails('Invalid credentials');
      whenRendered();
      await whenEmailEntered('user@example.com');
      await whenPasswordEntered('password123');
      await whenFormSubmitted();
      await thenErrorIsVisible('Invalid credentials');
    });

    it('disables submit button while signing in', async () => {
      server.use(http.post(LOGIN_URL, () => new Promise(() => {})));
      whenRendered();
      await whenEmailEntered('user@example.com');
      await whenPasswordEntered('password123');
      const submit = screen
        .getAllByRole('button')
        .find((b) => (b as HTMLButtonElement).type === 'submit');
      if (!submit) throw new Error('Submit button not found');
      fireEvent.click(submit);
      thenSubmitButtonIsDisabled();
    });
  });

  describe('register form', () => {
    it('toggles to register mode', async () => {
      whenRendered();
      await whenToggledToRegister();
      thenRegisterButtonIsVisible();
    });

    it('shows verify email message on success', async () => {
      givenRegisterSucceeds();
      whenRendered();
      await whenToggledToRegister();
      await whenEmailEntered('new@example.com');
      await whenPasswordEntered('password123');
      await whenFormSubmitted();
      await screen.findByText(/check your email/i);
    });

    it('shows error when registration fails', async () => {
      givenRegisterFails('Email already taken');
      whenRendered();
      await whenToggledToRegister();
      await whenEmailEntered('existing@example.com');
      await whenPasswordEntered('password123');
      await whenFormSubmitted();
      await thenErrorIsVisible('Email already taken');
    });
  });

  describe('validation', () => {
    it('shows error for short password without network call', async () => {
      whenRendered();
      await whenEmailEntered('user@example.com');
      await whenPasswordEntered('short');
      await whenFormSubmitted();
      await thenErrorIsVisible(/at least 8 characters/i);
    });
  });

  describe('already authenticated', () => {
    it('redirects to / without showing the form', async () => {
      givenUserIsAuthenticated();
      whenRendered();
      await thenFormIsNotVisible();
    });
  });

  function givenLoginSucceeds() {
    server.use(
      http.post(LOGIN_URL, () => HttpResponse.json(mockTokens)),
      http.get(ME_URL, () => HttpResponse.json(mockUser))
    );
  }

  function givenLoginFails(detail: string) {
    server.use(http.post(LOGIN_URL, () => HttpResponse.json({ detail }, { status: 401 })));
  }

  function givenRegisterSucceeds() {
    server.use(
      http.post(REGISTER_URL, () =>
        HttpResponse.json({ message: 'Verification email sent' }, { status: 201 })
      )
    );
  }

  function givenRegisterFails(detail: string) {
    server.use(http.post(REGISTER_URL, () => HttpResponse.json({ detail }, { status: 409 })));
  }

  function givenUserIsAuthenticated() {
    localStorage.setItem('yatzy_refresh_token', 'valid-token');
    server.use(
      http.post(REFRESH_URL, () => HttpResponse.json(mockTokens)),
      http.get(ME_URL, () => HttpResponse.json(mockUser))
    );
  }

  function whenRendered() {
    renderWithProviders(<LoginScreen />);
  }

  async function whenEmailEntered(email: string) {
    await userEvent.type(screen.getByLabelText(/email/i), email);
  }

  async function whenPasswordEntered(password: string) {
    await userEvent.type(screen.getByLabelText(/password/i), password);
  }

  async function whenFormSubmitted() {
    const submit = screen
      .getAllByRole('button')
      .find((b) => (b as HTMLButtonElement).type === 'submit');
    if (!submit) throw new Error('No submit button found');
    await userEvent.click(submit);
  }

  async function whenToggledToRegister() {
    await userEvent.click(screen.getByRole('button', { name: /register/i }));
  }

  function thenEmailInputIsVisible() {
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
  }

  function thenPasswordInputIsVisible() {
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  }

  function thenRegisterButtonIsVisible() {
    expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument();
  }

  function thenSubmitButtonIsDisabled() {
    const submit = screen
      .getAllByRole('button')
      .find((b) => (b as HTMLButtonElement).type === 'submit');
    expect(submit).toBeDisabled();
  }

  function thenNavigatedTo(path: string) {
    expect(mockNavigate).toHaveBeenCalledWith(path);
  }

  async function thenErrorIsVisible(message: string | RegExp) {
    await screen.findByText(message);
  }

  async function thenFormIsNotVisible() {
    await screen.findByLabelText(/email/i);
    await waitFor(() => expect(screen.queryByLabelText(/email/i)).not.toBeInTheDocument());
  }
});
