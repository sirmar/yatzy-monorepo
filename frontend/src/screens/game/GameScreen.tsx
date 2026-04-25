import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import type { components } from '@/api';
import { apiClient } from '@/api';
import { PageLayout } from '@/components/PageLayout';
import { usePlayer } from '@/hooks/PlayerContext';
import { useErrorToast } from '@/hooks/use-toast';
import { useEventSource } from '@/hooks/useEventSource';
import { DiceRoller } from './DiceRoller';
import { ScoreCard } from './ScoreCard';

type GameState = components['schemas']['GameState'];
type GameMode = components['schemas']['GameMode'];
type Die = components['schemas']['Die'];
type PlayerScorecard = components['schemas']['PlayerScorecard'];
type ScoringOption = components['schemas']['ScoringOption'];
type ScoreCategory = components['schemas']['ScoreCategory'];

export function GameScreen() {
  const { gameId } = useParams<{ gameId: string }>();
  const { player } = usePlayer();
  const navigate = useNavigate();
  const errorToast = useErrorToast();

  const [gameState, setGameState] = useState<GameState | null>(null);
  const [gameMode, setGameMode] = useState<GameMode | null>(null);
  const [dice, setDice] = useState<Die[]>([]);
  const [rollCount, setRollCount] = useState(0);
  const [scoreboard, setScoreboard] = useState<PlayerScorecard[]>([]);
  const [scoringOptions, setScoringOptions] = useState<ScoringOption[] | null>(null);
  const prevPlayerIdRef = useRef<number | null | undefined>(undefined);
  const pendingRollRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const isMyTurn = gameState?.current_player_id === player?.id;
  const rollsRemaining = gameState?.rolls_remaining ?? 0;
  const savedRolls = gameState?.saved_rolls ?? 0;
  const showSavedRolls = gameMode === 'maxi' || gameMode === 'maxi_sequential';
  const canRoll = isMyTurn && (rollsRemaining > 0 || savedRolls > 0);
  const hasRolled = gameState?.dice?.some((d) => d.value !== null) ?? false;

  useEffect(() => {
    if (!gameId) return;
    const gid = Number(gameId);
    const controller = new AbortController();

    Promise.all([
      apiClient.GET('/games/{game_id}', {
        params: { path: { game_id: gid } },
        signal: controller.signal,
      }),
      apiClient.GET('/games/{game_id}/state', {
        params: { path: { game_id: gid } },
        signal: controller.signal,
      }),
      apiClient.GET('/games/{game_id}/scoreboard', {
        params: { path: { game_id: gid } },
        signal: controller.signal,
      }),
    ]).then(([{ data: game }, { data: state }, { data: board }]) => {
      if (game) {
        setGameMode(game.mode);
      }
      if (state) {
        setGameState(state);
        setDice(state.dice ?? []);
        prevPlayerIdRef.current = state.current_player_id;
        if (state.status === 'finished') {
          navigate(`/games/${gameId}/end`);
        }
        if (state.status === 'abandoned') {
          navigate('/lobby');
        }
        const alreadyRolled = state.dice?.some((d) => d.value !== null) ?? false;
        const currentPlayerId = state.current_player_id;
        if (currentPlayerId !== undefined && currentPlayerId === player?.id && alreadyRolled) {
          apiClient
            .GET('/games/{game_id}/players/{player_id}/scoring-options', {
              params: { path: { game_id: gid, player_id: currentPlayerId } },
              signal: controller.signal,
            })
            .then(({ data: options }) => {
              if (options) setScoringOptions(options);
            });
        }
      }
      if (board) setScoreboard(board);
    });
    return () => controller.abort();
  }, [gameId, navigate, player?.id]);

  const fetchGameState = useCallback(async () => {
    if (!gameId) return;
    const { data } = await apiClient.GET('/games/{game_id}/state', {
      params: { path: { game_id: Number(gameId) } },
    });
    if (!data) return;

    const currentId = data.current_player_id;
    if (prevPlayerIdRef.current !== undefined && currentId !== prevPlayerIdRef.current) {
      setScoringOptions(null);
      const newDice = data.dice ?? [];
      if (newDice.some((d) => d.value !== null)) {
        setDice(newDice);
      } else {
        setDice((prev) => newDice.map((d, i) => ({ ...d, value: prev[i]?.value ?? null })));
      }
      const { data: board } = await apiClient.GET('/games/{game_id}/scoreboard', {
        params: { path: { game_id: Number(gameId) } },
      });
      if (board) setScoreboard(board);
    } else if (currentId !== player?.id) {
      const newDice = data.dice ?? [];
      const hasValues = newDice.some((d) => d.value !== null);
      const hasKept = newDice.some((d) => d.kept);
      if (hasValues && hasKept) {
        if (pendingRollRef.current) clearTimeout(pendingRollRef.current);
        setDice((prev) =>
          newDice.map((d, i) => (d.kept ? d : { ...d, value: prev[i]?.value ?? null }))
        );
        pendingRollRef.current = setTimeout(() => {
          setRollCount((c) => c + 1);
          setDice(newDice);
          pendingRollRef.current = null;
        }, 600);
      } else {
        if (hasValues) setRollCount((c) => c + 1);
        setDice(newDice);
      }
    }

    prevPlayerIdRef.current = currentId;
    setGameState(data);

    if (data.status === 'finished') {
      navigate(`/games/${gameId}/end`);
    }
    if (data.status === 'abandoned') {
      navigate('/lobby');
    }
  }, [gameId, navigate, player?.id]);

  useEventSource(
    gameState?.status === 'active' ? `/api/games/${gameId}/events` : null,
    fetchGameState
  );

  async function handleRoll() {
    if (!player || !gameId) return;
    const keptIndices = dice.filter((d) => d.kept).map((d) => d.index);
    const { data, error } = await apiClient.POST('/games/{game_id}/roll', {
      params: { path: { game_id: Number(gameId) } },
      body: { player_id: player.id, kept_dice: keptIndices },
    });
    if (error || !data) {
      errorToast('Failed to roll dice');
      return;
    }
    setDice(data.dice);
    setRollCount((c) => c + 1);
    setGameState((prev) => {
      if (!prev) return prev;
      if ((prev.rolls_remaining ?? 0) > 0) {
        return { ...prev, dice: data.dice, rolls_remaining: (prev.rolls_remaining ?? 0) - 1 };
      }
      return { ...prev, dice: data.dice, saved_rolls: (prev.saved_rolls ?? 0) - 1 };
    });
    const { data: options } = await apiClient.GET(
      '/games/{game_id}/players/{player_id}/scoring-options',
      { params: { path: { game_id: Number(gameId), player_id: player.id } } }
    );
    if (options) setScoringOptions(options);
  }

  function handleToggleDie(index: number) {
    if (!isMyTurn || !hasRolled) return;
    setDice((prev) => prev.map((d) => (d.index === index ? { ...d, kept: !d.kept } : d)));
  }

  async function handleScore(category: ScoreCategory) {
    if (!player || !gameId) return;
    const { error } = await apiClient.PUT('/games/{game_id}/players/{player_id}/scorecard', {
      params: { path: { game_id: Number(gameId), player_id: player.id } },
      body: { category },
    });
    if (error) {
      errorToast('Failed to score category');
      return;
    }
    setScoringOptions(null);
    const [{ data: newState }, { data: board }] = await Promise.all([
      apiClient.GET('/games/{game_id}/state', {
        params: { path: { game_id: Number(gameId) } },
      }),
      apiClient.GET('/games/{game_id}/scoreboard', {
        params: { path: { game_id: Number(gameId) } },
      }),
    ]);
    if (newState) {
      prevPlayerIdRef.current = newState.current_player_id;
      setGameState(newState);
      const newDice = newState.dice ?? [];
      if (newDice.some((d) => d.value !== null)) {
        setDice(newDice);
      } else {
        setDice((prev) => newDice.map((d, i) => ({ ...d, value: prev[i]?.value ?? null })));
      }
      if (newState.status === 'finished') {
        navigate(`/games/${gameId}/end`);
      }
      if (newState.status === 'abandoned') {
        navigate('/lobby');
      }
    }
    if (board) setScoreboard(board);
  }

  return (
    <PageLayout>
      <div className="flex flex-col gap-4">
        <DiceRoller
          dice={dice}
          rollCount={rollCount}
          canRoll={canRoll}
          hasRolled={hasRolled}
          rollsRemaining={rollsRemaining}
          savedRolls={savedRolls}
          showSavedRolls={showSavedRolls}
          isMyTurn={isMyTurn}
          onRoll={handleRoll}
          onToggle={handleToggleDie}
        />
        <ScoreCard
          scoreboard={scoreboard}
          currentPlayerId={gameState?.current_player_id ?? null}
          myPlayerId={player?.id ?? 0}
          scoringOptions={scoringOptions}
          hasRolled={hasRolled}
          isMyTurn={isMyTurn}
          mode={gameMode ?? undefined}
          onScore={handleScore}
        />
      </div>
    </PageLayout>
  );
}
