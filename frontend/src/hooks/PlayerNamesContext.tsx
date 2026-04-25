import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { apiClient } from '@/api';

interface PlayerNamesContextValue {
  names: Record<number, string>;
  pictures: Record<number, boolean>;
  refetch: () => void;
}

const PlayerNamesContext = createContext<PlayerNamesContextValue | null>(null);

export function PlayerNamesProvider({ children }: { children: React.ReactNode }) {
  const [names, setNames] = useState<Record<number, string>>({});
  const [pictures, setPictures] = useState<Record<number, boolean>>({});

  const refetch = useCallback(() => {
    apiClient.GET('/players').then(({ data }) => {
      if (!data) return;
      setNames(Object.fromEntries(data.map((p) => [p.id, p.name])));
      setPictures(Object.fromEntries(data.map((p) => [p.id, p.has_picture])));
    });
  }, []);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return (
    <PlayerNamesContext.Provider value={{ names, pictures, refetch }}>
      {children}
    </PlayerNamesContext.Provider>
  );
}

export function usePlayerNames(): PlayerNamesContextValue {
  const ctx = useContext(PlayerNamesContext);
  if (!ctx) throw new Error('usePlayerNames must be used within PlayerNamesProvider');
  return ctx;
}
