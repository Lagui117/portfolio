import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import '../styles/landing.css';

const LandingPage = () => {
  return (
    <div className="landing">
      <Navbar />

      {/* HERO */}
      <section className="hero">
        <div className="hero-container">
          <div className="hero-content">
            <div className="hero-badge">
              <span className="hero-badge-dot" />
              Plateforme IA Éducative
            </div>

            <h1 className="hero-title">
              Analysez. Comprenez.<br />
              <span className="gradient-text">Apprenez l'IA.</span>
            </h1>

            <p className="hero-subtitle">
              Découvrez comment l'intelligence artificielle analyse les données sportives 
              et financières. Une plateforme éducative pour comprendre le potentiel du machine learning.
            </p>

            <div className="hero-cta">
              <Link to="/signup" className="btn btn-primary btn-lg">
                Commencer gratuitement →
              </Link>
              <Link to="/login" className="btn btn-secondary btn-lg">
                Se connecter
              </Link>
            </div>

            <div className="hero-stats">
              <div className="hero-stat">
                <div className="hero-stat-value">2</div>
                <div className="hero-stat-label">Domaines d'analyse</div>
              </div>
              <div className="hero-stat">
                <div className="hero-stat-value">GPT-4</div>
                <div className="hero-stat-label">Powered by</div>
              </div>
              <div className="hero-stat">
                <div className="hero-stat-value">100%</div>
                <div className="hero-stat-label">Éducatif</div>
              </div>
            </div>
          </div>

          <div className="hero-preview">
            <div className="hero-preview-card">
              <div className="hero-preview-header">
                <div className="hero-preview-dots">
                  <span className="hero-preview-dot" />
                  <span className="hero-preview-dot" />
                  <span className="hero-preview-dot" />
                </div>
                <span className="hero-preview-title">PredictWise Dashboard</span>
              </div>
              <div className="hero-preview-content">
                <div className="hero-preview-item">
                  <div className="hero-preview-item-left">
                    <span className="hero-preview-item-icon">⚽</span>
                    <div>
                      <div className="hero-preview-item-name">PSG vs Marseille</div>
                      <div className="hero-preview-item-sub">Ligue 1 • Analyse IA</div>
                    </div>
                  </div>
                  <div className="hero-preview-item-value positive">73%</div>
                </div>
                <div className="hero-preview-item">
                  <div className="hero-preview-item-left">
                    <span className="hero-preview-item-icon">📈</span>
                    <div>
                      <div className="hero-preview-item-name">Apple (AAPL)</div>
                      <div className="hero-preview-item-sub">NASDAQ • Tendance</div>
                    </div>
                  </div>
                  <div className="hero-preview-item-value positive">+2.4%</div>
                </div>
                <div className="hero-preview-item">
                  <div className="hero-preview-item-left">
                    <span className="hero-preview-item-icon">🏀</span>
                    <div>
                      <div className="hero-preview-item-name">Lakers vs Warriors</div>
                      <div className="hero-preview-item-sub">NBA • Analyse IA</div>
                    </div>
                  </div>
                  <div className="hero-preview-item-value positive">68%</div>
                </div>
              </div>
            </div>

            <div className="hero-float-1">
              <div className="hero-float-badge">
                <span className="hero-float-badge-icon">🤖</span>
                <span>IA Active</span>
              </div>
            </div>

            <div className="hero-float-2">
              <div className="hero-float-badge">
                <span className="hero-float-badge-icon">🔒</span>
                <span>Sécurisé</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section className="features">
        <div className="section-header">
          <span className="section-badge">Fonctionnalités</span>
          <h2 className="section-title">Explorez deux univers d'analyse</h2>
          <p className="section-subtitle">
            Une plateforme complète pour découvrir comment l'IA traite et analyse les données
          </p>
        </div>

        <div className="features-grid">
          <div className="card feature-card">
            <div className="card-icon">⚽</div>
            <h3 className="card-title">Analyse Sportive</h3>
            <p className="card-description">
              Explorez les analyses de matchs basées sur l'historique des équipes, 
              les performances récentes et les statistiques avancées.
            </p>
          </div>

          <div className="card feature-card">
            <div className="card-icon">📈</div>
            <h3 className="card-title">Analyse Financière</h3>
            <p className="card-description">
              Comprenez comment l'IA analyse les tendances boursières, les indicateurs 
              techniques et le sentiment du marché.
            </p>
          </div>

          <div className="card feature-card">
            <div className="card-icon">🤖</div>
            <h3 className="card-title">Propulsé par GPT-4</h3>
            <p className="card-description">
              Notre moteur utilise les dernières avancées en intelligence artificielle 
              pour générer des analyses détaillées et pédagogiques.
            </p>
          </div>

          <div className="card feature-card">
            <div className="card-icon">📊</div>
            <h3 className="card-title">Visualisations</h3>
            <p className="card-description">
              Des graphiques interactifs et des tableaux de bord clairs pour mieux 
              comprendre les données et les tendances.
            </p>
          </div>

          <div className="card feature-card">
            <div className="card-icon">🎓</div>
            <h3 className="card-title">100% Éducatif</h3>
            <p className="card-description">
              Chaque analyse explique la méthodologie utilisée. Apprenez comment 
              fonctionne l'IA, pas seulement ses résultats.
            </p>
          </div>

          <div className="card feature-card">
            <div className="card-icon">🔐</div>
            <h3 className="card-title">Sécurisé</h3>
            <p className="card-description">
              Authentification sécurisée et protection de vos données. 
              Votre vie privée est notre priorité.
            </p>
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="how-it-works">
        <div className="section-header">
          <span className="section-badge">Comment ça marche</span>
          <h2 className="section-title">Simple comme 1, 2, 3</h2>
          <p className="section-subtitle">
            Commencez à explorer les analyses IA en quelques minutes
          </p>
        </div>

        <div className="steps-container">
          <div className="step-card">
            <div className="step-number">1</div>
            <h3 className="step-title">Créez votre compte</h3>
            <p className="step-description">
              Inscription gratuite en quelques secondes. Aucune carte bancaire requise.
            </p>
          </div>

          <div className="step-card">
            <div className="step-number">2</div>
            <h3 className="step-title">Choisissez un domaine</h3>
            <p className="step-description">
              Sports ou Finance ? Sélectionnez le domaine qui vous intéresse pour explorer.
            </p>
          </div>

          <div className="step-card">
            <div className="step-number">3</div>
            <h3 className="step-title">Explorez les analyses</h3>
            <p className="step-description">
              Posez vos questions et découvrez comment l'IA génère ses prédictions éducatives.
            </p>
          </div>
        </div>
      </section>

      {/* EXAMPLES */}
      <section className="examples">
        <div className="section-header">
          <span className="section-badge">Exemples</span>
          <h2 className="section-title">L'IA en action</h2>
          <p className="section-subtitle">
            Aperçu des analyses générées par notre plateforme
          </p>
        </div>

        <div className="examples-grid">
          <div className="card example-card">
            <div className="example-header">
              <span className="example-icon">⚽</span>
              <span className="example-category">Analyse Sportive</span>
            </div>
            <div className="example-body">
              <p className="example-question">
                "Analyse du match PSG vs Marseille"
              </p>
              <div className="example-result">
                <div className="example-result-row">
                  <span className="example-result-label">Confiance analyse</span>
                  <span className="example-result-value positive">73%</span>
                </div>
                <p className="example-reasoning">
                  L'IA a analysé 50 matchs historiques, les performances récentes (5 derniers matchs), 
                  les statistiques des joueurs clés et les conditions du match pour générer cette analyse éducative.
                </p>
              </div>
            </div>
          </div>

          <div className="card example-card">
            <div className="example-header">
              <span className="example-icon">📈</span>
              <span className="example-category">Analyse Financière</span>
            </div>
            <div className="example-body">
              <p className="example-question">
                "Tendance de l'action Apple (AAPL)"
              </p>
              <div className="example-result">
                <div className="example-result-row">
                  <span className="example-result-label">Tendance identifiée</span>
                  <span className="example-result-value positive">+2.4%</span>
                </div>
                <p className="example-reasoning">
                  Analyse basée sur les indicateurs techniques (RSI, MACD), les résultats trimestriels, 
                  le sentiment du marché et les actualités récentes pour comprendre les facteurs d'influence.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* DISCLAIMER */}
      <section className="disclaimer">
        <div className="disclaimer-content">
          <div className="disclaimer-icon">⚠️</div>
          <h3 className="disclaimer-title">Important : Projet Éducatif</h3>
          <p className="disclaimer-text">
            PredictWise est une plateforme <strong>purement éducative</strong> conçue pour démontrer 
            les capacités de l'intelligence artificielle. Les analyses générées ne constituent 
            <strong> en aucun cas</strong> des conseils d'investissement ou des recommandations de paris. 
            <br /><br />
            <strong>Ne prenez jamais de décisions financières</strong> basées sur ces analyses. 
            Ce projet est destiné à l'apprentissage et la démonstration technologique uniquement.
            Les performances passées ne garantissent pas les résultats futurs.
          </p>
        </div>
      </section>

      {/* CTA */}
      <section className="cta-section">
        <h2 className="cta-title">Prêt à explorer ?</h2>
        <p className="cta-subtitle">
          Rejoignez PredictWise et découvrez le potentiel de l'IA dans l'analyse de données.
        </p>
        <Link to="/signup" className="btn btn-primary btn-xl">
          Créer un compte gratuit →
        </Link>
      </section>

      {/* FOOTER */}
      <footer className="footer">
        <div className="footer-content">
          <div className="footer-logo">
            <span className="gradient-text">PredictWise</span>
          </div>
          <nav className="footer-links">
            <Link to="/login" className="footer-link">Connexion</Link>
            <Link to="/signup" className="footer-link">Inscription</Link>
            <span className="footer-link">À propos</span>
            <span className="footer-link">Contact</span>
          </nav>
          <p className="footer-copyright">
            © 2024 PredictWise. Projet éducatif — Aucune valeur financière ou de pari.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
