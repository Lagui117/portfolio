/**
 * Page de connexion.
 * Formulaire email + password avec gestion des erreurs.
 */

import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { login, storeAuthData } from '../services/authService';
import '../styles/auth.css';

function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(location.state?.message || '');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);
    
    try {
      const response = await login({
        email: formData.email,
        password: formData.password,
      });
      
      // Stocker le token et les infos utilisateur
      storeAuthData(response.access_token, response.user);
      
      // Rediriger vers le hub
      navigate('/app');
      
    } catch (err) {
      const message = err.response?.data?.error || 'Identifiants invalides.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <h1>Connexion</h1>
          <p>Accedez a votre compte PredictWise</p>
        </div>

        {success && (
          <div className="success-banner">
            {success}
          </div>
        )}

        {error && (
          <div className="error-banner">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="votre@email.com"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Mot de passe</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Votre mot de passe"
              required
            />
          </div>

          <button 
            type="submit" 
            className="btn btn-primary btn-full"
            disabled={loading}
          >
            {loading ? 'Connexion en cours...' : 'Se connecter'}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Pas encore inscrit ? <Link to="/signup">Creer un compte</Link>
          </p>
          <p>
            <Link to="/">Retour a l'accueil</Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
