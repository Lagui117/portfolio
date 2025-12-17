import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/auth.css';

const SignupPage = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [acceptTerms, setAcceptTerms] = useState(false);
  const navigate = useNavigate();
  const { register } = useAuth();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const validatePassword = (password) => {
    const minLength = password.length >= 8;
    const hasUpper = /[A-Z]/.test(password);
    const hasLower = /[a-z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password);
    return { minLength, hasUpper, hasLower, hasNumber, hasSpecial };
  };

  const passwordChecks = validatePassword(formData.password);
  const passwordStrength = Object.values(passwordChecks).filter(Boolean).length;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      return;
    }

    if (passwordStrength < 4) {
      setError('Le mot de passe ne respecte pas les critères de sécurité');
      return;
    }

    if (!acceptTerms) {
      setError('Veuillez accepter les conditions d\'utilisation');
      return;
    }

    setLoading(true);

    try {
      await register(formData.username, formData.email, formData.password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.message || 'Erreur lors de l\'inscription');
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
            <h1 className="auth-title">Créer un compte</h1>
            <p className="auth-subtitle">
              Rejoignez-nous pour explorer les analyses IA
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
              <label htmlFor="username" className="form-label">Nom d'utilisateur</label>
              <div className="input-wrapper">
                <span className="input-icon">��</span>
                <input
                  type="text"
                  id="username"
                  name="username"
                  className="form-input"
                  placeholder="john_doe"
                  value={formData.username}
                  onChange={handleChange}
                  required
                  autoComplete="username"
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="email" className="form-label">Email</label>
              <div className="input-wrapper">
                <span className="input-icon">📧</span>
                <input
                  type="email"
                  id="email"
                  name="email"
                  className="form-input"
                  placeholder="vous@exemple.com"
                  value={formData.email}
                  onChange={handleChange}
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
                  name="password"
                  className="form-input"
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  className="input-action"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? '👁️' : '👁️‍🗨️'}
                </button>
              </div>
              
              {formData.password && (
                <div className="password-strength">
                  <div className="password-strength-bar">
                    <div
                      className={`password-strength-fill strength-${passwordStrength}`}
                      style={{ width: `${(passwordStrength / 5) * 100}%` }}
                    />
                  </div>
                  <ul className="password-checks">
                    <li className={passwordChecks.minLength ? 'valid' : ''}>
                      {passwordChecks.minLength ? '✓' : '○'} 8 caractères minimum
                    </li>
                    <li className={passwordChecks.hasUpper ? 'valid' : ''}>
                      {passwordChecks.hasUpper ? '✓' : '○'} Une majuscule
                    </li>
                    <li className={passwordChecks.hasLower ? 'valid' : ''}>
                      {passwordChecks.hasLower ? '✓' : '○'} Une minuscule
                    </li>
                    <li className={passwordChecks.hasNumber ? 'valid' : ''}>
                      {passwordChecks.hasNumber ? '✓' : '○'} Un chiffre
                    </li>
                    <li className={passwordChecks.hasSpecial ? 'valid' : ''}>
                      {passwordChecks.hasSpecial ? '✓' : '○'} Un caractère spécial
                    </li>
                  </ul>
                </div>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="confirmPassword" className="form-label">Confirmer le mot de passe</label>
              <div className="input-wrapper">
                <span className="input-icon">🔒</span>
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="confirmPassword"
                  name="confirmPassword"
                  className="form-input"
                  placeholder="••••••••"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  required
                  autoComplete="new-password"
                />
                {formData.confirmPassword && (
                  <span className="input-status">
                    {formData.password === formData.confirmPassword ? '✅' : '❌'}
                  </span>
                )}
              </div>
            </div>

            <div className="form-options">
              <label className="checkbox-wrapper">
                <input
                  type="checkbox"
                  className="checkbox"
                  checked={acceptTerms}
                  onChange={(e) => setAcceptTerms(e.target.checked)}
                />
                <span className="checkbox-label">
                  J'accepte les <Link to="/terms" className="form-link-inline">conditions d'utilisation</Link>
                </span>
              </label>
            </div>

            <div className="auth-warning">
              <span className="auth-warning-icon">⚠️</span>
              <p className="auth-warning-text">
                Ce projet est <strong>purement éducatif</strong>. Les analyses ne constituent 
                pas des conseils d'investissement ou de paris.
              </p>
            </div>

            <button
              type="submit"
              className={`btn btn-primary btn-full ${loading ? 'btn-loading' : ''}`}
              disabled={loading || !acceptTerms}
            >
              {loading ? (
                <>
                  <span className="spinner" />
                  Création du compte...
                </>
              ) : (
                'Créer mon compte'
              )}
            </button>
          </form>

          <p className="auth-footer">
            Déjà un compte ?{' '}
            <Link to="/login" className="auth-footer-link">
              Se connecter
            </Link>
          </p>
        </div>

        <p className="auth-disclaimer">
          🎓 Projet éducatif — Aucune valeur financière
        </p>
      </div>
    </div>
  );
};

export default SignupPage;
