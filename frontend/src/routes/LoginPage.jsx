import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/auth.css';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const result = await login(email, password);
      
      if (result.success) {
        console.log('[LoginPage] Success, redirecting. User:', result.user);
        // Rediriger admin vers /admin, user vers /app
        const redirectPath = result.user?.is_admin ? '/admin' : '/app';
        navigate(redirectPath);
      } else {
        const errorMsg = typeof result.error === 'object'
          ? result.error.message || 'Email ou mot de passe incorrect'
          : result.error || 'Email ou mot de passe incorrect';
        setError(errorMsg);
      }
    } catch (err) {
      console.error('[LoginPage] Exception:', err);
      setError(err.response?.data?.message || 'Email ou mot de passe incorrect');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <Link to="/" className="auth-logo">
              <span className="gradient-text">PredictWise</span>
            </Link>
            <h1 className="auth-title">Accédez à votre dashboard</h1>
            <p className="auth-subtitle">
              Connectez-vous pour retrouver vos analyses
            </p>
          </div>

          {error && (
            <div className="alert alert-error">
              <span className="alert-icon">⚠️</span>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label htmlFor="email" className="form-label">Email</label>
              <div className="input-wrapper">
                <span className="input-icon">📧</span>
                <input
                  type="email"
                  id="email"
                  className="form-input"
                  placeholder="vous@exemple.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoComplete="email"
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="password" className="form-label">Mot de passe</label>
              <div className="input-wrapper">
                <span className="input-icon">🔒</span>
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  className="form-input"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  className="input-action"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? '👁️' : '👁️‍🗨️'}
                </button>
              </div>
            </div>

            <div className="form-options">
              <label className="checkbox-wrapper">
                <input type="checkbox" className="checkbox" />
                <span className="checkbox-label">Se souvenir de moi</span>
              </label>
              <Link to="/forgot-password" className="form-link">
                Mot de passe oublié ?
              </Link>
            </div>

            <button
              type="submit"
              className={`btn btn-primary btn-full ${loading ? 'btn-loading' : ''}`}
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="spinner" />
                  Connexion...
                </>
              ) : (
                'Se connecter'
              )}
            </button>
          </form>

          <div className="auth-divider">
            <span>ou</span>
          </div>

          <div className="auth-demo">
            <p className="auth-demo-text">Tester avec un compte démo :</p>
            <div className="auth-demo-accounts">
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => {
                  setEmail('demo@predictwise.com');
                  setPassword('Demo123!');
                }}
              >
                Compte Demo
              </button>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => {
                  setEmail('admin@predictwise.com');
                  setPassword('Admin123!');
                }}
              >
                Compte Admin
              </button>
            </div>
          </div>

          <p className="auth-footer">
            Pas encore de compte ?{' '}
            <Link to="/signup" className="auth-footer-link">
              Créer un compte
            </Link>
          </p>
        </div>

        <p className="auth-disclaimer">
          PredictWise — Analyse prédictive Sports & Finance
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
