import { type RenderOptions, render } from '@testing-library/react';
import { setupServer } from 'msw/node';
import type { ReactElement } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { afterAll, afterEach, beforeAll } from 'vitest';
import { Toaster } from '@/components/ui/toaster';
import { AuthProvider } from '@/hooks/AuthContext';
import { PlayerProvider } from '@/hooks/PlayerContext';

function Providers({ children }: { children: React.ReactNode }) {
  return (
    <BrowserRouter>
      <AuthProvider>
        <PlayerProvider>{children}</PlayerProvider>
      </AuthProvider>
      <Toaster />
    </BrowserRouter>
  );
}

export function renderWithProviders(ui: ReactElement, options?: Omit<RenderOptions, 'wrapper'>) {
  return render(ui, { wrapper: Providers, ...options });
}

export const ALICE = { id: 1, name: 'Alice', created_at: '' };
export const BOB = { id: 2, name: 'Bob', created_at: '' };

export function createMockServer() {
  const server = setupServer();
  beforeAll(() => server.listen());
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());
  return server;
}
