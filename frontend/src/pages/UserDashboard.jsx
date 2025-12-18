/**
 * UserDashboard - Tableau de bord utilisateur avancé.
 * Affiche KPIs, graphiques et insights personnalisés.
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import dashboardService from '../services/dashboardService';
import AIChatButton from '../components/AIChatButton';
import './UserDashboard.css';

const UserDashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [period, setPeriod] = useState('30d');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
  }, [period]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [statsData, perfData] = await Promise.all([
        dashboardService.getStats(period),
        dashboardService.getPerformance()
      ]);
      
      setStats(statsData);
      setPerformance(perfData);
    } catch (err) {
      console.error('Erreur chargement dashboard:', err);
      setError('Impossible de charger les données');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="user-dashboard">
        <div className="dashboard-loading">
          <div className="spinner"></div>
          <p>Chargement de votre tableau de bord...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="user-dashboard">
        <div className="dashboard-error">
          <span className="error-icon">⚠️</span>
          <p>{error}</p>
          <button className="btn btn-primary" onClick={loadData}>Réessayer</button>
        </div>
      </div>
    );
  }

  return (
    <div className="user-dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-content">
          <div>
            <h1>Mon Tableau de Bord</h1>
            <p className="welcome-text">Bienvenue, <strong>{user?.username}</strong> 👋</p>
          </div>
          
          {/* Period Selector */}
          <div className="period-selector">
            {['7d', '30d', '90d', 'all'].map(p => (
              <button
                key={p}
                className={`period-btn ${period === p ? 'active' : ''}`}
                onClick={() => setPeriod(p)}
              >
                {p === '7d' ? '7 jours' : 
                 p === '30d' ? '30 jours' : 
                 p === '90d' ? '3 mois' : 'Tout'}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* KPI Cards */}
      <section className="kpi-grid">
        <div className="kpi-card primary">
          <div className="kpi-icon">📊</div>
          <div className="kpi-content">
            <div className="kpi-value">{stats?.summary?.total_predictions || 0}</div>
            <div className="kpi-label">Analyses totales</div>
          </div>
        </div>

        <div className="kpi-card success">
          <div className="kpi-icon">🎯</div>
          <div className="kpi-content">
            <div className="kpi-value">{stats?.summary?.avg_confidence || 0}%</div>
            <div className="kpi-label">Confiance moyenne</div>
          </div>
        </div>

        <div className="kpi-card info">
          <div className="kpi-icon">⚽</div>
          <div className="kpi-content">
            <div className="kpi-value">{stats?.summary?.sports_predictions || 0}</div>
            <div className="kpi-label">Analyses Sports</div>
          </div>
        </div>

        <div className="kpi-card warning">
          <div className="kpi-icon">📈</div>
          <div className="kpi-content">
            <div className="kpi-value">{stats?.summary?.finance_predictions || 0}</div>
            <div className="kpi-label">Analyses Finance</div>
          </div>
        </div>
      </section>

      {/* Insights */}
      {stats?.insights && stats.insights.length > 0 && (
        <section className="insights-section">
          <h2>💡 Insights</h2>
          <div className="insights-grid">
            {stats.insights.map((insight, idx) => (
              <div key={idx} className={`insight-card ${insight.type}`}>
                <span className="insight-icon">{insight.icon}</span>
                <p>{insight.message}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Breakdown & Activity */}
      <div className="dashboard-grid">
        {/* Répartition */}
        <section className="dashboard-card">
          <h2>📊 Répartition des Prédictions</h2>
          
          <div className="breakdown-section">
            <h3>Sports</h3>
            <div className="breakdown-bars">
              {stats?.breakdown?.sports && Object.entries(stats.breakdown.sports).map(([key, count]) => (
                <div key={key} className="breakdown-item">
                  <span className="breakdown-label">{key}</span>
                  <div className="breakdown-bar">
                    <div 
                      className="breakdown-fill sports"
                      style={{ 
                        width: `${(count / stats.summary.sports_predictions) * 100}%` 
                      }}
                    ></div>
                  </div>
                  <span className="breakdown-count">{count}</span>
                </div>
              ))}
              {(!stats?.breakdown?.sports || Object.keys(stats.breakdown.sports).length === 0) && (
                <p className="no-data">Aucune donnée sports</p>
              )}
            </div>
          </div>

          <div className="breakdown-section">
            <h3>Finance</h3>
            <div className="breakdown-bars">
              {stats?.breakdown?.finance && Object.entries(stats.breakdown.finance).map(([key, count]) => (
                <div key={key} className="breakdown-item">
                  <span className="breakdown-label">{key}</span>
                  <div className="breakdown-bar">
                    <div 
                      className="breakdown-fill finance"
                      style={{ 
                        width: `${(count / stats.summary.finance_predictions) * 100}%` 
                      }}
                    ></div>
                  </div>
                  <span className="breakdown-count">{count}</span>
                </div>
              ))}
              {(!stats?.breakdown?.finance || Object.keys(stats.breakdown.finance).length === 0) && (
                <p className="no-data">Aucune donnée finance</p>
              )}
            </div>
          </div>
        </section>

        {/* Top Tickers */}
        <section className="dashboard-card">
          <h2>🏆 Top Actifs Analysés</h2>
          <div className="top-tickers">
            {stats?.top_tickers?.length > 0 ? (
              stats.top_tickers.map((item, idx) => (
                <div key={item.ticker} className="ticker-item">
                  <span className="ticker-rank">#{idx + 1}</span>
                  <span className="ticker-symbol">{item.ticker}</span>
                  <span className="ticker-count">{item.count} analyses</span>
                </div>
              ))
            ) : (
              <p className="no-data">Analysez des actifs pour voir vos favoris ici</p>
            )}
          </div>
        </section>
      </div>

      {/* Quick Actions */}
      <section className="quick-actions">
        <h2>🚀 Actions Rapides</h2>
        <div className="actions-grid">
          <Link to="/sports" className="action-card">
            <span className="action-icon">⚽</span>
            <span className="action-label">Analyser un Match</span>
          </Link>
          <Link to="/finance" className="action-card">
            <span className="action-icon">📈</span>
            <span className="action-label">Analyser un Actif</span>
          </Link>
          <Link to="/history" className="action-card">
            <span className="action-icon">📜</span>
            <span className="action-label">Voir l'Historique</span>
          </Link>
          <Link to="/watchlist" className="action-card">
            <span className="action-icon">⭐</span>
            <span className="action-label">Ma Watchlist</span>
          </Link>
        </div>
      </section>

      {/* AI Assistant */}
      <AIChatButton 
        domain="general"
        context={{ 
          page: 'dashboard',
          stats: stats?.summary,
          user: user?.username 
        }}
      />
    </div>
  );
};

export default UserDashboard;
