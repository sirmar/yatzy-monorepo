import type { components } from '@/api';
import { Avatar } from '@/components/Avatar';
import { cn } from '@/lib/utils';

type PlayerScorecard = components['schemas']['PlayerScorecard'];
type ScoringOption = components['schemas']['ScoringOption'];
type ScoreCategory = components['schemas']['ScoreCategory'];
type GameMode = components['schemas']['GameMode'];

const UPPER_CATEGORIES = new Set<ScoreCategory>([
  'ones',
  'twos',
  'threes',
  'fours',
  'fives',
  'sixes',
]);

const CATEGORY_LABELS: Record<ScoreCategory, string> = {
  ones: 'Ones',
  twos: 'Twos',
  threes: 'Threes',
  fours: 'Fours',
  fives: 'Fives',
  sixes: 'Sixes',
  one_pair: 'One pair',
  two_pairs: 'Two pairs',
  three_pairs: 'Three pairs',
  three_of_a_kind: 'Three of a kind',
  four_of_a_kind: 'Four of a kind',
  five_of_a_kind: 'Five of a kind',
  small_straight: 'Small straight',
  large_straight: 'Large straight',
  full_straight: 'Full straight',
  full_house: 'Full house',
  villa: 'Villa',
  tower: 'Tower',
  chance: 'Chance',
  maxi_yatzy: 'Maxi Yatzy',
  yatzy: 'Yatzy',
};

const BONUS_THRESHOLD: Partial<Record<GameMode, number>> = {
  maxi: 84,
  maxi_sequential: 84,
  yatzy: 63,
  yatzy_sequential: 63,
};

interface Props {
  scoreboard: PlayerScorecard[];
  playerNames: Record<number, string>;
  currentPlayerId: number | null;
  myPlayerId: number;
  scoringOptions: ScoringOption[] | null;
  hasRolled: boolean;
  isMyTurn: boolean;
  mode?: GameMode;
  onScore: (category: ScoreCategory) => void;
}

