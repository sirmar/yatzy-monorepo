import { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '@/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/hooks/AuthContext';
import { usePlayer } from '@/hooks/PlayerContext';
import { CreatePlayerForm } from './CreatePlayerForm';

export function PlayerScreen() {
  const { setPlayer } = usePlayer();
  const { accessToken } = useAuth();
  const navigate = useNavigate();
  const setPlayerRef = useRef(setPlayer);
  const navigateRef = useRef(navigate);

  useEffect(() => {
    if (!accessToken) return;
    const controller = new AbortController();
    apiClient.GET('/players/me', { signal: controller.signal }).then(({ data }) => {
      if (data) {
        setPlayerRef.current(data);
        navigateRef.current('/lobby');
      }
    });
    return () => controller.abort();
  }, [accessToken]);

  async function handleCreate(name: string) {
    const { data, error } = await apiClient.POST('/players', {
      body: { name },
    });
    if (error || !data) throw error ?? new Error('Failed to create player');
    setPlayer(data);
    navigate('/lobby');
  }

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center p-4">
      <Card className="w-full max-w-md bg-gray-900 border-gray-800">
        <CardHeader>
          <CardTitle className="text-3xl font-bold text-center text-white">Yatzy</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-6">
          <div>
            <h2 className="text-sm font-medium text-gray-400 mb-3 uppercase tracking-wider">
              Create player
            </h2>
            <CreatePlayerForm onCreated={handleCreate} />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
