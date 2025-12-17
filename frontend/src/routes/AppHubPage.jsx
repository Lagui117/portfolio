/**
 * Page Hub principale apres connexion.
 * Affiche les deux domaines d'analyse disponibles.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMe, getStoredUser } from '../services/authService';
import '../styles/hub.css';

function AppHubPage() {
  const navigate = useNavigate();
  const [user, setUser] = useState(getStoredUser());

  useEffect(() => {
    // Charger les infos utilisateur
    async function loadUser() {
      try {
        const response = await getMe();
        setUser(response.user);
      } catch (err) {
        console.error('Erreur chargement utilisateur:', err);
      }
    }
    loadUser();
  }, []);

  return (
    <div className="hub-page">
      <header className="hub-header">
        <h1>Bienvenue sur PredictWise</h1>
        {user && (
          <p className="welcome-message">
            Bonjour, {user.first_name || user.username} !
          </p>
        )}
      </header>

      <section className="hub-intro">
        <p>
          Choisissez un domaine d'analyse pour commencer a explorer les donnees
          et generer des predictions experimentales.
        </p>
      </section>

      <section className="hub-cards">
        <div 
          className="hub-card sports-card"
          onClick={() => navigate('/app/sports')}
        >
          <div className="card-icon">&#9917;</div>
          <h2>Analyse Sportive</h2>
          <p>
            Analysez les matchs de football et explorez les statistiques des equipes,
            leur forme recente et les facteurs qui peuvent influencer les resultats.
          </p>
          <ul className="card-features">
            <li>Statistiques des equipes</li>
            <li>Historique des confrontations</li>
            <li>Analyse des cotes</li>
            <li>Predictions ML + GPT</li>
          </ul>
          <button className="btn btn-primary">
            Explorer les sports
          </button>
        </div>

        <div 
          className="hub-card finance-card"
          onClick={() => navigate('/app/finance')}
        >
          <div className="card-icon">&#128200;</div>
          <h2>Analyse Financiere</h2>
          <p>
            Explorez les donnees boursieres, les indicateurs techniques et les
            tendances de marche pour comprendre les mouvements des actifs.
          </p>
          <ul className="card-features">
            <li>Historique des prix</li>
            <li>Indicateurs techniques (RSI, MA)</li>
            <li>Analyse de volatilite</li>
            <li>Predictions ML + GPT</li>
          </ul>
          <button className="btn btn-primary">
            Explorer la finance
          </button>
        </div>
      </section>

      <section className="hub-disclaimer">
        <h3>Rappel important</h3>
        <p>
          Cette plateforme est strictement educative. Les predictions generees
          sont experimentales et ne doivent pas etre utilisees pour des decisions
          de pari ou d'investissement reel. Les marches financiers et les evenements
          sportifs sont par nature imprevisibles.
        </p>
      </section>
    </div>
  );
}

export default AppHubPage;
