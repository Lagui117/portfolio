/**
 * AdminRoute - Composant de route réservée aux administrateurs.
 * Redirige vers le dashboard si l'utilisateur n'est pas admin.
 */

import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const AdminRoute = ({ children }) => {
  const { user, isAdmin, loading } = useAuth();
  const token = localStorage.getItem('access_token') || localStorage.getItem('token');

  // Attendre le chargement de l'auth
  if (loading) {
    return (
      <div className="admin-loading">
        <div className="spinner"></div>
        <p>Vérification des permissions...</p>
      </div>
    );
  }

  // Pas de token = redirection login
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  // Pas admin = redirection dashboard
  if (!isAdmin) {
    return <Navigate to="/app" replace />;
  }

  return children;
};

export default AdminRoute;
