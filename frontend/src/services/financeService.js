/**
 * Service pour les analyses financières.
 */

import apiClient from './apiClient';

/**
 * Obtient une prédiction pour un actif financier.
 */
export async function getFinancePrediction(ticker, period = '1mo') {
  const response = await apiClient.get(`/finance/predict/${ticker}`, {
    params: { period }
  });
  return response.data;
}

/**
 * Récupère la liste des actifs populaires.
 */
export async function getPopularStocks(options = {}) {
  const response = await apiClient.get('/finance/stocks', { params: options });
  return response.data;
}

/**
 * Récupère l'historique des prédictions finance.
 */
export async function getFinancePredictionsHistory(options = {}) {
  const response = await apiClient.get('/finance/predictions/history', { params: options });
  return response.data;
}

/**
 * Suggestions de tickers populaires.
 */
export const POPULAR_TICKERS = [
  { symbol: 'AAPL', name: 'Apple Inc.' },
  { symbol: 'GOOGL', name: 'Alphabet (Google)' },
  { symbol: 'MSFT', name: 'Microsoft' },
  { symbol: 'TSLA', name: 'Tesla' },
  { symbol: 'AMZN', name: 'Amazon' },
];
