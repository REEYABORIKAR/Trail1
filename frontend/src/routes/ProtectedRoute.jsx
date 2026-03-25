import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

/**
 * ProtectedRoute — wraps any route that requires authentication.
 * Redirects to /login if no user is found.
 *
 * Usage in App.jsx:
 *   <Route path="/chat" element={<ProtectedRoute><ChatPage /></ProtectedRoute>} />
 */
export function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="splash">Loading…</div>;
  }

  return user ? children : <Navigate to="/login" replace />;
}

/**
 * GuestRoute — wraps routes only accessible when NOT logged in.
 * Redirects to /chat if the user is already authenticated.
 *
 * Usage in App.jsx:
 *   <Route path="/login" element={<GuestRoute><LoginPage /></GuestRoute>} />
 */
export function GuestRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="splash">Loading…</div>;
  }

  return user ? <Navigate to="/chat" replace /> : children;
}