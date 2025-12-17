/**
 * Barre de navigation.
 * Affiche les liens et le statut d'authentification.
 */

import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { logout, isAuthenticated, getStoredUser } from '../services/authService';
import '../styles/navbar.css';

function Navbar() {
  const navigate = useNavigate();
  const authenticated = isAuthenticated();
  const user = getStoredUser();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to={authenticated ? "/app" : "/"} className="navbar-brand">
          PredictWise
        </Link>
        
        <div className="navbar-menu">
          {authenticated ? (
            <>
              <Link to="/app" className="navbar-link">Hub</Link>
              <Link to="/app/sports" className="navbar-link">Sports</Link>
              <Link to="/app/finance" className="navbar-link">Finance</Link>
              <span className="navbar-user">
                {user?.first_name || user?.username || 'Utilisateur'}
              </span>
              <button onClick={handleLogout} className="btn btn-secondary btn-small">
                Deconnexion
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="navbar-link">Connexion</Link>
              <Link to="/signup" className="btn btn-primary btn-small">
                Inscription
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
