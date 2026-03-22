import { apiClient } from '@/api';
import type { components } from '@/api';
import { usePlayer } from '@/hooks/PlayerContext';
import { useErrorToast } from '@/hooks/use-toast';
import { usePolling } from '@/hooks/usePolling';
import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CreateGameButton } from './CreateGameButton';
import { GameList } from './GameList';

type Game = components['schemas']['Game'];

export function LobbyScreen() {
  const [games, setGames] = useState<Game[]>([]);
  const [creating, setCreating] = useState(false);
  const [playerNames, setPlayerNames] = useState<Record<number, string>>({});
  const { player } = usePlayer();
  const navigate = useNavigate();
  const errorToast = useErrorToast();

  useEffect(() => {
    apiClient.GET('/players').then(({ data }) => {
      if (data) {
        setPlayerNames(Object.fromEntries(data.map((p) => [p.id, p.name])));
      }
    });
  }, []);

  const fetchGames = useCallback(async () => {
    if (!player) return;
    const { data } = await apiClient.GET('/games', { params: { query: { status: 'lobby' } } });
    setGames(data ?? []);
  }, [player]);

  useEffect(() => {
    fetchGames();
  }, [fetchGames]);

  usePolling(fetchGames, { interval: 2000 });

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
      const { error } = await apiClient.POST('/games', { body: { creator_id: player.id } });
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
    <div className="min-h-screen bg-gray-950 p-6">
      <div className="max-w-lg mx-auto flex flex-col gap-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-white">Lobby</h1>
          <CreateGameButton onCreate={handleCreate} loading={creating} />
        </div>
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
    </div>
  );
}
