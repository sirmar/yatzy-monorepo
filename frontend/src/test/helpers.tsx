import { type RenderOptions, render } from '@testing-library/react';
import type { ReactElement } from 'react';
import { BrowserRouter } from 'react-router-dom';
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
