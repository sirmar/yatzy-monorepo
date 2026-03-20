import type { components } from '@/api';
import { createContext, useContext, useState } from 'react';

type Player = components['schemas']['Player'];

interface PlayerContextValue {
  player: Player | null;
  setPlayer: (player: Player | null) => void;
}

const PlayerContext = createContext<PlayerContextValue | null>(null);

const STORAGE_KEY = 'yatzy_player';

export function PlayerProvider({ children }: { children: React.ReactNode }) {
  const [player, setPlayerState] = useState<Player | null>(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? (JSON.parse(stored) as Player) : null;
  });

  function setPlayer(player: Player | null) {
    setPlayerState(player);
    if (player) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(player));
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  }

  return <PlayerContext.Provider value={{ player, setPlayer }}>{children}</PlayerContext.Provider>;
}

export function usePlayer(): PlayerContextValue {
  const ctx = useContext(PlayerContext);
  if (!ctx) throw new Error('usePlayer must be used within PlayerProvider');
  return ctx;
}
