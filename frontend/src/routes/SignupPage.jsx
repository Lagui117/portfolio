import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';
import '../styles/auth.css';

const SignupPage = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  
  const { register } = useAuth();
  const navigate = useNavigate();

  const validateForm = () => {
    const errors = {};
    
    if (!formData.email) {
      errors.email = 'Email requis';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = 'Email invalide';
    }
    
    if (!formData.password) {
      errors.password = 'Mot de passe requis';
    } else if (formData.password.length < 6) {
      errors.password = 'Minimum 6 caractères';
    }
    
    if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = 'Les mots de passe ne correspondent pas';
    }
    
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (fieldErrors[name]) {
      setFieldErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) return;

    setIsLoading(true);

    try {
      await register(formData.email, formData.password);
      navigate('/app');
    } catch (err) {
      setError(err.response?.data?.error || "Erreur lors de l'inscription. Veuillez réessayer.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <div className="auth-page">
        <div className="auth-container">
          <Link to="/" className="auth-back">
            ← Retour à l'accueil
          </Link>
          
          <div className="auth-card">
            <div className="auth-header">
              <div className="auth-logo">
                <div className="auth-logo-icon">📊</div>
                <span className="auth-logo-text">PredictWise</span>
              </div>
              <h1 className="auth-title">Créer un compte</h1>
              <p className="auth-subtitle">
                Rejoignez la plateforme de prédictions IA éducatives
              </p>
            </div>

            {error && (
              <div className="auth-error">
                ⚠️ {error}
              </div>
            )}

            <form className="auth-form" onSubmit={handleSubmit}>
              <div className="auth-field">
                <label className="auth-label" htmlFor="email">
                  Adresse email
                </label>
                <div className="auth-input-wrapper">
                  <span className="auth-input-icon">✉️</span>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    className={`auth-input ${fieldErrors.email ? 'error' : ''}`}
                    placeholder="vous@exemple.com"
                    value={formData.email}
                    onChange={handleChange}
                    autoComplete="email"
                  />
                </div>
                {fieldErrors.email && (
                  <span className="field-error">{fieldErrors.email}</span>
                )}
              </div>

              <div className="auth-field">
                <label className="auth-label" htmlFor="password">
                  Mot de passe
                </label>
                <div className="auth-input-wrapper">
                  <span className="auth-input-icon">🔒</span>
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    className={`auth-input ${fieldErrors.password ? 'error' : ''}`}
                    placeholder="Minimum 6 caractères"
                    value={formData.password}
                    onChange={handleChange}
                    autoComplete="new-password"
                  />
                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() => setShowPassword(!showPassword)}
                    aria-label={showPassword ? 'Masquer' : 'Afficher'}
                  >
                    {showPassword ? '🙈' : '👁️'}
                  </button>
                </div>
                {fieldErrors.password && (
                  <span className="field-error">{fieldErrors.password}</span>
                )}
              </div>

              <div className="auth-field">
                <label className="auth-label" htmlFor="confirmPassword">
                  Confirmer le mot de passe
                </label>
                <div className="auth-input-wrapper">
                  <span className="auth-input-icon">🔒</span>
                  <input
                    id="confirmPassword"
                    name="confirmPassword"
                    type={showPassword ? 'text' : 'password'}
                    className={`auth-input ${fieldErrors.confirmPassword ? 'error' : ''}`}
                    placeholder="Retapez votre mot de passe"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    autoComplete="new-password"
                  />
                </div>
                {fieldErrors.confirmPassword && (
                  <span className="field-error">{fieldErrors.confirmPassword}</span>
                )}
              </div>

              <button 
                type="submit" 
                className={`auth-submit ${isLoading ? 'loading' : ''}`}
                disabled={isLoading}
              >
                {isLoading ? (
                  <span className="spinner"></span>
                ) : (
                  <>Créer mon compte →</>
                )}
              </button>
            </form>

            <p style={{ 
              fontSize: '0.75rem', 
              color: 'var(--color-text-muted)', 
              textAlign: 'center',
              marginTop: '1rem'
            }}>
              En créant un compte, vous acceptez que cette plateforme 
              est <strong>purement éducative</strong> et ne constitue pas 
              un conseil d'investissement.
            </p>

            <div className="auth-footer">
              Déjà un compte ?{' '}
              <Link to="/login">Se connecter</Link>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default SignupPage;
