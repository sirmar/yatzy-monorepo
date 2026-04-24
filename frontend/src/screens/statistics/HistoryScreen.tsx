import { useEffect, useState } from 'react';
import { apiClient } from '@/api';
import type { components } from '@/api/schema';
import { AvatarStack } from '@/components/Avatar';
import { PageLayout } from '@/components/PageLayout';
import { usePlayer } from '@/hooks/PlayerContext';

type HighScore = components['schemas']['HighScore'];
type GameMode = components['schemas']['GameMode'];

const MODE_LABELS: Record<GameMode, string> = {
  maxi: 'Maxi Yatzy',
  maxi_sequential: 'Maxi Sequential',
  yatzy: 'Yatzy',
  yatzy_sequential: 'Yatzy Sequential',
};

type VariantFilter = 'all' | 'maxi' | 'yatzy';
type TypeFilter = 'all' | 'regular' | 'sequential';
type ResultFilter = 'all' | 'wins' | 'losses';

function formatGameDate(iso: string): string {
  const date = new Date(iso);
  const now = new Date();
  const diffDays = Math.floor((now.getTime() - date.getTime()) / 86400000);
  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function ordinal(n: number): string {
  if (n === 1) return '1st';
  if (n === 2) return '2nd';
  if (n === 3) return '3rd';
  return `${n}th`;
}

export function HistoryScreen() {
  const { player } = usePlayer();
  const [allScores, setAllScores] = useState<HighScore[]>([]);
  const [variant, setVariant] = useState<VariantFilter>('all');
  const [type, setType] = useState<TypeFilter>('all');
  const [result, setResult] = useState<ResultFilter>('all');
  useEffect(() => {
    const controller = new AbortController();
    apiClient
      .GET('/high-scores', { signal: controller.signal })
      .then(({ data }) => {
        if (data) setAllScores(data);
      })
      .catch((e: unknown) => {
        if ((e as { name?: string })?.name !== 'AbortError') throw e;
      });
    return () => controller.abort();
  }, []);

  const myGames = allScores.filter((s) => s.player_id === player?.id);

  const gameIds = [...new Set(myGames.map((s) => s.game_id))];

  const rows = gameIds
    .map((gameId) => {
      const myEntry = myGames.find((s) => s.game_id === gameId);
      if (!myEntry) return null;
      const allInGame = allScores.filter((s) => s.game_id === gameId);
      const sorted = [...allInGame].sort((a, b) => b.total_score - a.total_score);
      const rank = sorted.findIndex((s) => s.player_id === player?.id) + 1;
      const isWin = rank === 1;
      return {
        gameId,
        mode: myEntry.mode,
        score: myEntry.total_score,
        finishedAt: myEntry.finished_at,
        rank,
        isWin,
        playerIds: sorted.map((s) => s.player_id),
        playerNames: sorted.map((s) => s.player_name),
      };
    })
    .filter(Boolean)
    .sort(
      (a, b) => new Date(b?.finishedAt ?? 0).getTime() - new Date(a?.finishedAt ?? 0).getTime()
    );

  const filtered = rows.filter((row) => {
    if (!row) return false;
    if (variant === 'maxi' && !row.mode.startsWith('maxi')) return false;
    if (variant === 'yatzy' && !row.mode.startsWith('yatzy')) return false;
    if (type === 'regular' && row.mode.includes('sequential')) return false;
    if (type === 'sequential' && !row.mode.includes('sequential')) return false;
    if (result === 'wins' && !row.isWin) return false;
    if (result === 'losses' && row.isWin) return false;
    return true;
  });

  function FilterSeg<T extends string>({
    options,
    value,
    onChange,
  }: {
    options: { label: string; value: T }[];
    value: T;
    onChange: (v: T) => void;
  }) {
    return (
      <div className="flex items-center gap-1 bg-[var(--surface-2)] rounded-full p-[3px]">
        {options.map((opt) => (
          <button
            key={opt.value}
            type="button"
            onClick={() => onChange(opt.value)}
            className={`h-[26px] px-3 rounded-full text-[12px] font-medium cursor-pointer border-none transition-colors ${
              value === opt.value
                ? 'bg-[var(--accent)] text-white'
                : 'bg-transparent text-[var(--text-muted)] hover:text-foreground'
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>
    );
  }

  return (
    <PageLayout>
      <div className="flex flex-col gap-4">
        <div className="bg-[var(--surface)] border border-[var(--border)] rounded-[14px] px-4 py-3 flex items-center gap-3 flex-wrap">
          <span className="text-[13px] font-semibold text-foreground">History</span>
          <FilterSeg
            options={[
              { label: 'All', value: 'all' as VariantFilter },
              { label: 'Maxi', value: 'maxi' as VariantFilter },
              { label: 'Yatzy', value: 'yatzy' as VariantFilter },
            ]}
            value={variant}
            onChange={setVariant}
          />
          <FilterSeg
            options={[
              { label: 'All', value: 'all' as TypeFilter },
              { label: 'Regular', value: 'regular' as TypeFilter },
              { label: 'Sequential', value: 'sequential' as TypeFilter },
            ]}
            value={type}
            onChange={setType}
          />
          <FilterSeg
            options={[
              { label: 'All', value: 'all' as ResultFilter },
              { label: 'Wins', value: 'wins' as ResultFilter },
              { label: 'Losses', value: 'losses' as ResultFilter },
            ]}
            value={result}
            onChange={setResult}
          />
        </div>

        <div className="bg-[var(--surface)] border border-[var(--border)] rounded-[14px] px-4 py-3">
          <ul className="flex flex-col divide-y divide-[var(--border)]">
            {filtered.map((row) => {
              if (!row) return null;
              return (
                <li key={row.gameId} className="py-3 first:pt-0 last:pb-0">
                  <div className="flex items-center gap-3">
                    <AvatarStack names={row.playerNames} size="md" />
                    <div className="flex flex-col gap-0.5 flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-[11px] font-semibold uppercase tracking-[0.06em] border border-[var(--border-2)] bg-[var(--surface-2)] text-[var(--text-muted)] rounded-full px-2 py-0.5">
                          {MODE_LABELS[row.mode]}
                        </span>
                      </div>
                      <div className="text-[12px] text-[var(--text-muted)] truncate">
                        {row.playerNames.join(', ')}
                      </div>
                    </div>
                    <div className="flex items-center gap-3 flex-shrink-0">
                      <span
                        className={`text-[11px] font-semibold px-2 py-0.5 rounded-full ${
                          row.isWin
                            ? 'bg-[rgba(94,203,138,0.15)] text-[var(--green)]'
                            : 'bg-[rgba(240,101,96,0.12)] text-[var(--red)]'
                        }`}
                      >
                        {ordinal(row.rank)}
                      </span>
                      <span className="text-[14px] font-bold text-foreground">{row.score}</span>
                      <span className="text-[11px] text-[var(--text-dim)] w-16 text-right">
                        {formatGameDate(row.finishedAt)}
                      </span>
                    </div>
                  </div>
                </li>
              );
            })}
            {filtered.length === 0 && (
              <li className="py-6 text-center text-[13px] text-[var(--text-muted)]">
                No games found
              </li>
            )}
          </ul>
          {filtered.length > 0 && (
            <div className="mt-3 pt-3 border-t border-[var(--border)] flex items-center justify-between">
              <span className="text-[11px] text-[var(--text-dim)] uppercase tracking-[0.06em] font-semibold">
                Total
              </span>
              <span className="text-[12px] font-semibold text-foreground">
                {filtered.length} {filtered.length === 1 ? 'game' : 'games'}
              </span>
            </div>
          )}
        </div>
      </div>
    </PageLayout>
  );
}
