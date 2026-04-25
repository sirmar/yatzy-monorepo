import { type RenderOptions, render } from '@testing-library/react';
import { HttpResponse, http } from 'msw';
import { setupServer } from 'msw/node';
import type { ReactElement } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { afterAll, afterEach, beforeAll } from 'vitest';
import { Toaster } from '@/components/ui/toaster';
import { AuthProvider } from '@/hooks/AuthContext';
import { PlayerProvider } from '@/hooks/PlayerContext';
import { PlayerNamesProvider } from '@/hooks/PlayerNamesContext';

function Providers({ children }: { children: React.ReactNode }) {
  return (
    <BrowserRouter>
      <AuthProvider>
        <PlayerProvider>
          <PlayerNamesProvider>{children}</PlayerNamesProvider>
        </PlayerProvider>
      </AuthProvider>
      <Toaster />
    </BrowserRouter>
  );
}

export function renderWithProviders(ui: ReactElement, options?: Omit<RenderOptions, 'wrapper'>) {
  return render(ui, { wrapper: Providers, ...options });
}

export const ALICE = { id: 1, name: 'Alice', is_bot: false, created_at: '' };
export const BOB = { id: 2, name: 'Bob', is_bot: false, created_at: '' };

export function createMockServer() {
  const server = setupServer(http.get('http://localhost/api/players', () => HttpResponse.json([])));
  beforeAll(() => server.listen({ onUnhandledRequest: 'bypass' }));
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());
  return server;
}
