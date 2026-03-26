import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '@/api';
import type { components } from '@/api/schema';
import { PageLayout } from '@/components/PageLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { usePlayer } from '@/hooks/PlayerContext';
import { useErrorToast } from '@/hooks/use-toast';
import { formatDate } from '@/lib/format';
import { INPUT_CLASS } from '@/lib/styles';

type PlayerStats = components['schemas']['PlayerStats'];

export function ProfileScreen() {
  const { player, setPlayer } = usePlayer();
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
      <div className="flex flex-col gap-6">
        <h1 className="text-2xl font-bold text-white">Profile</h1>
        <div className="grid grid-cols-2 gap-8">
          <form onSubmit={handleSave} className="flex flex-col gap-3">
            <div className="flex flex-col gap-1">
              <label htmlFor="player-name" className="text-sm text-gray-400">
                Name
              </label>
              <Input
                id="player-name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter your name"
                disabled={loading}
                className={INPUT_CLASS}
              />
            </div>
            <Button type="submit" disabled={loading || !name.trim()}>
              Save
            </Button>
          </form>
          {stats && (
            <div className="flex flex-col gap-3">
              <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wider">
                Statistics
              </h2>
              <table className="w-full text-sm text-white">
                <tbody>
                  {[
                    ['Member since', formatDate(stats.member_since)],
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
            </div>
          )}
        </div>
      </div>
    </PageLayout>
  );
}
