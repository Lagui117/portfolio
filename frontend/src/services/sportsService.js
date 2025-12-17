/**
 * Service pour les analyses sportives.
 */

import apiClient from './apiClient';

/**
 * Obtient une prediction pour un match.
 * @param {string} matchId - Identifiant du match.
 * @returns {Promise<Object>} Prediction avec analyse GPT.
 */
export async function getSportsPrediction(matchId) {
  const response = await apiClient.get(`/sports/predict/${matchId}`);
  return response.data;
}

/**
 * Recupere la liste des matchs disponibles.
 * @param {Object} [options] - Options de filtrage.
 * @param {string} [options.sport] - Type de sport.
 * @param {string} [options.league] - Ligue specifique.
 * @param {number} [options.limit] - Nombre max de resultats.
 * @returns {Promise<Object>} Liste des matchs.
 */
export async function getMatches(options = {}) {
  const response = await apiClient.get('/sports/matches', { params: options });
  return response.data;
}

/**
 * Recupere l'historique des predictions sports.
 * @param {Object} [options] - Options de pagination.
 * @param {number} [options.limit] - Nombre max de resultats.
 * @param {number} [options.offset] - Offset pour pagination.
 * @returns {Promise<Object>} Historique des predictions.
 */
export async function getSportsPredictionsHistory(options = {}) {
  const response = await apiClient.get('/sports/predictions/history', { params: options });
  return response.data;
}
