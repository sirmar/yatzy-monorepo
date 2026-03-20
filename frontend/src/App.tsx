import { usePlayer } from '@/hooks/PlayerContext';
import { EndScreen } from '@/screens/end/EndScreen';
import { GameScreen } from '@/screens/game/GameScreen';
import { LobbyScreen } from '@/screens/lobby/LobbyScreen';
import { PlayerScreen } from '@/screens/player/PlayerScreen';
import { Navigate, Route, Routes } from 'react-router-dom';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { player } = usePlayer();
  return player ? <>{children}</> : <Navigate to="/" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<PlayerScreen />} />
      <Route
        path="/lobby"
        element={
          <ProtectedRoute>
            <LobbyScreen />
          </ProtectedRoute>
        }
      />
      <Route
        path="/games/:gameId"
        element={
          <ProtectedRoute>
            <GameScreen />
          </ProtectedRoute>
        }
      />
      <Route
        path="/games/:gameId/end"
        element={
          <ProtectedRoute>
            <EndScreen />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}
