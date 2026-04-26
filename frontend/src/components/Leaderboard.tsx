import { Avatar } from '@/components/Avatar';
import { RANK_COLORS } from '@/lib/constants';

const TH = 'pb-2 px-2 text-[10px] font-bold uppercase tracking-[0.08em] text-[var(--text-dim)]';

export function LeaderboardHeader({
  rankColWidth = 'w-8',
  scoreLabel = 'Score',
}: {
  rankColWidth?: string;
  scoreLabel?: string;
}) {
  return (
    <thead>
      <tr className="border-b border-[var(--border)]">
        <th className={`${TH} ${rankColWidth} text-left`}>#</th>
        <th className={`${TH} text-left`}>Player</th>
        <th className={`${TH} text-right`}>{scoreLabel}</th>
      </tr>
    </thead>
  );
}

export function LeaderboardRow({
  rank,
  playerId,
  playerName,
  hasPicture,
  score,
}: {
  rank: number;
  playerId: number;
  playerName: string;
  hasPicture: boolean;
  score: number;
}) {
  const idx = rank - 1;
  return (
    <tr className="border-b border-[var(--border)] last:border-b-0">
      <td
        className={`py-[10px] px-2 text-[12px] font-bold w-8 ${RANK_COLORS[idx] ?? 'text-[var(--text-dim)]'}`}
      >
        {rank}
      </td>
      <td className="py-[10px] px-2">
        <div className="flex items-center gap-[10px]">
          <Avatar
            name={playerName}
            index={idx}
            size="lg"
            playerId={playerId}
            hasPicture={hasPicture}
          />
          <span className="text-[13px] font-medium text-foreground">{playerName}</span>
        </div>
      </td>
      <td className="py-[10px] px-2 text-[14px] font-bold text-right text-foreground">{score}</td>
    </tr>
  );
}
