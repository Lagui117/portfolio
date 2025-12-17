/**
 * DashboardPremium - Dashboard ultra-moderne avec sidebar + topbar + sections
 * Vue d'ensemble des analyses sportives et financières avec IA
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMe } from '../services/authService';
import './DashboardPremium.css';

function DashboardPremium() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  useEffect(() => {
    loadUserData();
  }, []);

  const loadUserData = async () => {
    try {
      const userData = await getMe();
      setUser(userData);
    } catch (error) {
      console.error('Erreur chargement utilisateur:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="pw-premium-layout">
        <div className="pw-loading">
          <div className="pw-spinner"></div>
          <span>Chargement du dashboard...</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`pw-premium-layout ${sidebarCollapsed ? 'collapsed' : ''}`}>
      {/* ========== SIDEBAR ========== */}
      <aside className="pw-sidebar">
        <div className="pw-logo">
          <span className="pw-logo-icon">⚡</span>
          {!sidebarCollapsed && <span className="pw-logo-text">PredictWise</span>}
        </div>
        
        <nav className="pw-nav">
          <button className="pw-nav-item active" onClick={() => navigate('/app/premium')}>
            <span className="pw-nav-icon">🏠</span>
            {!sidebarCollapsed && <span>Accueil</span>}
          </button>
          <button className="pw-nav-item" onClick={() => navigate('/app/sports')}>
            <span className="pw-nav-icon">⚽</span>
            {!sidebarCollapsed && <span>Sports</span>}
          </button>
          <button className="pw-nav-item" onClick={() => navigate('/app/finance')}>
            <span className="pw-nav-icon">📈</span>
            {!sidebarCollapsed && <span>Finance</span>}
          </button>
          <button className="pw-nav-item">
            <span className="pw-nav-icon">📊</span>
            {!sidebarCollapsed && <span>Historique</span>}
          </button>
          <button className="pw-nav-item">
            <span className="pw-nav-icon">⚙️</span>
            {!sidebarCollapsed && <span>Paramètres</span>}
          </button>
          <button className="pw-nav-item">
            <span className="pw-nav-icon">💬</span>
            {!sidebarCollapsed && <span>Support</span>}
          </button>
        </nav>
        
        <div className="pw-sidebar-footer">
          <button className="pw-sidebar-toggle" onClick={() => setSidebarCollapsed(!sidebarCollapsed)}>
            {sidebarCollapsed ? '→' : '←'}
          </button>
          {!sidebarCollapsed && (
            <div className="pw-mode-badge">Mode éducatif</div>
          )}
        </div>
      </aside>

      {/* ========== MAIN CONTENT ========== */}
      <div className="pw-main">
        {/* ========== TOPBAR ========== */}
        <header className="pw-topbar">
          <div className="pw-topbar-left">
            <h1>Dashboard Premium</h1>
            <p>Vue d'ensemble de vos analyses sportives et financières.</p>
          </div>
          <div className="pw-topbar-right">
            <div className="pw-search-wrapper">
              <input
                className="pw-search"
                placeholder="Rechercher (Ctrl + K)"
                type="text"
              />
              <span className="pw-search-icon">🔍</span>
            </div>
            <button className="pw-notif" title="Notifications">
              <span>🔔</span>
              <span className="pw-notif-badge">3</span>
            </button>
            <div className="pw-user-menu">
              <div className="pw-avatar">{user?.username?.charAt(0).toUpperCase() || 'U'}</div>
              <div className="pw-user-info">
                <span className="pw-username">{user?.username || 'Utilisateur'}</span>
                <span className="pw-user-role">Premium</span>
              </div>
              <div className="pw-dropdown">
                <button onClick={() => navigate('/app/settings')}>Profil</button>
                <button onClick={handleLogout}>Déconnexion</button>
              </div>
            </div>
          </div>
        </header>

        {/* ========== GRID PRINCIPALE ========== */}
        <div className="pw-grid">
          {/* ========== OVERVIEW SECTION ========== */}
          <section className="pw-card pw-overview">
            <h2>Vue d'ensemble</h2>
            <div className="pw-stats-grid">
              <div className="pw-stat-card">
                <div className="pw-stat-icon">📊</div>
                <div className="pw-stat-content">
                  <span className="pw-stat-label">Analyses totales</span>
                  <strong className="pw-stat-value">324</strong>
                  <span className="pw-stat-change up">+12% ce mois</span>
                </div>
              </div>
              <div className="pw-stat-card">
                <div className="pw-stat-icon">⚽</div>
                <div className="pw-stat-content">
                  <span className="pw-stat-label">Prédictions sport</span>
                  <strong className="pw-stat-value">182</strong>
                  <span className="pw-stat-change up">+8% cette semaine</span>
                </div>
              </div>
              <div className="pw-stat-card">
                <div className="pw-stat-icon">📈</div>
                <div className="pw-stat-content">
                  <span className="pw-stat-label">Prédictions finance</span>
                  <strong className="pw-stat-value">142</strong>
                  <span className="pw-stat-change neutral">Stable</span>
                </div>
              </div>
              <div className="pw-stat-card">
                <div className="pw-stat-icon">🎯</div>
                <div className="pw-stat-content">
                  <span className="pw-stat-label">Fiabilité moyenne</span>
                  <strong className="pw-stat-value">78%</strong>
                  <span className="pw-stat-change up">+3% ce mois</span>
                </div>
              </div>
            </div>
            <div className="pw-cta-row">
              <button className="pw-btn-primary" onClick={() => navigate('/app/sports')}>
                ⚽ Analyser un match
              </button>
              <button className="pw-btn-secondary" onClick={() => navigate('/app/finance')}>
                📈 Analyser un actif
              </button>
              <button className="pw-btn-ghost">
                📜 Voir l'historique
              </button>
            </div>
          </section>

          {/* ========== SPORTS PREVIEW ========== */}
          <section className="pw-card">
            <div className="pw-card-header">
              <h2>Sports – Matchs du jour</h2>
              <span className="pw-badge">3 matchs</span>
            </div>
            <ul className="pw-match-list">
              <li className="pw-match-item">
                <div className="pw-match-info">
                  <strong className="pw-match-title">PSG vs Marseille</strong>
                  <p className="pw-match-meta">
                    <span className="pw-league">🇫🇷 Ligue 1</span>
                    <span className="pw-form">Forme : V V N D V</span>
                  </p>
                </div>
                <div className="pw-probas">
                  <div className="pw-proba-item home">
                    <span className="pw-proba-label">Domicile</span>
                    <span className="pw-proba-value">72%</span>
                    <div className="pw-proba-bar" style={{width: '72%'}}></div>
                  </div>
                  <div className="pw-proba-item draw">
                    <span className="pw-proba-label">Nul</span>
                    <span className="pw-proba-value">18%</span>
                    <div className="pw-proba-bar" style={{width: '18%'}}></div>
                  </div>
                  <div className="pw-proba-item away">
                    <span className="pw-proba-label">Extérieur</span>
                    <span className="pw-proba-value">10%</span>
                    <div className="pw-proba-bar" style={{width: '10%'}}></div>
                  </div>
                </div>
                <button className="pw-btn-small">Analyser</button>
              </li>
              <li className="pw-match-item">
                <div className="pw-match-info">
                  <strong className="pw-match-title">Real Madrid vs Barça</strong>
                  <p className="pw-match-meta">
                    <span className="pw-league">🇪🇸 La Liga</span>
                    <span className="pw-form">Forme : V V V N V</span>
                  </p>
                </div>
                <div className="pw-probas">
                  <div className="pw-proba-item home">
                    <span className="pw-proba-label">Domicile</span>
                    <span className="pw-proba-value">55%</span>
                    <div className="pw-proba-bar" style={{width: '55%'}}></div>
                  </div>
                  <div className="pw-proba-item draw">
                    <span className="pw-proba-label">Nul</span>
                    <span className="pw-proba-value">25%</span>
                    <div className="pw-proba-bar" style={{width: '25%'}}></div>
                  </div>
                  <div className="pw-proba-item away">
                    <span className="pw-proba-label">Extérieur</span>
                    <span className="pw-proba-value">20%</span>
                    <div className="pw-proba-bar" style={{width: '20%'}}></div>
                  </div>
                </div>
                <button className="pw-btn-small">Analyser</button>
              </li>
              <li className="pw-match-item">
                <div className="pw-match-info">
                  <strong className="pw-match-title">Liverpool vs Man City</strong>
                  <p className="pw-match-meta">
                    <span className="pw-league">🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League</span>
                    <span className="pw-form">Forme : V N V V D</span>
                  </p>
                </div>
                <div className="pw-probas">
                  <div className="pw-proba-item home">
                    <span className="pw-proba-label">Domicile</span>
                    <span className="pw-proba-value">48%</span>
                    <div className="pw-proba-bar" style={{width: '48%'}}></div>
                  </div>
                  <div className="pw-proba-item draw">
                    <span className="pw-proba-label">Nul</span>
                    <span className="pw-proba-value">28%</span>
                    <div className="pw-proba-bar" style={{width: '28%'}}></div>
                  </div>
                  <div className="pw-proba-item away">
                    <span className="pw-proba-label">Extérieur</span>
                    <span className="pw-proba-value">24%</span>
                    <div className="pw-proba-bar" style={{width: '24%'}}></div>
                  </div>
                </div>
                <button className="pw-btn-small">Analyser</button>
              </li>
            </ul>
          </section>

          {/* ========== FINANCE PREVIEW ========== */}
          <section className="pw-card">
            <div className="pw-card-header">
              <h2>Finance – Actifs surveillés</h2>
              <span className="pw-badge">Top 5</span>
            </div>
            <div className="pw-table-wrapper">
              <table className="pw-table">
                <thead>
                  <tr>
                    <th>Ticker</th>
                    <th>Nom</th>
                    <th>Prix</th>
                    <th>Variation</th>
                    <th>Tendance IA</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><strong>AAPL</strong></td>
                    <td>Apple Inc.</td>
                    <td>195.42 $</td>
                    <td className="pw-change up">+1.23%</td>
                    <td>
                      <span className="pw-trend up">
                        <span className="pw-trend-icon">⬆️</span>
                        UP (0.68)
                      </span>
                    </td>
                    <td><button className="pw-btn-small">Étudier</button></td>
                  </tr>
                  <tr>
                    <td><strong>TSLA</strong></td>
                    <td>Tesla Inc.</td>
                    <td>242.10 $</td>
                    <td className="pw-change down">-0.84%</td>
                    <td>
                      <span className="pw-trend down">
                        <span className="pw-trend-icon">⬇️</span>
                        DOWN (0.61)
                      </span>
                    </td>
                    <td><button className="pw-btn-small">Étudier</button></td>
                  </tr>
                  <tr>
                    <td><strong>MSFT</strong></td>
                    <td>Microsoft Corp.</td>
                    <td>378.91 $</td>
                    <td className="pw-change up">+0.45%</td>
                    <td>
                      <span className="pw-trend neutral">
                        <span className="pw-trend-icon">↔️</span>
                        NEUTRAL (0.52)
                      </span>
                    </td>
                    <td><button className="pw-btn-small">Étudier</button></td>
                  </tr>
                  <tr>
                    <td><strong>GOOGL</strong></td>
                    <td>Alphabet Inc.</td>
                    <td>142.65 $</td>
                    <td className="pw-change up">+2.10%</td>
                    <td>
                      <span className="pw-trend up">
                        <span className="pw-trend-icon">⬆️</span>
                        UP (0.73)
                      </span>
                    </td>
                    <td><button className="pw-btn-small">Étudier</button></td>
                  </tr>
                  <tr>
                    <td><strong>AMZN</strong></td>
                    <td>Amazon.com Inc.</td>
                    <td>178.32 $</td>
                    <td className="pw-change down">-1.56%</td>
                    <td>
                      <span className="pw-trend down">
                        <span className="pw-trend-icon">⬇️</span>
                        DOWN (0.59)
                      </span>
                    </td>
                    <td><button className="pw-btn-small">Étudier</button></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          {/* ========== ANALYSE IA ========== */}
          <section className="pw-card pw-ai">
            <div className="pw-card-header">
              <h2>💡 Analyse IA</h2>
              <span className="pw-badge glow">Analyse automatique</span>
            </div>
            <p className="pw-ai-summary">
              L'IA estime une probabilité <strong>élevée de victoire à domicile</strong> pour le 
              prochain match sélectionné (PSG vs Marseille), mais souligne plusieurs incertitudes 
              liées à la forme récente et aux absences clés.
            </p>
            <ul className="pw-ai-points">
              <li className="pw-ai-point positive">
                <span className="pw-ai-icon">✔️</span>
                <span>Avantage domicile significatif (+12% probabilité)</span>
              </li>
              <li className="pw-ai-point positive">
                <span className="pw-ai-icon">✔️</span>
                <span>Forme offensive supérieure sur les 5 derniers matchs</span>
              </li>
              <li className="pw-ai-point warning">
                <span className="pw-ai-icon">⚠️</span>
                <span>Défense fragile sur coups de pied arrêtés</span>
              </li>
              <li className="pw-ai-point negative">
                <span className="pw-ai-icon">❌</span>
                <span>Absence du meneur de jeu clé (blessure)</span>
              </li>
            </ul>
            <div className="pw-ai-footer">
              <div className="pw-confidence-meter">
                <div className="pw-confidence-label">
                  <span>Confiance du modèle</span>
                  <strong>74%</strong>
                </div>
                <div className="pw-confidence-bar">
                  <div className="pw-confidence-fill" style={{width: '74%'}}></div>
                </div>
              </div>
              <div className="pw-disclaimer">
                <span className="pw-disclaimer-icon">ℹ️</span>
                <p>
                  <strong>Projet éducatif</strong> – PredictWise est conçu pour l'apprentissage. 
                  Ces analyses ne constituent en aucun cas des conseils de pari ou d'investissement financier.
                </p>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

export default DashboardPremium;
