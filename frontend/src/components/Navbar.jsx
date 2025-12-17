import { useState, useEffect, useRef } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/navbar.css';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Handle scroll
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    logout();
    setIsDropdownOpen(false);
    navigate('/');
  };

  const getInitials = (email) => {
    if (!email) return 'U';
    return email.charAt(0).toUpperCase();
  };

  return (
    <nav className={`navbar ${isScrolled ? 'scrolled' : ''}`}>
      <div className="navbar-container">
        {/* Logo */}
        <Link to={user ? '/hub' : '/'} className="navbar-logo">
          <div className="navbar-logo-icon">📊</div>
          <span className="navbar-logo-text">PredictWise</span>
        </Link>

        {/* Mobile Toggle */}
        <button 
          className="navbar-toggle"
          onClick={() => setIsMobileOpen(!isMobileOpen)}
          aria-label="Menu"
        >
          <span></span>
          <span></span>
          <span></span>
        </button>

        {/* Navigation Links */}
        {user && (
          <div className={`navbar-nav ${isMobileOpen ? 'open' : ''}`}>
            <NavLink 
              to="/hub" 
              className={({ isActive }) => `navbar-link ${isActive ? 'active' : ''}`}
              onClick={() => setIsMobileOpen(false)}
            >
              Hub
            </NavLink>
            <NavLink 
              to="/sports" 
              className={({ isActive }) => `navbar-link ${isActive ? 'active' : ''}`}
              onClick={() => setIsMobileOpen(false)}
            >
              Sports
            </NavLink>
            <NavLink 
              to="/finance" 
              className={({ isActive }) => `navbar-link ${isActive ? 'active' : ''}`}
              onClick={() => setIsMobileOpen(false)}
            >
              Finance
            </NavLink>
            <NavLink 
              to="/dashboard" 
              className={({ isActive }) => `navbar-link ${isActive ? 'active' : ''}`}
              onClick={() => setIsMobileOpen(false)}
            >
              Dashboard
            </NavLink>
          </div>
        )}

        {/* Actions */}
        <div className="navbar-actions">
          {user ? (
            <div className={`navbar-dropdown ${isDropdownOpen ? 'open' : ''}`} ref={dropdownRef}>
              <div 
                className="navbar-user"
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              >
                <span className="navbar-username">{user.email}</span>
                <div className="navbar-avatar">
                  {getInitials(user.email)}
                </div>
              </div>
              
              <div className="navbar-dropdown-menu">
                <Link 
                  to="/profile" 
                  className="navbar-dropdown-item"
                  onClick={() => setIsDropdownOpen(false)}
                >
                  👤 Mon profil
                </Link>
                <Link 
                  to="/dashboard" 
                  className="navbar-dropdown-item"
                  onClick={() => setIsDropdownOpen(false)}
                >
                  📊 Dashboard
                </Link>
                {user.role === 'admin' && (
                  <Link 
                    to="/admin" 
                    className="navbar-dropdown-item"
                    onClick={() => setIsDropdownOpen(false)}
                  >
                    ⚙️ Administration
                  </Link>
                )}
                <div className="navbar-dropdown-divider"></div>
                <button 
                  className="navbar-dropdown-item danger"
                  onClick={handleLogout}
                >
                  🚪 Déconnexion
                </button>
              </div>
            </div>
          ) : (
            <>
              <Link to="/login" className="navbar-btn navbar-btn-secondary">
                Se connecter
              </Link>
              <Link to="/signup" className="navbar-btn navbar-btn-primary">
                S'inscrire
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
