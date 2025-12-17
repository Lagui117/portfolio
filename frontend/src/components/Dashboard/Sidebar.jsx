/**
 * Sidebar - Navigation principale du dashboard
 */

import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Sidebar.css';

const menuItems = [
  { id: 'home', label: 'Accueil', icon: '🏠', path: '/app' },
  { id: 'sports', label: 'Sports', icon: '⚽', path: '/app/sports' },
  { id: 'finance', label: 'Finance', icon: '📈', path: '/app/finance' },
  { id: 'history', label: 'Historique', icon: '📊', path: '/app/history' },
  { id: 'settings', label: 'Paramètres', icon: '⚙️', path: '/app/settings' },
  { id: 'support', label: 'Support', icon: '💬', path: '/app/support' },
];

function Sidebar({ collapsed = false, onToggle }) {
  const location = useLocation();

  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <div className="logo-container">
          <div className="logo-icon gradient-text">PW</div>
          {!collapsed && <span className="logo-text gradient-text">PredictWise</span>}
        </div>
        <button className="collapse-btn" onClick={onToggle} title={collapsed ? 'Étendre' : 'Réduire'}>
          {collapsed ? '→' : '←'}
        </button>
      </div>

      <nav className="sidebar-nav">
        {menuItems.map(item => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.id}
              to={item.path}
              className={`nav-item ${isActive ? 'active' : ''}`}
              title={collapsed ? item.label : ''}
            >
              <span className="nav-icon">{item.icon}</span>
              {!collapsed && <span className="nav-label">{item.label}</span>}
              {isActive && <div className="active-indicator" />}
            </Link>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="user-badge">
          <div className="badge-icon">🎓</div>
          {!collapsed && (
            <div className="badge-text">
              <span className="badge-label">Mode</span>
              <span className="badge-value">Éducatif</span>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;
