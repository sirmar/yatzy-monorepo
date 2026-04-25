import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '@/api';
import type { components } from '@/api/schema';
import { AuthScreenLayout } from '@/components/AuthScreenLayout';
import { PicturePicker } from '@/components/PicturePicker';
import { useAuth } from '@/hooks/AuthContext';
import { usePlayer } from '@/hooks/PlayerContext';
import { CreatePlayerForm } from './CreatePlayerForm';

type Player = components['schemas']['Player'];

export function PlayerScreen() {
  const { setPlayer } = usePlayer();
  const { accessToken } = useAuth();
  const navigate = useNavigate();
  const setPlayerRef = useRef(setPlayer);
  const navigateRef = useRef(navigate);
  const [newPlayer, setNewPlayer] = useState<Player | null>(null);

  useEffect(() => {
    if (!accessToken) return;
    const controller = new AbortController();
    apiClient.GET('/players/me', { signal: controller.signal }).then(({ data }) => {
      if (data) {
        setPlayerRef.current(data);
        navigateRef.current('/lobby');
      }
    });
    return () => controller.abort();
  }, [accessToken]);

  async function handleCreate(name: string) {
    const { data, error } = await apiClient.POST('/players', {
      body: { name },
    });
    if (error || !data) throw error ?? new Error('Failed to create player');
    setNewPlayer(data);
  }

  function handleFinish(player: Player) {
    setPlayer(player);
    navigate('/lobby');
  }

  if (newPlayer) {
    return (
      <AuthScreenLayout>
        <div className="p-6 flex flex-col gap-4 items-center">
          <div className="flex flex-col gap-0.5 w-full">
            <div className="text-[15px] font-semibold text-foreground">Add a profile picture</div>
            <div className="text-[12px] text-[var(--text-muted)]">
              Optional — you can always add one later from your profile.
            </div>
          </div>
          <PicturePicker
            player={newPlayer}
            size="md"
            className="w-20 h-20 text-[30px]"
            onSuccess={setNewPlayer}
          />
          <button
            type="button"
            onClick={() => handleFinish(newPlayer)}
            className="w-full h-9 bg-[var(--accent)] text-white rounded-lg text-[13px] font-semibold cursor-pointer hover:opacity-90"
          >
            {newPlayer.has_picture ? 'Continue' : 'Skip'}
          </button>
        </div>
      </AuthScreenLayout>
    );
  }

  return (
    <AuthScreenLayout>
      <div className="p-6 flex flex-col gap-4">
        <div className="flex flex-col gap-0.5">
          <div className="text-[15px] font-semibold text-foreground">Set up your profile</div>
          <div className="text-[12px] text-[var(--text-muted)]">
            Choose a display name to get started.
          </div>
        </div>
        <CreatePlayerForm onCreated={handleCreate} />
      </div>
    </AuthScreenLayout>
  );
}
