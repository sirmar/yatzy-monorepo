import { screen } from '@testing-library/react';
import { HttpResponse, http } from 'msw';
import { setupServer } from 'msw/node';
import { afterAll, afterEach, beforeAll, beforeEach, describe, expect, it } from 'vitest';
import { renderWithProviders } from '@/test/helpers';
import { HighScoresScreen } from './HighScoresScreen';

const server = setupServer();
beforeAll(() => server.listen());
afterEach(() => {
  server.resetHandlers();
  sessionStorage.clear();
});
afterAll(() => server.close());

const HIGH_SCORES_URL = 'http://localhost/api/high-scores';

const ALICE = { id: 1, name: 'Alice', created_at: '' };

function makeHighScore(overrides: Partial<{
  player_id: number;
  player_name: string;
  game_id: number;
  finished_at: string;
  total_score: number;
}> = {}) {
  return {
    player_id: 1,
    player_name: 'Alice',
    game_id: 10,
    finished_at: '2024-06-01T12:00:00Z',
    total_score: 300,
    ...overrides,
  };
}

describe('HighScoresScreen', () => {
  beforeEach(() => {
    sessionStorage.setItem('yatzy_player', JSON.stringify(ALICE));
  });

  describe('loading state', () => {
    it('shows loading indicator before data arrives', () => {
      givenHighScoresPending();
      whenRendered();
      thenTextIsVisible('Loading...');
    });
  });

  describe('scores display', () => {
    it('shows the heading', async () => {
      givenHighScores([]);
      whenRendered();
      await thenTextEventuallyVisible('High Scores');
    });

    it('shows player names and scores', async () => {
      givenHighScores([
        makeHighScore({ player_name: 'Alice', total_score: 300 }),
        makeHighScore({ player_id: 2, player_name: 'Bob', game_id: 11, total_score: 250 }),
      ]);
      whenRendered();
      await thenTextEventuallyVisible('Alice');
      await thenTextEventuallyVisible('300');
      await thenTextEventuallyVisible('Bob');
      await thenTextEventuallyVisible('250');
    });

    it('numbers rows by rank', async () => {
      givenHighScores([
        makeHighScore({ player_name: 'Alice', total_score: 300 }),
        makeHighScore({ player_id: 2, player_name: 'Bob', game_id: 11, total_score: 250 }),
      ]);
      whenRendered();
      const rows = await screen.findAllByRole('row');
      thenRowContains(rows[1], '1');
      thenRowContains(rows[2], '2');
    });

    it('shows game id prefixed with #', async () => {
      givenHighScores([makeHighScore({ game_id: 42 })]);
      whenRendered();
      await thenTextEventuallyVisible('#42');
    });

    it('shows "No high scores yet" when list is empty', async () => {
      givenHighScores([]);
      whenRendered();
      await thenTextEventuallyVisible('No high scores yet');
    });
  });

  describe('error handling', () => {
    it('shows error message when fetch fails', async () => {
      givenHighScoresFetchFails();
      whenRendered();
      await thenTextEventuallyVisible('Failed to load high scores');
    });
  });

  function givenHighScores(scores: ReturnType<typeof makeHighScore>[]) {
    server.use(http.get(HIGH_SCORES_URL, () => HttpResponse.json(scores)));
  }

  function givenHighScoresPending() {
    server.use(http.get(HIGH_SCORES_URL, () => new Promise(() => {})));
  }

  function givenHighScoresFetchFails() {
    server.use(
      http.get(HIGH_SCORES_URL, () => HttpResponse.json({ detail: 'Error' }, { status: 500 }))
    );
  }

  function whenRendered() {
    renderWithProviders(<HighScoresScreen />);
  }

  function thenTextIsVisible(text: string) {
    expect(screen.getByText(text)).toBeInTheDocument();
  }

  async function thenTextEventuallyVisible(text: string) {
    await screen.findByText(new RegExp(text));
  }

  function thenRowContains(row: HTMLElement, text: string) {
    expect(row).toHaveTextContent(text);
  }
});
