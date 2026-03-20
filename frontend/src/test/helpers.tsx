import { PlayerProvider } from '@/hooks/PlayerContext';
import { type RenderOptions, render } from '@testing-library/react';
import type { ReactElement } from 'react';
import { BrowserRouter } from 'react-router-dom';

function Providers({ children }: { children: React.ReactNode }) {
  return (
    <BrowserRouter>
      <PlayerProvider>{children}</PlayerProvider>
    </BrowserRouter>
  );
}

export function renderWithProviders(ui: ReactElement, options?: Omit<RenderOptions, 'wrapper'>) {
  return render(ui, { wrapper: Providers, ...options });
}
