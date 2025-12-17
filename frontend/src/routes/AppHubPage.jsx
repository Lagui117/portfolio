/**
 * Hub principal de l'application.
 * Affiche un message de bienvenue et les deux modules (Sports/Finance).
 */

import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getMe, logout } from '../services/authService';
import { PageContainer, Card, LoadingIndicator, ErrorBanner } from '../components/UIComponents';
import '../styles/hub.css';

function AppHubPage() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadUserData();
  }, []);

  const loadUserData = async () => {
    setLoading(true);
    setError('');
    try {
      const userData = await getMe();
      setUser(userData);
    } catch (err) {
      setError('Impossible de charger vos informations. Veuillez vous reconnecter.');
      console.error('Erreur chargement utilisateur:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (loading) {
    return (
      <PageContainer>
        <LoadingIndicator message="Chargement de votre espace..." />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <div className="hub-header">
        <div>
          <h1>
            Bienvenue{user ? `, ${user.first_name}` : ''} !
          </h1>
          <p className="hub-subtitle">
            Choisissez un module pour commencer vos prédictions
          </p>
        </div>
        <button onClick={handleLogout} className="btn btn-secondary">
          Déconnexion
        </button>
      </div>

      <ErrorBanner message={error} onClose={() => setError('')} />

      <div className="modules-grid">
        <Card className="module-card sports-module">
          <div className="module-icon">⚽</div>
          <h2>Prédictions Sportives</h2>
          <p>
            Analysez les matchs de football avec notre IA pour prédire les résultats
            et obtenir des insights détaillés.
          </p>
          <Link to="/app/sports" className="btn btn-primary">
            Accéder au module Sports
          </Link>
        </Card>

        <Card className="module-card finance-module">
          <div className="module-icon">📈</div>
          <h2>Prédictions Financières</h2>
          <p>
            Analysez les actions boursières avec des indicateurs techniques et
            l'IA pour prédire les tendances.
          </p>
          <Link to="/app/finance" className="btn btn-primary">
            Accéder au module Finance
          </Link>
        </Card>
      </div>

      <div className="hub-footer">
        <p>
          Propulsé par GPT-4 • Données en temps réel
        </p>
      </div>
    </PageContainer>
  );
}

export default AppHubPage;
