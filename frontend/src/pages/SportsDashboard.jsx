import { useState } from 'react'
import sportsService from '../services/sportsService'
import './SportsDashboard.css'

export default function SportsDashboard() {
  const [matchId, setMatchId] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [predictionData, setPredictionData] = useState(null)

  const handleAnalyze = async (e) => {
    e.preventDefault()
    
    if (!matchId.trim()) {
      setError('Veuillez saisir un identifiant de match')
      return
    }

    setLoading(true)
    setError(null)
    setPredictionData(null)

    try {
      const data = await sportsService.getSportsPrediction(matchId)
      setPredictionData(data)
    } catch (err) {
      console.error('Error analyzing match:', err)
      setError(
        err.response?.data?.error || 
        err.message || 
        'Une erreur est survenue lors de l\'analyse du match'
      )
    } finally {
      setLoading(false)
    }
  }

  const handleSelectPreset = (id) => {
    setMatchId(id)
    setPredictionData(null)
    setError(null)
  }

  return (
    <div className="sports-dashboard">
      <header className="dashboard-header">
        <h1>Sports Analytics</h1>
        <p className="disclaimer">
          Analyse sportive propulsée par l'IA
        </p>
      </header>

      <section className="analysis-input">
        <h2>Analyser un match</h2>
        
        <div className="preset-matches">
          <p className="preset-label">Matchs populaires :</p>
          <div className="preset-buttons">
            <button 
              type="button" 
              onClick={() => handleSelectPreset('1')}
              className="preset-btn"
            >
              Match #1
            </button>
            <button 
              type="button" 
              onClick={() => handleSelectPreset('2')}
              className="preset-btn"
            >
              Match #2
            </button>
            <button 
              type="button" 
              onClick={() => handleSelectPreset('3')}
              className="preset-btn"
            >
              Match #3
            </button>
          </div>
        </div>

        <form onSubmit={handleAnalyze} className="analysis-form">
          <div className="form-group">
            <label htmlFor="matchId">Identifiant du match</label>
            <input
              id="matchId"
              type="text"
              value={matchId}
              onChange={(e) => setMatchId(e.target.value)}
              placeholder="Ex: 1, 2, 3..."
              className="form-input"
              disabled={loading}
            />
          </div>

          <button 
            type="submit" 
            className="analyze-btn"
            disabled={loading}
          >
            {loading ? 'Analyse en cours...' : 'Analyser ce match'}
          </button>
        </form>
      </section>

      {error && (
        <section className="error-section">
          <div className="error-card">
            <h3>Erreur</h3>
            <p>{error}</p>
          </div>
        </section>
      )}

      {loading && (
        <section className="loading-section">
          <div className="loading-spinner"></div>
          <p>Analyse en cours, veuillez patienter...</p>
        </section>
      )}

      {predictionData && !loading && (
        <section className="results-section">
          <h2>Résultats de l'analyse</h2>

          {/* Match Information */}
          {predictionData.match && (
            <div className="result-card match-info-card">
              <h3>Informations du match</h3>
              <div className="match-details">
                <div className="teams">
                  <span className="team-name">{predictionData.match.home_team || 'Équipe A'}</span>
                  <span className="vs">vs</span>
                  <span className="team-name">{predictionData.match.away_team || 'Équipe B'}</span>
                </div>
                {predictionData.match.date && (
                  <p className="match-date">Date : {predictionData.match.date}</p>
                )}
                {predictionData.match.competition && (
                  <p className="match-competition">Compétition : {predictionData.match.competition}</p>
                )}
              </div>
            </div>
          )}

          {/* ML Model Score */}
          {predictionData.model_score !== undefined && predictionData.model_score !== null && (
            <div className="result-card ml-score-card">
              <h3>Score du modèle ML</h3>
              <div className="ml-score">
                <div className="score-bar-container">
                  <div 
                    className="score-bar" 
                    style={{ width: `${predictionData.model_score * 100}%` }}
                  ></div>
                </div>
                <p className="score-value">{(predictionData.model_score * 100).toFixed(1)}%</p>
                <p className="score-description">
                  Probabilité de victoire de l'équipe à domicile selon le modèle
                </p>
              </div>
            </div>
          )}

          {/* GPT Analysis */}
          {predictionData.gpt_analysis && (
            <div className="result-card analysis-card">
              <h3>Analyse IA</h3>
              
              {predictionData.gpt_analysis.summary && (
                <div className="analysis-section">
                  <h4>Résumé</h4>
                  <p>{predictionData.gpt_analysis.summary}</p>
                </div>
              )}

              {predictionData.gpt_analysis.analysis && (
                <div className="analysis-section">
                  <h4>Analyse détaillée</h4>
                  <p>{predictionData.gpt_analysis.analysis}</p>
                </div>
              )}

              {predictionData.gpt_analysis.prediction_type && (
                <div className="analysis-section prediction-section">
                  <h4>Prédiction</h4>
                  <div className="prediction-details">
                    <span className="prediction-label">Type :</span>
                    <span className="prediction-value">{predictionData.gpt_analysis.prediction_type}</span>
                  </div>
                  {predictionData.gpt_analysis.prediction_value !== undefined && (
                    <div className="prediction-details">
                      <span className="prediction-label">Valeur :</span>
                      <span className="prediction-value">
                        {typeof predictionData.gpt_analysis.prediction_value === 'number' 
                          ? `${(predictionData.gpt_analysis.prediction_value * 100).toFixed(1)}%`
                          : predictionData.gpt_analysis.prediction_value}
                      </span>
                    </div>
                  )}
                </div>
              )}

              {predictionData.gpt_analysis.confidence !== undefined && (
                <div className="analysis-section confidence-section">
                  <h4>Niveau de confiance</h4>
                  <div className="confidence-bar-container">
                    <div 
                      className="confidence-bar" 
                      style={{ width: `${predictionData.gpt_analysis.confidence * 100}%` }}
                    ></div>
                  </div>
                  <p className="confidence-value">
                    {(predictionData.gpt_analysis.confidence * 100).toFixed(0)}%
                  </p>
                </div>
              )}

              {predictionData.gpt_analysis.caveats && (
                <div className="analysis-section caveats-section">
                  <h4>Avertissements</h4>
                  <p>{predictionData.gpt_analysis.caveats}</p>
                </div>
              )}

              {predictionData.gpt_analysis.educational_reminder && (
                <div className="analysis-section educational-section">
                  <h4>Avertissement</h4>
                  <p className="educational-text">{predictionData.gpt_analysis.educational_reminder}</p>
                </div>
              )}
            </div>
          )}
        </section>
      )}
    </div>
  )
}
