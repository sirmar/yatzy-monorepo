import { useEffect, useState } from 'react';
import { apiClient } from '@/api';
import type { components } from '@/api/schema';
import { Card } from '@/components/Card';
import { LeaderboardHeader, LeaderboardRow } from '@/components/Leaderboard';
import { ModeSelector } from '@/components/ModeSelector';
import { PageLayout } from '@/components/PageLayout';
import { usePlayerNames } from '@/hooks/PlayerNamesContext';
import { ignoreAbort } from '@/lib/utils';

type HighScore = components['schemas']['HighScore'];
type GameMode = components['schemas']['GameMode'];

const TABS: { label: string; value: GameMode }[] = [
  { label: 'Maxi Yatzy', value: 'maxi' },
  { label: 'Maxi Seq.', value: 'maxi_sequential' },
  { label: 'Yatzy', value: 'yatzy' },
  { label: 'Yatzy Seq.', value: 'yatzy_sequential' },
];

export function HighScoresScreen() {
  const [scores, setScores] = useState<HighScore[]>([]);
  const [mode, setMode] = useState<GameMode>('maxi');
  const { pictures } = usePlayerNames();

  useEffect(() => {
    const controller = new AbortController();
    apiClient
      .GET('/high-scores', { signal: controller.signal })
      .then(({ data }) => {
        if (data) setScores(data);
      })
      .catch(ignoreAbort);
    return () => controller.abort();
  }, []);

  const filtered = scores.filter((s) => s.mode === mode);

  return (
    <PageLayout>
      <div className="flex flex-col gap-4">
        <Card className="px-4 py-3 flex items-center gap-3 flex-wrap">
          <span className="text-[11px] font-bold uppercase tracking-[0.08em] text-foreground">
            High Scores
          </span>
          <ModeSelector options={TABS} selected={mode} onChange={setMode} />
        </Card>

        <Card className="px-4 py-[14px]">
          <table className="w-full border-collapse table-fixed">
            <LeaderboardHeader />
            <tbody>
              {filtered.map((score, idx) => (
                <LeaderboardRow
                  key={`${score.game_id}-${score.player_id}`}
                  rank={idx + 1}
                  playerId={score.player_id}
                  playerName={score.player_name}
                  hasPicture={pictures[score.player_id] ?? false}
                  score={score.total_score}
                />
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={3} className="py-6 text-center text-[13px] text-[var(--text-muted)]">
                    No scores yet
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
