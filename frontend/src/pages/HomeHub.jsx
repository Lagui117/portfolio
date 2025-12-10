import { useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth'
import { getDailySuggestion, getUserStats } from '../services/aiService'
import './HomeHub.css'

export default function HomeHub() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [aiInsight, setAiInsight] = useState({
    title: 'Suggestion IA du jour',
    text: 'Chargement...'
  })
  const [userStats, setUserStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      try {
        const [suggestion, stats] = await Promise.all([
          getDailySuggestion(),
          user ? getUserStats() : Promise.resolve(null)
        ])
        setAiInsight(suggestion)
        if (stats) {
          setUserStats(stats)
        }
      } catch (error) {
        console.error('Erreur lors du chargement des données:', error)
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [user])

  return (
    <div className="hub-layout">
      <header className="hub-header">
        <h1>PredictWise</h1>
        <p className="hub-subtitle">
          Plateforme éducative d'analyse sportive et financière assistée par IA.
        </p>
        {user && (
          <p className="hub-welcome">
            Bienvenue, <strong>{user.username}</strong> !
          </p>
        )}
        <p className="hub-disclaimer">
          Les prédictions et analyses sont expérimentales et ne doivent pas être utilisées
          pour des décisions de pari ou d'investissement réelles.
        </p>
      </header>

      <main className="hub-main">
        <section className="hub-choices">
          <div
            className="hub-card hub-card-sports"
            onClick={() => navigate('/sports')}
          >
            <div className="hub-card-icon">⚽</div>
            <h2>Analyse Sportive</h2>
            <p className="hub-card-subtitle">
              Statistiques de match, forme des équipes et analyse IA.
            </p>
            <ul>
              <li>Vue d'ensemble des matchs récents</li>
              <li>Statistiques d'équipes et tendances</li>
              <li>Analyse textuelle générée par IA</li>
              <li>Prédictions ML combinées à GPT</li>
            </ul>
            <button type="button">Accéder à la partie Sports</button>
          </div>

          <div
            className="hub-card hub-card-finance"
            onClick={() => navigate('/finance')}
          >
            <div className="hub-card-icon">📈</div>
            <h2>Analyse Financière</h2>
            <p className="hub-card-subtitle">
              Historique de prix, indicateurs et estimation de tendance.
            </p>
            <ul>
              <li>Graphiques de prix et indicateurs simples</li>
              <li>Tendance estimée (hausse/baisse)</li>
              <li>Analyse IA pédagogique sur le contexte</li>
              <li>Indicateurs techniques (MA, RSI, volatilité)</li>
            </ul>
            <button type="button">Accéder à la partie Bourse</button>
          </div>
        </section>

        <section className="hub-ai-highlight">
          <div className="hub-ai-icon">🤖</div>
          <h3>{aiInsight.title}</h3>
          <p>{loading ? 'Chargement de la suggestion IA...' : aiInsight.text}</p>
          <div className="hub-ai-badge">Propulsé par GPT-4</div>
        </section>

        {userStats && (
          <section className="hub-user-stats">
            <h3>Vos statistiques</h3>
            <div className="stats-grid">
              <div className="stat-card">
                <span className="stat-value">{userStats.total_predictions || 0}</span>
                <span className="stat-label">Prédictions totales</span>
              </div>
              <div className="stat-card">
                <span className="stat-value">{userStats.sports_predictions || 0}</span>
                <span className="stat-label">Analyses sportives</span>
              </div>
              <div className="stat-card">
                <span className="stat-value">{userStats.finance_predictions || 0}</span>
                <span className="stat-label">Analyses financières</span>
              </div>
              <div className="stat-card">
                <span className="stat-value">{userStats.total_consultations || 0}</span>
                <span className="stat-label">Consultations</span>
              </div>
            </div>
          </section>
        )}
      </main>

      <footer className="hub-footer">
        <p>
          PredictWise - Plateforme éducative | 
          <a href="/docs" className="hub-link"> Documentation</a> | 
          <a href="/about" className="hub-link"> À propos</a>
        </p>
      </footer>
    </div>
  )
}
