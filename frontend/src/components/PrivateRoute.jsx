import { Navigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

function PrivateRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return <div className="loading">Chargement...</div>
  }

  return isAuthenticated ? children : <Navigate to="/login" replace />
}

export default PrivateRoute
