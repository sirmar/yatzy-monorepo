import { useEffect, useState } from 'react';
import { apiClient } from '@/api';

export function usePlayerNames(): Record<number, string> {
  const [playerNames, setPlayerNames] = useState<Record<number, string>>({});

  useEffect(() => {
    const controller = new AbortController();
    apiClient.GET('/players', { signal: controller.signal }).then(({ data }) => {
      if (data) {
        setPlayerNames(Object.fromEntries(data.map((p) => [p.id, p.name])));
      }
    });
    return () => controller.abort();
  }, []);

  return playerNames;
}
