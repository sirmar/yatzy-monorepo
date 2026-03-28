import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { HttpResponse, http } from 'msw';
import { setupServer } from 'msw/node';
import { afterAll, afterEach, beforeAll, describe, expect, it } from 'vitest';
import { renderWithProviders } from '@/test/helpers';
import { ForgotPasswordScreen } from './ForgotPasswordScreen';

const FORGOT_PASSWORD_URL = 'http://localhost/auth/forgot-password';
const REFRESH_URL = 'http://localhost/auth/refresh';

const server = setupServer(http.post(REFRESH_URL, () => HttpResponse.json({}, { status: 401 })));
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('ForgotPasswordScreen', () => {
  it('shows email input and submit button', () => {
    whenRendered();
    thenEmailInputIsVisible();
    thenSubmitButtonIsVisible();
  });

  it('shows success message after submission', async () => {
    givenForgotPasswordSucceeds();
    whenRendered();
    await whenEmailEntered('user@example.com');
    await whenFormSubmitted();
    await screen.findByText(/reset link has been sent/i);
  });

  it('shows error message on failure', async () => {
    givenForgotPasswordFails('Something went wrong');
    whenRendered();
    await whenEmailEntered('user@example.com');
    await whenFormSubmitted();
    await screen.findByText('Something went wrong');
  });

  function givenForgotPasswordSucceeds() {
    server.use(http.post(FORGOT_PASSWORD_URL, () => HttpResponse.json({})));
  }

  function givenForgotPasswordFails(detail: string) {
    server.use(
      http.post(FORGOT_PASSWORD_URL, () => HttpResponse.json({ detail }, { status: 422 }))
    );
  }

  function whenRendered() {
    renderWithProviders(<ForgotPasswordScreen />);
  }

  async function whenEmailEntered(email: string) {
    await userEvent.type(screen.getByLabelText(/email/i), email);
  }

  async function whenFormSubmitted() {
    await userEvent.click(screen.getByRole('button', { name: /send reset link/i }));
  }

  function thenEmailInputIsVisible() {
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
  }

  function thenSubmitButtonIsVisible() {
    expect(screen.getByRole('button', { name: /send reset link/i })).toBeInTheDocument();
  }
});
