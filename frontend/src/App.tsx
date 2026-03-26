import { Navigate, Outlet, Route, Routes } from 'react-router-dom';
import { NavBar } from '@/components/NavBar';
import { Toaster } from '@/components/ui/toaster';
import { useAuth } from '@/hooks/AuthContext';
import { usePlayer } from '@/hooks/PlayerContext';
import { EndScreen } from '@/screens/end/EndScreen';
import { GameScreen } from '@/screens/game/GameScreen';
import { LobbyScreen } from '@/screens/lobby/LobbyScreen';
import { LoginScreen } from '@/screens/login/LoginScreen';
import { PlayerScreen } from '@/screens/player/PlayerScreen';
import { ProfileScreen } from '@/screens/player/ProfileScreen';
import { GamesPlayedScreen } from '@/screens/statistics/GamesPlayedScreen';
import { HighScoresScreen } from '@/screens/statistics/HighScoresScreen';

function AuthGuard() {
  const { user, isLoading } = useAuth();
  if (isLoading) return null;
  if (!user) return <Navigate to="/login" replace />;
  return <Outlet />;
}

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
        <Route path="/login" element={<LoginScreen />} />
        <Route element={<AuthGuard />}>
          <Route path="/" element={<PlayerScreen />} />
          <Route element={<ProtectedLayout />}>
            <Route path="/lobby" element={<LobbyScreen />} />
            <Route path="/profile" element={<ProfileScreen />} />
            <Route path="/games/:gameId" element={<GameScreen />} />
            <Route path="/games/:gameId/end" element={<EndScreen />} />
            <Route path="/statistics/high-scores" element={<HighScoresScreen />} />
            <Route path="/statistics/games-played" element={<GamesPlayedScreen />} />
          </Route>
        </Route>
      </Routes>
      <Toaster />
    </>
  );
}
