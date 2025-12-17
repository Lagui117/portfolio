/**
 * Topbar - Barre supérieure avec profil, recherche, notifications
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { logout } from '../../services/authService';
import './Topbar.css';

function Topbar({ user, onMenuToggle }) {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [showUserMenu, setShowUserMenu] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleSearch = (e) => {
    e.preventDefault();
    console.log('Recherche:', searchQuery);
  };

  return (
    <header className="topbar">
      <div className="topbar-left">
        <button className="mobile-menu-btn" onClick={onMenuToggle}>
          ☰
        </button>
        
        <form className="search-bar" onSubmit={handleSearch}>
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Rechercher un match, un actif, une analyse..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          <kbd className="search-shortcut">⌘K</kbd>
        </form>
      </div>

      <div className="topbar-right">
        <button className="icon-btn" title="Notifications">
          <span className="icon">🔔</span>
          <span className="badge-count">3</span>
        </button>

        <div className="user-menu-container">
          <button 
            className="user-profile-btn"
            onClick={() => setShowUserMenu(!showUserMenu)}
          >
            <div className="avatar">
              {user?.first_name?.[0] || user?.username?.[0] || 'U'}
            </div>
            <div className="user-info">
              <span className="user-name">{user?.first_name || user?.username || 'Utilisateur'}</span>
              <span className="user-role">Premium</span>
            </div>
            <span className="dropdown-arrow">▼</span>
          </button>

          {showUserMenu && (
            <div className="user-dropdown">
              <div className="dropdown-header">
                <div className="avatar-large">
                  {user?.first_name?.[0] || user?.username?.[0] || 'U'}
                </div>
                <div>
                  <div className="dropdown-name">
                    {user?.first_name} {user?.last_name}
                  </div>
                  <div className="dropdown-email">{user?.email}</div>
                </div>
              </div>
              
              <div className="dropdown-divider" />
              
              <button className="dropdown-item" onClick={() => navigate('/app/profile')}>
                <span>👤</span> Mon profil
              </button>
              <button className="dropdown-item" onClick={() => navigate('/app/settings')}>
                <span>⚙️</span> Paramètres
              </button>
              <button className="dropdown-item" onClick={() => navigate('/app/billing')}>
                <span>💳</span> Abonnement
              </button>
              
              <div className="dropdown-divider" />
              
              <button className="dropdown-item danger" onClick={handleLogout}>
                <span>🚪</span> Déconnexion
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

export default Topbar;
