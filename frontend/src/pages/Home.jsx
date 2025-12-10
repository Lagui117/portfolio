import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import './Home.css'

function Home() {
  const { isAuthenticated } = useAuth()

  return (
    <div className="home">
      <section className="hero">
        <h1>Bienvenue sur PredictWise</h1>
        <p className="hero-subtitle">
          Prédictions intelligentes pour le sport et la finance
        </p>
        <p className="hero-description">
          Utilisez le machine learning pour obtenir des insights sur vos équipes favorites
          et vos investissements financiers.
        </p>
        
        {!isAuthenticated && (
          <div className="hero-actions">
            <Link to="/signup" className="btn btn-primary btn-lg">
              Commencer gratuitement
            </Link>
            <Link to="/login" className="btn btn-secondary btn-lg">
              Se connecter
            </Link>
          </div>
        )}
      </section>

      <section className="features">
        <h2>Fonctionnalités</h2>
        <div className="features-grid">
          <div className="feature-card">
            <h3>📊 Module Sports</h3>
            <p>
              Accédez aux statistiques historiques, cotes et résultats.
              Obtenez des prédictions basées sur le machine learning.
            </p>
          </div>
          
          <div className="feature-card">
            <h3>💰 Module Finance</h3>
            <p>
              Données boursières en temps réel, indicateurs techniques (MA, RSI).
              Prédiction de tendances UP/DOWN.
            </p>
          </div>
          
          <div className="feature-card">
            <h3>🔐 Sécurisé</h3>
            <p>
              Authentification JWT, protection des données personnelles,
              historique de consultations.
            </p>
          </div>
        </div>
      </section>
    </div>
  )
}

export default Home
