import { useEffect, useState } from 'react';
import { apiClient } from '@/api';
import type { components } from '@/api/schema';
import { PageLayout } from '@/components/PageLayout';
import { formatDate } from '@/lib/format';

type HighScore = components['schemas']['HighScore'];
type GameMode = components['schemas']['GameMode'];

function HighScoresTable({ scores }: { scores: HighScore[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm text-white">
        <thead>
          <tr className="text-gray-400 text-left border-b border-gray-800">
            <th className="pb-2 w-8">#</th>
            <th className="pb-2">Player</th>
            <th className="pb-2 text-right">Score</th>
            <th className="pb-2 text-right">Game</th>
            <th className="pb-2 text-right">Date</th>
          </tr>
        </thead>
        <tbody>
          {scores.map((score, index) => (
            <tr key={`${score.game_id}-${score.player_id}`} className="border-b border-gray-800/50">
              <td className="py-2 text-gray-400">{index + 1}</td>
              <td className="py-2">{score.player_name}</td>
              <td className="py-2 text-right font-semibold">{score.total_score}</td>
              <td className="py-2 text-right text-gray-400">#{score.game_id}</td>
              <td className="py-2 text-right text-gray-400">{formatDate(score.finished_at)}</td>
            </tr>
          ))}
          {scores.length === 0 && (
            <tr>
              <td colSpan={5} className="py-4 text-center text-gray-400">
                No high scores yet
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

const MODE_LABELS: Record<GameMode, string> = {
  standard: 'Standard',
  sequential: 'Sequential',
};

const MODES: GameMode[] = ['standard', 'sequential'];

export function HighScoresScreen() {
  const [scores, setScores] = useState<HighScore[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiClient.GET('/high-scores').then(({ data, error }) => {
      if (error) {
        setError('Failed to load high scores');
      } else if (data) {
        setScores(data);
      }
      setIsLoading(false);
    });
  }, []);

  return (
    <PageLayout>
      <h1 className="text-white text-xl font-semibold mb-6">High Scores</h1>

      {isLoading && <p className="text-gray-400 text-sm">Loading...</p>}
      {error && <p className="text-red-400 text-sm">{error}</p>}

      {!isLoading && !error && (
        <div className="flex flex-col gap-8">
          {MODES.map((mode) => (
            <div key={mode}>
              <h2 className="text-white font-semibold mb-3">{MODE_LABELS[mode]}</h2>
              <HighScoresTable scores={scores.filter((s) => s.mode === mode)} />
            </div>
          ))}
        </div>
      )}
    </PageLayout>
  );
}
