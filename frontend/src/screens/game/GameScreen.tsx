import { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import type { components } from '@/api';
import { apiClient } from '@/api';
import { ConfirmDialog } from '@/components/ConfirmDialog';
import { ModeBadge } from '@/components/ModeBadge';
import { PageHeader } from '@/components/PageHeader';
import { PageLayout } from '@/components/PageLayout';
import { Button } from '@/components/ui/button';
import { usePlayer } from '@/hooks/PlayerContext';
import { useErrorToast } from '@/hooks/use-toast';
import { usePlayerNames } from '@/hooks/usePlayerNames';
import { usePolling } from '@/hooks/usePolling';
import { POLLING_INTERVAL_MS } from '@/lib/constants';
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
  const [creatorId, setCreatorId] = useState<number | null>(null);
  const [gameMode, setGameMode] = useState<GameMode | null>(null);
  const [dice, setDice] = useState<Die[]>([]);
  const [rollCount, setRollCount] = useState(0);
  const [scoreboard, setScoreboard] = useState<PlayerScorecard[]>([]);
  const [scoringOptions, setScoringOptions] = useState<ScoringOption[] | null>(null);
  const playerNames = usePlayerNames();
  const [confirmAbort, setConfirmAbort] = useState(false);

  const prevPlayerIdRef = useRef<number | null | undefined>(undefined);

  const isMyTurn = gameState?.current_player_id === player?.id;
  const rollsRemaining = gameState?.rolls_remaining ?? 0;
  const savedRolls = gameState?.saved_rolls ?? 0;
  const canRoll = isMyTurn && (rollsRemaining > 0 || savedRolls > 0);
  const hasRolled = dice.some((d) => d.value !== null);

  useEffect(() => {
    if (!gameId) return;
    const gid = Number(gameId);

    Promise.all([
      apiClient.GET('/games/{game_id}', { params: { path: { game_id: gid } } }),
      apiClient.GET('/games/{game_id}/state', { params: { path: { game_id: gid } } }),
      apiClient.GET('/games/{game_id}/scoreboard', { params: { path: { game_id: gid } } }),
    ]).then(([{ data: game }, { data: state }, { data: board }]) => {
      if (game) {
        setCreatorId(game.creator_id);
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
            })
            .then(({ data: options }) => {
              if (options) setScoringOptions(options);
            });
        }
      }
      if (board) setScoreboard(board);
    });
  }, [gameId, navigate, player?.id]);

  usePolling(
    async () => {
      if (!gameId) return;
      const { data } = await apiClient.GET('/games/{game_id}/state', {
        params: { path: { game_id: Number(gameId) } },
      });
      if (!data) return;

      const currentId = data.current_player_id;
      if (prevPlayerIdRef.current !== undefined && currentId !== prevPlayerIdRef.current) {
        setScoringOptions(null);
        setDice(data.dice ?? []);
        const { data: board } = await apiClient.GET('/games/{game_id}/scoreboard', {
          params: { path: { game_id: Number(gameId) } },
        });
        if (board) setScoreboard(board);
      } else if (currentId !== player?.id) {
        setDice(data.dice ?? []);
      }

      prevPlayerIdRef.current = currentId;
      setGameState(data);

      if (data.status === 'finished') {
        navigate(`/games/${gameId}/end`);
      }
      if (data.status === 'abandoned') {
        navigate('/lobby');
      }
    },
    { interval: POLLING_INTERVAL_MS, enabled: gameState?.status === 'active' }
  );

  function handleConfirmAbort() {
    setConfirmAbort(false);
    handleAbort();
  }

  async function handleAbort() {
    if (!gameId) return;
    const { error } = await apiClient.POST('/games/{game_id}/abort', {
      params: { path: { game_id: Number(gameId) } },
    });
    if (error) {
      errorToast('Failed to abort game');
      return;
    }
    navigate('/lobby');
  }

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
        return { ...prev, rolls_remaining: (prev.rolls_remaining ?? 0) - 1 };
      }
      return { ...prev, saved_rolls: (prev.saved_rolls ?? 0) - 1 };
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
    setDice([]);
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
      setDice(newState.dice ?? []);
      if (newState.status === 'finished') {
        navigate(`/games/${gameId}/end`);
      }
      if (newState.status === 'abandoned') {
        navigate('/lobby');
      }
    }
    if (board) setScoreboard(board);
  }

  const currentPlayerName =
    gameState?.current_player_id != null ? playerNames[gameState.current_player_id] : null;

  return (
    <PageLayout>
      <div className="flex flex-col gap-6">
        <PageHeader
          title={
            <div className="flex items-center gap-2">
              <span>Game #{gameId}</span>
              {gameMode != null && <ModeBadge mode={gameMode} />}
            </div>
          }
          action={
            player?.id === creatorId && gameState?.status === 'active' ? (
              <>
                <ConfirmDialog
                  open={confirmAbort}
                  title="Abort game"
                  description="Are you sure you want to abort this game? This cannot be undone."
                  confirmLabel="Abort"
                  onConfirm={handleConfirmAbort}
                  onCancel={() => setConfirmAbort(false)}
                />
                <Button
                  variant="ghost"
                  className="text-gray-500 hover:text-red-400 hover:bg-red-400/10"
                  onClick={() => setConfirmAbort(true)}
                >
                  Abort Game
                </Button>
              </>
            ) : undefined
          }
        />
        {currentPlayerName && (
          <p className="text-white text-lg font-semibold">{currentPlayerName}'s turn</p>
        )}
        <DiceRoller
          dice={dice}
          rollCount={rollCount}
          canRoll={canRoll}
          hasRolled={hasRolled}
          rollsRemaining={rollsRemaining}
          savedRolls={savedRolls}
          isMyTurn={isMyTurn}
          onRoll={handleRoll}
          onToggle={handleToggleDie}
        />
        <ScoreCard
          scoreboard={scoreboard}
          playerNames={playerNames}
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
