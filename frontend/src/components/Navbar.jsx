import { useState, useEffect, useRef } from 'react';
import { Link, NavLink, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/navbar.css';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    setIsMobileOpen(false);
  }, [location.pathname]);

  const handleLogout = () => {
    logout();
    setIsDropdownOpen(false);
    navigate('/');
  };

  const getInitials = (email) => email ? email.charAt(0).toUpperCase() : 'U';

  return (
    <nav className={`navbar ${isScrolled ? 'scrolled' : ''}`}>
      <div className="navbar-container">
        <Link to={user ? '/app' : '/'} className="navbar-logo">
          <div className="navbar-logo-icon">📊</div>
          <span className="navbar-logo-text">PredictWise</span>
        </Link>

        <button 
          className="navbar-toggle"
          onClick={() => setIsMobileOpen(!isMobileOpen)}
          aria-label="Menu"
        >
          <span /><span /><span />
        </button>

        {user && (
          <div className={`navbar-nav ${isMobileOpen ? 'open' : ''}`}>
            <NavLink to="/app" end className={({ isActive }) => `navbar-link ${isActive ? 'active' : ''}`}>
              Hub
            </NavLink>
            <NavLink to="/app/sports" className={({ isActive }) => `navbar-link ${isActive ? 'active' : ''}`}>
              Sports
            </NavLink>
            <NavLink to="/app/finance" className={({ isActive }) => `navbar-link ${isActive ? 'active' : ''}`}>
              Finance
            </NavLink>
          </div>
        )}

        <div className="navbar-actions">
          {user ? (
            <div 
              className={`navbar-user ${isDropdownOpen ? 'open' : ''}`} 
              ref={dropdownRef}
            >
              <div className="navbar-avatar" onClick={() => setIsDropdownOpen(!isDropdownOpen)}>
                {getInitials(user.email)}
              </div>
              <div className="navbar-dropdown">
                <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--color-border)' }}>
                  <div style={{ fontWeight: 600, color: 'var(--color-text-primary)', fontSize: '14px' }}>
                    {user.email}
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--color-text-muted)', marginTop: '2px' }}>
                    {user.role === 'admin' ? '👑 Administrateur' : '👤 Utilisateur'}
                  </div>
                </div>
                <Link to="/app/profile" className="navbar-dropdown-item" onClick={() => setIsDropdownOpen(false)}>
                  👤 Mon profil
                </Link>
                {user.role === 'admin' && (
                  <Link to="/app/admin" className="navbar-dropdown-item" onClick={() => setIsDropdownOpen(false)}>
                    ⚙️ Administration
                  </Link>
                )}
                <div className="navbar-dropdown-divider" />
                <button className="navbar-dropdown-item danger" onClick={handleLogout}>
                  🚪 Déconnexion
                </button>
              </div>
            </div>
          ) : (
            <>
              <Link to="/login" className="btn btn-ghost">Se connecter</Link>
              <Link to="/signup" className="btn btn-primary">Commencer</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
