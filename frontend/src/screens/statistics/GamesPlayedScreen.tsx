import { useEffect, useState } from 'react';
import { apiClient } from '@/api';
import type { components } from '@/api/schema';
import { ModeSelector } from '@/components/ModeSelector';
import { PageLayout } from '@/components/PageLayout';
import { RANK_TROPHY } from '@/lib/constants';

type GamesPlayed = components['schemas']['GamesPlayed'];
type SortBy = components['schemas']['GamesPlayedSortBy'];

const SECTIONS: { label: string; value: SortBy }[] = [
  { label: 'Total', value: 'total' },
  { label: 'Maxi Yatzy', value: 'maxi' },
  { label: 'Maxi Yatzy Sequential', value: 'maxi_sequential' },
  { label: 'Yatzy', value: 'yatzy' },
  { label: 'Yatzy Sequential', value: 'yatzy_sequential' },
];

const SORT_BY_KEY: Record<
  SortBy,
  keyof Pick<GamesPlayed, 'total' | 'maxi' | 'maxi_sequential' | 'yatzy' | 'yatzy_sequential'>
> = {
  total: 'total',
  maxi: 'maxi',
  maxi_sequential: 'maxi_sequential',
  yatzy: 'yatzy',
  yatzy_sequential: 'yatzy_sequential',
};

function GamesPlayedTable({ entries, sortBy }: { entries: GamesPlayed[]; sortBy: SortBy }) {
  const countKey = SORT_BY_KEY[sortBy];
  return (
    <div className="overflow-x-auto">
      <table className="w-full table-fixed text-sm text-white">
        <thead>
          <tr className="text-gray-400 text-left border-b border-gray-800">
            <th className="pb-2 w-8">#</th>
            <th className="pb-2">Player</th>
            <th className="pb-2 w-20 text-right">Games</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((entry, index) => (
            <tr key={entry.player_id} className="border-b border-gray-800/50">
              <td className="py-2 text-gray-400">{RANK_TROPHY[index + 1] ?? index + 1}</td>
              <td className="py-2">{entry.player_name}</td>
              <td className="py-2 text-right font-semibold">{entry[countKey]}</td>
            </tr>
          ))}
          {entries.length === 0 && (
            <tr>
              <td colSpan={3} className="py-4 text-center text-gray-400">
                No games played yet
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

export function GamesPlayedScreen() {
  const [selectedSortBy, setSelectedSortBy] = useState<SortBy>('total');
  const [entries, setEntries] = useState<GamesPlayed[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    setIsLoading(true);
    setError(null);
    apiClient
      .GET('/games-played-leaderboard', {
        params: { query: { sort_by: selectedSortBy } },
        signal: controller.signal,
      })
      .then(({ data, error }) => {
        if (error) {
          setError('Failed to load games played');
        } else {
          setEntries(data ?? []);
        }
        setIsLoading(false);
      })
      .catch((e: unknown) => {
        if ((e as { name?: string })?.name !== 'AbortError') throw e;
      });
    return () => controller.abort();
  }, [selectedSortBy]);

  return (
    <PageLayout>
      <h1 className="text-white text-xl font-semibold mb-6">Games Played</h1>
      <div className="mb-6">
        <ModeSelector options={SECTIONS} selected={selectedSortBy} onChange={setSelectedSortBy} />
      </div>
      {isLoading && <p className="text-gray-400 text-sm">Loading...</p>}
      {error && <p className="text-red-400 text-sm">{error}</p>}
      {!isLoading && !error && <GamesPlayedTable entries={entries} sortBy={selectedSortBy} />}
    </PageLayout>
  );
}
