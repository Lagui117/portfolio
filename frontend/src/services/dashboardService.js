/**
 * Service Dashboard - API pour les statistiques utilisateur avancées.
 */

import apiClient from './apiClient';

const dashboardService = {
  /**
   * Récupère les stats détaillées de l'utilisateur.
   * @param {string} period - '7d', '30d', '90d', 'all'
   */
  async getStats(period = '30d') {
    const response = await apiClient.get(`/dashboard/stats?period=${period}`);
    return response.data;
  },

  /**
   * Récupère les métriques de performance pour graphiques.
   */
  async getPerformance() {
    const response = await apiClient.get('/dashboard/performance');
    return response.data;
  },

  /**
   * Récupère l'historique des prédictions avec filtres.
   * @param {Object} params - Paramètres de filtrage et pagination
   */
  async getHistory(params = {}) {
    const queryParams = new URLSearchParams();
    
    if (params.type) queryParams.append('type', params.type);
    if (params.page) queryParams.append('page', params.page);
    if (params.per_page) queryParams.append('per_page', params.per_page);
    if (params.sort) queryParams.append('sort', params.sort);
    if (params.order) queryParams.append('order', params.order);
    if (params.ticker) queryParams.append('ticker', params.ticker);
    if (params.from_date) queryParams.append('from_date', params.from_date);
    if (params.to_date) queryParams.append('to_date', params.to_date);

    const response = await apiClient.get(`/dashboard/predictions/history?${queryParams}`);
    return response.data;
  },

  /**
   * Récupère l'overview (alias de getStats pour compatibilité).
   */
  async getOverview() {
    return this.getStats('30d');
  },

  /**
   * Récupère les KPIs avancés (inclus dans getStats).
   */
  async getKPIs() {
    return this.getStats('30d');
  }
};

export default dashboardService;
