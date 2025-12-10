import { useState } from 'react'
import financeService from '../services/financeService'
import './FinanceDashboard.css'

export default function FinanceDashboard() {
  const [ticker, setTicker] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [predictionData, setPredictionData] = useState(null)

  const handleAnalyze = async (e) => {
    e.preventDefault()
    
    if (!ticker.trim()) {
      setError('Veuillez saisir un symbole boursier')
      return
    }

    setLoading(true)
    setError(null)
    setPredictionData(null)

    try {
      const data = await financeService.getFinancePrediction(ticker.toUpperCase())
      setPredictionData(data)
    } catch (err) {
      console.error('Error analyzing stock:', err)
      setError(
        err.response?.data?.error || 
        err.message || 
        'Une erreur est survenue lors de l\'analyse du titre'
      )
    } finally {
      setLoading(false)
    }
  }

  const handleSelectPreset = (symbol) => {
    setTicker(symbol)
    setPredictionData(null)
    setError(null)
  }

  return (
    <div className="finance-dashboard">
      <header className="dashboard-header">
        <h1>Tableau de bord - Analyse financière</h1>
        <p className="disclaimer">
          Cette plateforme est un projet éducatif uniquement. Les analyses et prédictions 
          ne constituent pas des conseils financiers et ne doivent pas être utilisées pour 
          des décisions d'investissement réelles.
        </p>
      </header>

      <section className="analysis-input">
        <h2>Analyser un titre boursier</h2>
        
        <div className="preset-tickers">
          <p className="preset-label">Titres de démonstration :</p>
          <div className="preset-buttons">
            <button 
              type="button" 
              onClick={() => handleSelectPreset('AAPL')}
              className="preset-btn"
            >
              AAPL (Apple)
            </button>
            <button 
              type="button" 
              onClick={() => handleSelectPreset('TSLA')}
              className="preset-btn"
            >
              TSLA (Tesla)
            </button>
            <button 
              type="button" 
              onClick={() => handleSelectPreset('GOOGL')}
              className="preset-btn"
            >
              GOOGL (Google)
            </button>
            <button 
              type="button" 
              onClick={() => handleSelectPreset('MSFT')}
              className="preset-btn"
            >
              MSFT (Microsoft)
            </button>
          </div>
        </div>

        <form onSubmit={handleAnalyze} className="analysis-form">
          <div className="form-group">
            <label htmlFor="ticker">Symbole boursier (Ticker)</label>
            <input
              id="ticker"
              type="text"
              value={ticker}
              onChange={(e) => setTicker(e.target.value.toUpperCase())}
              placeholder="Ex: AAPL, TSLA, GOOGL..."
              className="form-input"
              disabled={loading}
            />
          </div>

          <button 
            type="submit" 
            className="analyze-btn"
            disabled={loading}
          >
            {loading ? 'Analyse en cours...' : 'Analyser ce titre'}
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

          {/* Stock Information */}
          {predictionData.asset && (
            <div className="result-card stock-info-card">
              <h3>Informations du titre</h3>
              <div className="stock-details">
                <div className="stock-header">
                  <div className="stock-name">
                    <span className="ticker-symbol">{predictionData.asset.ticker || ticker}</span>
                    {predictionData.asset.name && (
                      <span className="company-name">{predictionData.asset.name}</span>
                    )}
                  </div>
                  {predictionData.asset.current_price && (
                    <div className="current-price">
                      ${predictionData.asset.current_price.toFixed(2)}
                    </div>
                  )}
                </div>

                <div className="stock-metadata">
                  {predictionData.asset.sector && (
                    <p className="metadata-item">
                      <span className="label">Secteur :</span> {predictionData.asset.sector}
                    </p>
                  )}
                  {predictionData.asset.industry && (
                    <p className="metadata-item">
                      <span className="label">Industrie :</span> {predictionData.asset.industry}
                    </p>
                  )}
                  {predictionData.asset.market_cap && (
                    <p className="metadata-item">
                      <span className="label">Capitalisation :</span> ${(predictionData.asset.market_cap / 1e9).toFixed(2)}B
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Price History */}
          {predictionData.asset?.prices && Array.isArray(predictionData.asset.prices) && predictionData.asset.prices.length > 0 && (
            <div className="result-card price-history-card">
              <h3>Historique récent des prix</h3>
              <div className="price-bars">
                {predictionData.asset.prices.slice(-10).map((entry, index) => {
                  const maxPrice = Math.max(...predictionData.asset.prices.map(e => e.close || e.price || 0))
                  const price = entry.close || entry.price || 0
                  const widthPercent = maxPrice > 0 ? (price / maxPrice) * 100 : 0
                  
                  return (
                    <div key={index} className="price-bar-item">
                      <span className="price-date">{entry.date || `Jour ${index + 1}`}</span>
                      <div className="price-bar-container">
                        <div 
                          className="price-bar" 
                          style={{ width: `${widthPercent}%` }}
                        ></div>
                      </div>
                      <span className="price-value">${price.toFixed(2)}</span>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Technical Indicators */}
          {predictionData.asset?.indicators && Object.keys(predictionData.asset.indicators).length > 0 && (
            <div className="result-card indicators-card">
              <h3>Indicateurs techniques</h3>
              <div className="indicators-grid">
                {predictionData.asset.indicators.MA && (
                  <div className="indicator-item">
                    <span className="indicator-label">Moyenne mobile (MA)</span>
                    <span className="indicator-value">${predictionData.asset.indicators.MA.toFixed(2)}</span>
                  </div>
                )}
                {predictionData.asset.indicators.RSI !== undefined && (
                  <div className="indicator-item">
                    <span className="indicator-label">RSI</span>
                    <span className="indicator-value">{predictionData.asset.indicators.RSI.toFixed(2)}</span>
                  </div>
                )}
                {predictionData.asset.indicators.volatility !== undefined && (
                  <div className="indicator-item">
                    <span className="indicator-label">Volatilité</span>
                    <span className="indicator-value">{(predictionData.asset.indicators.volatility * 100).toFixed(2)}%</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ML Model Prediction */}
          {predictionData.model_score !== undefined && predictionData.model_score !== null && (
            <div className="result-card ml-score-card">
              <h3>Prédiction du modèle ML</h3>
              <div className="ml-score">
                <div className="score-bar-container">
                  <div 
                    className="score-bar" 
                    style={{ width: `${Math.abs(predictionData.model_score) * 100}%` }}
                  ></div>
                </div>
                <p className="score-value">
                  {predictionData.model_score > 0 ? '+' : ''}{(predictionData.model_score * 100).toFixed(1)}%
                </p>
                <p className="score-description">
                  Estimation de variation selon le modèle
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
                  {predictionData.gpt_analysis.prediction_value && (
                    <div className="prediction-details">
                      <span className="prediction-label">Tendance :</span>
                      <span className={`prediction-value trend-${String(predictionData.gpt_analysis.prediction_value).toLowerCase()}`}>
                        {predictionData.gpt_analysis.prediction_value}
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
                  <h4>Rappel éducatif</h4>
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
