/**
 * Service Administration - Communication avec l'API admin.
 */

import apiClient from './apiClient';

const adminService = {
  // ============================================
  // GESTION UTILISATEURS
  // ============================================
  
  /**
   * Liste les utilisateurs avec pagination et filtres.
   */
  async getUsers({ page = 1, perPage = 20, role, status, search } = {}) {
    const params = { page, per_page: perPage };
    if (role) params.role = role;
    if (status) params.status = status;
    if (search) params.search = search;
    
    const response = await apiClient.get('/admin/users', { params });
    return response.data;
  },

  /**
   * Récupère les détails d'un utilisateur.
   */
  async getUser(userId) {
    const response = await apiClient.get(`/admin/users/${userId}`);
    return response.data;
  },

  /**
   * Met à jour un utilisateur.
   */
  async updateUser(userId, data) {
    const response = await apiClient.put(`/admin/users/${userId}`, data);
    return response.data;
  },

  /**
   * Désactive ou supprime un utilisateur.
   */
  async deleteUser(userId, hard = false) {
    const response = await apiClient.delete(`/admin/users/${userId}`, {
      params: { hard: hard.toString() }
    });
    return response.data;
  },

  /**
   * Promouvoir en admin.
   */
  async promoteUser(userId) {
    const response = await apiClient.post(`/admin/users/${userId}/promote`);
    return response.data;
  },

  /**
   * Rétrograder en user standard.
   */
  async demoteUser(userId) {
    const response = await apiClient.post(`/admin/users/${userId}/demote`);
    return response.data;
  },

  // ============================================
  // STATISTIQUES
  // ============================================
  
  /**
   * Récupère les statistiques système.
   */
  async getStats() {
    const response = await apiClient.get('/admin/stats');
    return response.data;
  },

  // ============================================
  // LOGS D'ACTIVITÉ
  // ============================================
  
  /**
   * Récupère les logs d'activité.
   */
  async getActivity({ limit = 50, type } = {}) {
    const params = { limit };
    if (type) params.type = type;
    
    const response = await apiClient.get('/admin/activity', { params });
    return response.data;
  }
};

export default adminService;
