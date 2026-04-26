import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import type { components } from '@/api';
import { apiClient } from '@/api';
import { Avatar } from '@/components/Avatar';
import { Card } from '@/components/Card';
import { LeaderboardHeader } from '@/components/Leaderboard';
import { ModePill } from '@/components/ModePill';
import { PageLayout } from '@/components/PageLayout';
import { usePlayerNames } from '@/hooks/PlayerNamesContext';
import { useErrorToast } from '@/hooks/use-toast';

type PlayerScore = components['schemas']['PlayerScore'];
type GameMode = components['schemas']['GameMode'];

export function EndScreen() {
  const { gameId } = useParams<{ gameId: string }>();
  const navigate = useNavigate();
  const errorToast = useErrorToast();

  const [finalScores, setFinalScores] = useState<PlayerScore[]>([]);
  const [winnerIds, setWinnerIds] = useState<number[]>([]);
  const [gameMode, setGameMode] = useState<GameMode | null>(null);
  const { names: playerNames, pictures: playerPictures } = usePlayerNames();

  useEffect(() => {
    apiClient
      .GET('/games/{game_id}/state', { params: { path: { game_id: Number(gameId) } } })
      .then(({ data: state, error }) => {
        if (error || !state) {
          errorToast('Failed to load results');
          return;
        }
        if (state.status !== 'finished') {
          navigate(`/games/${gameId}`);
          return;
        }
        setFinalScores(state.final_scores ?? []);
        setWinnerIds(state.winner_ids ?? []);
        setGameMode(state.mode ?? null);
      })
      .catch(() => errorToast('Failed to load results'));
  }, [gameId, navigate, errorToast]);

  const sorted = [...finalScores].sort((a, b) => b.total - a.total);

  let rankCounter = 1;
  const withRanks = sorted.map((score, index) => {
    if (index === 0) {
      rankCounter = 1;
    } else if (sorted[index - 1].total !== score.total) {
      rankCounter = index + 1;
    }
    return { ...score, rank: rankCounter };
  });

  const winnerScore = withRanks[0];
  const winnerName = winnerScore
    ? (playerNames[winnerScore.player_id] ?? `Player ${winnerScore.player_id}`)
    : null;

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
    <PageLayout>
      <div className="flex flex-col gap-4">
        {winnerName && winnerScore && (
          <Card className="flex items-center gap-4 h-[78px] px-4">
            <div className="w-11 h-11 rounded-full flex items-center justify-center text-[17px] font-bold flex-shrink-0 bg-[rgba(240,180,41,0.2)] border-2 border-[rgba(240,180,41,0.5)] text-[var(--amber)]">
              {winnerName[0]?.toUpperCase()}
            </div>
            <div className="flex flex-col gap-0.5 flex-1">
              <div className="text-[17px] font-bold text-foreground">{winnerAnnouncement}</div>
              <div className="text-[12px] text-[var(--text-muted)]">
                {gameMode != null && <ModePill mode={gameMode} />}
              </div>
            </div>
            <div className="text-[28px] font-bold text-[var(--amber)] flex-shrink-0">
              {winnerScore.total}
            </div>
          </Card>
        )}

        <Card className="px-4 py-[14px]">
          <table className="w-full border-collapse">
            <LeaderboardHeader rankColWidth="w-7" />
            <tbody>
              {withRanks.map((score, idx) => {
                const isWinner = winnerIds.includes(score.player_id);
                const name = playerNames[score.player_id] ?? `Player ${score.player_id}`;
                return (
                  <tr
                    key={score.player_id}
                    data-testid={isWinner ? `winner-row-${score.player_id}` : undefined}
                    className="border-b border-[var(--border)] last:border-b-0"
                  >
                    <td
                      className={`py-[10px] px-2 text-[12px] font-bold w-7 ${isWinner ? 'text-[var(--amber)]' : 'text-[var(--text-dim)]'}`}
                    >
                      {score.rank}
                    </td>
                    <td className="py-[10px] px-2">
                      <div className="flex items-center gap-[10px]">
                        <Avatar
                          name={name}
                          index={idx}
                          playerId={score.player_id}
                          hasPicture={playerPictures[score.player_id] ?? false}
                          size="sm"
                        />
                        <span
                          className={`text-[13px] font-medium ${isWinner ? 'text-foreground' : 'text-foreground'}`}
                        >
                          {name}
                        </span>
                      </div>
                    </td>
                    <td
                      className={`py-[10px] px-2 text-[14px] font-bold text-right ${isWinner ? 'text-[var(--amber)]' : 'text-foreground'}`}
                    >
                      {score.total}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </Card>

        <div className="flex items-center justify-end">
          <button
            type="button"
            onClick={() => navigate('/lobby')}
            style={{ transitionTimingFunction: 'cubic-bezier(0.34,1.56,0.64,1)' }}
            className="h-[34px] px-[18px] rounded-lg bg-[var(--accent)] text-white text-[13px] font-semibold border-none cursor-pointer transition-[transform,box-shadow] duration-[180ms] hover:scale-[1.05] hover:shadow-[0_0_18px_rgba(124,158,248,0.4)] active:scale-[0.96]"
          >
            Available games
          </button>
        </div>
      </div>
    </PageLayout>
  );
}
