/**
 * AdminDashboard - Tableau de bord administrateur.
 * Vue d'ensemble du système et actions rapides.
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import adminService from '../services/adminService';
import '../styles/admin.css';

const AdminDashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [activity, setActivity] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [statsData, activityData] = await Promise.all([
        adminService.getStats(),
        adminService.getActivity({ limit: 10 })
      ]);
      setStats(statsData);
      setActivity(activityData.activities || []);
    } catch (err) {
      console.error('Erreur chargement données admin:', err);
      setError('Erreur de chargement des données');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="admin-page">
        <div className="admin-loading">
          <div className="spinner"></div>
          <p>Chargement du panneau d'administration...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="admin-page">
        <div className="admin-error">
          <span className="error-icon">⚠️</span>
          <p>{error}</p>
          <button className="btn btn-primary" onClick={loadData}>Réessayer</button>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-page">
      <header className="admin-header">
        <div className="admin-header-content">
          <div>
            <h1>Administration</h1>
            <p className="admin-subtitle">Supervision et gestion du système</p>
          </div>
          <div className="admin-user-badge">
            <span className="badge-icon">🛡️</span>
            <span>{user?.username}</span>
          </div>
        </div>
      </header>

      {/* Stats Cards */}
      <section className="admin-stats-grid">
        <div className="admin-stat-card">
          <div className="stat-icon users">👥</div>
          <div className="stat-content">
            <div className="stat-value">{stats?.users?.total || 0}</div>
            <div className="stat-label">Utilisateurs</div>
            <div className="stat-detail">
              {stats?.users?.active || 0} actifs • {stats?.users?.admins || 0} admins
            </div>
          </div>
        </div>

        <div className="admin-stat-card">
          <div className="stat-icon predictions">📊</div>
          <div className="stat-content">
            <div className="stat-value">{stats?.predictions?.total || 0}</div>
            <div className="stat-label">Analyses</div>
            <div className="stat-detail">
              {stats?.predictions?.sports || 0} sports • {stats?.predictions?.finance || 0} finance
            </div>
          </div>
        </div>

        <div className="admin-stat-card">
          <div className="stat-icon new-users">📈</div>
          <div className="stat-content">
            <div className="stat-value">+{stats?.users?.new_this_week || 0}</div>
            <div className="stat-label">Nouveaux cette semaine</div>
            <div className="stat-detail">Inscriptions 7 derniers jours</div>
          </div>
        </div>

        <div className="admin-stat-card">
          <div className="stat-icon consultations">🔍</div>
          <div className="stat-content">
            <div className="stat-value">{stats?.consultations?.total || 0}</div>
            <div className="stat-label">Consultations</div>
            <div className="stat-detail">Total historique</div>
          </div>
        </div>
      </section>

      {/* Quick Actions */}
      <section className="admin-section">
        <h2 className="section-title">Actions rapides</h2>
        <div className="admin-actions-grid">
          <Link to="/admin/users" className="admin-action-card">
            <span className="action-icon">👥</span>
            <span className="action-label">Gérer les utilisateurs</span>
            <span className="action-arrow">→</span>
          </Link>
          <Link to="/admin/activity" className="admin-action-card">
            <span className="action-icon">📋</span>
            <span className="action-label">Voir les logs</span>
            <span className="action-arrow">→</span>
          </Link>
          <Link to="/dashboard" className="admin-action-card">
            <span className="action-icon">📈</span>
            <span className="action-label">Dashboard utilisateur</span>
            <span className="action-arrow">→</span>
          </Link>
        </div>
      </section>

      {/* Recent Activity */}
      <section className="admin-section">
        <div className="section-header-row">
          <h2 className="section-title">Activité récente</h2>
          <Link to="/admin/activity" className="view-all-link">Voir tout →</Link>
        </div>
        
        <div className="activity-table-container">
          <table className="activity-table">
            <thead>
              <tr>
                <th>Type</th>
                <th>Utilisateur</th>
                <th>Détails</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {activity.length === 0 ? (
                <tr>
                  <td colSpan="4" className="empty-row">Aucune activité récente</td>
                </tr>
              ) : (
                activity.map((item, index) => (
                  <tr key={index}>
                    <td>
                      <span className={`activity-badge ${item.type}`}>
                        {item.type === 'prediction' ? '📊' : '🔍'}
                        {item.subtype || item.type}
                      </span>
                    </td>
                    <td className="user-cell">{item.user}</td>
                    <td className="details-cell">{item.details}</td>
                    <td className="date-cell">
                      {item.timestamp 
                        ? new Date(item.timestamp).toLocaleString('fr-FR', {
                            day: '2-digit',
                            month: '2-digit',
                            hour: '2-digit',
                            minute: '2-digit'
                          })
                        : '-'
                      }
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
};

export default AdminDashboard;
