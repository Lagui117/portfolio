/**
 * AdminUsers - Gestion des utilisateurs.
 * Liste, filtres, actions sur les comptes.
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import adminService from '../services/adminService';
import '../styles/admin.css';

const AdminUsers = () => {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState([]);
  const [pagination, setPagination] = useState({});
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Filtres
  const [filters, setFilters] = useState({
    search: '',
    role: '',
    status: ''
  });
  const [page, setPage] = useState(1);

  useEffect(() => {
    loadUsers();
  }, [page, filters]);

  const loadUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await adminService.getUsers({
        page,
        perPage: 15,
        ...filters
      });
      setUsers(data.users || []);
      setPagination(data.pagination || {});
    } catch (err) {
      console.error('Erreur chargement utilisateurs:', err);
      setError('Erreur de chargement des utilisateurs');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setPage(1);
  };

  const handlePromote = async (userId) => {
    try {
      setActionLoading(userId);
      await adminService.promoteUser(userId);
      setSuccess('Utilisateur promu administrateur');
      loadUsers();
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur lors de la promotion');
    } finally {
      setActionLoading(null);
      setTimeout(() => setSuccess(null), 3000);
    }
  };

  const handleDemote = async (userId) => {
    try {
      setActionLoading(userId);
      await adminService.demoteUser(userId);
      setSuccess('Droits administrateur révoqués');
      loadUsers();
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur lors de la rétrogradation');
    } finally {
      setActionLoading(null);
      setTimeout(() => setSuccess(null), 3000);
    }
  };

  const handleToggleActive = async (userId, currentStatus) => {
    try {
      setActionLoading(userId);
      await adminService.updateUser(userId, { is_active: !currentStatus });
      setSuccess(currentStatus ? 'Compte désactivé' : 'Compte réactivé');
      loadUsers();
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur lors de la modification');
    } finally {
      setActionLoading(null);
      setTimeout(() => setSuccess(null), 3000);
    }
  };

  return (
    <div className="admin-page">
      <header className="admin-header">
        <div className="admin-header-content">
          <div>
            <Link to="/admin" className="back-link">← Retour</Link>
            <h1>Gestion des utilisateurs</h1>
            <p className="admin-subtitle">{pagination.total || 0} utilisateurs enregistrés</p>
          </div>
        </div>
      </header>

      {/* Messages */}
      {error && (
        <div className="admin-alert error">
          <span>⚠️</span> {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}
      {success && (
        <div className="admin-alert success">
          <span>✓</span> {success}
        </div>
      )}

      {/* Filtres */}
      <section className="admin-filters">
        <div className="filter-group">
          <input
            type="text"
            className="filter-input"
            placeholder="Rechercher par email ou username..."
            value={filters.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
          />
        </div>
        <div className="filter-group">
          <select
            className="filter-select"
            value={filters.role}
            onChange={(e) => handleFilterChange('role', e.target.value)}
          >
            <option value="">Tous les rôles</option>
            <option value="user">Utilisateurs</option>
            <option value="admin">Administrateurs</option>
          </select>
        </div>
        <div className="filter-group">
          <select
            className="filter-select"
            value={filters.status}
            onChange={(e) => handleFilterChange('status', e.target.value)}
          >
            <option value="">Tous les statuts</option>
            <option value="active">Actifs</option>
            <option value="inactive">Inactifs</option>
          </select>
        </div>
        <button className="btn btn-secondary" onClick={loadUsers}>
          Actualiser
        </button>
      </section>

      {/* Table */}
      <section className="admin-section">
        {loading ? (
          <div className="admin-loading">
            <div className="spinner"></div>
          </div>
        ) : (
          <>
            <div className="users-table-container">
              <table className="users-table">
                <thead>
                  <tr>
                    <th>Utilisateur</th>
                    <th>Email</th>
                    <th>Rôle</th>
                    <th>Statut</th>
                    <th>Inscrit le</th>
                    <th>Analyses</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.length === 0 ? (
                    <tr>
                      <td colSpan="7" className="empty-row">Aucun utilisateur trouvé</td>
                    </tr>
                  ) : (
                    users.map((user) => (
                      <tr key={user.id} className={!user.is_active ? 'inactive-row' : ''}>
                        <td className="user-cell">
                          <div className="user-info">
                            <span className="user-avatar">
                              {user.username.charAt(0).toUpperCase()}
                            </span>
                            <span className="user-name">{user.username}</span>
                          </div>
                        </td>
                        <td className="email-cell">{user.email}</td>
                        <td>
                          <span className={`role-badge ${user.role}`}>
                            {user.role === 'admin' ? '🛡️ Admin' : '👤 User'}
                          </span>
                        </td>
                        <td>
                          <span className={`status-badge ${user.is_active ? 'active' : 'inactive'}`}>
                            {user.is_active ? 'Actif' : 'Inactif'}
                          </span>
                        </td>
                        <td className="date-cell">
                          {user.created_at 
                            ? new Date(user.created_at).toLocaleDateString('fr-FR')
                            : '-'
                          }
                        </td>
                        <td className="stats-cell">
                          {user.stats?.total_predictions || 0}
                        </td>
                        <td className="actions-cell">
                          {user.id === currentUser?.id ? (
                            <span className="self-badge">Vous</span>
                          ) : (
                            <div className="action-buttons">
                              {user.role === 'user' ? (
                                <button
                                  className="action-btn promote"
                                  onClick={() => handlePromote(user.id)}
                                  disabled={actionLoading === user.id}
                                  title="Promouvoir admin"
                                >
                                  ⬆️
                                </button>
                              ) : (
                                <button
                                  className="action-btn demote"
                                  onClick={() => handleDemote(user.id)}
                                  disabled={actionLoading === user.id}
                                  title="Rétrograder"
                                >
                                  ⬇️
                                </button>
                              )}
                              <button
                                className={`action-btn ${user.is_active ? 'deactivate' : 'activate'}`}
                                onClick={() => handleToggleActive(user.id, user.is_active)}
                                disabled={actionLoading === user.id}
                                title={user.is_active ? 'Désactiver' : 'Réactiver'}
                              >
                                {user.is_active ? '🚫' : '✅'}
                              </button>
                            </div>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {pagination.pages > 1 && (
              <div className="pagination">
                <button
                  className="pagination-btn"
                  disabled={!pagination.has_prev}
                  onClick={() => setPage(p => p - 1)}
                >
                  ← Précédent
                </button>
                <span className="pagination-info">
                  Page {pagination.page} sur {pagination.pages}
                </span>
                <button
                  className="pagination-btn"
                  disabled={!pagination.has_next}
                  onClick={() => setPage(p => p + 1)}
                >
                  Suivant →
                </button>
              </div>
            )}
          </>
        )}
      </section>
    </div>
  );
};

export default AdminUsers;
