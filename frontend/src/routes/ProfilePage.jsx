/**
 * Page Profil utilisateur.
 * Affiche les informations du compte et permet de les modifier.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMe, extractErrorMessage } from '../services/authService';
import apiClient from '../services/apiClient';
import { ErrorBanner, SuccessBanner } from '../components/UIComponents';
import '../styles/profile.css';

function ProfilePage() {
  const navigate = useNavigate();
  
  const [user, setUser] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Formulaire de modification
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    username: '',
  });
  
  // Formulaire de mot de passe
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });

  useEffect(() => {
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      setLoading(true);
      const response = await getMe(true);
      setUser(response.user);
      setStats(response.stats);
      setFormData({
        first_name: response.user.first_name || '',
        last_name: response.user.last_name || '',
        email: response.user.email || '',
        username: response.user.username || '',
      });
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData(prev => ({ ...prev, [name]: value }));
  };

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    
    try {
      const response = await apiClient.put('/auth/me', formData);
      setUser(response.data.user);
      setSuccess('Profil mis a jour avec succes');
      setEditing(false);
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    
    if (passwordData.new_password !== passwordData.confirm_password) {
      setError('Les mots de passe ne correspondent pas');
      return;
    }
    
    try {
      await apiClient.put('/auth/password', {
        current_password: passwordData.current_password,
        new_password: passwordData.new_password,
      });
      setSuccess('Mot de passe modifie avec succes');
      setShowPasswordForm(false);
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: '',
      });
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  };

  if (loading) {
    return (
      <div className="profile-page">
        <div className="loading">Chargement...</div>
      </div>
    );
  }

  return (
    <div className="profile-page">
      <div className="profile-container">
        <h1>Mon Profil</h1>
        
        <ErrorBanner message={error} onClose={() => setError('')} />
        <SuccessBanner message={success} onClose={() => setSuccess('')} />
        
        {/* Informations utilisateur */}
        <section className="profile-section">
          <div className="section-header">
            <h2>Informations personnelles</h2>
            {!editing && (
              <button 
                className="btn btn-secondary"
                onClick={() => setEditing(true)}
              >
                Modifier
              </button>
            )}
          </div>
          
          {editing ? (
            <form onSubmit={handleUpdateProfile} className="profile-form">
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="first_name">Prenom</label>
                  <input
                    type="text"
                    id="first_name"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleFormChange}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="last_name">Nom</label>
                  <input
                    type="text"
                    id="last_name"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleFormChange}
                  />
                </div>
              </div>
              
              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleFormChange}
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="username">Nom d'utilisateur</label>
                <input
                  type="text"
                  id="username"
                  name="username"
                  value={formData.username}
                  onChange={handleFormChange}
                />
              </div>
              
              <div className="form-actions">
                <button type="submit" className="btn btn-primary">
                  Enregistrer
                </button>
                <button 
                  type="button" 
                  className="btn btn-secondary"
                  onClick={() => setEditing(false)}
                >
                  Annuler
                </button>
              </div>
            </form>
          ) : (
            <div className="profile-info">
              <div className="info-row">
                <span className="label">Nom complet:</span>
                <span className="value">
                  {user?.first_name || '-'} {user?.last_name || '-'}
                </span>
              </div>
              <div className="info-row">
                <span className="label">Email:</span>
                <span className="value">{user?.email}</span>
              </div>
              <div className="info-row">
                <span className="label">Nom d'utilisateur:</span>
                <span className="value">{user?.username}</span>
              </div>
              <div className="info-row">
                <span className="label">Role:</span>
                <span className={`value role-badge ${user?.is_admin ? 'admin' : 'user'}`}>
                  {user?.is_admin ? 'Administrateur' : 'Utilisateur'}
                </span>
              </div>
              <div className="info-row">
                <span className="label">Membre depuis:</span>
                <span className="value">
                  {user?.created_at ? new Date(user.created_at).toLocaleDateString('fr-FR') : '-'}
                </span>
              </div>
              <div className="info-row">
                <span className="label">Derniere connexion:</span>
                <span className="value">
                  {user?.last_login ? new Date(user.last_login).toLocaleString('fr-FR') : '-'}
                </span>
              </div>
            </div>
          )}
        </section>
        
        {/* Statistiques */}
        {stats && (
          <section className="profile-section">
            <h2>Statistiques</h2>
            <div className="stats-grid">
              <div className="stat-card">
                <span className="stat-value">{stats.total_predictions}</span>
                <span className="stat-label">Predictions totales</span>
              </div>
              <div className="stat-card">
                <span className="stat-value">{stats.sports_predictions}</span>
                <span className="stat-label">Predictions sportives</span>
              </div>
              <div className="stat-card">
                <span className="stat-value">{stats.finance_predictions}</span>
                <span className="stat-label">Predictions financieres</span>
              </div>
              <div className="stat-card">
                <span className="stat-value">{stats.total_consultations}</span>
                <span className="stat-label">Consultations</span>
              </div>
            </div>
          </section>
        )}
        
        {/* Changement de mot de passe */}
        <section className="profile-section">
          <div className="section-header">
            <h2>Securite</h2>
            {!showPasswordForm && (
              <button 
                className="btn btn-secondary"
                onClick={() => setShowPasswordForm(true)}
              >
                Changer le mot de passe
              </button>
            )}
          </div>
          
          {showPasswordForm && (
            <form onSubmit={handleChangePassword} className="profile-form">
              <div className="form-group">
                <label htmlFor="current_password">Mot de passe actuel</label>
                <input
                  type="password"
                  id="current_password"
                  name="current_password"
                  value={passwordData.current_password}
                  onChange={handlePasswordChange}
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="new_password">Nouveau mot de passe</label>
                <input
                  type="password"
                  id="new_password"
                  name="new_password"
                  value={passwordData.new_password}
                  onChange={handlePasswordChange}
                  required
                  minLength={8}
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="confirm_password">Confirmer le mot de passe</label>
                <input
                  type="password"
                  id="confirm_password"
                  name="confirm_password"
                  value={passwordData.confirm_password}
                  onChange={handlePasswordChange}
                  required
                />
              </div>
              
              <div className="form-actions">
                <button type="submit" className="btn btn-primary">
                  Modifier
                </button>
                <button 
                  type="button" 
                  className="btn btn-secondary"
                  onClick={() => {
                    setShowPasswordForm(false);
                    setPasswordData({
                      current_password: '',
                      new_password: '',
                      confirm_password: '',
                    });
                  }}
                >
                  Annuler
                </button>
              </div>
            </form>
          )}
        </section>
        
        {/* Lien admin si admin */}
        {user?.is_admin && (
          <section className="profile-section">
            <h2>Administration</h2>
            <p>Vous avez acces au panneau d'administration.</p>
            <button 
              className="btn btn-primary"
              onClick={() => navigate('/app/admin')}
            >
              Acceder au panneau admin
            </button>
          </section>
        )}
      </div>
    </div>
  );
}

export default ProfilePage;
