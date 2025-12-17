/**
 * Service Chat IA - Communication avec le Copilote PredictWise.
 */

import apiClient from './apiClient';

const chatService = {
  /**
   * Envoie un message au Copilote IA.
   * @param {string} message - Message de l'utilisateur
   * @param {object} context - Contexte optionnel (analyse en cours, etc.)
   * @param {string} conversationId - ID de conversation pour continuité
   * @returns {Promise<object>} Réponse de l'assistant
   */
  async sendMessage(message, context = {}, conversationId = null) {
    const response = await apiClient.post('/chat/message', {
      message,
      context,
      conversation_id: conversationId
    });
    return response.data;
  },

  /**
   * Récupère l'historique des conversations.
   * @param {number} limit - Nombre max de messages
   * @param {string} conversationId - Filtrer par conversation
   * @returns {Promise<object>} Historique des messages
   */
  async getHistory(limit = 50, conversationId = null) {
    const params = { limit };
    if (conversationId) {
      params.conversation_id = conversationId;
    }
    const response = await apiClient.get('/chat/history', { params });
    return response.data;
  },

  /**
   * Efface l'historique des conversations.
   * @param {string} conversationId - Effacer une conversation spécifique
   * @returns {Promise<object>} Confirmation
   */
  async clearHistory(conversationId = null) {
    const params = conversationId ? { conversation_id: conversationId } : {};
    const response = await apiClient.delete('/chat/clear', { params });
    return response.data;
  },

  /**
   * Récupère des suggestions de questions.
   * @param {string} domain - 'sports', 'finance' ou 'general'
   * @returns {Promise<object>} Liste de suggestions
   */
  async getSuggestions(domain = 'general') {
    const response = await apiClient.get('/chat/suggestions', {
      params: { domain }
    });
    return response.data;
  }
};

export default chatService;
