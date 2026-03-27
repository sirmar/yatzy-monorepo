import type { components } from '@/api';
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

  function renderCell(playerId: number, category: ScoreCategory) {
    const entry = getEntry(playerId, category);

    if (entry?.score !== null && entry?.score !== undefined) {
      return <span>{entry.score}</span>;
    }

    if (playerId === myPlayerId && isMyTurn && hasRolled) {
      const option = scoringOptions?.find((o) => o.category === category);
      if (option) {
        return (
          <span className="relative inline-block text-yellow-300 font-semibold">
            {option.score}
            <span
              aria-hidden="true"
              className="absolute left-full pl-1 opacity-0 group-hover/row:opacity-100 text-white"
            >
              ✓
            </span>
          </span>
        );
      }
      if (mode === 'maxi_sequential' || mode === 'yatzy_sequential') return null;
      return (
        <span className="relative inline-block text-gray-500">
          ×
          <span
            aria-hidden="true"
            className="absolute left-full pl-1 opacity-0 group-hover/row:opacity-100 text-white"
          >
            ✓
          </span>
        </span>
      );
    }

    return null;
  }

  function renderCategoryRow(cat: ScoreCategory) {
    const clickable = isClickable(cat);
    return (
      <tr
        key={cat}
        className={cn(
          'border-b border-gray-800',
          clickable && 'group/row hover:bg-white/5 cursor-pointer'
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
        <th scope="row" className="text-left py-1 px-2 text-gray-400 font-normal">
          {CATEGORY_LABELS[cat]}
        </th>
        {playerIds.map((pid) => (
          <td key={pid} className="py-1 px-2 text-center">
            {renderCell(pid, cat)}
          </td>
        ))}
      </tr>
    );
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

  return (
    <div className="overflow-x-auto">
      <table className="text-sm text-white border-collapse">
        <thead>
          <tr className="border-b border-gray-700">
            <th className="text-left py-1 px-2 text-gray-400 font-normal w-36" />
            {playerIds.map((pid) => (
              <th
                key={pid}
                scope="col"
                className={cn(
                  'py-1 px-2 text-center font-semibold',
                  pid === currentPlayerId ? 'text-yellow-400' : 'text-white'
                )}
              >
                {playerNames[pid] ?? `Player ${pid}`}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {upperCategories.map(renderCategoryRow)}
          <tr className="border-b border-gray-700 bg-gray-800/50">
            <th scope="row" className="text-left py-1 px-2 text-gray-400 font-normal text-xs">
              Subtotal
            </th>
            {playerIds.map((pid) => (
              <td key={pid} className="py-1 px-2 text-center text-gray-300 text-xs">
                {upperSubtotal(pid)}
              </td>
            ))}
          </tr>
          <tr className="border-b border-gray-700 bg-gray-800/50">
            <th scope="row" className="text-left py-1 px-2 text-gray-400 font-normal text-xs">
              Bonus
            </th>
            {playerIds.map((pid) => (
              <td key={pid} className="py-1 px-2 text-center text-gray-300 text-xs">
                {getBonus(pid) ?? '—'}
              </td>
            ))}
          </tr>
          {lowerCategories.map(renderCategoryRow)}
          <tr className="border-t border-gray-600">
            <th scope="row" className="text-left py-1 px-2 text-white font-semibold">
              Total
            </th>
            {playerIds.map((pid) => (
              <td key={pid} className="py-1 px-2 text-center font-semibold text-white">
                {getTotal(pid)}
              </td>
            ))}
          </tr>
        </tbody>
      </table>
    </div>
  );
}
