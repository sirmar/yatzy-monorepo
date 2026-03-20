import { apiClient } from '@/api';
import type { components } from '@/api';
import { Button } from '@/components/ui/button';
import { usePlayer } from '@/hooks/PlayerContext';
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

  useEffect(() => {
    apiClient.GET('/players').then(({ data }) => {
      if (data) {
        setPlayerNames(Object.fromEntries(data.map((p) => [p.id, p.name])));
      }
    });
  }, []);

  const fetchGames = useCallback(async () => {
    if (!player) return;

    const [{ data: lobbyGames }, { data: activeGames }] = await Promise.all([
      apiClient.GET('/games', { params: { query: { status: 'lobby' } } }),
      apiClient.GET('/games', { params: { query: { status: 'active' } } }),
    ]);

    const active = activeGames?.find((g) => g.player_ids.includes(player.id));
    if (active) {
      navigate(`/games/${active.id}`);
      return;
    }

    setGames(lobbyGames ?? []);
  }, [player, navigate]);

  useEffect(() => {
    fetchGames();
  }, [fetchGames]);

  usePolling(fetchGames, { interval: 2000 });

  async function handleCreate() {
    if (!player) return;
    setCreating(true);
    await apiClient.POST('/games', { body: { creator_id: player.id } });
    setCreating(false);
    await fetchGames();
  }

  async function handleJoin(game: Game) {
    if (!player) return;
    await apiClient.POST('/games/{game_id}/join', {
      params: { path: { game_id: game.id } },
      body: { player_id: player.id },
    });
    await fetchGames();
  }

  async function handleDelete(game: Game) {
    await apiClient.DELETE('/games/{game_id}', {
      params: { path: { game_id: game.id } },
    });
    await fetchGames();
  }

  async function handleLeave(game: Game) {
    if (!player) return;
    await apiClient.DELETE('/games/{game_id}/players/{player_id}', {
      params: { path: { game_id: game.id, player_id: player.id } },
    });
    await fetchGames();
  }

  async function handleStart(game: Game) {
    if (!player) return;
    const { data } = await apiClient.POST('/games/{game_id}/start', {
      params: { path: { game_id: game.id } },
      body: { player_id: player.id },
    });
    if (data) navigate(`/games/${data.id}`);
  }

  return (
    <div className="min-h-screen bg-gray-950 p-6">
      <div className="max-w-lg mx-auto flex flex-col gap-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-white">Lobby</h1>
          <CreateGameButton onCreate={handleCreate} loading={creating} />
        </div>
        <div className="flex items-center justify-between text-sm text-gray-400">
          <span>Playing as <span className="text-white font-medium">{player?.name}</span></span>
          <Button variant="ghost" size="sm" className="text-gray-500 hover:text-white" onClick={() => navigate('/')}>
            Change player
          </Button>
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
