import { Navigate, Outlet, Route, Routes } from 'react-router-dom';
import { NavBar } from '@/components/NavBar';
import { Toaster } from '@/components/ui/toaster';
import { usePlayer } from '@/hooks/PlayerContext';
import { EndScreen } from '@/screens/end/EndScreen';
import { GameScreen } from '@/screens/game/GameScreen';
import { LobbyScreen } from '@/screens/lobby/LobbyScreen';
import { PlayerScreen } from '@/screens/player/PlayerScreen';

function ProtectedLayout() {
  const { player } = usePlayer();
  if (!player) return <Navigate to="/" replace />;
  return (
    <>
      <NavBar />
      <Outlet />
    </>
  );
}

export default function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<PlayerScreen />} />
        <Route element={<ProtectedLayout />}>
          <Route path="/lobby" element={<LobbyScreen />} />
          <Route path="/games/:gameId" element={<GameScreen />} />
          <Route path="/games/:gameId/end" element={<EndScreen />} />
        </Route>
      </Routes>
      <Toaster />
    </>
  );
}
