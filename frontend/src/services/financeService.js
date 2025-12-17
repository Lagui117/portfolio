/**
 * Service pour les analyses financieres.
 */

import apiClient from './apiClient';

/**
 * Obtient une prediction pour un actif financier.
 * @param {string} ticker - Symbole boursier (ex: AAPL).
 * @param {string} [period='1mo'] - Periode d'analyse.
 * @returns {Promise<Object>} Prediction avec analyse GPT.
 */
export async function getFinancePrediction(ticker, period = '1mo') {
  const response = await apiClient.get(`/finance/predict/${ticker}`, {
    params: { period }
  });
  return response.data;
}

/**
 * Recupere la liste des actifs populaires.
 * @param {Object} [options] - Options de filtrage.
 * @param {string} [options.sector] - Secteur specifique.
 * @param {number} [options.limit] - Nombre max de resultats.
 * @returns {Promise<Object>} Liste des actifs.
 */
export async function getPopularStocks(options = {}) {
  const response = await apiClient.get('/finance/stocks', { params: options });
  return response.data;
}

/**
 * Recupere l'historique des predictions finance.
 * @param {Object} [options] - Options de pagination.
 * @param {number} [options.limit] - Nombre max de resultats.
 * @param {number} [options.offset] - Offset pour pagination.
 * @returns {Promise<Object>} Historique des predictions.
 */
export async function getFinancePredictionsHistory(options = {}) {
  const response = await apiClient.get('/finance/predictions/history', { params: options });
  return response.data;
}
