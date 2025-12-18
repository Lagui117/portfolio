/**
 * Service Watchlist - API pour la gestion des favoris.
 */

import apiClient from './apiClient';

const watchlistService = {
  /**
   * Récupère la watchlist complète.
   * @param {Object} params - Filtres optionnels
   * @param {string} params.type - 'team', 'league', 'ticker', 'crypto'
   * @param {boolean} params.alerts_only - Filtrer par alertes actives
   */
  async getWatchlist(params = {}) {
    const queryParams = new URLSearchParams();
    if (params.type) queryParams.append('type', params.type);
    if (params.alerts_only) queryParams.append('alerts_only', 'true');
    
    const response = await apiClient.get(`/watchlist?${queryParams}`);
    return response.data;
  },

  /**
   * Ajoute un item à la watchlist.
   * @param {Object} item - Item à ajouter
   * @param {string} item.item_type - Type ('team', 'league', 'ticker', 'crypto')
   * @param {string} item.item_id - ID ou symbole
   * @param {string} item.item_name - Nom affichable
   * @param {Object} item.item_data - Données additionnelles (logo, etc.)
   * @param {string} item.notes - Notes optionnelles
   */
  async addToWatchlist(item) {
    const response = await apiClient.post('/watchlist', item);
    return response.data;
  },

  /**
   * Met à jour un item de la watchlist.
   * @param {number} itemId - ID de l'item
   * @param {Object} updates - Mises à jour (notes, alerts_enabled, etc.)
   */
  async updateItem(itemId, updates) {
    const response = await apiClient.put(`/watchlist/${itemId}`, updates);
    return response.data;
  },

  /**
   * Supprime un item de la watchlist.
   * @param {number} itemId - ID de l'item
   */
  async removeFromWatchlist(itemId) {
    const response = await apiClient.delete(`/watchlist/${itemId}`);
    return response.data;
  },

  /**
   * Vérifie si un item est dans la watchlist.
   * @param {string} type - Type d'item
   * @param {string} id - ID de l'item
   */
  async checkInWatchlist(type, id) {
    const response = await apiClient.get(`/watchlist/check?type=${type}&id=${id}`);
    return response.data;
  },

  /**
   * Ajoute plusieurs items en une fois.
   * @param {Array} items - Liste d'items à ajouter
   */
  async bulkAdd(items) {
    const response = await apiClient.post('/watchlist/bulk', { items });
    return response.data;
  },

  /**
   * Active/désactive les alertes sur un item.
   * @param {number} itemId - ID de l'item
   * @param {boolean} enabled - Activer ou désactiver
   * @param {Object} config - Configuration des alertes
   */
  async toggleAlerts(itemId, enabled, config = null) {
    return this.updateItem(itemId, {
      alerts_enabled: enabled,
      alert_config: config
    });
  }
};

export default watchlistService;
