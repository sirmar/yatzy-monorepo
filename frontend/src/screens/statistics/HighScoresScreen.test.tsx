import { screen } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
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

  describe('mode selector', () => {
    it('shows Standard and Sequential buttons', async () => {
      givenHighScores([]);
      whenRendered();
      await screen.findByRole('button', { name: 'Standard' });
      await screen.findByRole('button', { name: 'Sequential' });
    });

    it('defaults to Standard', async () => {
      givenHighScores([makeHighScore({ player_name: 'Alice', mode: 'standard' })]);
      whenRendered();
      await screen.findByText('Alice');
    });

    it('switches to Sequential on click', async () => {
      givenHighScores([
        makeHighScore({ player_name: 'Alice', mode: 'standard' }),
        makeHighScore({ player_id: 2, player_name: 'Bob', game_id: 11, mode: 'sequential' }),
      ]);
      whenRendered();
      await screen.findByText('Alice');
      await userEvent.click(screen.getByRole('button', { name: 'Sequential' }));
      expect(screen.queryByText('Alice')).not.toBeInTheDocument();
      expect(screen.getByText('Bob')).toBeInTheDocument();
    });
  });

  describe('scores display', () => {
    it('shows the heading', async () => {
      givenHighScores([]);
      whenRendered();
      await thenTextEventuallyVisible('High Scores');
    });

    it('shows player name, score, game id and date', async () => {
      givenHighScores([makeHighScore({ player_name: 'Alice', total_score: 300, game_id: 42 })]);
      whenRendered();
      await screen.findByText('Alice');
      expect(screen.getByText('300')).toBeInTheDocument();
      expect(screen.getByText('#42')).toBeInTheDocument();
    });

    it('numbers rows by rank', async () => {
      givenHighScores([
        makeHighScore({ player_name: 'Alice', total_score: 300 }),
        makeHighScore({ player_id: 2, player_name: 'Bob', game_id: 11, total_score: 250 }),
      ]);
      whenRendered();
      await screen.findByText('Alice');
      const rows = document.querySelectorAll('tbody tr');
      expect(rows[0]).toHaveTextContent('🥇');
      expect(rows[1]).toHaveTextContent('🥈');
    });

    it('shows "No high scores yet" when selected mode has no entries', async () => {
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
});
