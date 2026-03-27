import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { components } from '@/api';
import { apiClient } from '@/api';
import { PageHeader } from '@/components/PageHeader';
import { PageLayout } from '@/components/PageLayout';
import { usePlayer } from '@/hooks/PlayerContext';
import { useErrorToast } from '@/hooks/use-toast';
import { usePlayerNames } from '@/hooks/usePlayerNames';
import { usePolling } from '@/hooks/usePolling';
import { POLLING_INTERVAL_MS } from '@/lib/constants';
import { CreateGameButton } from './CreateGameButton';
import { GameList } from './GameList';

type Game = components['schemas']['Game'];
type GameMode = components['schemas']['GameMode'];

export function LobbyScreen() {
  const [games, setGames] = useState<Game[]>([]);
  const [creating, setCreating] = useState(false);
  const [mode, setMode] = useState<GameMode>('maxi');
  const playerNames = usePlayerNames();
  const { player } = usePlayer();
  const navigate = useNavigate();
  const errorToast = useErrorToast();

  const fetchGames = useCallback(async () => {
    if (!player) return;
    const { data } = await apiClient.GET('/games', { params: { query: { status: 'lobby' } } });
    setGames(data ?? []);
  }, [player]);

  useEffect(() => {
    fetchGames();
  }, [fetchGames]);

  usePolling(fetchGames, { interval: POLLING_INTERVAL_MS });

  async function withMutation(title: string, fn: () => Promise<{ error?: unknown }>) {
    const { error } = await fn();
    if (error) {
      errorToast(title);
      return;
    }
    await fetchGames();
  }

  async function handleCreate() {
    if (!player) return;
    setCreating(true);
    try {
      const { error } = await apiClient.POST('/games', { body: { creator_id: player.id, mode } });
      if (error) throw error;
    } catch {
      errorToast('Failed to create game');
      return;
    } finally {
      setCreating(false);
    }
    await fetchGames();
  }

  async function handleJoin(game: Game) {
    if (!player) return;
    await withMutation('Failed to join game', () =>
      apiClient.POST('/games/{game_id}/join', {
        params: { path: { game_id: game.id } },
        body: { player_id: player.id },
      })
    );
  }

  async function handleDelete(game: Game) {
    await withMutation('Failed to delete game', () =>
      apiClient.DELETE('/games/{game_id}', {
        params: { path: { game_id: game.id } },
      })
    );
  }

  async function handleLeave(game: Game) {
    if (!player) return;
    await withMutation('Failed to leave game', () =>
      apiClient.DELETE('/games/{game_id}/players/{player_id}', {
        params: { path: { game_id: game.id, player_id: player.id } },
      })
    );
  }

  async function handleStart(game: Game) {
    if (!player) return;
    try {
      const { data, error } = await apiClient.POST('/games/{game_id}/start', {
        params: { path: { game_id: game.id } },
        body: { player_id: player.id },
      });
      if (error || !data) throw error ?? new Error('Failed to start game');
      navigate(`/games/${data.id}`);
    } catch {
      errorToast('Failed to start game');
    }
  }

  return (
    <PageLayout>
      <div className="flex flex-col gap-6">
        <PageHeader
          title="Lobby"
          action={
            <div className="flex items-center gap-2">
              <label htmlFor="game-mode" className="text-sm text-gray-400 sr-only">
                Mode
              </label>
              <select
                id="game-mode"
                aria-label="Mode"
                value={mode}
                onChange={(e) => setMode(e.target.value as GameMode)}
                className="bg-gray-800 text-white text-sm rounded px-2 py-1.5 border border-gray-600 focus:outline-none focus:ring-1 focus:ring-gray-500"
              >
                <option value="maxi">Maxi Yatzy</option>
                <option value="maxi_sequential">Maxi Yatzy Sequential</option>
                <option value="yatzy">Yatzy</option>
                <option value="yatzy_sequential">Yatzy Sequential</option>
              </select>
              <CreateGameButton onCreate={handleCreate} loading={creating} />
            </div>
          }
        />
        <GameList
          games={games}
          currentPlayerId={player?.id ?? 0}
          playerNames={playerNames}
          onJoin={handleJoin}
          onDelete={handleDelete}
          onStart={handleStart}
          onLeave={handleLeave}
        />
      </div>
    </PageLayout>
  );
}
