import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import '../styles/landing.css';

const LandingPage = () => {
  return (
    <>
      <Navbar />
      <div className="landing-page">
        {/* Hero Section */}
        <section className="landing-hero">
          <span className="hero-badge">
            ✨ Plateforme IA Éducative
          </span>
          
          <h1 className="hero-title">
            Prédictions intelligentes<br />
            <span className="gradient-text">Sports & Finance</span>
          </h1>
          
          <p className="hero-subtitle">
            Découvrez comment l'intelligence artificielle analyse les données 
            pour générer des prédictions éducatives. Apprenez, explorez, comprenez.
          </p>
          
          <div className="hero-cta">
            <Link to="/signup" className="btn btn-primary btn-xl">
              Commencer gratuitement
            </Link>
            <Link to="/login" className="btn btn-secondary btn-xl">
              Se connecter
            </Link>
          </div>
          
          <div className="hero-stats">
            <div className="hero-stat">
              <div className="hero-stat-value">2</div>
              <div className="hero-stat-label">Domaines d'analyse</div>
            </div>
            <div className="hero-stat">
              <div className="hero-stat-value">IA</div>
              <div className="hero-stat-label">Powered by GPT</div>
            </div>
            <div className="hero-stat">
              <div className="hero-stat-value">100%</div>
              <div className="hero-stat-label">Éducatif</div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="landing-features">
          <div className="section-header">
            <span className="section-badge">Fonctionnalités</span>
            <h2 className="section-title">
              Une plateforme complète pour apprendre
            </h2>
            <p className="section-description">
              Explorez deux univers d'analyse avec notre intelligence artificielle
            </p>
          </div>
          
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">⚽</div>
              <h3 className="feature-title">Analyse Sportive</h3>
              <p className="feature-description">
                Découvrez comment l'IA analyse les performances des équipes, 
                les historiques de matchs et les statistiques pour générer 
                des analyses détaillées.
              </p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">📈</div>
              <h3 className="feature-title">Analyse Financière</h3>
              <p className="feature-description">
                Comprenez les mécanismes d'analyse des tendances boursières, 
                des indicateurs économiques et des données de marché.
              </p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">🤖</div>
              <h3 className="feature-title">Intelligence Artificielle</h3>
              <p className="feature-description">
                Notre moteur GPT analyse les données en temps réel et génère 
                des explications pédagogiques claires et détaillées.
              </p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3 className="feature-title">Visualisations</h3>
              <p className="feature-description">
                Des graphiques et tableaux de bord interactifs pour mieux 
                comprendre les analyses et les tendances identifiées.
              </p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">🎓</div>
              <h3 className="feature-title">Approche Éducative</h3>
              <p className="feature-description">
                Chaque prédiction est accompagnée d'explications sur la 
                méthodologie utilisée et les facteurs pris en compte.
              </p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">🔒</div>
              <h3 className="feature-title">Sécurisé</h3>
              <p className="feature-description">
                Vos données sont protégées. Authentification sécurisée et 
                respect de votre vie privée.
              </p>
            </div>
          </div>
        </section>

        {/* How it Works */}
        <section className="landing-how-it-works">
          <div className="section-header">
            <span className="section-badge">Comment ça marche</span>
            <h2 className="section-title">
              Simple et intuitif
            </h2>
            <p className="section-description">
              Trois étapes pour explorer le monde des prédictions IA
            </p>
          </div>
          
          <div className="steps-container">
            <div className="step-card">
              <div className="step-number">1</div>
              <h3 className="step-title">Créez votre compte</h3>
              <p className="step-description">
                Inscription gratuite en quelques secondes. 
                Accédez immédiatement à la plateforme.
              </p>
            </div>
            
            <div className="step-card">
              <div className="step-number">2</div>
              <h3 className="step-title">Choisissez un domaine</h3>
              <p className="step-description">
                Sports ou Finance ? Sélectionnez le domaine 
                qui vous intéresse pour explorer.
              </p>
            </div>
            
            <div className="step-card">
              <div className="step-number">3</div>
              <h3 className="step-title">Explorez les analyses</h3>
              <p className="step-description">
                Posez vos questions et découvrez comment 
                l'IA génère ses prédictions éducatives.
              </p>
            </div>
          </div>
        </section>

        {/* Examples Section */}
        <section className="landing-examples">
          <div className="section-header">
            <span className="section-badge">Exemples</span>
            <h2 className="section-title">
              Voyez l'IA en action
            </h2>
            <p className="section-description">
              Quelques exemples d'analyses générées par notre plateforme
            </p>
          </div>
          
          <div className="examples-grid">
            <div className="example-card">
              <div className="example-header">
                <span className="example-icon">⚽</span>
                <span className="example-category">Analyse Sportive</span>
              </div>
              <div className="example-body">
                <p className="example-question">
                  "Analyse du match PSG vs Marseille"
                </p>
                <div className="example-answer">
                  <div className="example-prediction">
                    <span className="prediction-label">Confiance analyse</span>
                    <span className="prediction-value">73%</span>
                  </div>
                  <p className="example-reasoning">
                    L'IA a analysé 50 matchs historiques, les performances 
                    récentes et les statistiques des joueurs clés pour 
                    générer cette analyse éducative.
                  </p>
                </div>
              </div>
            </div>
            
            <div className="example-card">
              <div className="example-header">
                <span className="example-icon">📈</span>
                <span className="example-category">Analyse Financière</span>
              </div>
              <div className="example-body">
                <p className="example-question">
                  "Tendance de l'action Apple (AAPL)"
                </p>
                <div className="example-answer">
                  <div className="example-prediction">
                    <span className="prediction-label">Tendance identifiée</span>
                    <span className="prediction-value">+2.3%</span>
                  </div>
                  <p className="example-reasoning">
                    Analyse basée sur les indicateurs techniques, les 
                    résultats trimestriels et le sentiment du marché 
                    pour comprendre les facteurs d'influence.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Disclaimer */}
        <section className="landing-disclaimer">
          <div className="disclaimer-content">
            <div className="disclaimer-icon">⚠️</div>
            <h3 className="disclaimer-title">
              Important : Projet Éducatif
            </h3>
            <p className="disclaimer-text">
              PredictWise est une plateforme <strong>purement éducative</strong> conçue 
              pour démontrer les capacités de l'intelligence artificielle. Les prédictions 
              générées ne constituent <strong>en aucun cas</strong> des conseils 
              d'investissement ou des paris. Ne prenez jamais de décisions financières 
              basées sur ces analyses. Ce projet est destiné à l'apprentissage et 
              la démonstration technologique uniquement.
            </p>
          </div>
        </section>

        {/* CTA Section */}
        <section className="landing-cta">
          <h2 className="cta-title">
            Prêt à explorer ?
          </h2>
          <p className="cta-description">
            Rejoignez PredictWise et découvrez le potentiel de l'IA 
            dans l'analyse de données.
          </p>
          <div className="hero-cta">
            <Link to="/signup" className="btn btn-primary btn-xl">
              Créer un compte gratuit
            </Link>
          </div>
        </section>

        {/* Footer */}
        <footer className="landing-footer">
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
              © 2024 PredictWise. Projet éducatif - Aucune valeur financière.
            </p>
          </div>
        </footer>
      </div>
    </>
  );
};

export default LandingPage;
