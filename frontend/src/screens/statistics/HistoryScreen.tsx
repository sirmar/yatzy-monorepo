import { useEffect, useState } from 'react';
import { apiClient } from '@/api';
import type { components } from '@/api/schema';
import { AvatarStack } from '@/components/Avatar';
import { Card } from '@/components/Card';
import { ModePill } from '@/components/ModePill';
import { ModeSelector } from '@/components/ModeSelector';
import { PageLayout } from '@/components/PageLayout';
import { usePlayer } from '@/hooks/PlayerContext';

type GameHistory = components['schemas']['GameHistory'];

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
  const [history, setHistory] = useState<GameHistory[]>([]);
  const [variant, setVariant] = useState<VariantFilter>('all');
  const [type, setType] = useState<TypeFilter>('all');
  const [result, setResult] = useState<ResultFilter>('all');

  useEffect(() => {
    if (!player) return;
    const controller = new AbortController();
    apiClient
      .GET('/players/{player_id}/game-history', {
        params: { path: { player_id: player.id } },
        signal: controller.signal,
      })
      .then(({ data }) => {
        if (data) setHistory(data);
      })
      .catch((e: unknown) => {
        if ((e as { name?: string })?.name !== 'AbortError') throw e;
      });
    return () => controller.abort();
  }, [player]);

  const filtered = history.filter((row) => {
    if (variant === 'maxi' && !row.mode.startsWith('maxi')) return false;
    if (variant === 'yatzy' && !row.mode.startsWith('yatzy')) return false;
    if (type === 'regular' && row.mode.includes('sequential')) return false;
    if (type === 'sequential' && !row.mode.includes('sequential')) return false;
    if (result === 'wins' && row.rank !== 1) return false;
    if (result === 'losses' && row.rank === 1) return false;
    return true;
  });

  return (
    <PageLayout>
      <div className="flex flex-col gap-4">
        <Card className="px-4 py-3 flex items-center gap-3 flex-wrap">
          <span className="text-[13px] font-semibold text-foreground">History</span>
          <ModeSelector
            options={[
              { label: 'All', value: 'all' as VariantFilter },
              { label: 'Maxi', value: 'maxi' as VariantFilter },
              { label: 'Yatzy', value: 'yatzy' as VariantFilter },
            ]}
            selected={variant}
            onChange={setVariant}
          />
          <ModeSelector
            options={[
              { label: 'All', value: 'all' as TypeFilter },
              { label: 'Regular', value: 'regular' as TypeFilter },
              { label: 'Sequential', value: 'sequential' as TypeFilter },
            ]}
            selected={type}
            onChange={setType}
          />
          <ModeSelector
            options={[
              { label: 'All', value: 'all' as ResultFilter },
              { label: 'Wins', value: 'wins' as ResultFilter },
              { label: 'Losses', value: 'losses' as ResultFilter },
            ]}
            selected={result}
            onChange={setResult}
          />
        </Card>

        <Card className="px-4 py-3">
          <ul className="flex flex-col divide-y divide-[var(--border)]">
            {filtered.map((row) => (
              <li key={row.game_id} className="py-3 first:pt-0 last:pb-0">
                <div className="flex items-center gap-3">
                  <AvatarStack names={row.players.map((p) => p.player_name)} size="md" />
                  <div className="flex flex-col gap-0.5 flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <ModePill mode={row.mode} />
                    </div>
                    <div className="text-[12px] text-[var(--text-muted)] truncate">
                      {row.players.map((p) => p.player_name).join(', ')}
                    </div>
                  </div>
                  <div className="flex items-center gap-3 flex-shrink-0">
                    <span
                      className={`text-[11px] font-semibold px-2 py-0.5 rounded-full ${
                        row.rank === 1
                          ? 'bg-[rgba(94,203,138,0.15)] text-[var(--green)]'
                          : 'bg-[rgba(240,101,96,0.12)] text-[var(--red)]'
                      }`}
                    >
                      {ordinal(row.rank)}
                    </span>
                    <span className="text-[14px] font-bold text-foreground">{row.score}</span>
                    <span className="text-[11px] text-[var(--text-dim)] w-16 text-right">
                      {formatGameDate(row.finished_at)}
                    </span>
                  </div>
                </div>
              </li>
            ))}
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
        </Card>
      </div>
    </PageLayout>
  );
}
