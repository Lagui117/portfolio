/**
 * History - Page d'historique des prédictions.
 * Filtres avancés et analyse des performances.
 */

import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import dashboardService from '../services/dashboardService';
import './History.css';

const History = () => {
  const { user } = useAuth();
  const [predictions, setPredictions] = useState([]);
  const [pagination, setPagination] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Filtres
  const [filters, setFilters] = useState({
    type: 'all',
    sort: 'date',
    order: 'desc',
    ticker: '',
    page: 1,
    per_page: 20
  });

  useEffect(() => {
    loadHistory();
  }, [filters]);

  const loadHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await dashboardService.getHistory(filters);
      setPredictions(data.predictions || []);
      setPagination(data.pagination || {});
    } catch (err) {
      console.error('Erreur chargement historique:', err);
      setError('Impossible de charger l\'historique');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
      page: key !== 'page' ? 1 : value // Reset page on filter change
    }));
  };

  const getConfidenceColor = (level) => {
    switch (level) {
      case 'high': return 'confidence-high';
      case 'medium': return 'confidence-medium';
      case 'low': return 'confidence-low';
      default: return '';
    }
  };

  const getPredictionIcon = (type) => {
    return type === 'sports' ? '⚽' : '📈';
  };

  return (
    <div className="history-page">
      {/* Header */}
      <header className="history-header">
        <div>
          <h1>📜 Historique des Analyses</h1>
          <p>Retrouvez toutes vos prédictions passées</p>
        </div>
      </header>

      {/* Filters */}
      <section className="filters-section">
        <div className="filters-grid">
          <div className="filter-group">
            <label>Type</label>
            <select 
              value={filters.type}
              onChange={(e) => handleFilterChange('type', e.target.value)}
            >
              <option value="all">Tous</option>
              <option value="sports">Sports</option>
              <option value="finance">Finance</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Trier par</label>
            <select 
              value={filters.sort}
              onChange={(e) => handleFilterChange('sort', e.target.value)}
            >
              <option value="date">Date</option>
              <option value="confidence">Confiance</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Ordre</label>
            <select 
              value={filters.order}
              onChange={(e) => handleFilterChange('order', e.target.value)}
            >
              <option value="desc">Plus récent</option>
              <option value="asc">Plus ancien</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Symbole/Ticker</label>
            <input 
              type="text"
              placeholder="Ex: AAPL, BTC..."
              value={filters.ticker}
              onChange={(e) => handleFilterChange('ticker', e.target.value)}
            />
          </div>
        </div>
      </section>

      {/* Stats Summary */}
      <section className="history-summary">
        <div className="summary-stat">
          <span className="summary-value">{pagination.total || 0}</span>
          <span className="summary-label">Total analyses</span>
        </div>
        <div className="summary-stat">
          <span className="summary-value">{pagination.pages || 0}</span>
          <span className="summary-label">Pages</span>
        </div>
      </section>

      {/* Results */}
      {loading ? (
        <div className="history-loading">
          <div className="spinner"></div>
          <p>Chargement...</p>
        </div>
      ) : error ? (
        <div className="history-error">
          <span>⚠️</span>
          <p>{error}</p>
          <button className="btn btn-primary" onClick={loadHistory}>Réessayer</button>
        </div>
      ) : predictions.length === 0 ? (
        <div className="history-empty">
          <span className="empty-icon">📭</span>
          <h3>Aucune analyse trouvée</h3>
          <p>Commencez par analyser un match ou un actif !</p>
        </div>
      ) : (
        <>
          <section className="predictions-list">
            {predictions.map(pred => (
              <div key={pred.id} className="prediction-card">
                <div className="prediction-header">
                  <span className="prediction-type">
                    {getPredictionIcon(pred.prediction_type)}
                    {pred.prediction_type === 'sports' ? 'Sports' : 'Finance'}
                  </span>
                  <span className="prediction-date">{pred.age || 'N/A'}</span>
                </div>
                
                <div className="prediction-body">
                  <div className="prediction-target">
                    {pred.ticker || pred.external_match_id || 'N/A'}
                  </div>
                  
                  <div className="prediction-result">
                    <span className="result-label">Prédiction:</span>
                    <span className="result-value">{pred.prediction_value || 'N/A'}</span>
                  </div>
                  
                  <div className={`prediction-confidence ${getConfidenceColor(pred.confidence_level)}`}>
                    <span className="confidence-label">Confiance:</span>
                    <span className="confidence-value">
                      {pred.confidence ? `${Math.round(pred.confidence * 100)}%` : 'N/A'}
                    </span>
                  </div>
                </div>

                {pred.gpt_analysis && (
                  <div className="prediction-analysis">
                    <details>
                      <summary>Voir l'analyse IA</summary>
                      <p>{typeof pred.gpt_analysis === 'string' 
                        ? pred.gpt_analysis 
                        : pred.gpt_analysis.summary || JSON.stringify(pred.gpt_analysis)}</p>
                    </details>
                  </div>
                )}
              </div>
            ))}
          </section>

          {/* Pagination */}
          {pagination.pages > 1 && (
            <section className="pagination">
              <button 
                className="pagination-btn"
                disabled={!pagination.has_prev}
                onClick={() => handleFilterChange('page', pagination.page - 1)}
              >
                ← Précédent
              </button>
              
              <span className="pagination-info">
                Page {pagination.page} sur {pagination.pages}
              </span>
              
              <button 
                className="pagination-btn"
                disabled={!pagination.has_next}
                onClick={() => handleFilterChange('page', pagination.page + 1)}
              >
                Suivant →
              </button>
            </section>
          )}
        </>
      )}
    </div>
  );
};

export default History;
