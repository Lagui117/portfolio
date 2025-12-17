/**
 * Page d'accueil (Landing Page).
 * Presentation de PredictWise avec liens vers inscription/connexion.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/landing.css';

function LandingPage() {
  return (
    <div className="landing-page">
      <header className="landing-header">
        <h1>PredictWise</h1>
        <p className="tagline">Plateforme educative d'analyse predictive</p>
      </header>

      <section className="landing-hero">
        <div className="hero-content">
          <h2>Explorez l'analyse de donnees</h2>
          <p>
            PredictWise est une plateforme pedagogique qui vous permet de decouvrir
            les techniques d'analyse et de prediction dans deux domaines passionnants :
          </p>
          
          <div className="features">
            <div className="feature">
              <span className="feature-icon">&#9917;</span>
              <h3>Analyse Sportive</h3>
              <p>
                Explorez les statistiques des matchs, la dynamique des equipes
                et les facteurs qui influencent les resultats sportifs.
              </p>
            </div>
            
            <div className="feature">
              <span className="feature-icon">&#128200;</span>
              <h3>Analyse Financiere</h3>
              <p>
                Decouvrez les indicateurs techniques, les tendances de marche
                et les principes de l'analyse boursiere.
              </p>
            </div>
          </div>

          <div className="cta-buttons">
            <Link to="/signup" className="btn btn-primary">
              S'inscrire
            </Link>
            <Link to="/login" className="btn btn-secondary">
              Se connecter
            </Link>
          </div>
        </div>
      </section>

      <section className="landing-disclaimer">
        <h3>Important</h3>
        <p>
          PredictWise est un projet strictement educatif. Les analyses et predictions
          presentees sont experimentales et ne doivent en aucun cas etre utilisees
          pour des decisions de pari ou d'investissement reel.
        </p>
        <p>
          Les marches financiers et les evenements sportifs sont par nature imprevisibles.
          Toute prediction comporte une marge d'erreur significative.
        </p>
      </section>

      <footer className="landing-footer">
        <p>&copy; 2025 PredictWise - Projet educatif</p>
      </footer>
    </div>
  );
}

export default LandingPage;
