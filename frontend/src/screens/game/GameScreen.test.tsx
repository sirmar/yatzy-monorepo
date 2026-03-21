import { renderWithProviders } from '@/test/helpers';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { afterAll, afterEach, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import { GameScreen } from './GameScreen';

const mockNavigate = vi.hoisted(() => vi.fn());
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useParams: () => ({ gameId: '42' }),
  };
});

const server = setupServer();
beforeAll(() => server.listen());
afterEach(() => {
  server.resetHandlers();
  mockNavigate.mockReset();
  sessionStorage.clear();
});
afterAll(() => server.close());

const STATE_URL = 'http://localhost/api/games/42/state';
const BOARD_URL = 'http://localhost/api/games/42/scoreboard';
const ROLL_URL = 'http://localhost/api/games/42/roll';
const OPTIONS_URL = (pid: number) => `http://localhost/api/games/42/players/${pid}/scoring-options`;
const SCORE_URL = (pid: number) => `http://localhost/api/games/42/players/${pid}/scorecard`;
const PLAYERS_URL = 'http://localhost/api/players';

const ALICE = { id: 1, name: 'Alice', created_at: '' };
const BOB = { id: 2, name: 'Bob', created_at: '' };

type ScoreCategory =
  | 'ones'
  | 'twos'
  | 'threes'
  | 'fours'
  | 'fives'
  | 'sixes'
  | 'one_pair'
  | 'two_pairs'
  | 'three_pairs'
  | 'three_of_a_kind'
  | 'four_of_a_kind'
  | 'five_of_a_kind'
  | 'small_straight'
  | 'large_straight'
  | 'full_straight'
  | 'full_house'
  | 'villa'
  | 'tower'
  | 'chance'
  | 'maxi_yatzy';

const ALL_CATEGORIES: ScoreCategory[] = [
  'ones',
  'twos',
  'threes',
  'fours',
  'fives',
  'sixes',
  'one_pair',
  'two_pairs',
  'three_pairs',
  'three_of_a_kind',
  'four_of_a_kind',
  'five_of_a_kind',
  'small_straight',
  'large_straight',
  'full_straight',
  'full_house',
  'villa',
  'tower',
  'chance',
  'maxi_yatzy',
];

function makeDice(values: (number | null)[] = Array(6).fill(null)) {
  return values.map((value, index) => ({ index, value, kept: false }));
}

function makeScorecard(playerId: number, scores: Partial<Record<ScoreCategory, number>> = {}) {
  return {
    player_id: playerId,
    entries: ALL_CATEGORIES.map((cat) => ({
      category: cat,
      score: scores[cat] ?? null,
    })),
    bonus: null,
    total: Object.values(scores).reduce((s, v) => s + (v ?? 0), 0),
  };
}

