import { screen } from '@testing-library/react';
import { HttpResponse, http } from 'msw';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { ALICE, createMockServer, renderWithProviders } from '@/test/helpers';
import { HighScoresScreen } from './HighScoresScreen';

const server = createMockServer();
afterEach(() => {
  sessionStorage.clear();
});

const HIGH_SCORES_URL = 'http://localhost/api/high-scores';

function makeHighScore(
  overrides: Partial<{
    player_id: number;
    player_name: string;
    game_id: number;
    finished_at: string;
    total_score: number;
    mode: string;
  }> = {}
) {
  return {
    player_id: 1,
    player_name: 'Alice',
    game_id: 10,
    finished_at: '2024-06-01T12:00:00Z',
    total_score: 300,
    mode: 'standard',
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

    it('shows section headings for each mode', async () => {
      givenHighScores([]);
      whenRendered();
      await thenTextEventuallyVisible('Standard');
      await thenTextEventuallyVisible('Sequential');
    });

    it('shows standard scores under Standard heading', async () => {
      givenHighScores([
        makeHighScore({ player_name: 'Alice', total_score: 300, mode: 'standard' }),
      ]);
      whenRendered();
      const heading = await screen.findByRole('heading', { name: 'Standard' });
      const section = heading.closest('div');
      expect(section).toHaveTextContent('Alice');
      expect(section).toHaveTextContent('300');
    });

    it('shows sequential scores under Sequential heading', async () => {
      givenHighScores([
        makeHighScore({ player_name: 'Bob', game_id: 11, total_score: 250, mode: 'sequential' }),
      ]);
      whenRendered();
      const heading = await screen.findByRole('heading', { name: 'Sequential' });
      const section = heading.closest('div');
      expect(section).toHaveTextContent('Bob');
      expect(section).toHaveTextContent('250');
    });

    it('does not show standard scores under Sequential heading', async () => {
      givenHighScores([
        makeHighScore({ player_name: 'Alice', total_score: 300, mode: 'standard' }),
      ]);
      whenRendered();
      const heading = await screen.findByRole('heading', { name: 'Sequential' });
      const section = heading.closest('div');
      expect(section).not.toHaveTextContent('Alice');
    });

    it('numbers rows by rank within each section', async () => {
      givenHighScores([
        makeHighScore({ player_name: 'Alice', total_score: 300, mode: 'standard' }),
        makeHighScore({
          player_id: 2,
          player_name: 'Bob',
          game_id: 11,
          total_score: 250,
          mode: 'standard',
        }),
      ]);
      whenRendered();
      const heading = await screen.findByRole('heading', { name: 'Standard' });
      const section = heading.closest('div') as HTMLElement;
      const rows = section.querySelectorAll('tbody tr');
      expect(rows[0]).toHaveTextContent('1');
      expect(rows[1]).toHaveTextContent('2');
    });

    it('shows game id prefixed with #', async () => {
      givenHighScores([makeHighScore({ game_id: 42 })]);
      whenRendered();
      await thenTextEventuallyVisible('#42');
    });

    it('shows "No high scores yet" in each empty section', async () => {
      givenHighScores([]);
      whenRendered();
      const noScores = await screen.findAllByText('No high scores yet');
      expect(noScores).toHaveLength(2);
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
});
