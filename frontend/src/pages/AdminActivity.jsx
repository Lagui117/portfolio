/**
 * AdminActivity - Logs d'activité système.
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import adminService from '../services/adminService';
import '../styles/admin.css';

const AdminActivity = () => {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('');
  const [limit, setLimit] = useState(50);

  useEffect(() => {
    loadActivity();
  }, [filter, limit]);

  const loadActivity = async () => {
    try {
      setLoading(true);
      const data = await adminService.getActivity({
        limit,
        type: filter || undefined
      });
      setActivities(data.activities || []);
    } catch (err) {
      console.error('Erreur chargement activité:', err);
      setError('Erreur de chargement des logs');
    } finally {
      setLoading(false);
    }
  };

  const getActivityIcon = (type, subtype) => {
    if (type === 'prediction') {
      return subtype === 'sports' ? '⚽' : '📈';
    }
    if (type === 'consultation') {
      return '🔍';
    }
    return '📋';
  };

  return (
    <div className="admin-page">
      <header className="admin-header">
        <div className="admin-header-content">
          <div>
            <Link to="/admin" className="back-link">← Retour</Link>
            <h1>Logs d'activité</h1>
            <p className="admin-subtitle">Historique des actions utilisateurs</p>
          </div>
        </div>
      </header>

      {/* Filtres */}
      <section className="admin-filters">
        <div className="filter-group">
          <select
            className="filter-select"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="">Toutes les activités</option>
            <option value="prediction">Analyses uniquement</option>
            <option value="consultation">Consultations uniquement</option>
          </select>
        </div>
        <div className="filter-group">
          <select
            className="filter-select"
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
          >
            <option value={25}>25 dernières</option>
            <option value={50}>50 dernières</option>
            <option value={100}>100 dernières</option>
            <option value={200}>200 dernières</option>
          </select>
        </div>
        <button className="btn btn-secondary" onClick={loadActivity}>
          Actualiser
        </button>
      </section>

      {error && (
        <div className="admin-alert error">
          <span>⚠️</span> {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      {/* Activity List */}
      <section className="admin-section">
        {loading ? (
          <div className="admin-loading">
            <div className="spinner"></div>
          </div>
        ) : (
          <div className="activity-list">
            {activities.length === 0 ? (
              <div className="empty-state">
                <span className="empty-icon">📋</span>
                <p>Aucune activité enregistrée</p>
              </div>
            ) : (
              activities.map((item, index) => (
                <div key={index} className="activity-item">
                  <div className="activity-icon">
                    {getActivityIcon(item.type, item.subtype)}
                  </div>
                  <div className="activity-content">
                    <div className="activity-main">
                      <span className="activity-user">{item.user}</span>
                      <span className="activity-action">
                        {item.type === 'prediction' ? 'a lancé une analyse' : 'a consulté'}
                      </span>
                      <span className={`activity-type ${item.subtype || item.type}`}>
                        {item.subtype || item.type}
                      </span>
                    </div>
                    <div className="activity-details">
                      {item.details !== 'N/A' && item.details}
                    </div>
                  </div>
                  <div className="activity-time">
                    {item.timestamp
                      ? new Date(item.timestamp).toLocaleString('fr-FR', {
                          day: '2-digit',
                          month: 'short',
                          hour: '2-digit',
                          minute: '2-digit'
                        })
                      : '-'
                    }
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </section>
    </div>
  );
};

export default AdminActivity;