export function ScoreCard({
  scoreboard,
  playerNames,
  currentPlayerId,
  myPlayerId,
  scoringOptions,
  hasRolled,
  isMyTurn,
  mode,
  onScore,
}: Props) {
  const playerIds = scoreboard.map((s) => s.player_id);
  const allCategories: ScoreCategory[] = scoreboard[0]?.entries.map((e) => e.category) ?? [];
  const upperCategories = allCategories.filter((c) => UPPER_CATEGORIES.has(c));
  const lowerCategories = allCategories.filter((c) => !UPPER_CATEGORIES.has(c));
  const bonusThreshold = mode ? (BONUS_THRESHOLD[mode] ?? null) : null;

  function getEntry(playerId: number, category: ScoreCategory) {
    return scoreboard
      .find((s) => s.player_id === playerId)
      ?.entries.find((e) => e.category === category);
  }

  function isClickable(category: ScoreCategory) {
    const entry = getEntry(myPlayerId, category);
    const isUnscored = entry?.score === null || entry?.score === undefined;
    if (!isMyTurn || !hasRolled || !isUnscored) return false;
    if (mode === 'maxi_sequential' || mode === 'yatzy_sequential') {
      return scoringOptions?.some((o) => o.category === category) ?? false;
    }
    return true;
  }

  function upperSubtotal(playerId: number) {
    return upperCategories.reduce((sum, cat) => {
      const entry = getEntry(playerId, cat);
      return sum + (entry?.score ?? 0);
    }, 0);
  }

  function getBonus(playerId: number) {
    return scoreboard.find((s) => s.player_id === playerId)?.bonus ?? null;
  }

  function getTotal(playerId: number) {
    return scoreboard.find((s) => s.player_id === playerId)?.total ?? 0;
  }

  function renderCell(playerId: number, category: ScoreCategory) {
    const entry = getEntry(playerId, category);
    const isActive = playerId === currentPlayerId;

    if (entry?.score !== null && entry?.score !== undefined) {
      return (
        <td
          key={playerId}
          className={cn(
            'py-[6px] px-[14px] text-[13px] text-right',
            entry.last_scored ? 'text-[var(--green)] font-semibold' : 'text-foreground font-medium',
            isActive && 'relative'
          )}
        >
          {isActive && (
            <span
              aria-hidden="true"
              className="absolute inset-0 bg-[rgba(124,158,248,0.05)] pointer-events-none"
            />
          )}
          {entry.score}
        </td>
      );
    }

    if (playerId === myPlayerId && isMyTurn && hasRolled) {
      const option = scoringOptions?.find((o) => o.category === category);
      if (option) {
        return (
          <td
            key={playerId}
            className={cn(
              'py-[6px] px-[14px] text-[13px] text-right text-[var(--amber)] font-semibold',
              isActive && 'relative'
            )}
          >
            {isActive && (
              <span
                aria-hidden="true"
                className="absolute inset-0 bg-[rgba(124,158,248,0.05)] pointer-events-none"
              />
            )}
            {option.score} ↑
          </td>
        );
      }
      if (mode === 'maxi_sequential' || mode === 'yatzy_sequential') {
        return (
          <td
            key={playerId}
            className={cn('py-[6px] px-[14px] text-[13px] text-right', isActive && 'relative')}
          >
            {isActive && (
              <span
                aria-hidden="true"
                className="absolute inset-0 bg-[rgba(124,158,248,0.05)] pointer-events-none"
              />
            )}
          </td>
        );
      }
      return (
        <td
          key={playerId}
          className={cn(
            'py-[6px] px-[14px] text-[13px] text-right text-[var(--text-dim)]',
            isActive && 'relative'
          )}
        >
          {isActive && (
            <span
              aria-hidden="true"
              className="absolute inset-0 bg-[rgba(124,158,248,0.05)] pointer-events-none"
            />
          )}
          —
        </td>
      );
    }

    return (
      <td
        key={playerId}
        className={cn(
          'py-[6px] px-[14px] text-[13px] text-right text-[var(--text-muted)]',
          isActive && 'relative'
        )}
      >
        {isActive && (
          <span
            aria-hidden="true"
            className="absolute inset-0 bg-[rgba(124,158,248,0.05)] pointer-events-none"
          />
        )}
      </td>
    );
  }

  function renderCategoryRow(cat: ScoreCategory) {
    const clickable = isClickable(cat);
    return (
      <tr
        key={cat}
        className={cn(
          'border-b border-[var(--border)] cursor-default',
          clickable && 'scorable hover:bg-[var(--surface-2)] cursor-pointer'
        )}
        onClick={clickable ? () => onScore(cat) : undefined}
        onKeyDown={
          clickable
            ? (e) => {
                if (e.key === 'Enter' || e.key === ' ') onScore(cat);
              }
            : undefined
        }
      >
        <td className="py-[6px] px-[14px] pl-5 text-[13px] font-medium text-foreground text-left">
          {CATEGORY_LABELS[cat]}
        </td>
        {playerIds.map((pid) => renderCell(pid, cat))}
      </tr>
    );
  }

  return (
    <div className="bg-[var(--surface)] border border-[var(--border)] rounded-[14px] overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full border-collapse min-w-[480px]">
          <thead>
            <tr className="border-b border-[var(--border-2)]">
              <th className="py-2 px-[14px] pl-5 text-[12px] font-semibold uppercase tracking-[0.06em] text-[var(--text-muted)] text-left align-middle">
                Category
              </th>
              {playerIds.map((pid, idx) => {
                const isActive = pid === currentPlayerId;
                const name = playerNames[pid] ?? `Player ${pid}`;
                return (
                  <th
                    key={pid}
                    className={cn(
                      'py-2 px-[14px] text-[12px] font-semibold uppercase tracking-[0.06em] text-right align-middle',
                      isActive ? 'text-foreground' : 'text-[var(--text-muted)]'
                    )}
                  >
                    <span className="inline-flex items-center justify-end gap-1.5">
                      {isActive && (
                        <span
                          aria-hidden="true"
                          className="inline-block w-[6px] h-[6px] rounded-full bg-[var(--green)] shadow-[0_0_6px_var(--green)] animate-pulse flex-shrink-0"
                        />
                      )}
                      <Avatar name={name} index={idx} size="sm" />
                      {name}
                    </span>
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody>
            <tr className="bg-[var(--surface-2)] border-b border-[var(--border)]">
              <td
                colSpan={playerIds.length + 1}
                className="py-[5px] px-[14px] pl-5 text-[10px] font-bold uppercase tracking-[0.1em] text-[var(--text-dim)]"
              >
                Upper section
              </td>
            </tr>
            {upperCategories.map(renderCategoryRow)}
            <tr className="bg-[var(--surface-2)] border-b border-[var(--border)]">
              <td
                colSpan={playerIds.length + 1}
                className="py-[5px] px-[14px] pl-5 text-[10px] font-bold uppercase tracking-[0.1em] text-[var(--text-dim)]"
              >
                Subtotal
              </td>
            </tr>
            <tr className="border-b border-[var(--border)]">
              <td className="py-[6px] px-[14px] pl-5 text-[13px] font-medium text-foreground text-left">
                Sum
              </td>
              {playerIds.map((pid) => {
                const sub = upperSubtotal(pid);
                const isActive = pid === currentPlayerId;
                return (
                  <td
                    key={pid}
                    className={cn(
                      'py-[6px] px-[14px] text-[13px] text-right text-foreground font-medium',
                      isActive && 'relative'
                    )}
                  >
                    {isActive && (
                      <span
                        aria-hidden="true"
                        className="absolute inset-0 bg-[rgba(124,158,248,0.05)] pointer-events-none"
                      />
                    )}
                    {bonusThreshold != null ? `${sub} / ${bonusThreshold}` : sub}
                  </td>
                );
              })}
            </tr>
            <tr className="border-b border-[var(--border)]">
              <td className="py-[6px] px-[14px] pl-5 text-[13px] font-medium text-foreground text-left">
                Bonus
              </td>
              {playerIds.map((pid) => {
                const bonus = getBonus(pid);
                const sub = upperSubtotal(pid);
                const isActive = pid === currentPlayerId;
                let content: string;
                let colorCls: string;
                if (bonus !== null) {
                  content = String(bonus);
                  colorCls = 'text-[var(--green)]';
                } else if (bonusThreshold != null) {
                  const needed = bonusThreshold - sub;
                  if (needed <= 0) {
                    content = '—';
                    colorCls = 'text-[var(--text-dim)]';
                  } else {
                    content = `+${needed} needed`;
                    colorCls = 'text-[var(--amber)]';
                  }
                } else {
                  content = '—';
                  colorCls = 'text-[var(--text-dim)]';
                }
                return (
                  <td
                    key={pid}
                    className={cn(
                      'py-[6px] px-[14px] text-[13px] text-right font-medium',
                      colorCls,
                      isActive && 'relative'
                    )}
                  >
                    {isActive && (
                      <span
                        aria-hidden="true"
                        className="absolute inset-0 bg-[rgba(124,158,248,0.05)] pointer-events-none"
                      />
                    )}
                    {content}
                  </td>
                );
              })}
            </tr>
            <tr className="bg-[var(--surface-2)] border-b border-[var(--border)]">
              <td
                colSpan={playerIds.length + 1}
                className="py-[5px] px-[14px] pl-5 text-[10px] font-bold uppercase tracking-[0.1em] text-[var(--text-dim)]"
              >
                Lower section
              </td>
            </tr>
            {lowerCategories.map(renderCategoryRow)}
            <tr className="bg-[var(--surface-2)]">
              <td className="py-2 px-[14px] pl-5 text-[11px] font-bold uppercase tracking-[0.08em] text-[var(--text-muted)] text-left">
                Total
              </td>
              {playerIds.map((pid) => {
                const isActive = pid === currentPlayerId;
                return (
                  <td
                    key={pid}
                    className={cn(
                      'py-2 px-[14px] text-[14px] font-bold text-foreground text-right',
                      isActive && 'relative'
                    )}
                  >
                    {isActive && (
                      <span
                        aria-hidden="true"
                        className="absolute inset-0 bg-[rgba(124,158,248,0.05)] pointer-events-none"
                      />
                    )}
                    {getTotal(pid)}
                  </td>
                );
              })}
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
