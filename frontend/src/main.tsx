import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { PlayerProvider } from '@/hooks/PlayerContext';
import './index.css';
import App from './App';

// biome-ignore lint/style/noNonNullAssertion: root element is guaranteed by index.html
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <PlayerProvider>
        <App />
      </PlayerProvider>
    </BrowserRouter>
  </StrictMode>
);
