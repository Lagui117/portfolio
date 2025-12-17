/**
 * Page d'administration.
 * Accessible uniquement aux administrateurs.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../services/apiClient';
import { extractErrorMessage } from '../services/authService';
import { ErrorBanner, SuccessBanner } from '../components/UIComponents';
import '../styles/admin.css';

function AdminPage() {
  const navigate = useNavigate();
  
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Pagination et filtres
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('');

  useEffect(() => {
    fetchStats();
    fetchUsers();
  }, [page, roleFilter]);

  const fetchStats = async () => {
    try {
      const response = await apiClient.get('/users/stats');
      setStats(response.data.stats);
    } catch (err) {
      if (err.response?.status === 403) {
        setError('Acces refuse. Vous devez etre administrateur.');
        setTimeout(() => navigate('/app'), 2000);
      }
    }
  };

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const params = {
        page,
        per_page: 10,
      };
      if (roleFilter) params.role = roleFilter;
      if (searchTerm) params.search = searchTerm;
      
      const response = await apiClient.get('/users', { params });
      setUsers(response.data.users);
      setTotalPages(response.data.pagination.pages);
    } catch (err) {
      if (err.response?.status === 403) {
        setError('Acces refuse. Vous devez etre administrateur.');
      } else {
        setError(extractErrorMessage(err));
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    fetchUsers();
  };

  const handlePromote = async (userId) => {
    try {
      setError('');
      await apiClient.post(`/users/${userId}/promote`);
      setSuccess('Utilisateur promu en administrateur');
      fetchUsers();
      fetchStats();
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  };

  const handleDemote = async (userId) => {
    try {
      setError('');
      await apiClient.post(`/users/${userId}/demote`);
      setSuccess('Droits administrateur revoques');
      fetchUsers();
      fetchStats();
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  };

  const handleToggleActive = async (userId, currentStatus) => {
    try {
      setError('');
      await apiClient.put(`/users/${userId}`, { is_active: !currentStatus });
      setSuccess(currentStatus ? 'Utilisateur desactive' : 'Utilisateur active');
      fetchUsers();
      fetchStats();
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  };

  const handleDelete = async (userId, username) => {
    if (!window.confirm(`Supprimer l'utilisateur ${username} ?`)) {
      return;
    }
    
    try {
      setError('');
      await apiClient.delete(`/users/${userId}`);
      setSuccess('Utilisateur supprime');
      fetchUsers();
      fetchStats();
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  };

  return (
    <div className="admin-page">
      <div className="admin-container">
        <h1>Panneau d'administration</h1>
        
        <ErrorBanner message={error} onClose={() => setError('')} />
        <SuccessBanner message={success} onClose={() => setSuccess('')} />
        
        {/* Statistiques globales */}
        {stats && (
          <section className="admin-section">
            <h2>Statistiques globales</h2>
            <div className="stats-grid">
              <div className="stat-card">
                <span className="stat-value">{stats.total_users}</span>
                <span className="stat-label">Utilisateurs totaux</span>
              </div>
              <div className="stat-card">
                <span className="stat-value">{stats.active_users}</span>
                <span className="stat-label">Utilisateurs actifs</span>
              </div>
              <div className="stat-card">
                <span className="stat-value">{stats.admin_users}</span>
                <span className="stat-label">Administrateurs</span>
              </div>
              <div className="stat-card">
                <span className="stat-value">{stats.inactive_users}</span>
                <span className="stat-label">Utilisateurs inactifs</span>
              </div>
            </div>
          </section>
        )}
        
        {/* Liste des utilisateurs */}
        <section className="admin-section">
          <h2>Gestion des utilisateurs</h2>
          
          {/* Filtres */}
          <div className="filters-bar">
            <form onSubmit={handleSearch} className="search-form">
              <input
                type="text"
                placeholder="Rechercher..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
              <button type="submit" className="btn btn-primary">
                Rechercher
              </button>
            </form>
            
            <select
              value={roleFilter}
              onChange={(e) => {
                setRoleFilter(e.target.value);
                setPage(1);
              }}
              className="role-filter"
            >
              <option value="">Tous les roles</option>
              <option value="user">Utilisateurs</option>
              <option value="admin">Administrateurs</option>
            </select>
          </div>
          
          {/* Tableau des utilisateurs */}
          {loading ? (
            <div className="loading">Chargement...</div>
          ) : (
            <>
              <table className="users-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Username</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Statut</th>
                    <th>Inscription</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map(user => (
                    <tr key={user.id} className={!user.is_active ? 'inactive' : ''}>
                      <td>{user.id}</td>
                      <td>{user.username}</td>
                      <td>{user.email}</td>
                      <td>
                        <span className={`role-badge ${user.is_admin ? 'admin' : 'user'}`}>
                          {user.is_admin ? 'Admin' : 'User'}
                        </span>
                      </td>
                      <td>
                        <span className={`status-badge ${user.is_active ? 'active' : 'inactive'}`}>
                          {user.is_active ? 'Actif' : 'Inactif'}
                        </span>
                      </td>
                      <td>
                        {user.created_at 
                          ? new Date(user.created_at).toLocaleDateString('fr-FR')
                          : '-'}
                      </td>
                      <td className="actions">
                        {user.is_admin ? (
                          <button
                            className="btn btn-sm btn-warning"
                            onClick={() => handleDemote(user.id)}
                            title="Revoquer admin"
                          >
                            Revoquer
                          </button>
                        ) : (
                          <button
                            className="btn btn-sm btn-success"
                            onClick={() => handlePromote(user.id)}
                            title="Promouvoir admin"
                          >
                            Promouvoir
                          </button>
                        )}
                        <button
                          className={`btn btn-sm ${user.is_active ? 'btn-warning' : 'btn-success'}`}
                          onClick={() => handleToggleActive(user.id, user.is_active)}
                        >
                          {user.is_active ? 'Desactiver' : 'Activer'}
                        </button>
                        <button
                          className="btn btn-sm btn-danger"
                          onClick={() => handleDelete(user.id, user.username)}
                        >
                          Supprimer
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              
              {/* Pagination */}
              {totalPages > 1 && (
                <div className="pagination">
                  <button
                    className="btn btn-secondary"
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                  >
                    Precedent
                  </button>
                  <span className="page-info">
                    Page {page} sur {totalPages}
                  </span>
                  <button
                    className="btn btn-secondary"
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                  >
                    Suivant
                  </button>
                </div>
              )}
            </>
          )}
        </section>
      </div>
    </div>
  );
}

export default AdminPage;
