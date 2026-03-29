import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '@/api';
import type { components } from '@/api/schema';
import { ModeSelector } from '@/components/ModeSelector';
import { PageLayout } from '@/components/PageLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { usePlayer } from '@/hooks/PlayerContext';
import { useErrorToast } from '@/hooks/use-toast';
import { formatDate } from '@/lib/format';
import { INPUT_CLASS } from '@/lib/styles';
import { ChangePasswordForm } from './ChangePasswordForm';
import { DeleteAccountSection } from './DeleteAccountSection';

type PlayerStats = components['schemas']['PlayerStats'];
type ModeStats = components['schemas']['ModeStats'];

const MODE_SECTIONS: {
  key: keyof Pick<PlayerStats, 'maxi' | 'maxi_sequential' | 'yatzy' | 'yatzy_sequential'>;
  label: string;
  yatzyLabel: string;
}[] = [
  { key: 'maxi', label: 'Maxi Yatzy', yatzyLabel: 'Maxi Yatzy' },
  { key: 'maxi_sequential', label: 'Maxi Yatzy Sequential', yatzyLabel: 'Maxi Yatzy' },
  { key: 'yatzy', label: 'Yatzy', yatzyLabel: 'Yatzy' },
  { key: 'yatzy_sequential', label: 'Yatzy Sequential', yatzyLabel: 'Yatzy' },
];

function ModeStatsTable({ modeStats, yatzyLabel }: { modeStats: ModeStats; yatzyLabel: string }) {
  return (
    <table className="w-full text-sm text-white">
      <tbody>
        {[
          ['Games played', modeStats.games_played],
          ['High score', modeStats.high_score ?? '—'],
          [
            'Average score',
            modeStats.average_score != null ? Math.round(modeStats.average_score) : '—',
          ],
          ['Bonus earned', modeStats.bonus_count],
          [yatzyLabel, modeStats.yatzy_hit_count],
        ].map(([label, value]) => (
          <tr key={label as string} className="border-b border-gray-800/50">
            <td className="py-1.5 text-gray-400">{label}</td>
            <td className="py-1.5 text-right">{value}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export function ProfileScreen() {
  const { player, setPlayer } = usePlayer();
  const navigate = useNavigate();
  const errorToast = useErrorToast();
  const [name, setName] = useState(player?.name ?? '');
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<PlayerStats | null>(null);
  const [selectedMode, setSelectedMode] = useState<(typeof MODE_SECTIONS)[number]['key'] | null>(
    null
  );

  useEffect(() => {
    if (!player) return;
    const controller = new AbortController();
    apiClient
      .GET('/players/{player_id}/stats', {
        params: { path: { player_id: player.id } },
        signal: controller.signal,
      })
      .then(({ data }) => {
        if (data) {
          setStats(data);
          setSelectedMode(MODE_SECTIONS[0].key);
        }
      });
    return () => controller.abort();
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
          <div className="flex flex-col gap-6">
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
              <Button type="submit" className="w-40" disabled={loading || !name.trim()}>
                Save
              </Button>
            </form>
            <ChangePasswordForm />
            <DeleteAccountSection />
          </div>
          {stats && (
            <div className="flex flex-col gap-4">
              <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wider">
                Statistics
              </h2>
              <div className="flex flex-col gap-1">
                <span className="text-xs text-gray-500">
                  Member since {formatDate(stats.member_since)}
                </span>
                <span className="text-sm text-white">
                  Total games played:{' '}
                  <span className="font-semibold">{stats.total_games_played}</span>
                </span>
              </div>
              <ModeSelector
                options={MODE_SECTIONS.map(({ key, label }) => ({ label, value: key }))}
                selected={selectedMode ?? MODE_SECTIONS[0].key}
                onChange={setSelectedMode}
              />
              {selectedMode &&
                (() => {
                  const section = MODE_SECTIONS.find(({ key }) => key === selectedMode);
                  return section ? (
                    <ModeStatsTable
                      modeStats={stats[selectedMode]}
                      yatzyLabel={section.yatzyLabel}
                    />
                  ) : null;
                })()}
            </div>
          )}
        </div>
      </div>
    </PageLayout>
  );
}
