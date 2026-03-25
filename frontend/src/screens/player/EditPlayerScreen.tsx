import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '@/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useAuth } from '@/hooks/AuthContext';
import { usePlayer } from '@/hooks/PlayerContext';
import { useErrorToast } from '@/hooks/use-toast';

export function EditPlayerScreen() {
  const { player, setPlayer } = usePlayer();
  const { accessToken } = useAuth();
  const navigate = useNavigate();
  const errorToast = useErrorToast();
  const [name, setName] = useState(player?.name ?? '');
  const [loading, setLoading] = useState(false);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    if (!player || !name.trim() || name.trim() === player.name) {
      navigate('/lobby');
      return;
    }
    setLoading(true);
    const { data, error } = await apiClient.PUT('/players/{player_id}', {
      params: { path: { player_id: player.id } },
      body: { name: name.trim() },
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    setLoading(false);
    if (error || !data) {
      errorToast('Failed to update player');
      return;
    }
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
              Edit player
            </h2>
            <form onSubmit={handleSave} className="flex flex-col gap-3">
              <div className="flex gap-2">
                <Input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Enter your name"
                  disabled={loading}
                  className="border-gray-600 bg-gray-800 text-white placeholder:text-gray-500 hover:border-yellow-400/50 focus-visible:ring-yellow-400/50"
                />
                <Button type="submit" disabled={loading || !name.trim()}>
                  Save
                </Button>
              </div>
              <Button
                type="button"
                variant="ghost"
                onClick={() => navigate('/lobby')}
                className="text-gray-400 hover:text-white"
              >
                Cancel
              </Button>
            </form>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
