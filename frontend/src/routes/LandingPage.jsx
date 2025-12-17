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
              Propulsé par GPT-4
            </div>

            <h1 className="hero-title">
              L'avantage<br />
              <span className="gradient-text">décisionnel.</span>
            </h1>

            <p className="hero-subtitle">
              Intelligence artificielle de pointe pour l'analyse Sports & Finance. 
              Transformez les données en décisions stratégiques.
            </p>

            <div className="hero-cta">
              <Link to="/signup" className="btn btn-primary btn-lg">
                Commencer l'analyse →
              </Link>
              <Link to="/login" className="btn btn-secondary btn-lg">
                Accéder au dashboard
              </Link>
            </div>

            <div className="hero-stats">
              <div className="hero-stat">
                <div className="hero-stat-value">+10K</div>
                <div className="hero-stat-label">Analyses générées</div>
              </div>
              <div className="hero-stat">
                <div className="hero-stat-value">GPT-4</div>
                <div className="hero-stat-label">Moteur IA</div>
              </div>
              <div className="hero-stat">
                <div className="hero-stat-value">Real-time</div>
                <div className="hero-stat-label">Data streaming</div>
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
                <span className="hero-preview-title">PredictWise Analytics</span>
              </div>
              <div className="hero-preview-content">
                <div className="hero-preview-item">
                  <div className="hero-preview-item-left">
                    <span className="hero-preview-item-icon">⚽</span>
                    <div>
                      <div className="hero-preview-item-name">PSG vs Marseille</div>
                      <div className="hero-preview-item-sub">Ligue 1 • Live Analysis</div>
                    </div>
                  </div>
                  <div className="hero-preview-item-value positive">73%</div>
                </div>
                <div className="hero-preview-item">
                  <div className="hero-preview-item-left">
                    <span className="hero-preview-item-icon">��</span>
                    <div>
                      <div className="hero-preview-item-name">Apple (AAPL)</div>
                      <div className="hero-preview-item-sub">NASDAQ • Bullish Signal</div>
                    </div>
                  </div>
                  <div className="hero-preview-item-value positive">+2.4%</div>
                </div>
                <div className="hero-preview-item">
                  <div className="hero-preview-item-left">
                    <span className="hero-preview-item-icon">🏀</span>
                    <div>
                      <div className="hero-preview-item-name">Lakers vs Warriors</div>
                      <div className="hero-preview-item-sub">NBA • High Confidence</div>
                    </div>
                  </div>
                  <div className="hero-preview-item-value positive">68%</div>
                </div>
              </div>
            </div>

            <div className="hero-float-1">
              <div className="hero-float-badge">
                <span className="hero-float-badge-icon">⚡</span>
                <span>Live</span>
              </div>
            </div>

            <div className="hero-float-2">
              <div className="hero-float-badge">
                <span className="hero-float-badge-icon">🔒</span>
                <span>Encrypted</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section className="features">
        <div className="section-header">
          <span className="section-badge">Capacités</span>
          <h2 className="section-title">Une plateforme, deux marchés</h2>
          <p className="section-subtitle">
            Technologie propriétaire d'analyse prédictive multi-domaines
          </p>
        </div>

        <div className="features-grid">
          <div className="card feature-card">
            <div className="card-icon">⚽</div>
            <h3 className="card-title">Sports Analytics</h3>
            <p className="card-description">
              Modèles prédictifs basés sur 50+ variables : historique, forme, 
              compositions, conditions météo, facteur domicile.
            </p>
          </div>

          <div className="card feature-card">
            <div className="card-icon">📈</div>
            <h3 className="card-title">Market Intelligence</h3>
            <p className="card-description">
              Analyse technique et fondamentale combinées. RSI, MACD, 
              sentiment analysis et corrélations sectorielles.
            </p>
          </div>

          <div className="card feature-card">
            <div className="card-icon">🤖</div>
            <h3 className="card-title">Moteur GPT-4</h3>
            <p className="card-description">
              Analyses contextualisées en langage naturel. 
              Comprendre le "pourquoi" derrière chaque signal.
            </p>
          </div>

          <div className="card feature-card">
            <div className="card-icon">📊</div>
            <h3 className="card-title">Dashboards Pro</h3>
            <p className="card-description">
              Visualisations interactives, alertes personnalisées, 
              et exports de données pour vos propres analyses.
            </p>
          </div>

          <div className="card feature-card">
            <div className="card-icon">⚡</div>
            <h3 className="card-title">Real-time Data</h3>
            <p className="card-description">
              Flux de données en temps réel. Mises à jour instantanées 
              des signaux et indicateurs de confiance.
            </p>
          </div>

          <div className="card feature-card">
            <div className="card-icon">🔐</div>
            <h3 className="card-title">Enterprise Security</h3>
            <p className="card-description">
              Chiffrement AES-256, authentification multi-facteurs, 
              conformité RGPD et audits de sécurité réguliers.
            </p>
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="how-it-works">
        <div className="section-header">
          <span className="section-badge">Processus</span>
          <h2 className="section-title">De la donnée à la décision</h2>
          <p className="section-subtitle">
            Notre pipeline d'analyse en trois étapes
          </p>
        </div>

        <div className="steps-container">
          <div className="step-card">
            <div className="step-number">1</div>
            <h3 className="step-title">Collecte & Agrégation</h3>
            <p className="step-description">
              Sources de données multiples agrégées et normalisées en temps réel.
            </p>
          </div>

          <div className="step-card">
            <div className="step-number">2</div>
            <h3 className="step-title">Analyse IA</h3>
            <p className="step-description">
              Modèles ML + GPT-4 pour une analyse quantitative et qualitative.
            </p>
          </div>

          <div className="step-card">
            <div className="step-number">3</div>
            <h3 className="step-title">Insights Actionnables</h3>
            <p className="step-description">
              Signaux clairs avec niveaux de confiance et facteurs explicatifs.
            </p>
          </div>
        </div>
      </section>

      {/* USE CASES */}
      <section className="examples">
        <div className="section-header">
          <span className="section-badge">Use Cases</span>
          <h2 className="section-title">Analyses en temps réel</h2>
          <p className="section-subtitle">
            Exemples de signaux générés par notre plateforme
          </p>
        </div>

        <div className="examples-grid">
          <div className="card example-card">
            <div className="example-header">
              <span className="example-icon">⚽</span>
              <span className="example-category">Sports Signal</span>
            </div>
            <div className="example-body">
              <p className="example-question">
                PSG vs Marseille — Ligue 1
              </p>
              <div className="example-result">
                <div className="example-result-row">
                  <span className="example-result-label">Confidence Score</span>
                  <span className="example-result-value positive">73%</span>
                </div>
                <p className="example-reasoning">
                  Analyse multi-facteurs : 12 confrontations directes, forme sur 5 matchs, 
                  absences clés, coefficient domicile, conditions météo.
                </p>
              </div>
            </div>
          </div>

          <div className="card example-card">
            <div className="example-header">
              <span className="example-icon">📈</span>
              <span className="example-category">Market Signal</span>
            </div>
            <div className="example-body">
              <p className="example-question">
                Apple (AAPL) — NASDAQ
              </p>
              <div className="example-result">
                <div className="example-result-row">
                  <span className="example-result-label">Trend Signal</span>
                  <span className="example-result-value positive">Bullish +2.4%</span>
                </div>
                <p className="example-reasoning">
                  RSI oversold recovery, MACD crossover, earnings beat consensus +8%, 
                  institutional inflows detected, sector momentum positive.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="cta-section">
        <h2 className="cta-title">Prêt à prendre l'avantage ?</h2>
        <p className="cta-subtitle">
          Rejoignez les analystes qui utilisent l'IA pour optimiser leurs décisions.
        </p>
        <Link to="/signup" className="btn btn-primary btn-xl">
          Créer un compte →
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
            <span className="footer-link">API</span>
            <span className="footer-link">Contact</span>
          </nav>
          <p className="footer-legal">
            Les informations fournies par PredictWise sont à caractère informatif uniquement et ne constituent 
            ni un conseil en investissement, ni une incitation aux jeux d'argent. Les performances passées 
            ne garantissent pas les résultats futurs. Consultez un conseiller financier agréé avant toute décision.
          </p>
          <p className="footer-copyright">
            © 2024 PredictWise. Tous droits réservés.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
