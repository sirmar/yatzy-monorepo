import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '@/api';
import type { components } from '@/api/schema';
import { PageLayout } from '@/components/PageLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAuth } from '@/hooks/AuthContext';
import { usePlayer } from '@/hooks/PlayerContext';
import { useErrorToast } from '@/hooks/use-toast';

type PlayerStats = components['schemas']['PlayerStats'];

export function EditPlayerScreen() {
  const { player, setPlayer } = usePlayer();
  const { accessToken } = useAuth();
  const navigate = useNavigate();
  const errorToast = useErrorToast();
  const [name, setName] = useState(player?.name ?? '');
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<PlayerStats | null>(null);

  useEffect(() => {
    if (!player) return;
    apiClient
      .GET('/players/{player_id}/stats', { params: { path: { player_id: player.id } } })
      .then(({ data }) => {
        if (data) setStats(data);
      });
  }, [player]);

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
    <PageLayout>
      <div className="max-w-md flex flex-col gap-6">
        <h1 className="text-2xl font-bold text-white">Profile</h1>
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
        {stats && (
          <table className="w-full text-sm text-white">
            <tbody>
              {[
                ['Member since', new Date(stats.member_since).toLocaleDateString()],
                ['Games played', stats.games_played],
                ['High score', stats.high_score ?? '—'],
                [
                  'Average score',
                  stats.average_score != null ? Math.round(stats.average_score) : '—',
                ],
                ['Bonuses', stats.bonus_count],
                ['Maxi Yatzy', stats.maxi_yatzy_count],
              ].map(([label, value]) => (
                <tr key={label as string} className="border-b border-gray-800/50">
                  <td className="py-2 text-gray-400">{label}</td>
                  <td className="py-2 text-right">{value}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </PageLayout>
  );
}
