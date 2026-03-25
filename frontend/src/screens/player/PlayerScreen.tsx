import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { components } from '@/api';
import { apiClient } from '@/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/hooks/AuthContext';
import { usePlayer } from '@/hooks/PlayerContext';
import { useErrorToast } from '@/hooks/use-toast';
import { CreatePlayerForm } from './CreatePlayerForm';
import { PlayerList } from './PlayerList';

type Player = components['schemas']['Player'];

export function PlayerScreen() {
  const [players, setPlayers] = useState<Player[]>([]);
  const { setPlayer } = usePlayer();
  const { user, accessToken } = useAuth();
  const navigate = useNavigate();
  const errorToast = useErrorToast();

  useEffect(() => {
    if (!accessToken) return;
    apiClient
      .GET('/players/me', { headers: { Authorization: `Bearer ${accessToken}` } })
      .then(({ data }) => {
        if (data) {
          setPlayer(data);
          navigate('/lobby');
        }
      });
  }, [accessToken, setPlayer, navigate]);

  useEffect(() => {
    apiClient.GET('/players').then(({ data }) => {
      if (data) setPlayers(data);
    });
  }, []);

  async function handleCreate(name: string) {
    const { data, error } = await apiClient.POST('/players', {
      body: { name },
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    if (error || !data) throw error ?? new Error('Failed to create player');
    setPlayer(data);
    navigate('/lobby');
  }

  async function handleUpdate(player: Player, newName: string) {
    const { data, error } = await apiClient.PUT('/players/{player_id}', {
      params: { path: { player_id: player.id } },
      body: { name: newName },
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    if (error || !data) {
      errorToast('Failed to update player');
      throw error ?? new Error('Failed to update player');
    }
    setPlayers((prev) => prev.map((p) => (p.id === data.id ? data : p)));
  }

  async function handleDelete(player: Player) {
    const { error } = await apiClient.DELETE('/players/{player_id}', {
      params: { path: { player_id: player.id } },
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    if (error) {
      errorToast('Failed to delete player');
      return;
    }
    setPlayers((prev) => prev.filter((p) => p.id !== player.id));
    setPlayer(null);
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
          <div>
            <h2 className="text-sm font-medium text-gray-400 mb-3 uppercase tracking-wider">
              Players
            </h2>
            <PlayerList
              players={players}
              currentAccountId={user?.id}
              onUpdate={handleUpdate}
              onDelete={handleDelete}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
