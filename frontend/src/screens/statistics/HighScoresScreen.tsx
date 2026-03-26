import { useEffect, useState } from 'react';
import { apiClient } from '@/api';
import type { components } from '@/api/schema';
import { PageLayout } from '@/components/PageLayout';
import { formatDate } from '@/lib/format';

type HighScore = components['schemas']['HighScore'];
type GameMode = components['schemas']['GameMode'];

const MODES: { label: string; value: GameMode }[] = [
  { label: 'Standard', value: 'standard' },
  { label: 'Sequential', value: 'sequential' },
];

const RANK_TROPHY: Record<number, string> = { 1: '🥇', 2: '🥈', 3: '🥉' };

function HighScoresTable({ scores }: { scores: HighScore[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full table-fixed text-sm text-white">
        <thead>
          <tr className="text-gray-400 text-left border-b border-gray-800">
            <th className="pb-2 w-8">#</th>
            <th className="pb-2">Player</th>
            <th className="pb-2 w-20 text-right">Score</th>
            <th className="pb-2 w-16 text-right">Game</th>
            <th className="pb-2 w-28 text-right">Date</th>
          </tr>
        </thead>
        <tbody>
          {scores.map((score, index) => (
            <tr key={`${score.game_id}-${score.player_id}`} className="border-b border-gray-800/50">
              <td className="py-2 text-gray-400">{RANK_TROPHY[index + 1] ?? index + 1}</td>
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

export function HighScoresScreen() {
  const [scores, setScores] = useState<HighScore[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedMode, setSelectedMode] = useState<GameMode>('standard');

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

      <div className="flex gap-2 mb-6">
        {MODES.map(({ label, value }) => (
          <button
            key={value}
            type="button"
            onClick={() => setSelectedMode(value)}
            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
              selectedMode === value
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

      {!isLoading && !error && (
        <HighScoresTable scores={scores.filter((s) => s.mode === selectedMode)} />
      )}
    </PageLayout>
  );
}
