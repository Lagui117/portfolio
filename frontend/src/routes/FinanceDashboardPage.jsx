/**
 * Dashboard d'analyse financiere.
 * Permet d'analyser un actif par son ticker.
 */

import React, { useState } from 'react';
import { getFinancePrediction } from '../services/financeService';
import '../styles/dashboard.css';

function FinanceDashboardPage() {
  const [ticker, setTicker] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAnalyze = async (e) => {
    e.preventDefault();
    
    if (!ticker.trim()) {
      setError('Veuillez entrer un symbole boursier.');
      return;
    }
    
    setError('');
    setPrediction(null);
    setLoading(true);
    
    try {
      const result = await getFinancePrediction(ticker.trim().toUpperCase());
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

  const renderTrendBadge = (trend) => {
    const trendClass = {
      'UP': 'trend-up',
      'DOWN': 'trend-down',
      'NEUTRAL': 'trend-neutral'
    }[trend] || 'trend-neutral';
    
    const trendLabel = {
      'UP': 'Haussier',
      'DOWN': 'Baissier',
      'NEUTRAL': 'Neutre'
    }[trend] || trend;
    
    return (
      <span className={`trend-badge ${trendClass}`}>
        {trendLabel}
      </span>
    );
  };

  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <h1>Analyse Financiere</h1>
        <p>Entrez un symbole boursier pour generer une analyse predictive.</p>
      </header>

      <section className="analysis-form-section">
        <form onSubmit={handleAnalyze} className="analysis-form">
          <div className="form-group">
            <label htmlFor="ticker">Symbole boursier (Ticker)</label>
            <input
              type="text"
              id="ticker"
              value={ticker}
              onChange={(e) => setTicker(e.target.value.toUpperCase())}
              placeholder="Ex: AAPL, GOOGL, MSFT..."
            />
            <small className="form-hint">
              Essayez AAPL (Apple), GOOGL (Google), MSFT (Microsoft), TSLA (Tesla)
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
          
          {/* Informations de l'actif */}
          <div className="result-card asset-info">
            <h3>Actif</h3>
            <div className="asset-header">
              <span className="ticker">{prediction.asset?.ticker}</span>
              <span className="name">{prediction.asset?.name}</span>
            </div>
            <div className="asset-details">
              <p><strong>Secteur:</strong> {prediction.asset?.sector || 'N/A'}</p>
              <p><strong>Industrie:</strong> {prediction.asset?.industry || 'N/A'}</p>
              <p>
                <strong>Prix actuel:</strong> {
                  prediction.asset?.current_price 
                    ? `$${prediction.asset.current_price.toFixed(2)}` 
                    : 'N/A'
                }
              </p>
            </div>
          </div>

          {/* Indicateurs techniques */}
          {prediction.asset?.indicators && (
            <div className="result-card indicators">
              <h3>Indicateurs techniques</h3>
              <div className="indicators-grid">
                <div className="indicator">
                  <span className="indicator-label">RSI</span>
                  <span className="indicator-value">
                    {prediction.asset.indicators.RSI?.toFixed(2) || 'N/A'}
                  </span>
                </div>
                <div className="indicator">
                  <span className="indicator-label">MA 5</span>
                  <span className="indicator-value">
                    {prediction.asset.indicators.MA_5?.toFixed(2) || 'N/A'}
                  </span>
                </div>
                <div className="indicator">
                  <span className="indicator-label">MA 20</span>
                  <span className="indicator-value">
                    {prediction.asset.indicators.MA_20?.toFixed(2) || 'N/A'}
                  </span>
                </div>
                <div className="indicator">
                  <span className="indicator-label">Volatilite</span>
                  <span className="indicator-value">
                    {prediction.asset.indicators.volatility_daily 
                      ? `${(prediction.asset.indicators.volatility_daily * 100).toFixed(2)}%`
                      : 'N/A'
                    }
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Score du modele */}
          <div className="result-card model-score">
            <h3>Score du modele ML</h3>
            <div className="score-display">
              <span className="score-value">
                {prediction.model_score !== null && prediction.model_score !== undefined
                  ? prediction.model_score.toFixed(3)
                  : 'N/A'
                }
              </span>
              <span className="score-label">
                {prediction.model_score > 0 ? 'Signal haussier' : 
                 prediction.model_score < 0 ? 'Signal baissier' : 'Signal neutre'}
              </span>
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
                <h4>Prediction de tendance</h4>
                <p>
                  <strong>Type:</strong> {prediction.gpt_analysis.prediction_type}
                </p>
                <p>
                  <strong>Tendance:</strong> {renderTrendBadge(prediction.gpt_analysis.prediction_value)}
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

              {prediction.gpt_analysis.disclaimer && (
                <div className="analysis-reminder">
                  <h4>Avertissement</h4>
                  <p>{prediction.gpt_analysis.disclaimer}</p>
                </div>
              )}
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

export default FinanceDashboardPage;
