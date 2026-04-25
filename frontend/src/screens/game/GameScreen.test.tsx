import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { HttpResponse, http } from 'msw';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { ALICE, BOB, createMockServer, renderWithProviders } from '@/test/helpers';
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

const server = createMockServer();
afterEach(() => {
  vi.useRealTimers();
  mockNavigate.mockReset();
  sessionStorage.clear();
});

const GAME_URL = 'http://localhost/api/games/42';
const STATE_URL = 'http://localhost/api/games/42/state';
const BOARD_URL = 'http://localhost/api/games/42/scoreboard';
const ROLL_URL = 'http://localhost/api/games/42/roll';
const OPTIONS_URL = (pid: number) => `http://localhost/api/games/42/players/${pid}/scoring-options`;
const SCORE_URL = (pid: number) => `http://localhost/api/games/42/players/${pid}/scorecard`;
const PLAYERS_URL = 'http://localhost/api/players';

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
    vi.useFakeTimers({ toFake: ['setInterval', 'clearInterval'] });
    sessionStorage.setItem('yatzy_player', JSON.stringify(ALICE));
    givenPlayers([ALICE, BOB]);
    givenGame({ id: 42, creator_id: ALICE.id });
    givenGameState({
      status: 'active',
      mode: 'maxi',
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

    it('shows filled scores from scoreboard', async () => {
      givenScoreboard([makeScorecard(ALICE.id, { ones: 3 }), makeScorecard(BOB.id)]);
      whenRendered();
      await thenScoreVisible(3);
    });
  });

  describe('rolling dice', () => {
    it('shows roll button when it is my turn', async () => {
      whenRendered();
      await thenRollButtonIsVisible();
    });

    it('clicking roll shows updated dice values', async () => {
      givenRollSucceeds([3, 4, 5, 1, 2, 6]);
      givenScoringOptions(ALICE.id, []);
      whenRendered();
      await whenRollClicked();
      await thenDieHasValue(0, '3');
    });

    it('disables roll button after 3 rolls', async () => {
      givenRollSucceeds([3, 4, 5, 1, 2, 6]);
      givenScoringOptions(ALICE.id, []);
      whenRendered();
      await whenRollClicked();
      await thenDieHasValue(0, '3');
      await whenRollClicked();
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
      await screen.findByRole('columnheader', { name: /bob/i });
      thenRollButtonIsNotVisible();
    });
  });

  describe('keeping dice', () => {
    it('can toggle a die to kept after rolling', async () => {
      givenRollSucceeds([3, 4, 5, 1, 2, 6]);
      givenScoringOptions(ALICE.id, []);
      whenRendered();
      await whenRollClicked();
      await thenDieIsEnabled(0);
      await whenDieClicked(0);
      thenDieIsKept(0);
    });

    it('cannot toggle dice before rolling', async () => {
      whenRendered();
      await thenRollButtonIsVisible();
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

    it('unfilled categories without a scoring option show dash', async () => {
      givenRollSucceeds([1, 1, 1, 2, 3, 4]);
      givenScoringOptions(ALICE.id, [{ category: 'ones', score: 3 }]);
      whenRendered();
      await whenRollClicked();
      await thenScoringOptionVisible('Ones', 3);
      thenRowShowsDash('Twos');
    });

    describe('sequential mode', () => {
      beforeEach(() => {
        givenGame({ id: 42, creator_id: ALICE.id, mode: 'maxi_sequential' });
      });

      it('only shows scoring option for the next required category', async () => {
        givenRollSucceeds([1, 1, 1, 2, 3, 4]);
        givenScoringOptions(ALICE.id, [{ category: 'ones', score: 3 }]);
        whenRendered();
        await whenRollClicked();
        await thenScoringOptionVisible('Ones', 3);
      });

      it('does not show dash for other unfilled categories in sequential mode', async () => {
        givenRollSucceeds([1, 1, 1, 2, 3, 4]);
        givenScoringOptions(ALICE.id, [{ category: 'ones', score: 3 }]);
        whenRendered();
        await whenRollClicked();
        await thenScoringOptionVisible('Ones', 3);
        thenRowIsEmpty('Twos');
      });

      it('does not allow clicking non-option categories in sequential mode', async () => {
        let scoreCalled = false;
        server.use(
          http.put(SCORE_URL(ALICE.id), async () => {
            scoreCalled = true;
            return HttpResponse.json(makeScorecard(ALICE.id));
          })
        );
        givenRollSucceeds([1, 1, 1, 2, 3, 4]);
        givenScoringOptions(ALICE.id, [{ category: 'ones', score: 3 }]);
        whenRendered();
        await whenRollClicked();
        await thenScoringOptionVisible('Ones', 3);
        await whenCategoryClicked('Twos');
        thenScoreWasNotCalled(scoreCalled);
      });
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
      await thenScoreWasCalled(() => scoreCalled);
    });
  });

  describe('game ends', () => {
    it('navigates to /games/42/end when game state is finished', async () => {
      givenGameState({ status: 'finished', current_player_id: null, dice: null });
      whenRendered();
      await thenNavigatedTo('/games/42/end');
    });

    it('navigates to /games/42/end when scoring the last category ends the game', async () => {
      givenRollSucceeds([1, 1, 1, 2, 3, 4]);
      givenScoringOptions(ALICE.id, [{ category: 'ones', score: 3 }]);
      server.use(
        http.put(SCORE_URL(ALICE.id), () => {
          givenGameState({ status: 'finished', current_player_id: null, dice: null });
          return HttpResponse.json(makeScorecard(ALICE.id, { ones: 3 }));
        })
      );
      whenRendered();
      await whenRollClicked();
      await thenScoringOptionVisible('Ones', 3);
      await whenCategoryClicked('Ones');
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
      await thenTextIsVisible('Failed to roll dice');
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
      await thenTextIsVisible('Failed to score category');
    });
  });

  function givenPlayers(players: { id: number; name: string; created_at: string }[]) {
    server.use(http.get(PLAYERS_URL, () => HttpResponse.json(players)));
  }

  function givenGame(game: { id: number; creator_id: number; mode?: string }) {
    server.use(http.get(GAME_URL, () => HttpResponse.json({ mode: 'maxi', ...game })));
  }

  function givenGameState(state: {
    status: string;
    mode?: string;
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

  async function whenCategoryClicked(label: string) {
    const cell = await screen.findByText(label);
    await userEvent.click(cell);
  }

  async function thenScoringOptionVisible(category: string, score: number) {
    await waitFor(() => {
      const cell = screen.getByText(category);
      expect(cell.closest('tr')).toHaveTextContent(`${score} ↑`);
    });
  }

  function thenRowShowsDash(category: string) {
    const cell = screen.getByText(category);
    expect(cell.closest('tr')).toHaveTextContent('—');
  }

  function thenRowIsEmpty(category: string) {
    const cell = screen.getByText(category);
    const row = cell.closest('tr');
    expect(row).not.toHaveTextContent('—');
    expect(row).not.toHaveTextContent('↑');
  }

  async function thenColumnHeaderIsVisible(name: string) {
    await screen.findByRole('columnheader', { name: new RegExp(name) });
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
    await waitFor(() => expect(mockNavigate).toHaveBeenCalledWith(path));
  }

  async function thenTextIsVisible(text: string) {
    await screen.findByText(text);
  }

  async function thenScoreVisible(score: number) {
    await screen.findAllByText(String(score));
  }

  async function thenRollButtonIsVisible() {
    await screen.findByRole('button', { name: /roll/i });
  }

  function thenRollButtonIsNotVisible() {
    expect(screen.queryByRole('button', { name: /roll/i })).toBeNull();
  }

  async function thenDieHasValue(index: number, value: string) {
    await waitFor(() =>
      expect(screen.getByRole('button', { name: `Die ${index}` })).toHaveAttribute(
        'data-value',
        value
      )
    );
  }

  async function thenDieIsEnabled(index: number) {
    await waitFor(() =>
      expect(screen.getByRole('button', { name: `Die ${index}` })).not.toBeDisabled()
    );
  }

  function thenScoreWasNotCalled(scoreCalled: boolean) {
    expect(scoreCalled).toBe(false);
  }

  async function thenScoreWasCalled(getScoreCalled: () => boolean) {
    await waitFor(() => expect(getScoreCalled()).toBe(true));
  }
});
