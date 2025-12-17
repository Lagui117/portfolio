/**
 * Dashboard d'analyse sportive.
 * Permet d'analyser un match par son ID.
 */

import React, { useState } from 'react';
import { getSportsPrediction } from '../services/sportsService';
import '../styles/dashboard.css';

function SportsDashboardPage() {
  const [matchId, setMatchId] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAnalyze = async (e) => {
    e.preventDefault();
    
    if (!matchId.trim()) {
      setError('Veuillez entrer un identifiant de match.');
      return;
    }
    
    setError('');
    setPrediction(null);
    setLoading(true);
    
    try {
      const result = await getSportsPrediction(matchId.trim());
      setPrediction(result);
    } catch (err) {
      const message = err.response?.data?.error || 'Erreur lors de l\'analyse.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const renderConfidenceBar = (confidence) => {
    const percentage = Math.round((confidence || 0) * 100);
    return (
      <div className="confidence-bar">
        <div 
          className="confidence-fill" 
          style={{ width: `${percentage}%` }}
        />
        <span className="confidence-label">{percentage}%</span>
      </div>
    );
  };

  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <h1>Analyse Sportive</h1>
        <p>Entrez l'identifiant d'un match pour generer une analyse predictive.</p>
      </header>

      <section className="analysis-form-section">
        <form onSubmit={handleAnalyze} className="analysis-form">
          <div className="form-group">
            <label htmlFor="matchId">Identifiant du match</label>
            <input
              type="text"
              id="matchId"
              value={matchId}
              onChange={(e) => setMatchId(e.target.value)}
              placeholder="Ex: 1, 2, 3..."
            />
            <small className="form-hint">
              Essayez les IDs 1, 2 ou 3 pour des matchs de demonstration.
            </small>
          </div>
          
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Analyse en cours...' : 'Analyser'}
          </button>
        </form>
      </section>

      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}

      {loading && (
        <div className="loading-section">
          <div className="spinner"></div>
          <p>Generation de l'analyse en cours...</p>
        </div>
      )}

      {prediction && (
        <section className="prediction-results">
          <h2>Resultats de l'analyse</h2>
          
          {/* Informations du match */}
          <div className="result-card match-info">
            <h3>Match</h3>
            <div className="match-teams">
              <span className="team home">{prediction.match?.home_team}</span>
              <span className="vs">VS</span>
              <span className="team away">{prediction.match?.away_team}</span>
            </div>
            <div className="match-details">
              <p><strong>Competition:</strong> {prediction.match?.competition}</p>
              <p><strong>Date:</strong> {prediction.match?.date ? new Date(prediction.match.date).toLocaleDateString('fr-FR') : 'N/A'}</p>
            </div>
          </div>

          {/* Score du modele */}
          <div className="result-card model-score">
            <h3>Score du modele ML</h3>
            <div className="score-display">
              <span className="score-value">
                {prediction.model_score ? `${(prediction.model_score * 100).toFixed(1)}%` : 'N/A'}
              </span>
              <span className="score-label">probabilite victoire domicile</span>
            </div>
          </div>

          {/* Analyse GPT */}
          {prediction.gpt_analysis && (
            <div className="result-card gpt-analysis">
              <h3>Analyse IA</h3>
              
              <div className="analysis-summary">
                <h4>Resume</h4>
                <p>{prediction.gpt_analysis.summary}</p>
              </div>

              <div className="analysis-details">
                <h4>Analyse detaillee</h4>
                <p>{prediction.gpt_analysis.analysis}</p>
              </div>

              <div className="analysis-prediction">
                <h4>Prediction</h4>
                <p>
                  <strong>Type:</strong> {prediction.gpt_analysis.prediction_type}
                </p>
                <p>
                  <strong>Valeur:</strong> {
                    typeof prediction.gpt_analysis.prediction_value === 'number' 
                      ? `${(prediction.gpt_analysis.prediction_value * 100).toFixed(1)}%`
                      : prediction.gpt_analysis.prediction_value
                  }
                </p>
                <p>
                  <strong>Confiance:</strong>
                </p>
                {renderConfidenceBar(prediction.gpt_analysis.confidence)}
              </div>

              <div className="analysis-caveats">
                <h4>Limitations</h4>
                <p>{prediction.gpt_analysis.caveats}</p>
              </div>

              <div className="analysis-reminder">
                <h4>Rappel educatif</h4>
                <p>{prediction.gpt_analysis.educational_reminder}</p>
              </div>
            </div>
          )}

          {/* Disclaimer */}
          <div className="disclaimer-box">
            <p>{prediction.disclaimer}</p>
          </div>
        </section>
      )}
    </div>
  );
}

export default SportsDashboardPage;
