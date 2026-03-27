import { useEffect, useState } from 'react';
import { apiClient } from '@/api';
import type { components } from '@/api/schema';
import { PageLayout } from '@/components/PageLayout';

type GamesPlayed = components['schemas']['GamesPlayed'];
type SortBy = components['schemas']['GamesPlayedSortBy'];

const SECTIONS: { label: string; sortBy: SortBy }[] = [
  { label: 'Total', sortBy: 'total' },
  { label: 'Maxi Yatzy', sortBy: 'maxi' },
  { label: 'Maxi Yatzy Sequential', sortBy: 'maxi_sequential' },
  { label: 'Yatzy', sortBy: 'yatzy' },
  { label: 'Yatzy Sequential', sortBy: 'yatzy_sequential' },
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

const RANK_TROPHY: Record<number, string> = { 1: '🥇', 2: '🥈', 3: '🥉' };

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
    setIsLoading(true);
    setError(null);
    apiClient
      .GET('/games-played-leaderboard', { params: { query: { sort_by: selectedSortBy } } })
      .then(({ data, error }) => {
        if (error) {
          setError('Failed to load games played');
        } else {
          setEntries(data ?? []);
        }
        setIsLoading(false);
      });
  }, [selectedSortBy]);

  return (
    <PageLayout>
      <h1 className="text-white text-xl font-semibold mb-6">Games Played</h1>

      <div className="flex gap-2 mb-6">
        {SECTIONS.map(({ label, sortBy }) => (
          <button
            key={sortBy}
            type="button"
            onClick={() => setSelectedSortBy(sortBy)}
            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
              selectedSortBy === sortBy
                ? 'bg-yellow-400 text-gray-900'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {isLoading && <p className="text-gray-400 text-sm">Loading...</p>}
      {error && <p className="text-red-400 text-sm">{error}</p>}

      {!isLoading && !error && <GamesPlayedTable entries={entries} sortBy={selectedSortBy} />}
    </PageLayout>
  );
}
