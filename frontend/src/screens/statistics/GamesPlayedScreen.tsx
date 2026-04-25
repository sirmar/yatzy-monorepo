import { useEffect, useState } from 'react';
import { apiClient } from '@/api';
import type { components } from '@/api/schema';
import { Avatar } from '@/components/Avatar';
import { Card } from '@/components/Card';
import { ModeSelector } from '@/components/ModeSelector';
import { PageLayout } from '@/components/PageLayout';
import { usePlayerNames } from '@/hooks/PlayerNamesContext';

type GamesPlayed = components['schemas']['GamesPlayed'];
type SortBy = components['schemas']['GamesPlayedSortBy'];

const TABS: { label: string; value: SortBy }[] = [
  { label: 'Total', value: 'total' },
  { label: 'Maxi Yatzy', value: 'maxi' },
  { label: 'Maxi Seq.', value: 'maxi_sequential' },
  { label: 'Yatzy', value: 'yatzy' },
  { label: 'Yatzy Seq.', value: 'yatzy_sequential' },
];

const RANK_COLORS = [
  'text-[var(--amber)]',
  'text-[rgba(180,180,200,0.9)]',
  'text-[rgba(180,140,80,0.9)]',
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
      .catch((e: unknown) => {
        if ((e as { name?: string })?.name !== 'AbortError') throw e;
      });
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
            <thead>
              <tr className="border-b border-[var(--border)]">
                <th className="pb-2 px-2 w-8 text-[10px] font-bold uppercase tracking-[0.08em] text-[var(--text-dim)] text-left">
                  #
                </th>
                <th className="pb-2 px-2 text-[10px] font-bold uppercase tracking-[0.08em] text-[var(--text-dim)] text-left">
                  Player
                </th>
                <th className="pb-2 px-2 text-[10px] font-bold uppercase tracking-[0.08em] text-[var(--text-dim)] text-right">
                  Games
                </th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry, idx) => (
                <tr
                  key={entry.player_id}
                  className="border-b border-[var(--border)] last:border-b-0"
                >
                  <td
                    className={`py-[10px] px-2 text-[12px] font-bold w-8 ${RANK_COLORS[idx] ?? 'text-[var(--text-dim)]'}`}
                  >
                    {idx + 1}
                  </td>
                  <td className="py-[10px] px-2">
                    <div className="flex items-center gap-[10px]">
                      <Avatar
                        name={entry.player_name}
                        index={idx}
                        size="lg"
                        playerId={entry.player_id}
                        hasPicture={pictures[entry.player_id] ?? false}
                      />
                      <span className="text-[13px] font-medium text-foreground">
                        {entry.player_name}
                      </span>
                    </div>
                  </td>
                  <td className="py-[10px] px-2 text-[14px] font-bold text-right text-foreground">
                    {entry[countKey] as number}
                  </td>
                </tr>
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