describe('GameScreen', () => {
  beforeEach(() => {
    sessionStorage.setItem('yatzy_player', JSON.stringify(ALICE));
    givenPlayers([ALICE, BOB]);
    givenGameState({
      status: 'active',
      current_player_id: ALICE.id,
      dice: makeDice(),
      rolls_remaining: 3,
      saved_rolls: 0,
    });
    givenScoreboard([makeScorecard(ALICE.id), makeScorecard(BOB.id)]);
  });

  describe('game state display', () => {
    it('shows player names in scorecard header', async () => {
      whenRendered();
      await thenColumnHeaderIsVisible('Alice');
      await thenColumnHeaderIsVisible('Bob');
    });

    it('shows whose turn it is', async () => {
      whenRendered();
      await screen.findByText("Alice's turn");
    });

    it('shows filled scores from scoreboard', async () => {
      givenScoreboard([makeScorecard(ALICE.id, { ones: 3 }), makeScorecard(BOB.id)]);
      whenRendered();
      await screen.findAllByText('3');
    });
  });

  describe('rolling dice', () => {
    it('shows roll button when it is my turn', async () => {
      whenRendered();
      await screen.findByRole('button', { name: /roll/i });
    });

    it('clicking roll shows updated dice values', async () => {
      givenRollSucceeds([3, 4, 5, 1, 2, 6]);
      givenScoringOptions(ALICE.id, []);
      whenRendered();
      await whenRollClicked();
      await screen.findByText('3');
    });

    it('disables roll button after 3 rolls', async () => {
      givenRollSucceeds([3, 4, 5, 1, 2, 6]);
      givenScoringOptions(ALICE.id, []);
      whenRendered();
      await whenRollClicked();
      await screen.findByText('Rolls remaining: 2');
      await whenRollClicked();
      await screen.findByText('Rolls remaining: 1');
      await whenRollClicked();
      await thenRollButtonIsDisabled();
    });

    it('does not show roll button when it is not my turn', async () => {
      givenGameState({
        status: 'active',
        current_player_id: BOB.id,
        dice: makeDice(),
        rolls_remaining: 3,
        saved_rolls: 0,
      });
      whenRendered();
      await screen.findByText("Bob's turn");
      expect(screen.queryByRole('button', { name: /roll/i })).toBeNull();
    });
  });

  describe('keeping dice', () => {
    it('can toggle a die to kept after rolling', async () => {
      givenRollSucceeds([3, 4, 5, 1, 2, 6]);
      givenScoringOptions(ALICE.id, []);
      whenRendered();
      await whenRollClicked();
      await screen.findByText('3');
      await whenDieClicked(0);
      thenDieIsKept(0);
    });

    it('cannot toggle dice before rolling', async () => {
      whenRendered();
      await screen.findByRole('button', { name: /roll/i });
      thenDieIsDisabled(0);
    });
  });

  describe('scoring', () => {
    it('shows scoring options highlighted after rolling', async () => {
      givenRollSucceeds([1, 1, 1, 2, 3, 4]);
      givenScoringOptions(ALICE.id, [{ category: 'ones', score: 3 }]);
      whenRendered();
      await whenRollClicked();
      await thenScoringOptionVisible('Ones', 3);
    });

    it('unfilled categories without a scoring option are also clickable', async () => {
      givenRollSucceeds([1, 1, 1, 2, 3, 4]);
      givenScoringOptions(ALICE.id, [{ category: 'ones', score: 3 }]);
      whenRendered();
      await whenRollClicked();
      await thenScoringOptionVisible('Ones', 3);
      thenRowShowsX('Twos');
    });

    it('clicking a category calls the score endpoint and clears scoring options', async () => {
      let scoreCalled = false;
      server.use(
        http.put(SCORE_URL(ALICE.id), async () => {
          scoreCalled = true;
          return HttpResponse.json(makeScorecard(ALICE.id, { ones: 3 }));
        })
      );
      givenRollSucceeds([1, 1, 1, 2, 3, 4]);
      givenScoringOptions(ALICE.id, [{ category: 'ones', score: 3 }]);
      whenRendered();
      await whenRollClicked();
      await thenScoringOptionVisible('Ones', 3);
      await whenCategoryClicked('Ones');
      await vi.waitFor(() => expect(scoreCalled).toBe(true));
    });
  });

  describe('game ends', () => {
    it('navigates to /games/42/end when game state is finished', async () => {
      givenGameState({ status: 'finished', current_player_id: null, dice: null });
      whenRendered();
      await thenNavigatedTo('/games/42/end');
    });
  });

  describe('error handling', () => {
    it('shows error toast when roll fails', async () => {
      server.use(
        http.post(ROLL_URL, () => HttpResponse.json({ detail: 'Error' }, { status: 500 }))
      );
      whenRendered();
      await whenRollClicked();
      await screen.findByText('Failed to roll dice');
    });

    it('shows error toast when score fails', async () => {
      server.use(
        http.put(SCORE_URL(ALICE.id), () => HttpResponse.json({ detail: 'Error' }, { status: 500 }))
      );
      givenRollSucceeds([1, 1, 1, 2, 3, 4]);
      givenScoringOptions(ALICE.id, [{ category: 'ones', score: 3 }]);
      whenRendered();
      await whenRollClicked();
      await thenScoringOptionVisible('Ones', 3);
      await whenCategoryClicked('Ones');
      await screen.findByText('Failed to score category');
    });
  });

  function givenPlayers(players: { id: number; name: string; created_at: string }[]) {
    server.use(http.get(PLAYERS_URL, () => HttpResponse.json(players)));
  }

  function givenGameState(state: {
    status: string;
    current_player_id: number | null;
    dice?: ReturnType<typeof makeDice> | null;
    rolls_remaining?: number | null;
    saved_rolls?: number | null;
  }) {
    server.use(http.get(STATE_URL, () => HttpResponse.json(state)));
  }

  function givenScoreboard(scoreboard: ReturnType<typeof makeScorecard>[]) {
    server.use(http.get(BOARD_URL, () => HttpResponse.json(scoreboard)));
  }

  function givenRollSucceeds(values: number[]) {
    server.use(http.post(ROLL_URL, () => HttpResponse.json({ dice: makeDice(values) })));
  }

  function givenScoringOptions(playerId: number, options: { category: string; score: number }[]) {
    server.use(http.get(OPTIONS_URL(playerId), () => HttpResponse.json(options)));
  }

  function whenRendered() {
    renderWithProviders(<GameScreen />);
  }

  async function whenRollClicked() {
    await userEvent.click(await screen.findByRole('button', { name: /roll/i }));
  }

  async function whenDieClicked(index: number) {
    await userEvent.click(screen.getByRole('button', { name: `Die ${index}` }));
  }

  async function whenCategoryClicked(name: string) {
    await userEvent.click(await screen.findByRole('rowheader', { name: new RegExp(name, 'i') }));
  }

  async function thenScoringOptionVisible(category: string, score: number) {
    await vi.waitFor(() => {
      const header = screen.getByRole('rowheader', { name: category });
      expect(header.closest('tr')).toHaveTextContent(String(score));
    });
  }

  function thenRowShowsX(category: string) {
    const header = screen.getByRole('rowheader', { name: category });
    expect(header.closest('tr')).toHaveTextContent('×');
  }

  async function thenColumnHeaderIsVisible(name: string) {
    await screen.findByRole('columnheader', { name });
  }

  function thenDieIsKept(index: number) {
    expect(screen.getByRole('button', { name: `Die ${index}` })).toHaveAttribute(
      'aria-pressed',
      'true'
    );
  }

  function thenDieIsDisabled(index: number) {
    expect(screen.getByRole('button', { name: `Die ${index}` })).toBeDisabled();
  }

  async function thenRollButtonIsDisabled() {
    const rollBtn = await screen.findByRole('button', { name: /roll/i });
    expect(rollBtn).toBeDisabled();
  }

  async function thenNavigatedTo(path: string) {
    await vi.waitFor(() => expect(mockNavigate).toHaveBeenCalledWith(path));
  }
});
