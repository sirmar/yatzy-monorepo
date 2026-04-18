import { useCallback, useEffect, useState } from 'react';
import { apiClient } from '@/api';

export function usePlayerNames(): [Record<number, string>, () => void] {
  const [playerNames, setPlayerNames] = useState<Record<number, string>>({});

  const refetch = useCallback(() => {
    apiClient.GET('/players').then(({ data }) => {
      if (data) {
        setPlayerNames(Object.fromEntries(data.map((p) => [p.id, p.name])));
      }
    });
  }, []);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return [playerNames, refetch];
}
