/**
 * Service Risk - API pour la gestion des risques.
 */

import apiClient from './apiClient';

const riskService = {
  /**
   * Évalue le risque d'une prédiction.
   * @param {Object} predictionData - Données de la prédiction
   */
  async assessRisk(predictionData) {
    const response = await apiClient.post('/risk/assess', predictionData);
    return response.data;
  },

  /**
   * Récupère le risque global du portefeuille.
   * @param {string} period - '7d', '30d', 'all'
   */
  async getPortfolioRisk(period = '30d') {
    const response = await apiClient.get('/risk/portfolio', { params: { period } });
    return response.data;
  },

  /**
   * Récupère le risque d'une prédiction spécifique.
   * @param {number} predictionId - ID de la prédiction
   */
  async getPredictionRisk(predictionId) {
    const response = await apiClient.get(`/risk/prediction/${predictionId}`);
    return response.data;
  },

  /**
   * Récupère les alertes de risque actives.
   */
  async getAlerts() {
    const response = await apiClient.get('/risk/alerts');
    return response.data;
  }
};

export default riskService;
