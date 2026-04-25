import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
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
    mode: 'maxi',
    ...overrides,
  };
}

describe('HighScoresScreen', () => {
  beforeEach(() => {
    sessionStorage.setItem('yatzy_player', JSON.stringify(ALICE));
  });

  describe('mode selector', () => {
    it('shows all mode buttons', async () => {
      givenHighScores([]);
      whenRendered();
      await thenModeButtonsVisible(['Maxi Yatzy', 'Maxi Seq.', 'Yatzy', 'Yatzy Seq.']);
    });

    it('defaults to Maxi Yatzy', async () => {
      givenHighScores([makeHighScore({ player_name: 'Alice', mode: 'maxi' })]);
      whenRendered();
      await thenPlayerVisible('Alice');
    });

    it('switches to Maxi Sequential on click', async () => {
      givenHighScores([
        makeHighScore({ player_name: 'Alice', mode: 'maxi' }),
        makeHighScore({ player_id: 2, player_name: 'Bob', game_id: 11, mode: 'maxi_sequential' }),
      ]);
      whenRendered();
      await thenPlayerVisible('Alice');
      await whenModeSelected('Maxi Seq.');
      thenPlayerNotVisible('Alice');
      await thenPlayerVisible('Bob');
    });

    it('switches to Yatzy on click', async () => {
      givenHighScores([
        makeHighScore({ player_name: 'Alice', mode: 'maxi' }),
        makeHighScore({ player_id: 2, player_name: 'Bob', game_id: 11, mode: 'yatzy' }),
      ]);
      whenRendered();
      await thenPlayerVisible('Alice');
      await whenModeSelected('Yatzy');
      thenPlayerNotVisible('Alice');
      await thenPlayerVisible('Bob');
    });

    it('switches to Yatzy Sequential on click', async () => {
      givenHighScores([
        makeHighScore({ player_name: 'Alice', mode: 'maxi' }),
        makeHighScore({ player_id: 2, player_name: 'Bob', game_id: 11, mode: 'yatzy_sequential' }),
      ]);
      whenRendered();
      await thenPlayerVisible('Alice');
      await whenModeSelected('Yatzy Seq.');
      thenPlayerNotVisible('Alice');
      await thenPlayerVisible('Bob');
    });
  });

  describe('scores display', () => {
    it('shows the heading text', async () => {
      givenHighScores([]);
      whenRendered();
      await thenTextEventuallyVisible('High Scores');
    });

    it('shows player name and score', async () => {
      givenHighScores([makeHighScore({ player_name: 'Alice', total_score: 300 })]);
      whenRendered();
      await thenPlayerVisible('Alice');
      await thenTextEventuallyVisible('300');
    });

    it('numbers rows by rank', async () => {
      givenHighScores([
        makeHighScore({ player_name: 'Alice', total_score: 300 }),
        makeHighScore({ player_id: 2, player_name: 'Bob', game_id: 11, total_score: 250 }),
      ]);
      whenRendered();
      await thenPlayerVisible('Alice');
      await thenRowHasRank(0, '1');
      await thenRowHasRank(1, '2');
    });

    it('shows "No scores yet" when selected mode has no entries', async () => {
      givenHighScores([]);
      whenRendered();
      await thenTextEventuallyVisible('No scores yet');
    });
  });

  function givenHighScores(scores: ReturnType<typeof makeHighScore>[]) {
    server.use(http.get(HIGH_SCORES_URL, () => HttpResponse.json(scores)));
  }

  function whenRendered() {
    renderWithProviders(<HighScoresScreen />);
  }

  async function whenModeSelected(label: string) {
    await userEvent.click(await screen.findByRole('button', { name: label }));
  }

  async function thenTextEventuallyVisible(text: string) {
    await screen.findByText(new RegExp(text));
  }

  async function thenModeButtonsVisible(labels: string[]) {
    for (const label of labels) {
      expect(await screen.findByRole('button', { name: label })).toBeInTheDocument();
    }
  }

  async function thenPlayerVisible(name: string) {
    await screen.findByText(name);
  }

  function thenPlayerNotVisible(name: string) {
    expect(screen.queryByText(name)).not.toBeInTheDocument();
  }

  async function thenRowHasRank(index: number, rank: string) {
    const rows = document.querySelectorAll('tbody tr');
    expect(rows[index]).toHaveTextContent(rank);
  }
});
