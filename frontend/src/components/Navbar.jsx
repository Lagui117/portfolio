import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import './Navbar.css'

function Navbar() {
  const { user, isAuthenticated, logout } = useAuth()

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to={isAuthenticated ? "/hub" : "/"} className="navbar-brand">
          PredictWise
        </Link>
        
        <div className="navbar-menu">
          {isAuthenticated ? (
            <>
              <Link to="/hub" className="navbar-link">Hub IA</Link>
              <Link to="/sports" className="navbar-link">Sports</Link>
              <Link to="/finance" className="navbar-link">Finance</Link>
              <Link to="/dashboard" className="navbar-link">Dashboard</Link>
              <span className="navbar-user">Bonjour, {user?.username}</span>
              <button onClick={logout} className="btn btn-secondary">
                Déconnexion
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="navbar-link">Connexion</Link>
              <Link to="/signup" className="btn btn-primary">
                Inscription
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}

export default Navbar
