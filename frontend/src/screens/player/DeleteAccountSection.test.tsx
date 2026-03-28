import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { HttpResponse, http } from 'msw';
import { setupServer } from 'msw/node';
import { afterAll, afterEach, beforeAll, describe, expect, it, vi } from 'vitest';
import { renderWithProviders } from '@/test/helpers';
import { DeleteAccountSection } from './DeleteAccountSection';

const DELETE_ACCOUNT_URL = 'http://localhost/auth/me';
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

const server = setupServer(
  http.post(REFRESH_URL, () => HttpResponse.json(mockTokens)),
  http.get(ME_URL, () => HttpResponse.json(mockUser))
);
beforeAll(() => server.listen());
afterEach(() => {
  server.resetHandlers();
  mockNavigate.mockReset();
  localStorage.clear();
});
afterAll(() => server.close());

describe('DeleteAccountSection', () => {
  it('shows a delete button that opens a confirmation dialog', async () => {
    whenRendered();
    await whenDeleteButtonClicked();
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText(/cannot be undone/i)).toBeInTheDocument();
  });

  it('does not delete if user cancels', async () => {
    whenRendered();
    await whenDeleteButtonClicked();
    await whenCancelClicked();
    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it('calls deleteAccount and redirects to /login on confirm', async () => {
    givenAuthenticated();
    givenDeleteAccountSucceeds();
    whenRendered();
    await whenDeleteButtonClicked();
    await whenConfirmClicked();
    await vi.waitFor(() => expect(mockNavigate).toHaveBeenCalledWith('/login'));
  });

  function givenAuthenticated() {
    localStorage.setItem('yatzy_refresh_token', 'valid-token');
  }

  function givenDeleteAccountSucceeds() {
    server.use(http.delete(DELETE_ACCOUNT_URL, () => new HttpResponse(null, { status: 204 })));
  }

  function whenRendered() {
    renderWithProviders(<DeleteAccountSection />);
  }

  async function whenDeleteButtonClicked() {
    await userEvent.click(screen.getByRole('button', { name: /delete account/i }));
  }

  async function whenCancelClicked() {
    await userEvent.click(screen.getByRole('button', { name: /cancel/i }));
  }

  async function whenConfirmClicked() {
    const buttons = screen.getAllByRole('button', { name: /delete account/i });
    const confirmButton = buttons[buttons.length - 1];
    await userEvent.click(confirmButton);
  }
});
