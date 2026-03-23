import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import type { components } from '@/api';
import { apiClient } from '@/api';
import { Button } from '@/components/ui/button';
import { toast } from '@/hooks/use-toast';

type PlayerScore = components['schemas']['PlayerScore'];

function errorToast(title: string) {
  toast({ variant: 'destructive', title, description: 'Please try again.' });
}

export function EndScreen() {
  const { gameId } = useParams<{ gameId: string }>();
  const navigate = useNavigate();

  const [finalScores, setFinalScores] = useState<PlayerScore[]>([]);
  const [winnerIds, setWinnerIds] = useState<number[]>([]);
  const [playerNames, setPlayerNames] = useState<Record<number, string>>({});

  useEffect(() => {
    Promise.all([
      apiClient.GET('/players'),
      apiClient.GET('/games/{game_id}/state', { params: { path: { game_id: Number(gameId) } } }),
    ])
      .then(([{ data: players }, { data: state, error }]) => {
        if (error || !state) {
          errorToast('Failed to load results');
          return;
        }
        if (state.status !== 'finished') {
          navigate(`/games/${gameId}`);
          return;
        }
        if (players) {
          setPlayerNames(Object.fromEntries(players.map((p) => [p.id, p.name])));
        }
        setFinalScores(state.final_scores ?? []);
        setWinnerIds(state.winner_ids ?? []);
      })
      .catch(() => errorToast('Failed to load results'));
  }, [gameId, navigate]);

  const sorted = [...finalScores].sort((a, b) => b.total - a.total);

  const ranked = sorted.map((score, index) => {
    const rank = index === 0 ? 1 : sorted[index - 1].total === score.total ? 0 : index + 1;
    return { ...score, rank };
  });

  let rankCounter = 1;
  const withRanks = ranked.map((score, index) => {
    if (index === 0) {
      rankCounter = 1;
    } else if (sorted[index - 1].total !== score.total) {
      rankCounter = index + 1;
    }
    return { ...score, rank: rankCounter };
  });

  const winnerNames = winnerIds.map((id) => playerNames[id]).filter(Boolean);
  const winnerAnnouncement =
    winnerNames.length === 0
      ? null
      : winnerNames.length === 1
        ? `${winnerNames[0]} wins!`
        : winnerNames.length === 2
          ? `${winnerNames[0]} & ${winnerNames[1]} win!`
          : "It's a tie!";

  return (
    <div className="min-h-screen bg-gray-950 p-6">
      <div className="max-w-lg mx-auto flex flex-col gap-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Yatzy</h1>
          <p className="text-gray-400 text-sm">Game #{gameId}</p>
        </div>

        {winnerAnnouncement && (
          <p className="text-xl font-semibold text-yellow-400">🏆 {winnerAnnouncement}</p>
        )}

        <table className="w-full text-sm text-white">
          <thead>
            <tr className="text-gray-400 text-left border-b border-gray-800">
              <th className="pb-2 w-8">#</th>
              <th className="pb-2">Player</th>
              <th className="pb-2 text-right">Score</th>
            </tr>
          </thead>
          <tbody>
            {withRanks.map((score) => {
              const isWinner = winnerIds.includes(score.player_id);
              return (
                <tr
                  key={score.player_id}
                  data-testid={isWinner ? `winner-row-${score.player_id}` : undefined}
                  className={isWinner ? 'text-yellow-400' : ''}
                >
                  <td className="py-2">{score.rank}</td>
                  <td className="py-2">
                    {playerNames[score.player_id] ?? `Player ${score.player_id}`}
                  </td>
                  <td className="py-2 text-right">{score.total}</td>
                </tr>
              );
            })}
          </tbody>
        </table>

        <Button onClick={() => navigate('/lobby')}>Back to Lobby</Button>
      </div>
    </div>
  );
}
