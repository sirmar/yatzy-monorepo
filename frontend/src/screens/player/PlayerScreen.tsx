import { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '@/api';
import { AuthScreenLayout } from '@/components/AuthScreenLayout';
import { useAuth } from '@/hooks/AuthContext';
import { usePlayer } from '@/hooks/PlayerContext';
import { CreatePlayerForm } from './CreatePlayerForm';

export function PlayerScreen() {
  const { setPlayer } = usePlayer();
  const { accessToken } = useAuth();
  const navigate = useNavigate();
  const setPlayerRef = useRef(setPlayer);
  const navigateRef = useRef(navigate);

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
    setPlayer(data);
    navigate('/lobby');
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
