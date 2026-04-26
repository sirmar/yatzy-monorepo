import { useEffect, useState } from 'react';
import { apiClient } from '@/api';
import type { components } from '@/api/schema';
import { Card } from '@/components/Card';
import { LeaderboardHeader, LeaderboardRow } from '@/components/Leaderboard';
import { ModeSelector } from '@/components/ModeSelector';
import { PageLayout } from '@/components/PageLayout';
import { usePlayerNames } from '@/hooks/PlayerNamesContext';
import { ignoreAbort } from '@/lib/utils';

type GamesPlayed = components['schemas']['GamesPlayed'];
type SortBy = components['schemas']['GamesPlayedSortBy'];

const TABS: { label: string; value: SortBy }[] = [
  { label: 'Total', value: 'total' },
  { label: 'Maxi Yatzy', value: 'maxi' },
  { label: 'Maxi Seq.', value: 'maxi_sequential' },
  { label: 'Yatzy', value: 'yatzy' },
  { label: 'Yatzy Seq.', value: 'yatzy_sequential' },
];

const COUNT_KEY: Record<SortBy, keyof GamesPlayed> = {
  total: 'total',
  maxi: 'maxi',
  maxi_sequential: 'maxi_sequential',
  yatzy: 'yatzy',
  yatzy_sequential: 'yatzy_sequential',
};

export function GamesPlayedScreen() {
  const [entries, setEntries] = useState<GamesPlayed[]>([]);
  const [sortBy, setSortBy] = useState<SortBy>('total');
  const { pictures } = usePlayerNames();

  useEffect(() => {
    const controller = new AbortController();
    apiClient
      .GET('/games-played-leaderboard', {
        params: { query: { sort_by: sortBy } },
        signal: controller.signal,
      })
      .then(({ data }) => {
        if (data) setEntries(data);
      })
      .catch(ignoreAbort);
    return () => controller.abort();
  }, [sortBy]);

  const countKey = COUNT_KEY[sortBy];

  return (
    <PageLayout>
      <div className="flex flex-col gap-4">
        <Card className="px-4 py-3 flex items-center gap-3 flex-wrap">
          <span className="text-[13px] font-semibold text-foreground">Most Games Played</span>
          <ModeSelector options={TABS} selected={sortBy} onChange={setSortBy} />
        </Card>

        <Card className="px-4 py-[14px]">
          <table className="w-full border-collapse table-fixed">
            <LeaderboardHeader scoreLabel="Games" />
            <tbody>
              {entries.map((entry, idx) => (
                <LeaderboardRow
                  key={entry.player_id}
                  rank={idx + 1}
                  playerId={entry.player_id}
                  playerName={entry.player_name}
                  hasPicture={pictures[entry.player_id] ?? false}
                  score={entry[countKey] as number}
                />
              ))}
              {entries.length === 0 && (
                <tr>
                  <td colSpan={3} className="py-6 text-center text-[13px] text-[var(--text-muted)]">
                    No games played yet
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </Card>
      </div>
    </PageLayout>
  );
}
